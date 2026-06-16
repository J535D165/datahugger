import io
import os
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Union
from urllib.parse import quote
from urllib.parse import unquote
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

    REGEXP_ID = r"datadryad\.org[\:]*[43]{0,3}\/dataset\/doi:(?P<record_id>.*)"

    # the base entry point of the REST API
    API_URL = "https://datadryad.org/api/v2"

    # the files and metadata about the dataset
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
        return base_url + record["_links"]["stash:download"]["href"]


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

    REGEXP_ID = r"osf\.io\/(?P<record_id>[^\/]*)\/{0,1}"

    # the base entry point of the REST API
    API_URL = "https://api.osf.io/v2/nodes/"

    # the files and metadata about the dataset
    API_URL_META = "{api_url}{record_id}/files/"
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

    def _get_node_providers(self):
        """Get the providers of a node."""
        record_id = self._params["record_id"]
        res = requests.get(f"{self.API_URL}/{record_id}/files/")
        return set([prov["attributes"]["provider"] for prov in res.json()["data"]])

    def _get_files_recursive(self, url, folder_name=None, base_url=None):
        files = []
        # In case of the top-level folder, we need to get first the providers
        if folder_name is None:
            for provider in self._get_node_providers():
                # and then the files of each provider
                files.extend(
                    super()._get_files_recursive(f"{url}{provider}/", None, base_url)
                )
        else:
            files = super()._get_files_recursive(url, folder_name, base_url)
        return files


class ZenodoDataset(DatasetDownloader):
    """Downloader for Zenodo repository.

    For Zenodo records, new versions have new identifiers.
    """

    REGEXP_ID = r"zenodo\.org\/record(s*)\/(?P<record_id>\d+).*"

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


class DataEuropaDataset(DatasetDownloader):
    """Downloader for European data repository."""

    REGEXP_ID = r"data\.europa\.eu\/data\/datasets\/(?P<record_id>.+)"

    # the base entry point of the REST API
    API_URL = "https://data.europa.eu/api/hub/repo/"

    API_URL_META = "{api_url}datasets/{record_id}"
    META_FILES_JSONPATH = '$.@graph[?(@.@type == "dcat:Distribution")]'

    # paths to file attributes
    ATTR_FILE_LINK_JSONPATH = "'dcat:accessURL'.@id"
    ATTR_NAME_JSONPATH = "'dct:title'"
    ATTR_SIZE_JSONPATH = "'dcat:byteSize'.@value"


class SeaNoeDataset(DatasetDownloader):
    """Downloader for SeaNoe publication."""

    REGEXP_ID = r"https://www.seanoe\.org/data/[0-9]+/(?P<record_id>.*)/"

    # the base entry point of the REST API
    API_URL = "https://www.seanoe.org/api/"

    # the files and metadata about the dataset
    API_URL_META = "{api_url}find-by-id/{record_id}"
    META_FILES_JSONPATH = "files[*]"

    # paths to file attributes
    ATTR_NAME_JSONPATH = "fileName"
    ATTR_FILE_LINK_JSONPATH = "fileUrl"
    ATTR_SIZE_JSONPATH = "size"
    ATTR_HASH_JSONPATH = "checksum"
    ATTR_HASH_TYPE_VALUE = "sha256"


class B2shareDataset(DatasetDownloader):
    """Downloader for B2Share repository."""

    REGEXP_ID = r"b2share\.eudat\.eu\/records\/(?P<record_id>[0-9a-z]+)"

    # the base entry point of the REST API
    API_URL = "https://b2share.eudat.eu/api/"

    # the files and metadata about the dataset
    API_URL_META = "{api_url}records/{record_id}"
    META_FILES_JSONPATH = "files[*]"

    # paths to file attributes
    ATTR_NAME_JSONPATH = "key"
    ATTR_FILE_LINK_JSONPATH = "ePIC_PID"
    ATTR_SIZE_JSONPATH = "size"
    ATTR_HASH_JSONPATH = "checksum"
    ATTR_HASH_TYPE_VALUE = "md5"


