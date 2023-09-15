import argparse
import datetime
import json
from pathlib import Path

import pandas as pd
import requests

# from pydatacite import DOIs
import datahugger
from datahugger import RepositoryNotSupportedError

BENCHMARK_FILE = Path("benchmark", "benchmark_datasets.csv")
BENCHMARK_OUTPUT_FILE = Path("benchmark", "benchmark_datasets_tested.csv")


def create_dataset(args):
    records = [
        x
        for y in range(1)
        for x in requests.get(
            "https://api.datacite.org/dois?random=true&page[size]=100"
        ).json()["data"]
    ]

    result = []
    for r in records:
        result.append({"id": r["id"], "type": r["type"], "url": r["attributes"]["url"]})

    pd.DataFrame(result).to_csv(
        Path("benchmark", "datacite", f"datacite_random_{datetime.datetime.now()}"),
        index=False,
    )


def merge_datasets(args):
    datasets = Path("benchmark", "datacite").glob("*")

    df = pd.concat([pd.read_csv(d) for d in datasets], axis=0)
    df.drop_duplicates(inplace=True)

    df.to_csv(BENCHMARK_FILE, index=False)


def run(args):
    df = pd.read_csv(BENCHMARK_FILE)

    df[["service", "error"]] = df.apply(test_repo, axis=1, result_type="expand")
    df.to_csv(BENCHMARK_OUTPUT_FILE)

    print(df)


def test_repo(r):
    try:
        cl = datahugger.info(r["id"]).__class__.__name__
        print(r["id"], f"service found: {cl}")
        return {"service": cl, "error": None}
    except RepositoryNotSupportedError:
        # Repository not supported, but no error
        return {"service": None, "error": None}
    except Exception as err:
        print(r["id"], f"results in: {err}")
        return {"service": None, "error": str(err)}


def get_coverage(args):
    df = pd.read_csv(BENCHMARK_OUTPUT_FILE)
    cov = df["service"].notnull().sum() / len(df)

    print(f"Dataset coverage: {cov * 100}%")

    with open(".datacite_coverage.json", "w") as f:
        json.dump({"datasets": cov * 100}, f)


def get_report(args):
    df = pd.read_csv(BENCHMARK_OUTPUT_FILE, index_col=0)

    frac_supported = df["service"].notnull().sum() / len(df)
    frac_with_error = df["error"].notnull().sum() / len(df)
    frac_not_supported = 1 - frac_supported - frac_with_error

    print("## Coverage report")
    print(
        f"The following benchmark was applied to {len(df)}",
        "randomly selected records from Datacite.",
    )
    print()
    print("### Percentages")
    print(f"Percentage of datasets supported: {frac_supported*100:.1f}%")
    print(f"Percentage of datasets not supported: {frac_not_supported*100:.1f}%")
    print(f"Percentage of datasets with error: {frac_with_error*100:.1f}%")

    print()
    print("### Table with unexpected errors")
    print(df[df["error"].notnull()].to_markdown())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help="Coverage tool")

    parser_create = subparsers.add_parser("create_dataset", help="Create dataset")
    parser_create.set_defaults(func=create_dataset)

    parser_merge = subparsers.add_parser("merge_dataset", help="merge dataset")
    parser_merge.set_defaults(func=merge_datasets)

    parser_run = subparsers.add_parser("run", help="Run coverage on dataset")
    parser_run.set_defaults(func=run)

    parser_coverage = subparsers.add_parser("coverage", help="Coverage on dataset")
    parser_coverage.set_defaults(func=get_coverage)

    parser_coverage = subparsers.add_parser("report", help="Report on dataset")
    parser_coverage.set_defaults(func=get_report)

    args = parser.parse_args()
    args.func(args)
