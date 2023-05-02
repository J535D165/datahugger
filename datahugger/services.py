import io
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Union
from urllib.parse import quote

import requests
from jsonpath_ng import parse

from datahugger.base import DatasetDownloader
from datahugger.base import DatasetResult


class ZenodoDataset(DatasetDownloader, DatasetResult):
    """Downloader for Zenodo repository.

    For Zenodo records, new versions have new identifiers.
    """

    REGEXP_ID = r"zenodo\.org\/record\/(\d+).*"

    # the base entry point of the REST API
    API_URL = "https://zenodo.org/api/"

    # the files and metadata about the dataset
    API_URL_META = "{api_url}records/{api_record_id}"
    META_FILES_JSONPATH = "files"

    # paths to file attributes
    ATTR_NAME_JSONPATH = "key"
    ATTR_FILE_LINK_JSONPATH = "links.self"
    ATTR_SIZE_JSONPATH = "size"
    ATTR_HASH_JSONPATH = "checksum"

    def _get_attr_hash(self, record):

        return self._get_attr_attr(record, self.ATTR_HASH_JSONPATH).split(
            ":"
        )[1]

    def _get_attr_hash_type(self, record):

        return self._get_attr_attr(record, self.ATTR_HASH_JSONPATH).split(
            ":"
        )[0]


class DataverseDataset(DatasetDownloader, DatasetResult):
    """Downloader for Dataverse repository."""

    REGEXP_ID = r"dataset\.xhtml\?persistentId=(.*)"

    # the files and metadata about the dataset
    API_URL_META = "{base_url}/api/datasets/:persistentId/?persistentId={api_record_id}"
    META_FILES_JSONPATH = "data.latestVersion.files"

    # paths to file attributes
    ATTR_NAME_JSONPATH = "dataFile.filename"
    ATTR_SIZE_JSONPATH = "dataFile.filesize"
    ATTR_HASH_JSONPATH = "dataFile.md5"
    ATTR_HASH_TYPE_VALUE = "md5"

    def _get_attr_link(self, record):

        return "{}/api/access/datafile/{}".format(
            self.base_url, record["dataFile"]["id"]
        )


class FigShareDataset(DatasetDownloader, DatasetResult):
    """Downloader for FigShare repository."""

    REGEXP_ID_AND_VERSION = r"articles\/.*\/.*\/(\d+)\/(\d+)"
    REGEXP_ID = r"articles\/.*\/.*\/(\d+)"

    # the base entry point of the REST API
    API_URL = "https://api.figshare.com/v2"

    # the files and metadata about the dataset
    API_URL_META = "{api_url}/articles/{api_record_id}/files"

    # paths to file attributes
    ATTR_FILE_LINK_JSONPATH = "download_url"
    ATTR_NAME_JSONPATH = "name"
    ATTR_SIZE_JSONPATH = "size"
    ATTR_HASH_JSONPATH = "computed_md5"
    ATTR_HASH_TYPE_VALUE = "md5"


class Djehuty(FigShareDataset):
    """Downloader for Djehuty repository."""

    REGEXP_ID_AND_VERSION = r"articles\/.*\/(\d+)\/(\d+)"
    REGEXP_ID = r"articles\/.*\/(\d+)"

    # the base entry point of the REST API
    API_URL = "https://data.4tu.nl/v2"


class OSFDataset(DatasetDownloader, DatasetResult):
    """Downloader for OSF repository."""

    REGEXP_ID = r"osf\.io\/(.*)/"

    # the base entry point of the REST API
    API_URL = "https://api.osf.io/v2/registrations/"

    # the files and metadata about the dataset
    API_URL_META = "{api_url}{api_record_id}/files/osfstorage/?format=jsonapi"
    META_FILES_JSONPATH = "data"

    PAGINATION_JSONPATH = "links.next"

    # paths to file attributes
    ATTR_KIND_JSONPATH = "attributes.kind"

    ATTR_FILE_LINK_JSONPATH = "links.download"
    ATTR_FOLDER_LINK_JSONPATH = "relationships.files.links.related.href"

    ATTR_NAME_JSONPATH = "attributes.name"
    ATTR_SIZE_JSONPATH = "attributes.size"
    ATTR_HASH_JSONPATH = "attributes.extra.hashes.sha256"
    ATTR_HASH_TYPE_VALUE = "sha256"


