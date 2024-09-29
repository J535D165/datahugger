from pathlib import Path
from pathlib import PosixPath

import pytest

import datahugger


def test_get_repositories(location, files, ignored_files, dh_kwargs, tmpdir):
    datahugger.get(location, tmpdir, **dh_kwargs)

    # print the files in the tmpdir (for debugging)
    for file in Path(tmpdir).iterdir():
        print(file.relative_to(tmpdir))

    if files:
        assert PosixPath(tmpdir, files).exists()

    if ignored_files:
        assert not PosixPath(tmpdir, ignored_files).exists()


@pytest.mark.skip("Not implemented")
def test_info(location, files, ignored_files, dh_kwargs, tmpdir):
    dh_info = datahugger.info(location)

    assert files in dh_info.files
