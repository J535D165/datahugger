import logging
import os
import re
from pathlib import Path
from typing import Union

import natsort as ns
import requests
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


class DatasetResult(object):
    """Result class after downloading the dataset."""

    def __init__(self, output_folder):
        self.output_folder = output_folder

    def __str__(self):

        return f"<{self.__class__.__name__} n_files={len(self)} >"

    def __len__(self):
        count = 0
        for root_dir, cur_dir, files in os.walk(self.output_folder):
            count += len(files)

        return count

    def tree(self, **kwargs):
        """Return the folder tree.

        Tree based on scientific sort.
        """

        return scitree(self.output_folder, **kwargs)


class DatasetDownloader(object):
    """Base class for downloading resources from repositories."""

    def __init__(
        self,
        base_url=None,
        max_file_size=None,
        force_download=False,
        progress=True,
        unzip=True,
    ):
        super(DatasetDownloader, self).__init__()
        self.base_url = base_url
        self.max_file_size = max_file_size
        self.force_download = force_download
        self.progress = progress
        self.unzip = unzip

    def download(
        self,
        url,
        base_output_folder,
        output_fn,
        file_size=None,
        file_hash=None,
        file_hash_type=None,
    ):
        """Download a single file.

        Arguments
        ---------
        url: str
            Path to the file to download.
        base_output_folder: str
            The folder to store the downloaded file.
        output_fn: str
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
            logging.info("Skipping large file {}".format(url))
            return

        logging.info("Downloading file {}".format(url))
        res = requests.get(url, stream=True)

        output_fp = Path(base_output_folder, output_fn)

        if not self.force_download and output_fp.exists():
            print("File already exists:", output_fn)
            return

        if self.progress:
            with tqdm.wrapattr(
                open(output_fp, "wb"),
                "write",
                miniters=1,
                desc=_format_filename(output_fn),
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

    def get(
        self,
        record_id_or_url: Union[str, int],
        output_folder: Union[Path, str],
        version: int = None,
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

        if isinstance(record_id_or_url, str) and _is_url(record_id_or_url):
            record_id, version = self._parse_url(record_id_or_url)
        else:
            record_id, version = record_id_or_url, version

        self._get(record_id, output_folder, version=version, **kwargs)

        return DatasetResult(output_folder)
