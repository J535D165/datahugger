import pytest

import datahugger
from datahugger.api import _resolve_service
from datahugger.handles import DOI
from datahugger.handles import ArXiv
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


def test_get_doi_metadata_cls(tmpdir):
    doi = DOI.parse("10.34894/FXUGHW")
    doi.resolve()

    m = doi.metadata.cls()

    assert isinstance(m, dict)


def test_get_doi_metadata_bibtex(tmpdir):
    doi = DOI.parse("10.34894/FXUGHW")
    doi.resolve()

    m = doi.metadata.bibtex()

    assert isinstance(m, str)


def test_arxiv_handle(tmpdir):
    arxiv = ArXiv.parse("https://arxiv.org/abs/astro-ph/9802301v1")

    m = arxiv.metadata.cls()

    assert isinstance(m, dict)


def test_get_doi_metadata_from_instance(tmpdir):
    # initiate datahugger downloader and then get metadata
    service = datahugger.info("10.34894/FXUGHW")
    m1 = service.resource.metadata.citation()

    # initiate datahugger resource and get metadata
    doi = DOI.parse("10.34894/FXUGHW")
    doi.resolve()
    m2 = doi.metadata.citation()

    assert m1 == m2 is not None
