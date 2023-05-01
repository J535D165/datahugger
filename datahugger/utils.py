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

    if len_s is None:
        return s

    s = str(s)

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


def get_base_url(url):

    uri = urlparse(url)

    return uri.scheme + "://" + uri.netloc


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

    if r.status_code == 406:
        raise ValueError("Publisher not known to DataCite")

    tree = ET.fromstring(r.content)

    node_pub = tree.find("{http://datacite.org/schema/kernel-4}publisher")
    if node_pub is not None:
        return node_pub.text


def get_re3data_repositories(url="https://www.re3data.org/api/v1/repositories"):

    r = requests.get(url)

    if r.status_code != 200:
        raise Exception("Failed to download Re3data reposities.")

    tree = ET.fromstring(r.content)

    for node in tree:
        yield {elem.tag: elem.text for elem in node if not elem.tag == "link"}


def get_re3data_repository(re3data_id):

    namespaces = {"r3d": "http://www.re3data.org/schema/2-2"}
    r = requests.get(f"https://www.re3data.org/api/v1/repository/{re3data_id}")

    tree = ET.fromstring(r.content)

    return (
        tree[0]
        .find("r3d:software", namespaces)
        .find("r3d:softwareName", namespaces)
        .text
    )


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