class DataDryadDataset(DatasetDownloader, DatasetResult):
    """Downloader for DataDryad repository."""

    REGEXP_ID = r"datadryad\.org[\:]*[43]{0,3}\/stash\/dataset\/doi:(.*)"

    # the base entry point of the REST API
    API_URL = "https://datadryad.org/api/v2"

    # paths to file attributes
    ATTR_NAME_JSONPATH = "path"
    ATTR_SIZE_JSONPATH = "size"

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
                    "kind": "file",
                    "link": self._get_attr_link(f),
                    "name": self._get_attr_name(f),
                    "size": self._get_attr_size(f),
                    "hash": self._get_attr_hash(f),
                    "hash_type": self._get_attr_hash_type(f),
                }
            )

        self._files = x
        return self._files

    def _get_attr_link(self, record):

        return "https://datadryad.org" + record["_links"]["stash:file-download"]["href"]


class DataOneDataset(DatasetDownloader, DatasetResult):
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

        x = []
        for data_elem in meta_tree.find("dataset"):
            if data_elem.tag in ["otherEntity", "dataTable"]:
                x.append(
                    {
                        "link": data_elem.find(
                            "./physical/distribution/online/url[@function='download']"
                        ).text,
                        "name": data_elem.find("entityName").text,
                        "size": data_elem.find("./physical/size").text,
                        "hash": None,
                        "hash_type": None,
                    }
                )

        self._files = x
        return self._files


class DSpaceDataset(DatasetDownloader, DatasetResult):
    """Downloader for DSpaceDataset repositories."""

    REGEXP_ID = r"handle/(\d+\/\d+)"

    # paths to file attributes
    ATTR_KIND_JSONPATH = "attributes.kind"

    ATTR_FILE_LINK_JSONPATH = "link"

    ATTR_NAME_JSONPATH = "name"
    ATTR_SIZE_JSONPATH = "sizeBytes"
    ATTR_HASH_JSONPATH = "checkSum.checkSumAlgorithm"
    ATTR_HASH_TYPE_VALUE = "checkSum.value"

    def _get_attr_link(self, record):

        return self.base_url + record["retrieveLink"]

    def _pre_files(self):

        handle_id_url = "{base_url}/rest/handle/{api_record_id}".format(
            base_url=self.base_url, api_record_id=self.api_record_id
        )
        res = requests.get(handle_id_url)

        # set the API_URL_META
        self.API_URL_META = self.base_url + res.json()["link"] + "/bitstreams"


class MendeleyDataset(DatasetDownloader, DatasetResult):
    """Downloader for Mendeley repository."""

    REGEXP_ID_WITH_VERSION = r"data\.mendeley\.com\/datasets\/([0-9a-z]+)\/(\d+)"
    REGEXP_ID = r"data\.mendeley\.com\/datasets\/([0-9a-z]+)"

    # the base entry point of the REST API
    API_URL = "https://data.mendeley.com/public-api/"

    # version url
    API_URL_VERSION = "{api_url}datasets/{api_record_id}/versions"

    # the files and metadata about the dataset
    API_URL_META = (
        "{api_url}datasets/{api_record_id}/files?folder_id=root&version={version}"
    )

    # paths to file attributes
    ATTR_FILE_LINK_JSONPATH = "content_details.download_url"
    ATTR_NAME_JSONPATH = "filename"
    ATTR_SIZE_JSONPATH = "size"
    ATTR_HASH_JSONPATH = "content_details.sha256_hash"
    ATTR_HASH_TYPE_VALUE = "sha256"

    def _pre_files(self):

        if self.version is None:
            r_version = requests.get(
                self.API_URL_VERSION.format(
                    api_url=self.API_URL,
                    api_record_id=self.api_record_id)
            )
            self.version = r_version.json()[-1]["version"]


class GitHubDataset(DatasetDownloader, DatasetResult):
    """Downloader for GitHub repository."""

    API_URL = "https://github.com/"
    REGEXP_ID = r"github\.com\/([a-zA-Z0-9]+\/[a-zA-Z0-9]+)[\/]*.*"

    def _get(self, output_folder: Union[Path, str], *args, **kwargs):

        res = requests.get(
            f"{self.API_URL}{self.api_record_id}/archive/refs/heads/master.zip"
        )
        z = zipfile.ZipFile(io.BytesIO(res.content))
        z.extractall(output_folder)


class HuggingFaceDataset(DatasetDownloader, DatasetResult):
    """Downloader for Huggingface repository."""

    REGEXP_ID = r"huggingface.co/datasets/(.*)"

    def _get(
        self,
        output_folder: Union[Path, str],
        **kwargs,
    ):

        try:
            from datasets import load_dataset
        except ImportError as err:
            raise ImportError(
                "Install 'datasets' to use HuggingFace Datasets"
                " or use 'pip install datahugger[all]'"
            ) from err

        load_dataset(self.api_record_id, cache_dir=output_folder, **kwargs)
