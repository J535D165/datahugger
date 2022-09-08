import argparse
import logging

from datahugger import __version__
from datahugger import load_repository

# test with
# python -m datahugger https://doi.org/10.5061/dryad.31zcrjdm5 tmp/my_test; rm -r tmp/my_test


def main():

    parser = argparse.ArgumentParser(
        prog="datahugger",
        description="One data downloader for all scientific data.",
    )
    parser.add_argument(
        "url_or_doi",
        help="An URL or DOI to scientific data repository.",
    )

    parser.add_argument(
        "output_dir",
        help="The dir to store the output to.",
    )

    parser.add_argument(
        "--max_file_size",
        default=None,
        help="Skip files larger than this size. Might not work for all services.",
    )

    parser.add_argument(
        "--download_mode",
        default="skip_if_exists",
        help="Skip files if they already exist.",
    )

    parser.add_argument(
        "--log", default="WARNING", help="Python based log levels. Default: WARNING."
    )

    # version
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version='%(prog)s {version}'.format(version=__version__)
    )

    args, _ = parser.parse_known_args()

    logging.basicConfig(level=args.log)

    # Start downloading
    load_repository(
        args.url_or_doi,
        args.output_dir,
        max_file_size=args.max_file_size,
        download_mode=args.download_mode,
    )

    print("\u001b[32mRepository content succesfully downloaded.\u001b[0m")


if __name__ == "__main__":

    main()
