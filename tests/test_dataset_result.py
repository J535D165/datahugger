import pytest

import datahugger


@pytest.mark.parametrize(
    "url_or_id",
    [
        ("https://doi.org/10.5281/zenodo.6614829"),
    ],
)
def test_load_zenodo_6614829(url_or_id, tmpdir, capsys):
    dh = datahugger.get(url_or_id, tmpdir, max_file_size=1e6)

    dh.tree()

    captured = capsys.readouterr()
    assert "quasiperiod.m" in captured.out

    # test count
    assert "12 file" in captured.out
    assert 12 == (len(dh) - 1)


def test_load_github_cbsodata(tmpdir, capsys):
    dh = datahugger.get("https://github.com/j535d165/cbsodata", tmpdir)

    dh.tree()

    captured = capsys.readouterr()
    assert ".gitignore" in captured.out
