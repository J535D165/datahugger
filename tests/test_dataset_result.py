import pytest

import datahugger


@pytest.mark.parametrize(
    "url_or_id",
    [
        ("10.5281/zenodo.6614829"),
        ("https://zenodo.org/record/6614829"),
        ("https://doi.org/10.5281/zenodo.6614829"),
    ],
)
def test_load_zenodo_6614829(url_or_id, tmpdir, capsys):
    dataset = datahugger.get(url_or_id, tmpdir, max_file_size=1e6)

    dataset.tree()

    captured = capsys.readouterr()
    assert "quasiperiod.m" in captured.out

    # test count
    assert "12 file" in captured.out
    assert 12 == len(dataset)


def test_load_github_cbsodata(tmpdir, capsys):
    dataset = datahugger.get("https://github.com/j535d165/cbsodata", tmpdir)

    dataset.tree()

    captured = capsys.readouterr()
    assert ".gitignore" in captured.out
