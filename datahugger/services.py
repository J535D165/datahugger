import io
import logging
import os
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Union
from urllib.parse import quote

import requests
from jsonpath_ng import jsonpath, parse

from datahugger.base import DatasetDownloader, DatasetResult
from datahugger.utils import _is_url


class ZenodoDataset(DatasetDownloader, DatasetResult):
    """Downloader for Zenodo repository.

    For Zenodo records, new versions have new identifiers.
    """

    REGEXP_ID = r"zenodo\.org\/record\/(\d+).*"

    # the base entry point of the REST API
    API_URL = "https://zenodo.org/api/"

    # the files and metadata about the dataset
    API_URL_META = API_URL + "records/{api_record_id}"
    META_FILES_JSONPATH = "files"

    # jsonpaths to file attributes
    META_FILE_NAME_JSONPATH = "key"
    META_FILE_LINK_JSONPATH = "links.self"
    META_FILE_SIZE_JSONPATH = "size"
    META_FILE_HASH_JSONPATH = "checksum"

    def _get_file_meta_hash(self, record):

        return self._get_file_meta_attr(record, self.META_FILE_HASH_JSONPATH).split(
            ":"
        )[1]

    def _get_file_meta_hash_type(self, record):

        return self._get_file_meta_attr(record, self.META_FILE_HASH_JSONPATH).split(
            ":"
        )[0]


class DataverseDataset(DatasetDownloader, DatasetResult):
    """Downloader for Dataverse repository."""

    REGEXP_ID = r"dataset\.xhtml\?persistentId=(.*)"

    # the base entry point of the REST API
    # API_URL = "https://zenodo.org/api/"

    # the files and metadata about the dataset
    API_URL_META = "{base_url}/api/datasets/:persistentId/?persistentId={api_record_id}"
    META_FILES_JSONPATH = "data.latestVersion.files"

    # jsonpaths to file attributes
    META_FILE_NAME_JSONPATH = "dataFile.filename"
    META_FILE_SIZE_JSONPATH = "dataFile.filesize"
    META_FILE_HASH_JSONPATH = "dataFile.md5"

    def _get_file_meta_link(self, record):

        return "{}/api/access/datafile/{}".format(
            self.base_url, record["dataFile"]["id"]
        )

    def _get_file_meta_hash_type(self, record):

        return "md5"


class FigShareDataset(DatasetDownloader):
    """Downloader for FigShare repository."""

    REGEXP_ID_AND_VERSION = r"articles\/dataset\/.*\/(\d+)\/(\d+)"
    REGEXP_ID = r"articles\/dataset\/.*\/(\d+)"

    # the base entry point of the REST API
    API_URL = "https://api.figshare.com/v2"

    # the files and metadata about the dataset
    API_URL_META = API_URL + "/articles/{api_record_id}/files"

    # jsonpaths to file attributes
    META_FILE_LINK_JSONPATH = "download_url"
    META_FILE_NAME_JSONPATH = "name"
    META_FILE_SIZE_JSONPATH = "size"
    META_FILE_HASH_JSONPATH = "computed_md5"

    def _get_file_meta_hash_type(self, record):

        return "md5"


class OSFDownload(DatasetDownloader):
    """Downloader for OSF repository."""

    REGEXP_ID = r"osf\.io\/(.*)/"

    # the base entry point of the REST API
    API_URL = "https://api.osf.io/v2/registrations/"

    # the files and metadata about the dataset
    API_URL_META = API_URL + "{api_record_id}/files/osfstorage/?format=jsonapi"
    META_FILES_JSONPATH = "data"

    # jsonpaths to file attributes
    META_FILE_LINK_JSONPATH = "links.download"
    META_FILE_NAME_JSONPATH = "attributes.name"
    META_FILE_SIZE_JSONPATH = "attributes.size"
    META_FILE_HASH_JSONPATH = "attributes.extra.hashes.sha256"

    def _get_file_meta_hash_type(self, record):

        return "sha256"


