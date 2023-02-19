from pathlib import Path

import pytest

import datahugger
from datahugger.utils import _is_url


TESTS_URLS = [
    # ("https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/KBHLOD", "tutorial1.py"),
    # ("https://doi.org/10.7910/DVN/KBHLOD", "tutorial1.py"),
    # ("https://doi.org/10.6084/m9.figshare.8851784.v1", "cross_year_data2.csv"),
    # ("https://figshare.com/articles/dataset/Long-term_behavioral_repeatability_in_wild_adult_and_captive_juvenile_turtles_implications_for_personality_development/8851784", "cross_year_data2.csv"),
    ("https://datadryad.org/stash/dataset/doi:10.5061/dryad.31zcrjdm5", "ReadmeFile.txt"),
    ("https://doi.org/10.5061/dryad.31zcrjdm5", "ReadmeFile.txt")
]



def test_url_checker():

    assert not _is_url("82949")
    assert _is_url("https://doi.org/10.5281/zenodo.6614829")


@pytest.mark.parametrize("url_or_id,output_file", TESTS_URLS)
def test_load_dyno(url_or_id, output_file, tmpdir):
    """Load repository with the generic loader."""
    datahugger.get(url_or_id, tmpdir)

    assert Path(tmpdir, output_file).exists()


def test_zenodo_unzip(tmpdir):
    """Test unzip on single file for zenodo."""

    datahugger.get("10.5281/zenodo.6625880", tmpdir)

    assert Path(tmpdir, "README.md").exists()


@pytest.mark.parametrize(
    "url_or_id",
    [
        ("10.5281/zenodo.6614829"),
        ("https://zenodo.org/record/6614829"),
        ("https://doi.org/10.5281/zenodo.6614829"),
    ],
)
def test_load_zenodo_6614829(url_or_id, tmpdir):
    datahugger.get(url_or_id, tmpdir, max_file_size=1e6)

    assert Path(tmpdir, "quasiperiod.m").exists()
    assert not Path(tmpdir, "quasiperiod.txt.gz").exists()


def test_load_github_cbsodata(tmpdir):

    datahugger.get("https://github.com/j535d165/cbsodata", tmpdir)


@pytest.mark.parametrize(
    "url_or_id",
    [
        ("https://doi.org/10.4121/21989216.v1"),
    ],
)
def test_load_figshare_4tu(url_or_id, tmpdir):
    """Load repository with the generic loader."""
    datahugger.get(url_or_id, tmpdir)

    assert Path(tmpdir, "README.txt").exists()

@pytest.mark.parametrize(
    "url_or_id,fn",
    [
        ("https://doi.org/10.18739/A2KH0DZ42", "2012F_Temperature_Data.csv"),
    ],
)
def test_load_dataone(url_or_id, tmpdir, fn):
    """Load repository with the generic loader."""
    datahugger.get(url_or_id, tmpdir)

    assert Path(tmpdir, fn).exists()


@pytest.mark.parametrize(
    "url_or_id",
    [
        ("https://osf.io/kq573/"),
        ("https://doi.org/10.17605/OSF.IO/KQ573"),
    ],
)
def test_load_osf_kq573(url_or_id, tmpdir):
    """Load repository with the generic loader."""
    datahugger.get(url_or_id, tmpdir)

    assert Path(tmpdir, "nest_area_data.xlsx").exists()


@pytest.mark.parametrize(
    "url_or_id",
    [
        ("10.17632/p6wmtv6t5g.2"),
        ("10.17632/p6wmtv6t5g"),
    ],
)
def test_load_mendeley_p6wmtv6t5g(url_or_id, tmpdir):
    """Load repository with the generic loader."""
    datahugger.get(url_or_id, tmpdir)

    assert Path(tmpdir, "READMI Stranding Sea Turtle records.pdf").exists()
