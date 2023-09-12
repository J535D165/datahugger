import logging
import re
from urllib.parse import urlparse

from datahugger.config import RE3DATA_SOFTWARE
from datahugger.config import SERVICES_NETLOC
from datahugger.config import SERVICES_NETLOC_REGEXP
from datahugger.handles import DOI
from datahugger.utils import _get_url
from datahugger.utils import get_datapublisher_from_doi
from datahugger.utils import get_re3data_repositories
from datahugger.utils import get_re3data_repository


def _resolve_service(uri):
    # initial attempt to resolve service
    service_class = _resolve_service_from_netloc(uri)

    if service_class is not None:
        logging.info("Service found: " + str(service_class))
        return service_class

    # try to resolve from re3data
    service_class = _resolve_service_with_re3data(uri)

    if service_class is not None:
        logging.info("Service found: " + str(service_class))
        return service_class

    raise ValueError(f"Data protocol for {uri} not found.")


def _resolve_service_from_netloc(uri):
    url = _get_url(uri)

    uri = urlparse(url)

    if not uri.hostname:
        return None

    logging.info(f"Resolve service for netloc '{uri.hostname}'")
    if uri.hostname in SERVICES_NETLOC.keys():
        return SERVICES_NETLOC[uri.hostname]

    for netloc_re, service in SERVICES_NETLOC_REGEXP.items():
        if re.match(netloc_re, url):
            return service

    logging.info("Netloc not found")


def _resolve_service_with_re3data(doi):
    if not isinstance(doi, DOI):
        return None

    logging.info("Resolve service with datacite and re3data")
    publisher = get_datapublisher_from_doi(doi)
    logging.info(f"Datacite publisher of dataset: {publisher}")

    if not publisher:
        raise ValueError("Can't resolve the publisher from the DOI.")

    data_repos = get_re3data_repositories()

    for repo in data_repos:
        if publisher.lower() == repo["name"].lower():
            r_software = get_re3data_repository(repo["id"])

            return RE3DATA_SOFTWARE[r_software.lower()]

    logging.info("Repository not found")
