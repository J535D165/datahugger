import io
import os
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Union
from urllib.parse import quote

import requests

from datahugger.base import DatasetDownloader


class ZenodoDownload(DatasetDownloader):
    """Downloader for Zenodo repositories.

    Parameters
    ----------
    auto_unzip: True
        Unzip the repository if it is a single zipped file.
        This is often the case for repos published via the
        GitHub-Zenodo integration.

    """

    API_URL = "https://zenodo.org/api/"
    REGEXP_ID = r"zenodo\.org\/record\/(\d+).*"

    def __init__(self, auto_unzip=True, *args, **kwargs):
        super(ZenodoDownload, self).__init__(*args, **kwargs)

        self.auto_unzip = auto_unzip

    def _is_single_file(self, zip_url, output_folder):

        r = requests.get(zip_url)
        z = zipfile.ZipFile(io.BytesIO(r.content))

        for zip_info in z.infolist():
            if zip_info.filename[-1] == "/":
                continue
            zip_info.filename = os.path.basename(zip_info.filename)
            z.extract(zip_info, output_folder)

    def _get(
        self,
        record_id: Union[str, int],
        output_folder: Union[Path, str],
        **kwargs,
    ):
        res = requests.get(self.API_URL + "records/" + str(record_id))
        files = res.json()["files"]

        if len(files) == 1 and files[0]["links"]["self"].endswith(".zip"):
            self._is_single_file(files[0]["links"]["self"], output_folder)
            return

        for f in files:
            self.download(
                f["links"]["self"], output_folder, f["key"], file_size=f["size"]
            )


class DataverseDownload(DatasetDownloader):
    """Downloader for Dataverse repositories."""

    REGEXP_ID = r"dataset\.xhtml\?persistentId=(.*)"

    def _get(
        self,
        record_id: Union[str, int],
        output_folder: Union[Path, str],
        **kwargs,
    ):

        dataset_metadata_url = self.base_url + \
            "/api/datasets/:persistentId/?persistentId=" + record_id

        res = requests.get(dataset_metadata_url)
        files = res.json()["data"]["latestVersion"]["files"]

        for f in files:

            self.download(
                self.base_url + "/api/access/datafile/{}".format(f["dataFile"]["id"]),
                output_folder,
                f["dataFile"]["filename"],
                file_size=f["dataFile"]["filesize"],
            )


class GitHubDownload(DatasetDownloader):
    """Downloader for GitHub repositories."""

    API_URL = "https://github.com/"
    REGEXP_ID = r"github\.com\/([a-zA-Z0-9]+\/[a-zA-Z0-9]+)[\/]*.*"

    def _get(self, record_id: str, output_folder: Union[Path, str], *args, **kwargs):

        res = requests.get(self.API_URL + record_id + "/archive/refs/heads/master.zip")
        z = zipfile.ZipFile(io.BytesIO(res.content))
        z.extractall(output_folder)


class FigShareDownload(DatasetDownloader):
    """Downloader for FigShare repositories."""

    API_URL = "https://api.figshare.com/v2"
    REGEXP_ID_AND_VERSION = r"figshare\.com\/articles\/dataset\/.*\/(\d+)\/(\d+)"
    REGEXP_ID = r"figshare\.com\/articles\/dataset\/.*\/(\d+)"

    def _get(
        self,
        record_id: Union[str, int],
        output_folder: Union[Path, str],
        **kwargs,
    ):

        res = requests.get(self.API_URL + "/articles/{}/files".format(record_id))
        files = res.json()

        # TODO skip is_link_only

        for f in files:
            self.download(
                f["download_url"], output_folder, f["name"], file_size=f["size"]
            )


class DataDryadDownload(DatasetDownloader):
    """Downloader for DataDryad repositories.

    Note
    ----

    The zip file not immediately available "The version
    of the dataset is being assembled. Check back in around
    1 minute and it should be ready to download.".

    """

    API_URL = "https://datadryad.org/api/v2"
    REGEXP_ID = r"datadryad\.org[\:]*[43]{0,3}\/stash\/dataset\/doi:(.*)"

    def _get(
        self,
        record_id: Union[str, int],
        output_folder: Union[Path, str],
        **kwargs,
    ):

        datadryad_doi_safe = quote(f"doi:{record_id}", safe="")
        dataset_metadata_url = self.API_URL + "/datasets/" + datadryad_doi_safe

        res = requests.get(dataset_metadata_url)
        dataset_metadata = res.json()

        # get the latest version of the dataset
        latest_version = dataset_metadata["_links"]["stash:version"]["href"]
        url_latest_version = "https://datadryad.org" + latest_version + "/files"

        res_files = requests.get(url_latest_version)
        files_metadata = res_files.json()

        for f in files_metadata["_embedded"]["stash:files"]:
            self.download(
                "https://datadryad.org" + f["_links"]["stash:file-download"]["href"],
                output_folder,
                f["path"],
                file_size=f["size"],
            )


class HuggingFaceDownload(DatasetDownloader):
    """Downloader for Huggingface repositories."""

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
                self.download(
                    data_elem.find(
                        "./physical/distribution/online/url[@function='download']"
                    ).text,  # noqa
                    output_folder,
                    data_elem.find("entityName").text,
                    file_size=data_elem.find("./physical/size").text,
                )


class OSFDownload(DatasetDownloader):
    """Downloader for OSF repositories."""

    API_URL = "https://api.osf.io/v2/registrations/"
    REGEXP_ID = r"osf\.io\/(.*)/"

    def _get(
        self,
        record_id: Union[str, int],
        output_folder: Union[Path, str],
        **kwargs,
    ):

        r_meta = requests.get(
            self.API_URL + record_id + "/files/osfstorage/?format=jsonapi"
        )
        dataset_metadata = r_meta.json()

        for f in dataset_metadata["data"]:
            self.download(
                f["links"]["download"],
                output_folder,
                f["attributes"]["name"],
                file_size=f["attributes"]["size"],
            )


class MendeleyDownload(DatasetDownloader):
    """Downloader for Mendeley repositories."""

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
            self.download(
                f["content_details"]["download_url"],
                output_folder,
                f["filename"],
                file_size=f["size"],
            )
