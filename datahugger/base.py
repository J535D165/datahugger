import logging
import os
import re
from pathlib import Path
from typing import Union

import natsort as ns
import requests
from scitree import scitree
from tqdm import tqdm
from jsonpath_ng import jsonpath, parse

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


class DatasetResult(object):
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


class DatasetDownloader(object):
    """Base class for downloading resources from repositories."""

    def __init__(
        self,
        url: Union[str, int],
        version=None,
        base_url=None,
        max_file_size=None,
        force_download=False,
        progress=True,
        unzip=True,
    ):
        super(DatasetDownloader, self).__init__()
        self.url = url
        self.version = version
        self.base_url = base_url
        self.max_file_size = max_file_size
        self.force_download = force_download
        self.progress = progress
        self.unzip = unzip

    def _get_file_meta_attr(self, record, jsonp):

        try:
            jsonpath_expression = parse(jsonp)
            return jsonpath_expression.find(record)[0].value
        except Exception as err:
            return None

    def _get_file_meta_link(self, record):

        if not hasattr(self, "META_FILE_LINK_JSONPATH"):
            return None

        return self._get_file_meta_attr(record, self.META_FILE_LINK_JSONPATH)

    def _get_file_meta_name(self, record):

        if not hasattr(self, "META_FILE_NAME_JSONPATH"):
            return None

        return self._get_file_meta_attr(record, self.META_FILE_NAME_JSONPATH)

    def _get_file_meta_size(self, record):

        if not hasattr(self, "META_FILE_SIZE_JSONPATH"):
            return None

        return self._get_file_meta_attr(record, self.META_FILE_SIZE_JSONPATH)

    def _get_file_meta_hash(self, record):

        if not hasattr(self, "META_FILE_HASH_JSONPATH"):
            return None

        return self._get_file_meta_attr(record, self.META_FILE_HASH_JSONPATH)

    def _get_file_meta_hash_type(self, record):

        if hasattr(self, "META_FILE_HASH_TYPE_VALUE"):
            return self.META_FILE_HASH_TYPE_VALUE

        if not hasattr(self, "META_FILE_HASH_TYPE_JSONPATH"):
            return None

        return self._get_file_meta_attr(record, self.META_FILE_HASH_TYPE_JSONPATH)

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
            logging.info("Skipping large file {}".format(file_link))
            return

        logging.info("Downloading file {}".format(file_link))
        res = requests.get(file_link, stream=True)

        output_fp = Path(output_folder, file_name)

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
            ) as fout:
                for chunk in res.iter_content(chunk_size=4096):
                    fout.write(chunk)
        else:
            with open(output_fp, "wb") as f:
                f.write(res.content)

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

        return None, None

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

    @property
    def files(self):

        if hasattr(self, "_files"):
            return self._files

        self._pre_files()

        res = requests.get(
            self.API_URL_META.format(
                api_record_id=self.api_record_id,
                version=self.version,
                base_url=self.base_url,
            )
        )

        if hasattr(self, "META_FILES_JSONPATH"):
            jsonpath_expression = parse(self.META_FILES_JSONPATH)
            files_raw = jsonpath_expression.find(res.json())[0].value
        else:
            files_raw = res.json()

        x = []
        for f in files_raw:
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

    def _get(
        self,
        output_folder: Union[Path, str],
        **kwargs,
    ):

        if len(self.files) == 1 and self.files[0]["file_link"].endswith(".zip"):
            self._unpack_single_folder(self.files[0]["file_link"], output_folder)
            return

        for f in self.files:
            self.download_file(output_folder=output_folder, **f)

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

        return self
