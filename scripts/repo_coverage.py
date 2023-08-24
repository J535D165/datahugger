import pandas as pd
from pydatacite import DOIs

import datahugger as dh


def collect():
    records = [x for y in range(10) for x in DOIs().random().get(per_page=100)]

    for r in records:
        yield {"id": r["id"], "type": r["type"], "url": r["attributes"]["url"]}


def test_repo(r):
    try:
        cl = dh.info(r["id"]).__class__.__name__
        print(r["id"], f"service found: {cl}")
        return {"service": cl, "error": None}
    except Exception as err:
        print(r["id"], f"results in: {err}")
        return {"service": None, "error": str(err)}


if __name__ == "__main__":
    df = pd.read_csv("repos_benchmark.csv")

    df[["service", "error"]] = df.apply(test_repo, axis=1, result_type="expand")
    df.to_csv("repos_benchmark_tested.csv")

    print(df)
