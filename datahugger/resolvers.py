import logging
import re
from urllib.parse import urlparse

import requests

from datahugger.config import RE3DATA_SOFTWARE
from datahugger.config import SERVICES_NETLOC
from datahugger.config import SERVICES_NETLOC_REGEXP
from datahugger.exceptions import RepositoryNotSupportedError
from datahugger.handles import DOI
from datahugger.utils import _get_url
from datahugger.utils import get_datapublisher_from_doi
from datahugger.utils import get_re3data_repositories
from datahugger.utils import get_re3data_repository


def _resolve_service(resource):
    for resolver in [
        _resolve_service_from_netloc,
        _resolve_service_from_url_pattern,
        _resolve_service_with_re3data,
    ]:
        service_class = resolver(resource)

        if service_class is not None:
            logging.info(f"Service found: {service_class}")
            return service_class

    raise RepositoryNotSupportedError(f"Data protocol for {resource} not found.")


def _resolve_service_from_netloc(resource):
    uri = urlparse(_get_url(resource))

    if not uri.hostname:
        return None

    logging.info(f"Resolve service for netloc '{uri.hostname}'")
    if uri.hostname in SERVICES_NETLOC.keys():
        return SERVICES_NETLOC[uri.hostname]


def _resolve_service_from_url_pattern(resource):
    url = _get_url(resource)

    for netloc_re, service in SERVICES_NETLOC_REGEXP.items():
        if re.match(netloc_re, url):
            return service


def _resolve_service_with_re3data(doi):
    if not isinstance(doi, DOI):
        return None

    logging.info("Resolve service with datacite and re3data")
    try:
        publisher = get_datapublisher_from_doi(doi)
    except requests.HTTPError:
        return None
    logging.info(f"Datacite publisher of dataset: {publisher}")

    if not publisher:
        logging.info("Can't resolve the publisher from the DOI.")
        return None

    data_repos = get_re3data_repositories()

    for repo in data_repos:
        if publisher.lower() == repo["name"].lower():
            r_software = get_re3data_repository(repo["id"])

            try:
                return RE3DATA_SOFTWARE[r_software.lower()]
            except KeyError:
                return None
