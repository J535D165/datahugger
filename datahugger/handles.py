import logging
import re

import requests

from datahugger.exceptions import DOIError
from datahugger.utils import _is_url


class DOI:
    """docstring for DOI"""

    def __init__(self, doi):
        super().__init__()
        self.doi = doi

    def __str__(self):
        return f"{self.doi}"

    @classmethod
    def parse(cls, doi_str):
        if doi_str.startswith("doi:"):
            doi_str = doi_str[4:]

        if _is_url(doi_str) and "doi.org" in doi_str:
            doi_str = doi_str.split("doi.org/")[1]

        # Thanks to Andrew Gilmartin
        # https://www.crossref.org/blog/dois-and-matching-regular-expressions/
        match = re.match(r"^10.\d{4,9}/[-._;()/:A-Z0-9]+$", doi_str, re.IGNORECASE)
        if not (match is not None and match.group() is not None):
            raise ValueError("Not a valid DOI")

        return cls(match.group())

    @property
    def url(self):
        """Return the url."""

        if hasattr(self, "_resolved_url"):
            return self._resolved_url

        return None

    def resolve(self):
        if hasattr(self, "_resolved_url"):
            return self._resolved_url

        url = f"https://doi.org/{self.doi}"
        r = requests.head(url, allow_redirects=True, timeout=(3, 10))

        if r.status_code == 404 and r.url and r.url.startswith("https://doi.org"):
            raise DOIError(f"DOI {self.doi} not found in the DOI system")
        elif r.status_code in [404, 405]:
            # head request not allowed or possible, try get request
            r = requests.get(url, allow_redirects=True, timeout=(3, 10))
        elif r.status_code in [403]:
            # Most likely a service that tries to prevent webscraping.
            # Might still have an API, so forwaring the response url.
            pass
        else:
            r.raise_for_status()

        logging.info(f"Redirect from {url} to {r.url}")
        self._resolved_url = r.url

        return self._resolved_url


def is_doi(s: str) -> bool:
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

    try:
        DOI.parse(s)
        return True
    except ValueError:
        return False


class Handle:
    """docstring for Handle"""

    def __init__(self, handle):
        super().__init__()
        self.handle = handle

    def __str__(self):
        return f"{self.handle}"

    @classmethod
    def parse(cls, s):
        if s.startswith("hdl:"):
            s = s[4:]

        match = re.match(r"^https\:\/\/hdl\.handle\.net\/(.*)$", s, re.IGNORECASE)
        if not (match is not None and match.group() is not None):
            raise ValueError("Not a valid Handle")

        return cls(match.group())

    @property
    def url(self):
        """Return the url."""

        if hasattr(self, "_resolved_url"):
            return self._resolved_url

        return None

    def resolve(self):
        if hasattr(self, "_resolved_url"):
            return self._resolved_url

        url = f"https://hdl.handle.net/{self.handle}"
        r = requests.head(url, allow_redirects=True, timeout=(3, 10))

        if r.status_code == 404 and r.url and r.url.startswith("https://handle.org"):
            raise ValueError(f"Handle {self.handle} not found in the Handle system")
        elif r.status_code in [404, 405]:
            # head request not allowed or possible, try get request
            r = requests.get(url, allow_redirects=True, timeout=(3, 10))
        elif r.status_code in [403]:
            # Most likely a service that tries to prevent webscraping.
            # Might still have an API, so forwaring the response url.
            pass
        else:
            r.raise_for_status()

        logging.info(f"Redirect from {url} to {r.url}")
        self._resolved_url = r.url

        return self._resolved_url


def is_handle(s: str) -> bool:
    """Check if string is Handle.

    Parameters
    ----------
    s: str
        The string to check for Handle

    Returns
    -------
    bool:
        Is the string a pure Handle or not.
    """

    try:
        Handle.parse(s)
        return True
    except ValueError:
        return False
