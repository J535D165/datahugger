import pytest

from datahugger import load_repository
from datahugger.api import _resolve_service
from datahugger.services import DataverseDownload


def test_resolve_service():

    url = "https://dataverse.nl/dataset.xhtml?persistentId=doi:10.34894/FXUGHW"
    doi = "10.34894/FXUGHW"

    assert _resolve_service(url, doi) == DataverseDownload


@pytest.mark.xfail(raises=ValueError)
def test_doi_not_found(tmpdir):

    doi = "10.1038/s42256-020-00287"

    load_repository(doi, tmpdir)
