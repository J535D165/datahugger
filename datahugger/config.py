from datahugger.services import ArXivDataset
from datahugger.services import DataDryadDataset
from datahugger.services import DataOneDataset
from datahugger.services import DataverseDataset
from datahugger.services import DjehutyDataset
from datahugger.services import DSpaceDataset
from datahugger.services import FigShareDataset
from datahugger.services import GitHubDataset
from datahugger.services import HuggingFaceDataset
from datahugger.services import MendeleyDataset
from datahugger.services import OSFDataset
from datahugger.services import PangaeaDataset
from datahugger.services import ZenodoDataset

# fast lookup
SERVICES_NETLOC = {
    "arxiv.org": ArXivDataset,
    "zenodo.org": ZenodoDataset,
    "github.com": GitHubDataset,
    "datadryad.org": DataDryadDataset,
    "huggingface.co": HuggingFaceDataset,
    "osf.io": OSFDataset,
    "data.mendeley.com": MendeleyDataset,
    # Figshare download
    "figshare.com": FigShareDataset,
    # Djehuty
    "data.4tu.nl": DjehutyDataset,
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
    "doi.pangaea.de": PangaeaDataset,
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
    r".*\/dataset\.xhtml\?persistentId\=.*": DataverseDataset,
}

# add keys in lower-case for fast case-insensitive lookups
RE3DATA_SOFTWARE = {
    "dataverse": DataverseDataset,
    "dspace": DSpaceDataset,
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