class DataDryadDataset(DatasetDownloader):
    """Downloader for DataDryad repository."""

    API_URL = "https://datadryad.org/api/v2"
    REGEXP_ID = r"datadryad\.org[\:]*[43]{0,3}\/stash\/dataset\/doi:(.*)"

    # jsonpaths to file attributes
    META_FILE_NAME_JSONPATH = "path"
    META_FILE_SIZE_JSONPATH = "size"

    @property
    def files(self):

        if hasattr(self, "_files"):
            return self._files

        datadryad_doi_safe = quote(f"doi:{self.api_record_id}", safe="")
        dataset_metadata_url = self.API_URL + "/datasets/" + datadryad_doi_safe

        res = requests.get(dataset_metadata_url)
        dataset_metadata = res.json()

        # get the latest version of the dataset
        latest_version = dataset_metadata["_links"]["stash:version"]["href"]
        url_latest_version = "https://datadryad.org" + latest_version + "/files"

        res = requests.get(url_latest_version)
        res.json()["_embedded"]["stash:files"]

        if hasattr(self, "META_FILES_JSONPATH"):
            jsonpath_expression = parse(self.META_FILES_JSONPATH)
            files_raw = jsonpath_expression.find(res.json())[0].value
        else:
            files_raw = res.json()

        x = []
        for f in files_raw["_embedded"]["stash:files"]:
            x.append(
                {
                    "file_link": self._get_file_meta_link(f),
                    "file_name": self._get_file_meta_name(f),
                    "file_size": self._get_file_meta_size(f),
                    "file_hash": self._get_file_meta_hash(f),
                    "file_hash_type": self._get_file_meta_hash_type(f),
                }
            )

        self._files = x
        return self._files

    def _get_file_meta_link(self, record):

        return "https://datadryad.org" + record["_links"]["stash:file-download"]["href"]


class DataOneDownload(DatasetDownloader):
    """Downloader for DataOne repositories."""

    API_URL = "https://cn.dataone.org/cn/v2/object/"
    REGEXP_ID = r"DataOne.co/datasets/(.*)"

    def _get(
        self,
        record_id: Union[str, int] = None,
        output_folder: Union[Path, str] = None,
        doi: str = None,
        **kwargs,
    ):

        res = requests.get(self.API_URL + quote("doi:" + doi, safe=""))
        meta_tree = ET.fromstring(res.content)

        for data_elem in meta_tree.find("dataset"):
            if data_elem.tag in ["otherEntity", "dataTable"]:
                logging.debug(data_elem)
                self.download_file(
                    data_elem.find(
                        "./physical/distribution/online/url[@function='download']"
                    ).text,  # noqa
                    output_folder,
                    data_elem.find("entityName").text,
                    file_size=data_elem.find("./physical/size").text,
                )


class MendeleyDownload(DatasetDownloader):
    """Downloader for Mendeley repository."""

    REGEXP_ID_WITH_VERSION = r"data\.mendeley\.com\/datasets\/([0-9a-z]+)\/(\d+)"
    REGEXP_ID = r"data\.mendeley\.com\/datasets\/([0-9a-z]+)"

    API_VERSION = "https://data.mendeley.com/public-api/datasets/{}/versions"  # noqa
    API_FILES = "https://data.mendeley.com/public-api/datasets/{}/files?folder_id=root&version={}"  # noqa

    def _get(
        self,
        record_id: Union[str, int],
        output_folder: Union[Path, str],
        version: int = None,
        **kwargs,
    ):

        if version is None:
            r_version = requests.get(self.API_VERSION.format(record_id))
            version = r_version.json()[-1]["version"]

        r_meta = requests.get(self.API_FILES.format(record_id, version))
        dataset_metadata = r_meta.json()

        for f in dataset_metadata:
            logging.debug(f)
            self.download_file(
                f["content_details"]["download_url"],
                output_folder,
                f["filename"],
                file_size=f["size"],
                file_hash=f["content_details"]["sha256_hash"],
                file_hash_type="sha256",
            )


class GitHubDownload(DatasetDownloader):
    """Downloader for GitHub repository."""

    API_URL = "https://github.com/"
    REGEXP_ID = r"github\.com\/([a-zA-Z0-9]+\/[a-zA-Z0-9]+)[\/]*.*"

    def _get(self, record_id: str, output_folder: Union[Path, str], *args, **kwargs):

        res = requests.get(f"{self.API_URL}{record_id}/archive/refs/heads/master.zip")
        z = zipfile.ZipFile(io.BytesIO(res.content))
        z.extractall(output_folder)


class HuggingFaceDownload(DatasetDownloader):
    """Downloader for Huggingface repository."""

    REGEXP_ID = r"huggingface.co/datasets/(.*)"

    def _get(
        self,
        record_id: Union[str, int],
        output_folder: Union[Path, str],
        **kwargs,
    ):

        try:
            from datasets import load_dataset
        except ImportError:
            raise ImportError(
                "Install 'datasets' to use HuggingFace Datasets"
                " or use 'pip install datahugger[all]'"
            )

        load_dataset(record_id, cache_dir=output_folder, **kwargs)
