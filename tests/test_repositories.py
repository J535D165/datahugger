from pathlib import Path

import pytest

import datahugger
from datahugger.utils import _is_url

TESTS_URLS = [
    # Zenodo
    ("10.5281/zenodo.6625880", "README.md"),
    # Dataverse
    (
        "https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/KBHLOD",
        "tutorial1.py",
    ),
    ("https://doi.org/10.7910/DVN/KBHLOD", "tutorial1.py"),
    ("https://hdl.handle.net/10622/NHJZUD", "ERRHS_7_01_data_1795.tab"),
    # Dataverse single file
    ("10.7910/DVN/HZBYG7/RQ26H2", "Table 2.do"),
    # Figshare
    ("https://doi.org/10.6084/m9.figshare.8851784.v1", "cross_year_data2.csv"),
    (
        "https://figshare.com/articles/dataset/Long-term_behavioral_repeatability_in_wild_adult_and_captive_juvenile_turtles_implications_for_personality_development/8851784",
        "cross_year_data2.csv",
    ),
    (
        "https://doi.org/10.15131/shef.data.22010159.v2",
        "ScHARR QUIT evaluation statistical and health economic analysis plan.pdf",
    ),
    # Djehuty
    ("https://doi.org/10.4121/21989216.v1", "README.txt"),
    # Dryad
    (
        "https://datadryad.org/stash/dataset/doi:10.5061/dryad.31zcrjdm5",
        "ReadmeFile.txt",
    ),
    ("https://doi.org/10.5061/dryad.31zcrjdm5", "ReadmeFile.txt"),
    # OSF
    ("https://osf.io/kq573/", "nest_area_data.xlsx"),
    ("https://doi.org/10.17605/OSF.IO/KQ573", "nest_area_data.xlsx"),
    ("https://doi.org/10.17605/OSF.IO/9X6CA", "jobs.sh"),
    # Mendeley
    (
        "https://doi.org/10.17632/p6wmtv6t5g.2",
        "READMI Stranding Sea Turtle records.pdf",
    ),
    ("https://doi.org/10.17632/p6wmtv6t5g", "READMI Stranding Sea Turtle records.pdf"),
    # Dataone
    ("https://doi.org/10.18739/A2KH0DZ42", "2012F_Temperature_Data.csv"),
    # DSpace
    ("https://uhra.herts.ac.uk/handle/2299/26087", "pdf.pdf"),
    (
        "https://repositorioinstitucional.ceu.es/handle/10637/2741",
        "Aquaporin_1_JAMartin_et_al_MedSport_2009.pdf",
    ),
    # huggingface
    # ("10.57967/hf/0034", "test.csv"),
    # Pangaea
    ("https://doi.org/10.1594/PANGAEA.954547", "Gubbio_age.tab"),
    ("https://doi.pangaea.de/10.1594/PANGAEA.954543", "AA_age.tab"),
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


def test_info_without_loading(tmpdir):
    dh_get = datahugger.get("https://osf.io/wdzh5/", output_folder=".", print_only=True)

    dh_info = datahugger.info("https://osf.io/wdzh5/")

    assert dh_get.dataset.files == dh_info.files


def test_huggingface(tmpdir):
    datahugger.get(
        "https://huggingface.co/datasets/wikitext",
        tmpdir,
        params={"name": "wikitext-2-v1"},
    )


def test_huggingface_without_params(tmpdir):
    with pytest.raises(ValueError):
        datahugger.get("https://huggingface.co/datasets/wikitext", tmpdir)
