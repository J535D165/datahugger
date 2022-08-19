import logging
import re
from pathlib import Path
from typing import Union

import requests
from tqdm import tqdm

from datahugger.utils import _format_filename
from datahugger.utils import _is_url


class BaseRepoDownloader(object):
    """Base class for downloading resources from repositories."""

    def __init__(self, max_file_size=None, download_mode="skip_if_exists"):
        super(BaseRepoDownloader, self).__init__()
        self.max_file_size = max_file_size
        self.download_mode = download_mode

        if download_mode not in ["skip_if_exists", "force_redownload"]:
            raise ValueError(f"Download mode {download_mode} not recognised")

    def download(
        self, url, base_output_folder, output_fn, file_size=None, file_hash=None
    ):

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

        if self.download_mode == "skip_if_exists" and output_fp.exists():
            print("File already exists:", output_fn)
            return

        with tqdm.wrapattr(
            open(output_fp, "wb"),
            "write",
            miniters=1,
            desc=_format_filename(output_fn),
            total=int(res.headers.get("content-length", 0)),
        ) as fout:
            for chunk in res.iter_content(chunk_size=4096):
                fout.write(chunk)

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
