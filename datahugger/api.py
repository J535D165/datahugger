import logging
from urllib.parse import urlparse

import requests

from datahugger.services import DataDryadDownload
from datahugger.services import DataOneDownload
from datahugger.services import DataverseDownload
from datahugger.services import FigShareDownload
from datahugger.services import GitHubDownload
from datahugger.services import HuggingFaceDownload
from datahugger.services import MendeleyDownload
from datahugger.services import OSFDownload
from datahugger.services import ZenodoDownload
from datahugger.utils import _is_doi
from datahugger.utils import _is_url
from datahugger.utils import get_datapublisher_from_doi
from datahugger.utils import get_re3data_repositories
from datahugger.utils import get_re3data_repository

URL_RESOLVE = ["doi.org"]

SERVICES_NETLOC = {
    "zenodo.org": ZenodoDownload,
    "figshare.com": FigShareDownload,
    "github.com": GitHubDownload,
    "datadryad.org": DataDryadDownload,
    "datadryad.org:443": DataDryadDownload,
    "huggingface.co": HuggingFaceDownload,
    "osf.io": OSFDownload,
    "data.mendeley.com": MendeleyDownload,
    # DataOne repositories
    "arcticdata.io": DataOneDownload,
    "knb.ecoinformatics.org": DataOneDownload,
    "data.pndb.fr": DataOneDownload,
    "opc.dataone.org": DataOneDownload,
    "portal.edirepository.org": DataOneDownload,
    "goa.nceas.ucsb.edu": DataOneDownload,
    "data.piscoweb.org": DataOneDownload,
    "adc.arm.gov": DataOneDownload,
    "scidb.cn": DataOneDownload,
    "data.ess-dive.lbl.gov": DataOneDownload,
    "hydroshare.org": DataOneDownload,
    "ecl.earthchem.org": DataOneDownload,
    "get.iedadata.org": DataOneDownload,
    "usap-dc.org": DataOneDownload,
    "iys.hakai.org": DataOneDownload,
    "doi.pangaea.de": DataOneDownload,
    "rvdata.us": DataOneDownload,
    "sead-published.ncsa.illinois.edu": DataOneDownload,
}

RE3DATA_SOFTWARE = {
    "DataVerse": DataverseDownload,  # Hits on re3data 2022-09-02: (145)
    # "DSpace": DSpaceDownload,  # Hits on re3data 2022-09-02: (115)
    # "CKAN": CKANDownload,  # Hits on re3data 2022-09-02: (89)
    # "MySQL": MySQLDownload,  # Hits on re3data 2022-09-02: (86)
    # "Fedora": FedoraDownload,  # Hits on re3data 2022-09-02: (43)
    # "EPrints": EPrintsDownload,  # Hits on re3data 2022-09-02: (34)
    # "Nesstar": NesstarDownload,  # Hits on re3data 2022-09-02: (19)
    # "DigitalCommons": DigitalCommonsDownload,  # Hits on re3data 2022-09-02: (4)
    # "eSciDoc": eSciDocDownload,  # Hits on re3data 2022-09-02: (3)
    # "Opus": OpusDownload,  # Hits on re3data 2022-09-02: (2)
    # "dLibra": dLibraDownload,  # Hits on re3data 2022-09-02: (2)
}


def load_repository(
    url,
    output_folder,
    doi=None,
    max_file_size=None,
    download_mode="skip_if_exists",
    *args,
    **kwargs,
):
    """Load content of repository.

    Arguments
    ---------
    url:
        The url to the repo.
    output_folder:
        The folder to download the files to.

    Returns
    -------

    FileTree
        The file tree of the repository.
    """

    # check if the url is a doi, if so, make a proper doi url out of it.
    if url.startswith("doi:"):
        url = url[4:]

    if _is_doi(url):
        doi = url
        url = "https://doi.org/" + url

    if _is_url(url) and "doi.org" in url:
        doi = url.split("doi.org/")[1]

    # is url
    uri = urlparse(url)

    # if netloc is doi.org, follow the redirect
    if uri.netloc in URL_RESOLVE:
        r = requests.head(url, allow_redirects=True)
        logging.info(f"Redirect from {url} to {r.url}")
        return load_repository(
            r.url,
            output_folder,
            max_file_size=max_file_size,
            doi=doi,
            download_mode=download_mode,
            *args,
            **kwargs,
        )

    service_class = _resolve_service(url, doi)

    if service_class is None:
        raise ValueError(f"Data service for {url} is not supported.")

    logging.debug("Service found: " + str(service_class))

    return service_class(
        base_url=uri.scheme + "://" + uri.netloc,
        max_file_size=max_file_size,
        download_mode=download_mode,
        *args,
        **kwargs,
    ).get(url, output_folder, doi=doi)

    raise ValueError(f"Data service for {url} is not supported.")


def _resolve_service(url, doi):

    # initial attempt to resolve service
    service_class = _resolve_service_from_netloc(url)

    if service_class is not None:
        return service_class

    # try to resolve from re3data
    service_class = _resolve_service_with_re3data(doi)

    if service_class is not None:
        return service_class

    return None


def _resolve_service_from_netloc(url):

    uri = urlparse(url)

    if uri.netloc in SERVICES_NETLOC.keys():
        logging.debug("Service found: " + uri.netloc)

        return SERVICES_NETLOC[uri.netloc]


def _resolve_service_with_re3data(doi):

    publisher = get_datapublisher_from_doi(doi)
    logging.debug(f"Publisher of dataset: {publisher}")

    if not publisher:
        raise ValueError("Can't resolve the publisher from the DOI.")

    data_repos = get_re3data_repositories()

    for repo in data_repos:

        if publisher.lower() == repo["name"].lower():

            r_software = get_re3data_repository(repo["id"])

            return RE3DATA_SOFTWARE[r_software]
