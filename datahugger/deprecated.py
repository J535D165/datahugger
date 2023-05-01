from datahugger.api import get


def load_repository(
    url,
    output_folder,
    doi=None,
    max_file_size=None,
    force_download=False,
    unzip=True,
    progress=True,
    print_only=False,
    **kwargs,
):
    """Load repository is deprecated.

    Use datahugger.get() instead.
    """
    return get(
        url,
        output_folder,
        doi=doi,
        max_file_size=max_file_size,
        force_download=force_download,
        unzip=unzip,
        progress=progress,
        print_only=print_only,
        **kwargs,
    )
