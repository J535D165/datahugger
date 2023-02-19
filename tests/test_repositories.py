from pathlib import Path

import pytest

import datahugger
from datahugger.utils import _is_url

TESTS_URLS = [

    # Zenodo
    ("10.5281/zenodo.6625880", "README.md"),

    # Dataverse
    ("https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/KBHLOD", "tutorial1.py"),
    ("https://doi.org/10.7910/DVN/KBHLOD", "tutorial1.py"),

    # Figshare
    ("https://doi.org/10.6084/m9.figshare.8851784.v1", "cross_year_data2.csv"),
    ("https://figshare.com/articles/dataset/Long-term_behavioral_repeatability_in_wild_adult_and_captive_juvenile_turtles_implications_for_personality_development/8851784", "cross_year_data2.csv"),
    ("https://doi.org/10.4121/21989216.v1", "README.txt"),

    # Dryad
    ("https://datadryad.org/stash/dataset/doi:10.5061/dryad.31zcrjdm5", "ReadmeFile.txt"),
    ("https://doi.org/10.5061/dryad.31zcrjdm5", "ReadmeFile.txt"),

    # OSF
    ("https://osf.io/kq573/", "nest_area_data.xlsx"),
    ("https://doi.org/10.17605/OSF.IO/KQ573", "nest_area_data.xlsx"),

    # Mendeley
    ("https://doi.org/10.17632/p6wmtv6t5g.2", "READMI Stranding Sea Turtle records.pdf"),
    ("https://doi.org/10.17632/p6wmtv6t5g", "READMI Stranding Sea Turtle records.pdf"),

    # Dataone
    ("https://doi.org/10.18739/A2KH0DZ42", "2012F_Temperature_Data.csv"),
]


def test_url_checker():

    assert not _is_url("82949")
    assert _is_url("https://doi.org/10.5281/zenodo.6614829")


@pytest.mark.parametrize("url_or_id,output_file", TESTS_URLS)
def test_load_dyno(url_or_id, output_file, tmpdir):
    """Load repository with the generic loader."""
    datahugger.get(url_or_id, tmpdir)

    assert Path(tmpdir, output_file).exists()


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
