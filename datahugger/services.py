import io
import logging
import os
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Union
from urllib.parse import quote

import requests
from jsonpath_ng import parse

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
    META_FILE_HASH_TYPE_VALUE = "md5"

    def _get_file_meta_link(self, record):

        return "{}/api/access/datafile/{}".format(
            self.base_url, record["dataFile"]["id"]
        )


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
    META_FILE_HASH_TYPE_VALUE = "md5"


class OSFDataset(DatasetDownloader):
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
    META_FILE_HASH_TYPE_VALUE = "sha256"


class DataDryadDataset(DatasetDownloader):
    """Downloader for DataDryad repository."""

    REGEXP_ID = r"datadryad\.org[\:]*[43]{0,3}\/stash\/dataset\/doi:(.*)"

    # the base entry point of the REST API
    API_URL = "https://datadryad.org/api/v2"

    # jsonpaths to file attributes
    META_FILE_NAME_JSONPATH = "path"
    META_FILE_SIZE_JSONPATH = "size"

    @property
    def files(self):

        if hasattr(self, "_files"):
            return self._files

        doi_safe = quote(f"doi:{self.api_record_id}", safe="")
        dataset_metadata_url = self.API_URL + "/datasets/" + doi_safe

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


class DataOneDataset(DatasetDownloader):
    """Downloader for DataOne repositories."""

    REGEXP_ID = r"view/doi:(.*)"

    # the base entry point of the REST API
    API_URL = "https://cn.dataone.org/cn/v2/object/"

    @property
    def files(self):

        if hasattr(self, "_files"):
            return self._files

        doi_safe = quote(f"doi:{self.api_record_id}", safe="")

        res = requests.get(self.API_URL + doi_safe)
        meta_tree = ET.fromstring(res.content)

        print(self.url)
        print(self.api_record_id)
        print(res.content)

        x = []
        for data_elem in meta_tree.find("dataset"):
            if data_elem.tag in ["otherEntity", "dataTable"]:
                x.append(
                    {
                        "file_link": data_elem.find(
                            "./physical/distribution/online/url[@function='download']"
                        ).text,
                        "file_name": data_elem.find("entityName").text,
                        "file_size": data_elem.find("./physical/size").text,
                        "file_hash": None,
                        "file_hash_type": None,
                    }
                )

        self._files = x
        return self._files


class MendeleyDataset(DatasetDownloader):
    """Downloader for Mendeley repository."""

    REGEXP_ID_WITH_VERSION = r"data\.mendeley\.com\/datasets\/([0-9a-z]+)\/(\d+)"
    REGEXP_ID = r"data\.mendeley\.com\/datasets\/([0-9a-z]+)"

    # the base entry point of the REST API
    API_URL = "https://data.mendeley.com/public-api/"

    # version url
    API_URL_VERSION = API_URL + "datasets/{api_record_id}/versions"

    # the files and metadata about the dataset
    API_URL_META = (
        API_URL + "datasets/{api_record_id}/files?folder_id=root&version={version}"
    )

    # jsonpaths to file attributes
    META_FILE_LINK_JSONPATH = "content_details.download_url"
    META_FILE_NAME_JSONPATH = "filename"
    META_FILE_SIZE_JSONPATH = "size"
    META_FILE_HASH_JSONPATH = "content_details.sha256_hash"
    META_FILE_HASH_TYPE_VALUE = "sha256"

    def _pre_files(self):

        if self.version is None:
            r_version = requests.get(
                self.API_URL_VERSION.format(api_record_id=self.api_record_id)
            )
            self.version = r_version.json()[-1]["version"]


class GitHubDataset(DatasetDownloader):
    """Downloader for GitHub repository."""

    API_URL = "https://github.com/"
    REGEXP_ID = r"github\.com\/([a-zA-Z0-9]+\/[a-zA-Z0-9]+)[\/]*.*"

    def _get(self, output_folder: Union[Path, str], *args, **kwargs):

        res = requests.get(
            f"{self.API_URL}{self.api_record_id}/archive/refs/heads/master.zip"
        )
        z = zipfile.ZipFile(io.BytesIO(res.content))
        z.extractall(output_folder)


class HuggingFaceDataset(DatasetDownloader):
    """Downloader for Huggingface repository."""

    REGEXP_ID = r"huggingface.co/datasets/(.*)"

    def _get(
        self,
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

        load_dataset(self.api_record_id, cache_dir=output_folder, **kwargs)
