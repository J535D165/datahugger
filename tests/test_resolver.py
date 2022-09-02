from datahugger.api import _resolve_service
from datahugger.services import DataverseDownload


def test_resolve_service():

    url = "https://dataverse.nl/dataset.xhtml?persistentId=doi:10.34894/FXUGHW"
    doi = "10.34894/FXUGHW"

    assert _resolve_service(url, doi) == DataverseDownload
