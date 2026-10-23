import pytest

import datahugger
from datahugger.api import _resolve_service
from datahugger.exceptions import RepositoryNotSupportedError
from datahugger.handles import DOI
from datahugger.handles import ArXiv
from datahugger.services import DataverseDataset


def test_resolve_service():
    doi = DOI.parse("10.34894/FXUGHW")
    doi.resolve()

    service = _resolve_service(doi)(doi)

    assert isinstance(service, DataverseDataset)


@pytest.mark.xfail(raises=ValueError)
def test_doi_not_found(tmpdir):
    doi = "10.1038/s42256-020-00287"

    datahugger.get(doi, tmpdir)


def test_resolve_service_via_doi_handle(tmpdir):
    doi = DOI.parse("10.34894/FXUGHW")
    doi.resolve()

    r = datahugger.get(doi, tmpdir)

    assert isinstance(doi, DOI)
    assert isinstance(r.dataset, DataverseDataset)


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


@pytest.mark.parametrize(
    "url",
    [
        "https://evil.example.org/dataset.xhtml?persistentId=doi:10.1234",
        "https://evil.example.org/handle/123/456",
        "https://evil.example.org/articles/dataset/name/123",
    ],
)
def test_unknown_host_not_supported(url):
    with pytest.raises(RepositoryNotSupportedError):
        _resolve_service(url)


def test_unknown_host_pattern_must_match_path():
    url = "https://evil.example.org/?next=/dataset.xhtml?persistentId=doi:10.1234"

    with pytest.raises(RepositoryNotSupportedError):
        _resolve_service(url, allow_unknown_hosts=True)


def test_unknown_host_allowed_when_opted_in():
    url = "https://dataverse.example.org/dataset.xhtml?persistentId=doi:10.1234"

    assert _resolve_service(url, allow_unknown_hosts=True) is DataverseDataset
