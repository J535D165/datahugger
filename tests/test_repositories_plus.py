from pathlib import Path

import pytest

import datahugger


def test_huggingface(tmpdir):
    datahugger.get(
        "https://huggingface.co/datasets/wikitext",
        tmpdir,
        params={"name": "wikitext-2-v1"},
    )


def test_huggingface_without_params(tmpdir):
    with pytest.raises(ValueError):
        datahugger.get("https://huggingface.co/datasets/wikitext", tmpdir)


def test_filter(tmpdir):
    datahugger.get("https://zenodo.org/records/6614829", tmpdir, filter_files=r".*\.m")

    files = [file for file in Path(tmpdir).iterdir()]
    assert len(files) == 1
    assert files[0].name == "quasiperiod.m"
