import logging
from urllib.parse import urlparse

from pyDataverse.api import NativeApi
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

    # match uri to services and initiate class
    if uri.netloc in SERVICES_NETLOC.keys():
        logging.info("Service found: " + uri.netloc)
        return SERVICES_NETLOC[uri.netloc](
            max_file_size=max_file_size, download_mode=download_mode, *args, **kwargs
        ).get(url, output_folder, doi=doi)

    # Unknown services
    #
    # The service is not in the list of known domains. Do a check if it belong
    # to self hosted data repositories like Dataverse.
    if uri.netloc.startswith("dataverse"):
        return DataverseDownload(
            uri.scheme + "://" + uri.netloc,
            max_file_size=max_file_size,
            download_mode=download_mode,
            *args,
            **kwargs,
        ).get(url, output_folder, doi=doi)

    # check if api returns dataverse instance
    try:
        NativeApi(uri.scheme + "://" + uri.netloc).get_info_version()
    except Exception:
        # not a dataverse instance
        pass

    raise ValueError(f"Data service for {url} is not supported.")
