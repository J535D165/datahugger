import io
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Union
from urllib.parse import quote
from urllib.parse import urlparse

import requests
from jsonpath_ng.jsonpath import Fields
from jsonpath_ng.jsonpath import Slice

from datahugger.base import DatasetDownloader
from datahugger.utils import _get_url


class ArXivDataset(DatasetDownloader):
    """Downloader for ArXiv publication."""

    REGEXP_ID = r"https://arxiv\.org/abs/(?P<record_id>.*)"

    @property
    def files(self):
        return [
            {
                "link": f"https://arxiv.org/pdf/{self._params['record_id']}.pdf",
                "name": self._params["record_id"].split("/")[-1] + ".pdf",
                "size": None,
                "hash": None,
                "hash_type": None,
            }
        ]


class DataverseDataset(DatasetDownloader):
    """Downloader for Dataverse repository."""

    REGEXP_ID = r"(?P<type>dataset|file)\.xhtml\?persistentId=(?P<record_id>.*)"

    # paths to file attributes
    ATTR_NAME_JSONPATH = "filename"
    ATTR_SIZE_JSONPATH = "filesize"
    ATTR_HASH_JSONPATH = "md5"
    ATTR_HASH_TYPE_VALUE = "md5"

    @property
    def API_URL_META(self):
        if self._params.get("version", None):
            v = self._params["version"]
        else:
            v = ":latest-published"

        if self._params.get("type", None) == "file":
            return "{base_url}/api/files/:persistentId/?persistentId={record_id}"
        else:
            return (
                "{base_url}/api/datasets/:persistentId/versions/"
                f"{v}/?persistentId={{record_id}}"
            )

    @property
    def META_FILES_JSONPATH(self):
        if self._params.get("type", None) == "file":
            return "data.dataFile"
        else:
            return "data.files[*].dataFile"

    def _get_attr_link(self, record, base_url=None):
        return f"{base_url}/api/access/datafile/{record['id']}"


class DataDryadDataset(DatasetDownloader):
    """Downloader for DataDryad repository."""

    REGEXP_ID = r"datadryad\.org[\:]*[43]{0,3}\/stash\/dataset\/doi:(?P<record_id>.*)"

    # the base entry point of the REST API
    API_URL = "https://datadryad.org/api/v2"

    # the files and metadata about the dataset
    API_URL_META = "{api_url}{record_id}/files/osfstorage/?format=jsonapi"
    META_FILES_JSONPATH = (
        Fields("_embedded").child(Fields("stash:files")).child(Slice())
    )

    # paths to file attributes
    ATTR_NAME_JSONPATH = "path"
    ATTR_SIZE_JSONPATH = "size"

    @property
    def API_URL_META(self):
        doi_safe = quote(f"doi:{self._params['record_id']}", safe="")
        dataset_metadata_url = self.API_URL + "/datasets/" + doi_safe

        res = requests.get(dataset_metadata_url)
        res.raise_for_status()
        dataset_metadata = res.json()

        # get the latest version of the dataset
        latest_version = dataset_metadata["_links"]["stash:version"]["href"]
        return f"https://datadryad.org{latest_version}/files"

    def _get_attr_link(self, record, base_url):
        return base_url + record["_links"]["stash:file-download"]["href"]


class DataOneDataset(DatasetDownloader):
    """Downloader for DataOne repositories."""

    REGEXP_ID = r"view/doi:(?P<record_id>.*)"

    # the base entry point of the REST API
    API_URL = "https://cn.dataone.org/cn/v2/object/"

    @property
    def files(self):
        if hasattr(self, "_files"):
            return self._files

        doi_safe = quote(f"doi:{self._params['record_id']}", safe="")

        res = requests.get(self.API_URL + doi_safe)
        res.raise_for_status()
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


class PangaeaDataset(DatasetDownloader):
    """Downloader for PangaeaDataset repository."""

    REGEXP_ID = r"doi\.pangaea\.de/(?P<record_id>.*)"

    # the base entry point of the REST API
    API_URL = "https://doi.pangaea.de/"

    @property
    def files(self):
        # get the difference between collection and file
        r = requests.get(
            f"{self.API_URL}{self._params['record_id']}?format=metadata_jsonld"
        )
        r.raise_for_status()
        dists = r.json()["distribution"]

        if isinstance(dists, dict):
            dists = [dists]

        files = []
        for d in dists:
            if d["encodingFormat"] in ["text/tab-separated-values", "application/zip"]:
                r_filename = requests.head(d["contentUrl"])
                content_d = r_filename.headers["content-disposition"]

                files.append(
                    {
                        "link": d["contentUrl"],
                        "name": re.findall("filename=(.+)", content_d)[0],
                        "size": None,
                        "hash": None,
                        "hash_type": None,
                    }
                )

        return files


class DSpaceDataset(DatasetDownloader):
    """Downloader for DSpaceDataset repositories."""

    REGEXP_ID = r"handle/(?P<record_id>\d+\/\d+)"

    # paths to file attributes
    ATTR_KIND_JSONPATH = "attributes.kind"

    ATTR_FILE_LINK_JSONPATH = "link"

    ATTR_NAME_JSONPATH = "name"
    ATTR_SIZE_JSONPATH = "sizeBytes"
    ATTR_HASH_JSONPATH = "checkSum.checkSumAlgorithm"
    ATTR_HASH_TYPE_VALUE = "checkSum.value"

    def _get_attr_link(self, record, base_url):
        return base_url + record["retrieveLink"]

    @property
    def API_URL_META(self):
        uri = urlparse(_get_url(self.resource))
        base_url = uri.scheme + "://" + uri.netloc

        handle_id_url = f"{base_url}/rest/handle/{self._params['record_id']}"
        res = requests.get(handle_id_url)
        res.raise_for_status()

        return base_url + res.json()["link"] + "/bitstreams"


