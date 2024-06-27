from pathlib import Path

import datahugger


def test_get_repositories(location, files, ignored_files, dh_kwargs, tmpdir):
    datahugger.get(location, tmpdir, **dh_kwargs)

    if files:
        assert Path(tmpdir, files).exists()

    if ignored_files:
        assert not Path(tmpdir, ignored_files).exists()


# def test_info_without_loading(tmpdir):
#     dh_get = datahugger.get(
#         "https://osf.io/wdzh5/", output_folder=".", print_only=True)

#     dh_info = datahugger.info("https://osf.io/wdzh5/")

#     assert dh_get.dataset.files == dh_info.files
