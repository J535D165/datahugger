import argparse
import logging

from datahugger import __version__
from datahugger import load_repository
from datahugger.exceptions import DOIError

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
        type=int,
        help="Skip files larger than this size. Might not work for all services.",
    )

    parser.add_argument("-f", "--force-download", dest="force_download", action="store_true")
    parser.set_defaults(force_download=False)

    parser.add_argument("--unzip", action="store_true")
    parser.add_argument("--no-unzip", dest="unzip", action="store_false")
    parser.set_defaults(unzip=True)

    parser.add_argument("--progress", action="store_true")
    parser.add_argument("--no-progress", dest="progress", action="store_false")
    parser.set_defaults(progress=True)

    parser.add_argument(
        "--log", default="WARNING", help="Python based log levels. Default: WARNING."
    )

    # version
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=__version__),
    )

    args, _ = parser.parse_known_args()

    logging.basicConfig(level=args.log)

    try:

        # Start downloading
        load_repository(
            args.url_or_doi,
            args.output_dir,
            max_file_size=args.max_file_size,
            force_download=args.force_download,
            unzip=args.unzip,
            progress=args.progress,
        )

    except DOIError as doi_err:
        # raise error when log level is DEBUG
        if logging.DEBUG == logging.root.level:
            raise doi_err
        else:
            print(f"\u001b[31mDOI Error: {doi_err}\u001b[0m")
            exit(1)

    except Exception as err:
        # raise error when log level is DEBUG
        if logging.DEBUG == logging.root.level:
            raise err
        else:
            print(f"\u001b[31mFailed to download: {err}\u001b[0m")
            exit(1)

    print("\u001b[32mDataset successfully downloaded.\u001b[0m")


if __name__ == "__main__":

    main()