class FigShareDataset(DatasetDownloader):
    """Downloader for FigShare repository."""

    REGEXP_ID = r"articles\/.*?\/.*?\/(?P<record_id>\d+)(?:\/(?P<version>\d+)|)"

    # the base entry point of the REST API
    API_URL = "https://api.figshare.com/v2"

    # the files and metadata about the dataset
    META_FILES_JSONPATH = "files[*]"

    # paths to file attributes
    ATTR_FILE_LINK_JSONPATH = "download_url"
    ATTR_NAME_JSONPATH = "name"
    ATTR_SIZE_JSONPATH = "size"
    ATTR_HASH_JSONPATH = "computed_md5"
    ATTR_HASH_TYPE_VALUE = "md5"

    @property
    def API_URL_META(self):
        s = "{api_url}/articles/{record_id}"

        if self._params.get("version", None):
            s += "/versions/{version}"

        return s


class DjehutyDataset(FigShareDataset):
    """Downloader for Djehuty repository."""

    REGEXP_ID = r"articles\/.*?\/(?P<record_id>\d+)(?:\/(?P<version>\d+)|)"

    # the base entry point of the REST API
    API_URL = "https://data.4tu.nl/v2"


class GitHubDataset(DatasetDownloader):
    """Downloader for GitHub repository."""

    API_URL = "https://github.com/"
    REGEXP_ID = r"github\.com\/(?P<record_id>[a-zA-Z0-9]+\/[a-zA-Z0-9]+)[\/]*.*"

    def _get(self, output_folder: Union[Path, str], *args, **kwargs):
        res = requests.get(
            f"{self.API_URL}{self._params['record_id']}/archive/refs/heads/master.zip"
        )
        z = zipfile.ZipFile(io.BytesIO(res.content))
        z.extractall(output_folder)

    @property
    def files(self):
        # at the moment, .files is not available for GitHub
        raise NotImplementedError("'files' is not available for GitHub")


class HuggingFaceDataset(DatasetDownloader):
    """Downloader for Huggingface repository."""

    REGEXP_ID = r"huggingface.co/datasets/(?P<record_id>.*)"

    def _get(
        self,
        output_folder: Union[Path, str],
    ):
        try:
            from datasets import load_dataset
        except ImportError as err:
            raise ImportError(
                "Install 'datasets' to use HuggingFace Datasets"
                " or use 'pip install datahugger[all]'"
            ) from err

        params = self.params if self.params else {}
        load_dataset(self._params["record_id"], cache_dir=output_folder, **params)

    @property
    def files(self):
        # at the moment, .files is not available for HuggingFace
        raise NotImplementedError("'files' is not available for HuggingFace")


class MendeleyDataset(DatasetDownloader):
    """Downloader for Mendeley repository."""

    REGEXP_ID = r"data\.mendeley\.com\/datasets\/(?P<record_id>[0-9a-z]+)(?:\/(?P<version>\d+)|)"  # noqa

    # the base entry point of the REST API
    API_URL = "https://data.mendeley.com/public-api/"

    # version url
    API_URL_VERSION = "{api_url}datasets/{record_id}/versions"

    # the files and metadata about the dataset
    API_URL_META = (
        "{api_url}datasets/{record_id}/files?folder_id=root&version={version}"
    )

    # paths to file attributes
    ATTR_FILE_LINK_JSONPATH = "content_details.download_url"
    ATTR_NAME_JSONPATH = "filename"
    ATTR_SIZE_JSONPATH = "size"
    ATTR_HASH_JSONPATH = "content_details.sha256_hash"
    ATTR_HASH_TYPE_VALUE = "sha256"


class OSFDataset(DatasetDownloader):
    """Downloader for OSF repository."""

    REGEXP_ID = r"osf\.io\/(?P<record_id>.*)/"

    # the base entry point of the REST API
    API_URL = "https://api.osf.io/v2/registrations/"

    # the files and metadata about the dataset
    API_URL_META = "{api_url}{record_id}/files/osfstorage/?format=jsonapi"
    META_FILES_JSONPATH = "data[*]"

    PAGINATION_JSONPATH = "links.next"

    # paths to file attributes
    ATTR_KIND_JSONPATH = "attributes.kind"

    ATTR_FILE_LINK_JSONPATH = "links.download"
    ATTR_FOLDER_LINK_JSONPATH = "relationships.files.links.related.href"

    ATTR_NAME_JSONPATH = "attributes.name"
    ATTR_SIZE_JSONPATH = "attributes.size"
    ATTR_HASH_JSONPATH = "attributes.extra.hashes.sha256"
    ATTR_HASH_TYPE_VALUE = "sha256"


class ZenodoDataset(DatasetDownloader):
    """Downloader for Zenodo repository.

    For Zenodo records, new versions have new identifiers.
    """

    REGEXP_ID = r"zenodo\.org\/record\/(?P<record_id>\d+).*"

    # the base entry point of the REST API
    API_URL = "https://zenodo.org/api/"

    # the files and metadata about the dataset
    API_URL_META = "{api_url}records/{record_id}"
    META_FILES_JSONPATH = "files[*]"

    # paths to file attributes
    ATTR_NAME_JSONPATH = "key"
    ATTR_FILE_LINK_JSONPATH = "links.self"
    ATTR_SIZE_JSONPATH = "size"
    ATTR_HASH_JSONPATH = "checksum"

    def _get_attr_hash(self, record):
        return self._get_attr_attr(record, self.ATTR_HASH_JSONPATH).split(":")[1]

    def _get_attr_hash_type(self, record):
        return self._get_attr_attr(record, self.ATTR_HASH_JSONPATH).split(":")[0]
