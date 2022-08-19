import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

import requests


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


def _format_filename(s, len_s=35) -> str:

    # README_Pfaller_Robinson_2022_Global_Sea_Turtle_Epibiont_Database.txt

    if len(s) <= len_s:
        return s.ljust(len_s, " ")

    len_suffixes = len("".join(Path(s).suffixes))

    return s[0 : (len_s - (len_suffixes + 5))] + "[...]" + "".join(Path(s).suffixes)


def _is_doi(s: str) -> bool:
    """Check if string is DOI.

    Parameters
    ----------
    s: str
        The string to check for DOI

    Returns
    -------
    bool:
        Is the string a pure DOI or not.
    """
    # Thanks to Andrew Gilmartin
    # https://www.crossref.org/blog/dois-and-matching-regular-expressions/
    match = re.match(r"^10.\d{4,9}/[-._;()/:A-Z0-9]+$", s, re.IGNORECASE)

    return match is not None and match.group() is not None


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

    r = requests.get(
        f"https://doi.org/{doi}",
        headers={"Accept": "application/vnd.datacite.datacite+xml"},
        allow_redirects=True,
    )

    if r.status_code != 200:
        raise ValueError("DOI not found")

    tree = ET.fromstring(r.content)

    node_pub = tree.find("{http://datacite.org/schema/kernel-4}publisher")
    if node_pub is not None:
        return node_pub.text

    return None


def get_url_from_doi(doi):
    """Get the url from the DOI.
    Arguments
    ---------
    doi: str
        The DOI to find the url for.
    Returns
    -------
    str:
        The url.
    """

    try:
        r = requests.head(f"https://doi.org/{doi}", allow_redirects=True)
    except requests.exceptions.ConnectionError:
        return None

    return r.url
