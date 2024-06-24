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
