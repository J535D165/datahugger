import logging
import re
from urllib.parse import urlparse

import requests

from datahugger.exceptions import DOIError
from datahugger.services import DataDryadDataset
from datahugger.services import DataOneDataset
from datahugger.services import DataverseDataset
from datahugger.services import Djehuty
from datahugger.services import DSpaceDataset
from datahugger.services import FigShareDataset
from datahugger.services import GitHubDataset
from datahugger.services import HuggingFaceDataset
from datahugger.services import MendeleyDataset
from datahugger.services import OSFDataset
from datahugger.services import ZenodoDataset
from datahugger.utils import _is_doi
from datahugger.utils import _is_url
from datahugger.utils import get_base_url
from datahugger.utils import get_datapublisher_from_doi
from datahugger.utils import get_re3data_repositories
from datahugger.utils import get_re3data_repository

URL_RESOLVE = ["doi.org"]

# fast lookup
SERVICES_NETLOC = {
    "zenodo.org": ZenodoDataset,
    "github.com": GitHubDataset,
    "datadryad.org": DataDryadDataset,
    "huggingface.co": HuggingFaceDataset,
    "osf.io": OSFDataset,
    "data.mendeley.com": MendeleyDataset,
    # Figshare download
    "figshare.com": FigShareDataset,
    # Djehuty
    "data.4tu.nl": Djehuty,
    # DataOne repositories
    "arcticdata.io": DataOneDataset,
    "knb.ecoinformatics.org": DataOneDataset,
    "data.pndb.fr": DataOneDataset,
    "opc.dataone.org": DataOneDataset,
    "portal.edirepository.org": DataOneDataset,
    "goa.nceas.ucsb.edu": DataOneDataset,
    "data.piscoweb.org": DataOneDataset,
    "adc.arm.gov": DataOneDataset,
    "scidb.cn": DataOneDataset,
    "data.ess-dive.lbl.gov": DataOneDataset,
    "hydroshare.org": DataOneDataset,
    "ecl.earthchem.org": DataOneDataset,
    "get.iedadata.org": DataOneDataset,
    "usap-dc.org": DataOneDataset,
    "iys.hakai.org": DataOneDataset,
    "doi.pangaea.de": DataOneDataset,
    "rvdata.us": DataOneDataset,
    "sead-published.ncsa.illinois.edu": DataOneDataset,
    # DataVerse repositories (extracted from re3data)
    "dataverse.acg.maine.edu": DataverseDataset,
    "dataverse.icrisat.org": DataverseDataset,
    "datos.pucp.edu.pe": DataverseDataset,
    "datos.uchile.cl": DataverseDataset,
    "opendata.pku.edu.cn": DataverseDataset,
    "www.march.es": DataverseDataset,
    "www.murray.harvard.edu": DataverseDataset,
    "abacus.library.ubc.ca": DataverseDataset,
    "ada.edu.au": DataverseDataset,
    "adattar.unideb.hu": DataverseDataset,
    "archive.data.jhu.edu": DataverseDataset,
    "borealisdata.ca": DataverseDataset,
    "dados.ipb.pt": DataverseDataset,
    "dadosdepesquisa.fiocruz.br": DataverseDataset,
    "darus.uni-stuttgart.de": DataverseDataset,
    "data.aussda.at": DataverseDataset,
    "data.cimmyt.org": DataverseDataset,
    "data.fz-juelich.de": DataverseDataset,
    "data.goettingen-research-online.de": DataverseDataset,
    "data.inrae.fr": DataverseDataset,
    "data.scielo.org": DataverseDataset,
    "data.sciencespo.fr": DataverseDataset,
    "data.tdl.org": DataverseDataset,
    "data.univ-gustave-eiffel.fr": DataverseDataset,
    "datarepositorium.uminho.pt": DataverseDataset,
    "datasets.iisg.amsterdam": DataverseDataset,
    "dataspace.ust.hk": DataverseDataset,
    "dataverse.asu.edu": DataverseDataset,
    "dataverse.cirad.fr": DataverseDataset,
    "dataverse.csuc.cat": DataverseDataset,
    "dataverse.harvard.edu": DataverseDataset,
    "dataverse.iit.it": DataverseDataset,
    "dataverse.ird.fr": DataverseDataset,
    "dataverse.lib.umanitoba.ca": DataverseDataset,
    "dataverse.lib.unb.ca": DataverseDataset,
    "dataverse.lib.virginia.edu": DataverseDataset,
    "dataverse.nl": DataverseDataset,
    "dataverse.no": DataverseDataset,
    "dataverse.openforestdata.pl": DataverseDataset,
    "dataverse.scholarsportal.info": DataverseDataset,
    "dataverse.theacss.org": DataverseDataset,
    "dataverse.ucla.edu": DataverseDataset,
    "dataverse.unc.edu": DataverseDataset,
    "dataverse.unimi.it": DataverseDataset,
    "dataverse.yale-nus.edu.sg": DataverseDataset,
    "dorel.univ-lorraine.fr": DataverseDataset,
    "dvn.fudan.edu.cn": DataverseDataset,
    "edatos.consorciomadrono.es": DataverseDataset,
    "edmond.mpdl.mpg.de": DataverseDataset,
    "heidata.uni-heidelberg.de": DataverseDataset,
    "lida.dataverse.lt": DataverseDataset,
    "mxrdr.icm.edu.pl": DataverseDataset,
    "osnadata.ub.uni-osnabrueck.de": DataverseDataset,
    "planetary-data-portal.org": DataverseDataset,
    "qdr.syr.edu": DataverseDataset,
    "rdm.aau.edu.et": DataverseDataset,
    "rdr.kuleuven.be": DataverseDataset,
    "rds.icm.edu.pl": DataverseDataset,
    "recherche.data.gouv.fr": DataverseDataset,
    "redu.unicamp.br": DataverseDataset,
    "repod.icm.edu.pl": DataverseDataset,
    "repositoriopesquisas.ibict.br": DataverseDataset,
    "research-data.urosario.edu.co": DataverseDataset,
    "researchdata.cuhk.edu.hk": DataverseDataset,
    "researchdata.ntu.edu.sg": DataverseDataset,
    "rin.lipi.go.id": DataverseDataset,
    "ssri.is": DataverseDataset,
    "trolling.uit.no": DataverseDataset,
    "www.sodha.be": DataverseDataset,
    "www.uni-hildesheim.de": DataverseDataset,
}

