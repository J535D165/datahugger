import pytest

from datahugger import load_repository


@pytest.mark.parametrize(
    "url_or_id",
    [
        ("10.5281/zenodo.6614829"),
        ("https://zenodo.org/record/6614829"),
        ("https://doi.org/10.5281/zenodo.6614829"),
    ],
)
def test_load_zenodo_6614829(url_or_id, tmpdir):
    dataset = load_repository(url_or_id, tmpdir, max_file_size=1e6)

    dataset.tree()

    s_tree = dataset.tree(printout=False)

    assert "quasiperiod.m" in s_tree


def test_load_github_cbsodata(tmpdir):
    dataset = load_repository("https://github.com/j535d165/cbsodata", tmpdir)

    dataset.tree()

    s_tree = dataset.tree(printout=False)

    assert ".gitignore" in s_tree
