from datahugger.handles import DOI
from datahugger.handles import ArXiv
from datahugger.handles import Handle
from datahugger.handles import is_arxiv
from datahugger.handles import is_doi
from datahugger.handles import is_handle
from datahugger.resolvers import _resolve_service


def info(
    resource,
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
    resource: str, pathlib.Path
        The URL, DOI, or Handle of the dataset.
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

    if isinstance(resource, str) and is_doi(resource):
        handle = DOI.parse(resource)
        handle.resolve()
    elif isinstance(resource, str) and is_handle(resource):
        handle = Handle.parse(resource)
        handle.resolve()
    elif isinstance(resource, str) and is_arxiv(resource):
        handle = ArXiv.parse(resource)
    else:
        handle = resource

    service_class = _resolve_service(handle)

    return service_class(
        handle,
        max_file_size=max_file_size,
        force_download=force_download,
        unzip=unzip,
        progress=progress,
        print_only=print_only,
        **kwargs,
    )


def get(
    resource,
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
    resource: str, pathlib.Path
        The URL, DOI, or Handle of the dataset.
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
        resource,
        max_file_size=max_file_size,
        force_download=force_download,
        unzip=unzip,
        progress=progress,
        print_only=print_only,
        **kwargs,
    )

    return service.download(output_folder)
