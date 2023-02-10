import logging
from urllib.parse import urlparse

import requests

from datahugger.exceptions import DOIError
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
from datahugger.utils import get_base_url
from datahugger.utils import get_datapublisher_from_doi
from datahugger.utils import get_re3data_repositories
from datahugger.utils import get_re3data_repository

URL_RESOLVE = ["doi.org"]

# fast lookup
SERVICES_NETLOC = {
    "zenodo.org": ZenodoDownload,
    "github.com": GitHubDownload,
    "datadryad.org": DataDryadDownload,
    "huggingface.co": HuggingFaceDownload,
    "osf.io": OSFDownload,
    "data.mendeley.com": MendeleyDownload,
    # Figshare download
    "figshare.com": FigShareDownload,
    "data.4tu.nl": FigShareDownload,
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
    # DataVerse repositories (extracted from re3data)
    "dataverse.acg.maine.edu": DataverseDownload,
    "dataverse.icrisat.org": DataverseDownload,
    "datos.pucp.edu.pe": DataverseDownload,
    "datos.uchile.cl": DataverseDownload,
    "opendata.pku.edu.cn": DataverseDownload,
    "www.march.es": DataverseDownload,
    "www.murray.harvard.edu": DataverseDownload,
    "abacus.library.ubc.ca": DataverseDownload,
    "ada.edu.au": DataverseDownload,
    "adattar.unideb.hu": DataverseDownload,
    "archive.data.jhu.edu": DataverseDownload,
    "borealisdata.ca": DataverseDownload,
    "dados.ipb.pt": DataverseDownload,
    "dadosdepesquisa.fiocruz.br": DataverseDownload,
    "darus.uni-stuttgart.de": DataverseDownload,
    "data.aussda.at": DataverseDownload,
    "data.cimmyt.org": DataverseDownload,
    "data.fz-juelich.de": DataverseDownload,
    "data.goettingen-research-online.de": DataverseDownload,
    "data.inrae.fr": DataverseDownload,
    "data.scielo.org": DataverseDownload,
    "data.sciencespo.fr": DataverseDownload,
    "data.tdl.org": DataverseDownload,
    "data.univ-gustave-eiffel.fr": DataverseDownload,
    "datarepositorium.uminho.pt": DataverseDownload,
    "datasets.iisg.amsterdam": DataverseDownload,
    "dataspace.ust.hk": DataverseDownload,
    "dataverse.asu.edu": DataverseDownload,
    "dataverse.cirad.fr": DataverseDownload,
    "dataverse.csuc.cat": DataverseDownload,
    "dataverse.harvard.edu": DataverseDownload,
    "dataverse.iit.it": DataverseDownload,
    "dataverse.ird.fr": DataverseDownload,
    "dataverse.lib.umanitoba.ca": DataverseDownload,
    "dataverse.lib.unb.ca": DataverseDownload,
    "dataverse.lib.virginia.edu": DataverseDownload,
    "dataverse.nl": DataverseDownload,
    "dataverse.no": DataverseDownload,
    "dataverse.openforestdata.pl": DataverseDownload,
    "dataverse.scholarsportal.info": DataverseDownload,
    "dataverse.theacss.org": DataverseDownload,
    "dataverse.ucla.edu": DataverseDownload,
    "dataverse.unc.edu": DataverseDownload,
    "dataverse.unimi.it": DataverseDownload,
    "dataverse.yale-nus.edu.sg": DataverseDownload,
    "dorel.univ-lorraine.fr": DataverseDownload,
    "dvn.fudan.edu.cn": DataverseDownload,
    "edatos.consorciomadrono.es": DataverseDownload,
    "edmond.mpdl.mpg.de": DataverseDownload,
    "heidata.uni-heidelberg.de": DataverseDownload,
    "lida.dataverse.lt": DataverseDownload,
    "mxrdr.icm.edu.pl": DataverseDownload,
    "osnadata.ub.uni-osnabrueck.de": DataverseDownload,
    "planetary-data-portal.org": DataverseDownload,
    "qdr.syr.edu": DataverseDownload,
    "rdm.aau.edu.et": DataverseDownload,
    "rdr.kuleuven.be": DataverseDownload,
    "rds.icm.edu.pl": DataverseDownload,
    "recherche.data.gouv.fr": DataverseDownload,
    "redu.unicamp.br": DataverseDownload,
    "repod.icm.edu.pl": DataverseDownload,
    "repositoriopesquisas.ibict.br": DataverseDownload,
    "research-data.urosario.edu.co": DataverseDownload,
    "researchdata.cuhk.edu.hk": DataverseDownload,
    "researchdata.ntu.edu.sg": DataverseDownload,
    "rin.lipi.go.id": DataverseDownload,
    "ssri.is": DataverseDownload,
    "trolling.uit.no": DataverseDownload,
    "www.sodha.be": DataverseDownload,
    "www.uni-hildesheim.de": DataverseDownload,
}

# regexp lookup
SERVICES_NETLOC_REGEXP = {"*.figshare.com": FigShareDownload}

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
    force_download=False,
    unzip=True,
    progress=True,
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
    if uri.hostname in URL_RESOLVE:

        r = requests.head(url, allow_redirects=True)
        if r.status_code == 404:
            raise DOIError(
                f"DOI cannot be found in the DOI System, see https://doi.org/{doi}"
            )
        if r.status_code != 200:
            raise ValueError("Error")

        logging.info(f"Redirect from {url} to {r.url}")

        return load_repository(
            r.url,
            output_folder,
            max_file_size=max_file_size,
            doi=doi,
            force_download=force_download,
            unzip=unzip,
            progress=progress,
            *args,
            **kwargs,
        )

    service_class = _resolve_service(url, doi)

    if service_class is None:
        raise ValueError(f"Data service for {url} is not supported.")

    logging.debug("Service found: " + str(service_class))

    return service_class(
        base_url=get_base_url(url),
        max_file_size=max_file_size,
        force_download=force_download,
        unzip=unzip,
        progress=progress,
        *args,
        **kwargs,
    ).get(url, output_folder, doi=doi)


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
