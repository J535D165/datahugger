import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

import requests
import requests_cache


def _is_url(s: str) -> bool:
    """Check if the string is a URL.

    Arguments
    ---------
    s: str
        The url to check.

    Returns
    -------
    bool:
        Boolean that indicates whether the string is url."""

    return urlparse(s).netloc != ""


def _get_url(s: str) -> str:
    return s if isinstance(s, str) else s.url


def _format_filename(s, len_s=35) -> str:
    # README_Pfaller_Robinson_2022_Global_Sea_Turtle_Epibiont_Database.txt

    if len_s is None:
        return s

    s = str(s)

    if len(s) <= len_s:
        return s.ljust(len_s, " ")

    len_suffixes = len("".join(Path(s).suffixes))

    return s[0 : (len_s - (len_suffixes + 5))] + "[...]" + "".join(Path(s).suffixes)


def get_id_from_url(regexp, url):
    match = re.search(regexp, url)

    if match.group(1):
        return match.group(1)


def get_datapublisher_from_doi(doi):
    """Get the publisher from the DOI.

    Arguments
    ---------
    doi: str
        The DOI to find the publisher for.

    Returns
    -------
    str:
        The publisher.

    """

    r = requests.get(f"https://api.datacite.org/dois/{doi}")
    r.raise_for_status()

    record = r.json()

    return record["data"]["attributes"]["publisher"]


def get_re3data_repositories(
    url="https://www.re3data.org/api/v1/repositories", expire_after=3600
):
    # use cached version here
    session = requests_cache.CachedSession(
        "datahugger_cache",
        expire_after=expire_after,
        backend="filesystem",
        use_cache_dir=True,
    )
    r = session.get(url)
    r.raise_for_status()

    tree = ET.fromstring(r.content)

    for node in tree:
        yield {elem.tag: elem.text for elem in node if not elem.tag == "link"}


def get_re3data_repository(re3data_id):
    namespaces = {"r3d": "http://www.re3data.org/schema/2-2"}
    r = requests.get(f"https://www.re3data.org/api/v1/repository/{re3data_id}")
    r.raise_for_status()

    tree = ET.fromstring(r.content)

    return (
        tree[0]
        .find("r3d:software", namespaces)
        .find("r3d:softwareName", namespaces)
        .text
    )