# regexp lookup
SERVICES_NETLOC_REGEXP = {
    r".*\/articles\/.*\/.*\/\d+": FigShareDataset,
    r".*\/handle\/\d+\/\d+": DSpaceDataset,
}

RE3DATA_SOFTWARE = {
    "DataVerse": DataverseDataset,  # Hits on re3data 2022-09-02: (145)
    # "DSpace": DSpaceDataset,  # Hits on re3data 2022-09-02: (115)
    # "CKAN": CKANDataset,  # Hits on re3data 2022-09-02: (89)
    # "MySQL": MySQLDataset,  # Hits on re3data 2022-09-02: (86)
    # "Fedora": FedoraDataset,  # Hits on re3data 2022-09-02: (43)
    # "EPrints": EPrintsDataset,  # Hits on re3data 2022-09-02: (34)
    # "Nesstar": NesstarDataset,  # Hits on re3data 2022-09-02: (19)
    # "DigitalCommons": DigitalCommonsDataset,  # Hits on re3data 2022-09-02: (4)
    # "eSciDoc": eSciDocDataset,  # Hits on re3data 2022-09-02: (3)
    # "Opus": OpusDataset,  # Hits on re3data 2022-09-02: (2)
    # "dLibra": dLibraDataset,  # Hits on re3data 2022-09-02: (2)
}


def _base_request(
    url,
    doi=None,
    max_file_size=None,
    force_download=False,
    unzip=True,
    progress=True,
    print_only=False,
    **kwargs,
):

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
    if uri.hostname in URL_RESOLVE:

        r = requests.head(url, allow_redirects=True)
        if r.status_code == 404 and r.url and r.url.startswith("https://doi.org"):
            raise DOIError(
                f"DOI cannot be found in the DOI System, see https://doi.org/{doi}"
            )
        elif r.status_code == 405:
            # head request not allowed, try get request
            r = requests.get(url, allow_redirects=True)
        else:
            r.raise_for_status()

        logging.info(f"Redirect from {url} to {r.url}")

        return _base_request(
            r.url,
            max_file_size=max_file_size,
            doi=doi,
            force_download=force_download,
            unzip=unzip,
            progress=progress,
            print_only=print_only,
            **kwargs,
        )

    service_class = _resolve_service(url, doi)

    if service_class is None:
        raise ValueError(f"Data service for {url} is not supported.")

    logging.debug("Service found: " + str(service_class))

    return service_class(
        url,
        base_url=get_base_url(url),
        max_file_size=max_file_size,
        force_download=force_download,
        unzip=unzip,
        progress=progress,
        print_only=print_only,
        **kwargs,
    )


def get(
    url,
    output_folder,
    doi=None,
    max_file_size=None,
    force_download=False,
    unzip=True,
    progress=True,
    print_only=False,
    **kwargs,
):
    """Get the content of repository.

    Download the content of the dataset to a local folder. Provide a
    URL or DOI to the dataset in the data repository.

    Arguments
    ---------
    url: str, pathlib.Path
        The DOI of URL to the dataset.
    output_folder: str, pathlib.Path
        The folder to download the dataset files to.
    max_file_size: int
        The maximum number of bytes for a single file. If exceeded,
        the file is skipped.
    force_download: bool
        Force the download of the dataset even if there are already
        files in the distination folder. Default: False.
    unzip: bool
        Unzip is the output is a single zip file. Default: True.
    progress: bool
        Print the progress of the download. Default: True.
    print_only: bool
        Print the output of the dataset download without downloading
        the actual files (Dry run). Default: False.

    Returns
    -------

    datahugger.base.DatasetDownloader
        The dataset download object for the specific service.
    """
    return _base_request(
        url,
        doi=doi,
        max_file_size=max_file_size,
        force_download=force_download,
        unzip=unzip,
        progress=progress,
        print_only=print_only,
        **kwargs,
    ).download(output_folder, doi=doi)


def info(
    url,
    doi=None,
    **kwargs,
):
    """Get info on the content of the dataset.

    Arguments
    ---------
    url: str, pathlib.Path
        The DOI of URL to the dataset.

    Returns
    -------

    datahugger.base.DatasetDownloader
        The dataset download object for the specific service.
    """
    b = _base_request(
        url,
        doi=doi,
        **kwargs,
    )

    # collect the files
    logging.info(b.files)

    return b


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

    logging.debug(f"Resolve service: search netloc '{uri.hostname}'")
    if uri.hostname in SERVICES_NETLOC.keys():
        logging.debug("Service found: " + uri.hostname)

        return SERVICES_NETLOC[uri.hostname]

    for netloc_re, service in SERVICES_NETLOC_REGEXP.items():
        if re.match(netloc_re, url):
            return service


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
