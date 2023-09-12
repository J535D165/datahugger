import logging

from datahugger.handles import DOI
from datahugger.handles import Handle
from datahugger.handles import is_doi
from datahugger.handles import is_handle
from datahugger.resolvers import _resolve_service


def info(
    url,
    max_file_size=None,
    force_download=False,
    unzip=True,
    progress=True,
    print_only=False,
    **kwargs,
):
    """Get info on the content of the dataset.

    Arguments
    ---------
    url: str, pathlib.Path
        The DOI of URL to the dataset.
    output_folder: str, pathlib.Path
        The folder to download the dataset files to.
    max_file_size: int
        The maximum number of bytes for a single file. If exceeded,
        the file is skipped.
    force_download: bool
        Force the download of the dataset even if there are already
        files in the destination folder. Default: False.
    unzip: bool
        Unzip is the output is a single zip file. Default: True.
    progress: bool
        Print the progress of the download. Default: True.
    print_only: bool
        Print the output of the dataset download without downloading
        the actual files (Dry run). Default: False.

    Returns
    -------

    datahugger.base.DatasetDownloader
        The dataset download object for the specific service.
    """

    if is_doi(url):
        handle = DOI.parse(url)
        handle.resolve()
    elif is_handle(url):
        handle = Handle.parse(url)
        handle.resolve()
    else:
        handle = url

    service_class = _resolve_service(handle)

    service = service_class(
        handle,
        max_file_size=max_file_size,
        force_download=force_download,
        unzip=unzip,
        progress=progress,
        print_only=print_only,
        **kwargs,
    )

    # collect the files
    logging.info(service.files)

    return service


def get(
    url,
    output_folder,
    max_file_size=None,
    force_download=False,
    unzip=True,
    progress=True,
    print_only=False,
    **kwargs,
):
    """Get the content of repository.

    Download the content of the dataset to a local folder. Provide a
    URL or DOI to the dataset in the data repository.

    Arguments
    ---------
    url: str, pathlib.Path
        The DOI of URL to the dataset.
    output_folder: str, pathlib.Path
        The folder to download the dataset files to.
    max_file_size: int
        The maximum number of bytes for a single file. If exceeded,
        the file is skipped.
    force_download: bool
        Force the download of the dataset even if there are already
        files in the destination folder. Default: False.
    unzip: bool
        Unzip is the output is a single zip file. Default: True.
    progress: bool
        Print the progress of the download. Default: True.
    print_only: bool
        Print the output of the dataset download without downloading
        the actual files (Dry run). Default: False.

    Returns
    -------

    datahugger.base.DatasetDownloader
        The dataset download object for the specific service.
    """

    service = info(
        url,
        max_file_size=max_file_size,
        force_download=force_download,
        unzip=unzip,
        progress=progress,
        print_only=print_only,
        **kwargs,
    )

    return service.download(output_folder)
