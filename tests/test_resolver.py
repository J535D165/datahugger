import pytest

import datahugger
from datahugger.api import _resolve_service
from datahugger.services import DataverseDataset


def test_resolve_service():

    url = "https://dataverse.nl/dataset.xhtml?persistentId=doi:10.34894/FXUGHW"
    doi = "10.34894/FXUGHW"

    assert _resolve_service(url, doi) == DataverseDataset


@pytest.mark.xfail(raises=ValueError)
def test_doi_not_found(tmpdir):

    doi = "10.1038/s42256-020-00287"

    datahugger.get(doi, tmpdir)
