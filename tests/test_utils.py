from datahugger.utils import _is_url
from datahugger.utils import get_re3data_repositories


def test_url_checker():
    assert not _is_url("82949")
    assert _is_url("https://doi.org/10.5281/zenodo.6614829")


def test_re3data_repos():
    get_re3data_repositories()
