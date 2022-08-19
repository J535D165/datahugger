from pathlib import Path

import pytest

from datahugger import load_repository
from datahugger.utils import _is_url


def test_url_checker():

    assert not _is_url("82949")
    assert _is_url("https://doi.org/10.5281/zenodo.6614829")


def test_zenodo_unzip(tmpdir):
    """Test unzip on single file for zenodo."""

    load_repository("10.5281/zenodo.6625880", tmpdir)

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
    load_repository(url_or_id, tmpdir, max_file_size=1e6)

    assert Path(tmpdir, "quasiperiod.m").exists()
    assert not Path(tmpdir, "quasiperiod.txt.gz").exists()


@pytest.mark.parametrize(
    "url_or_id",
    [
        ("10.7910/DVN/KBHLOD"),
        ("doi:10.7910/DVN/KBHLOD"),
        (
            "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/KBHLOD"
        ),
        ("https://doi.org/10.7910/DVN/KBHLOD"),
    ],
)
def test_load_dataverse_KBHLOD(url_or_id, tmpdir):
    """Load repository with the generic loader."""
    load_repository(url_or_id, tmpdir)

    assert Path(tmpdir, "tutorial1.py").exists()


def test_load_github_cbsodata(tmpdir):

    load_repository("https://github.com/j535d165/cbsodata", tmpdir)


@pytest.mark.parametrize(
    "url_or_id",
    [
        ("10.6084/m9.figshare.8851784.v1"),
        ("https://figshare.com/articles/dataset/Long-term_behavioral_repeatability_in_wild_adult_and_captive_juvenile_turtles_implications_for_personality_development/8851784"),  # noqa
        ("https://doi.org/10.6084/m9.figshare.8851784.v1"),
    ],
)
def test_load_figshare_8851784(url_or_id, tmpdir):
    """Load repository with the generic loader."""
    load_repository(url_or_id, tmpdir)

    assert Path(tmpdir, "cross_year_data2.csv").exists()


@pytest.mark.parametrize(
    "url_or_id",
    [
        ("https://datadryad.org/stash/dataset/doi:10.5061/dryad.31zcrjdm5"),
        ("https://doi.org/10.5061/dryad.31zcrjdm5"),
    ],
)
def test_load_dryad_31zcrjdm5(url_or_id, tmpdir):
    """Load repository with the generic loader."""
    load_repository(url_or_id, tmpdir)

    assert Path(tmpdir, "ReadmeFile.txt").exists()


@pytest.mark.parametrize(
    "url_or_id,fn",
    [
        ("https://doi.org/10.18739/A2KH0DZ42", "2012F_Temperature_Data.csv"),
    ],
)
def test_load_dataone(url_or_id, tmpdir, fn):
    """Load repository with the generic loader."""
    load_repository(url_or_id, tmpdir)

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
    load_repository(url_or_id, tmpdir)

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
    load_repository(url_or_id, tmpdir)

    assert Path(tmpdir, "READMI Stranding Sea Turtle records.pdf").exists()