class RadboudDataRepositoryDataset(DatasetDownloader):
    """Downloader for the Radboud Data Repository (RDR).

    The RDR (formerly the Donders Data Repository, https://data.ru.nl, legacy
    https://data.donders.ru.nl) serves data over WebDAV. "Open access"
    collections download anonymously through the public mirror; restricted
    collections require HTTP Basic authentication with RDR *data access*
    credentials (obtained from the data.ru.nl portal -- these are distinct
    from the institutional SSO password).

    Credentials are read, in order of precedence, from the ``username`` /
    ``password`` params (``-p username=... -p password=...`` on the CLI) or
    from the ``RDR_USERNAME`` / ``RDR_PASSWORD`` environment variables. When
    neither is set, access is anonymous via the public mirror.

    Files are enumerated from the per-collection ``MANIFEST.txt`` (one
    ``<sha256> <relative/path>`` entry per line); the WebDAV PROPFIND listing
    is used only to discover the version (``_vN``) suffix when it is not
    otherwise known.
    """

    # Matches the host in every accepted form (DOI-resolved/pasted landing
    # page on data(.donders).ru.nl, or a direct public/webdav collection URL).
    # No named groups: the real parsing happens in ``_collection_url`` so that
    # ``_params`` keeps the credentials passed via ``-p`` untouched.
    REGEXP_ID = r"(?:public\.|webdav\.)?data(?:\.donders)?\.ru\.nl"

    PUBLIC_BASE = "https://public.data.ru.nl"
    WEBDAV_BASE = "https://webdav.data.ru.nl"

    DAV = "{DAV:}"  # ElementTree namespace prefix (XML uses the 'a:' alias)

    def _auth(self):
        user = self._params.get("username") or os.environ.get("RDR_USERNAME")
        password = self._params.get("password") or os.environ.get("RDR_PASSWORD")
        if user and password:
            return (user, password)
        return None

    @property
    def _base_host(self):
        # Authenticated access needs the full WebDAV host; anonymous access
        # uses the public mirror (published collections only).
        return self.WEBDAV_BASE if self._auth() else self.PUBLIC_BASE

    def download_file(self, file_link, *args, **kwargs):
        try:
            return super().download_file(file_link, *args, **kwargs)
        except requests.HTTPError as err:
            response = getattr(err, "response", None)
            if response is not None and response.status_code in (401, 403):
                raise PermissionError(
                    f"Access to {file_link} was denied (HTTP "
                    f"{response.status_code}). This collection requires Radboud "
                    "Data Repository data-access credentials; set the "
                    "RDR_USERNAME and RDR_PASSWORD environment variables, or pass "
                    "'-p username=... -p password=...'."
                ) from err
            raise

    def _collection_url(self):
        """Resolve the input to a versioned WebDAV collection URL."""
        url = _get_url(self.resource)
        parsed = urlparse(url)
        host = parsed.hostname or ""
        parts = parsed.path.strip("/").split("/")

        if host.startswith(("public.", "webdav.")):
            # Direct WebDAV URL: {ou}/{COLLECTION}_vN[/...] (version present).
            ou, collection = parts[0], parts[1]
            if not re.search(r"_v\d+$", collection):
                collection = self._resolve_version(ou, collection)
        else:
            # Landing page: collections/{org}/{ou}/{COLLECTION} (no version).
            ou, collection = parts[2], parts[3]
            collection = self._resolve_version(ou, collection)

        return f"{self._base_host}/{ou}/{collection}"

    def _resolve_version(self, ou, collection):
        """Return ``{collection}_vN`` for the requested version.

        Precedence: explicit ``-p version=N`` > the exact version pinned by
        the DOI (via DataCite) > the highest version found by listing the
        parent organisational unit over WebDAV.
        """
        version = self._params.get("version")
        if version:
            return f"{collection}_v{version}"

        from_doi = self._version_from_datacite(collection)
        if from_doi:
            return from_doi

        return self._version_from_propfind(ou, collection)

    def _version_from_datacite(self, collection):
        doi = getattr(self.resource, "doi", None)
        if not doi:
            return None
        try:
            res = self.session.get(f"https://api.datacite.org/dois/{doi}")
            res.raise_for_status()
            identifiers = res.json()["data"]["attributes"].get("identifiers", [])
        except (requests.RequestException, KeyError, ValueError):
            return None
        for ident in identifiers:
            if ident.get("identifierType") == "URL":
                name = ident.get("identifier", "").rstrip("/").rsplit("/", 1)[-1]
                if name.startswith(f"{collection}_v"):
                    return name
        return None

    def _version_from_propfind(self, ou, collection):
        ou_url = f"{self._base_host}/{ou}/"
        res = self.session.request("PROPFIND", ou_url, headers={"Depth": "1"})
        res.raise_for_status()
        names = self._parse_propfind_names(res.content, ou_url)
        matches = [n for n in names if n.startswith(f"{collection}_v")]
        if not matches:
            raise ValueError(
                f"No versioned collection for '{collection}' found under {ou_url}"
            )
        return max(matches, key=lambda n: int(n.rsplit("_v", 1)[-1]))

    def _parse_propfind_names(self, content, parent_url):
        """Return the immediate child names from a PROPFIND multistatus body."""
        tree = ET.fromstring(content)
        parent_path = urlparse(parent_url).path
        names = []
        for href in tree.iter(f"{self.DAV}href"):
            if not href.text:
                continue
            path = unquote(urlparse(href.text).path)
            rel = path[len(parent_path) :].strip("/")
            if rel:
                names.append(rel.split("/")[0])
        return names

    @property
    def files(self):
        if hasattr(self, "_files"):
            return self._files

        base = self._collection_url()
        res = self.session.get(f"{base}/MANIFEST.txt")
        res.raise_for_status()

        self._files = []
        for line in res.text.splitlines():
            line = line.strip()
            if not line:
                continue
            file_hash, _, name = line.partition(" ")
            name = name.strip()
            if not name:
                continue
            self._files.append(
                {
                    "link": f"{base}/{quote(name)}",
                    "name": name,
                    "size": None,  # MANIFEST.txt carries no file sizes
                    "hash": file_hash,
                    "hash_type": "sha256",
                }
            )

        return self._files
