import io
import logging
import os
import re
import zipfile
from pathlib import Path
from typing import Union

import natsort as ns
import requests
from jsonpath_ng import parse
from scitree import scitree
from tqdm import tqdm

from datahugger.utils import _format_filename
from datahugger.utils import _is_url

FILE_RANKING = [
    ["readme", "read_me", "read-me"],
    ["license"],
    ["installation", "install", "setup"],
]


def _scientific_sort(f, alg=ns.PATH):

    for rank, names in enumerate(FILE_RANKING):
        if Path(f).stem.lower() in names:
            prio = rank
            break
    else:
        prio = len(FILE_RANKING)

    x = (prio,) + ns.natsort_keygen(alg=alg)(f)

    return x


class DatasetResult:
    """Result class after downloading the dataset."""

    def __str__(self):

        return f"<{self.__class__.__name__} n_files={len(self)} >"

    def __len__(self):

        return len(self.files)

    def tree(self, **kwargs):
        """Return the folder tree.

        Tree based on scientific sort.
        """

        return scitree(self.output_folder, **kwargs)


class DatasetDownloader:
    """Base class for downloading resources from repositories."""

    API_URL = None

    def __init__(
        self,
        url: Union[str, int],
        version=None,
        base_url=None,
        max_file_size=None,
        force_download=False,
        progress=True,
        unzip=True,
        print_only=False,
    ):
        super().__init__()
        self.url = url
        self.version = version
        self.base_url = base_url
        self.max_file_size = max_file_size
        self.force_download = force_download
        self.progress = progress
        self.unzip = unzip
        self.print_only = print_only

    def _get_attr_attr(self, record, jsonp):

        try:
            jsonpath_expression = parse(jsonp)
            return jsonpath_expression.find(record)[0].value
        except Exception:
            return None

    def _get_attr_link(self, record):

        # get the link to the folder
        if self._get_attr_kind(record) == "folder":

            if not hasattr(self, "ATTR_FOLDER_LINK_JSONPATH"):
                return None

            return self._get_attr_attr(record, self.ATTR_FOLDER_LINK_JSONPATH)

        # get the link to the file
        else:

            if not hasattr(self, "ATTR_FILE_LINK_JSONPATH"):
                return None

            return self._get_attr_attr(record, self.ATTR_FILE_LINK_JSONPATH)

    def _get_attr_name(self, record):

        if not hasattr(self, "ATTR_NAME_JSONPATH"):
            return None

        return self._get_attr_attr(record, self.ATTR_NAME_JSONPATH)

    def _get_attr_size(self, record):

        if not hasattr(self, "ATTR_SIZE_JSONPATH"):
            return None

        return self._get_attr_attr(record, self.ATTR_SIZE_JSONPATH)

    def _get_attr_hash(self, record):

        if not hasattr(self, "ATTR_HASH_JSONPATH"):
            return None

        return self._get_attr_attr(record, self.ATTR_HASH_JSONPATH)

    def _get_attr_hash_type(self, record):

        if hasattr(self, "ATTR_HASH_TYPE_VALUE"):
            return self.ATTR_HASH_TYPE_VALUE

        if not hasattr(self, "ATTR_HASH_TYPE_JSONPATH"):
            return None

        return self._get_attr_attr(record, self.ATTR_HASH_TYPE_JSONPATH)

    def _get_attr_kind(self, record):

        if not hasattr(self, "ATTR_KIND_JSONPATH"):
            return "file"

        return self._get_attr_attr(record, self.ATTR_KIND_JSONPATH)

    def download_file(
        self,
        file_link,
        output_folder,
        file_name,
        file_size=None,
        file_hash=None,
        file_hash_type=None,
    ):
        """Download a single file.

        Arguments
        ---------
        file_link: str
            Path to the file to download.
        output_folder: str
            The folder to store the downloaded file.
        file_name: str
            The filename of the downloaded file.
        file_size: int
            The size of the file in bytes.
        file_hash: str
            The MD5 hash of the file.

        """
        if (
            file_size is not None
            and self.max_file_size is not None
            and file_size >= self.max_file_size
        ):
            logging.info(f"Skipping large file {file_link}")
            if self.progress:
                print(f"{_format_filename(file_name)}: SKIPPED")
            return

        if not self.print_only:
            logging.info(f"Downloading file {file_link}")
            res = requests.get(file_link, stream=True)

            output_fp = Path(output_folder, file_name)
            Path(output_fp).parent.mkdir(parents=True, exist_ok=True)

            if not self.force_download and output_fp.exists():
                print("File already exists:", file_name)
                return

            if self.progress:
                with tqdm.wrapattr(
                    open(output_fp, "wb"),
                    "write",
                    miniters=1,
                    desc=_format_filename(file_name),
                    total=int(res.headers.get("content-length", 0)),
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}",
                ) as fout:
                    for chunk in res.iter_content(chunk_size=4096):
                        fout.write(chunk)
            else:
                with open(output_fp, "wb") as f:
                    f.write(res.content)
        else:
            print(f"{_format_filename(file_name)}: COMPLETE")

    def _parse_url(self, url):
        if not isinstance(url, str) or not _is_url(url):
            raise ValueError("Not a valid URL.")

        # first try to parse with version number
        if hasattr(self, "REGEXP_ID_AND_VERSION"):
            match = re.search(self.REGEXP_ID_AND_VERSION, url)

            if match and match.group(1):
                if match.group(2) == "":
                    return match.group(1), None
                return match.group(1), match.group(2)

        # then try to parse without version number
        if hasattr(self, "REGEXP_ID"):
            match = re.search(self.REGEXP_ID, url)

            if match and match.group(1):
                return match.group(1), None

        raise ValueError(f"Failed to parse record identifier from URL '{url}'")

    def _unpack_single_folder(self, zip_url, output_folder):

        r = requests.get(zip_url)
        z = zipfile.ZipFile(io.BytesIO(r.content))

        for zip_info in z.infolist():
            if zip_info.filename[-1] == "/":
                continue
            zip_info.filename = os.path.basename(zip_info.filename)
            z.extract(zip_info, output_folder)

    @property
    def api_record_id(self):

        if hasattr(self, "_api_record_id"):
            return self._api_record_id

        if isinstance(self.url, str) and _is_url(self.url):
            self._api_record_id, self.version = self._parse_url(self.url)
        else:
            self._api_record_id, self.version = self.url, self.version

        return self._api_record_id

    def _pre_files(self):
        pass

    def _get_files_recursive(self, url, folder_name=None):

        if not isinstance(url, str):
            ValueError(f"Expected url to be string type, got {type(url)}")

        result = []

        # get the data from URL
        res = requests.get(url)
        reponse = res.json()

        # find path to raw files
        if hasattr(self, "META_FILES_JSONPATH"):
            jsonpath_expression = parse(self.META_FILES_JSONPATH)
            files_raw = jsonpath_expression.find(reponse)[0].value
        else:
            files_raw = reponse

        for f in files_raw:

            # create the file or folder path
            if folder_name is None:
                f_path = self._get_attr_name(f)
            else:
                f_path = str(Path(folder_name, self._get_attr_name(f)))

            if self._get_attr_kind(f) == "folder":

                result.extend(
                    self._get_files_recursive(
                        self._get_attr_link(f), folder_name=f_path)
                )
            else:

                result.append(
                    {
                        "link": self._get_attr_link(f),
                        "name": f_path,
                        "size": self._get_attr_size(f),
                        "hash": self._get_attr_hash(f),
                        "hash_type": self._get_attr_hash_type(f),
                    }
                )

        if hasattr(self, "PAGINATION_JSONPATH"):
            jsonpath_expression = parse(self.PAGINATION_JSONPATH)
            next_url = jsonpath_expression.find(reponse)[0].value

            if next_url:
                result.extend(
                    self._get_files_recursive(
                        next_url, folder_name=folder_name)
                )

        return result

    @property
    def files(self):

        if hasattr(self, "_files"):
            return self._files

        self._pre_files()

        self._files = self._get_files_recursive(
            self.API_URL_META.format(
                api_url=self.API_URL,
                api_record_id=self.api_record_id,
                version=self.version,
                base_url=self.base_url,
            )
        )

        return self._files

    def _get(
        self,
        output_folder: Union[Path, str],
        **kwargs,
    ):

        if len(self.files) == 1 and self.files[0]["link"].endswith(".zip"):
            self._unpack_single_folder(self.files[0]["link"], output_folder)
            return

        for f in self.files:
            self.download_file(
                f["link"],
                output_folder,
                file_name=f["name"],
                file_size=f["size"],
                file_hash=f["hash"],
                file_hash_type=f["hash_type"]
            )

    def download(
        self,
        output_folder: Union[Path, str],
        **kwargs,
    ):
        """Download files for the given URL or record id.

        Arguments
        ---------
        record_id_or_url: str
            The identifier of the record or the url to the resource
            to download.
        output_folder: str
            The folder to store the downloaded results.
        version: str, int
            The version of the dataset

        """
        Path(output_folder).mkdir(parents=True, exist_ok=True)

        self._get(output_folder, **kwargs)

        # store the location of the last known output folder
        self.output_folder = output_folder

        return self
