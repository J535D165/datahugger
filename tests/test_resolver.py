import pytest

import datahugger
from datahugger.api import _resolve_service
from datahugger.handles import DOI
from datahugger.services import DataverseDataset


def test_resolve_service():
    url = "https://dataverse.nl/dataset.xhtml?persistentId=doi:10.34894/FXUGHW"
    doi = "10.34894/FXUGHW"

    assert _resolve_service(url, doi) == DataverseDataset


@pytest.mark.xfail(raises=ValueError)
def test_doi_not_found(tmpdir):
    doi = "10.1038/s42256-020-00287"

    datahugger.get(doi, tmpdir)


def test_resolve_service_via_doi_handle(tmpdir):
    doi = DOI.parse("10.34894/FXUGHW")
    doi.resolve()

    assert isinstance(doi, DOI)
    assert isinstance(datahugger.get(doi, tmpdir), DataverseDataset)


def test_get_doi_metadata(tmpdir):
    doi = DOI.parse("10.34894/FXUGHW")
    doi.resolve()

    m = doi.metadata.get_doi_metadata()

    assert isinstance(m, dict)


def test_get_doi_metadata_bibtex(tmpdir):
    doi = DOI.parse("10.34894/FXUGHW")
    doi.resolve()

    m = doi.metadata.bibtex()

    assert isinstance(m, str)
