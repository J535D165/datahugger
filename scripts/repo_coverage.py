import pandas as pd
from pydatacite import DOIs

import datahugger as dh


def collect():
    records = [x for y in range(10) for x in DOIs().random().get(per_page=100)]

    for r in records:
        yield {"id": r["id"], "type": r["type"], "url": r["attributes"]["url"]}


def test_repo(df):
    for index, record in df.iterrows():
        print(index)
        try:
            print(dh.info(record["id"]).__class__.__name__)
        except Exception as err:
            print(err)


if __name__ == "__main__":
    # df = pd.DataFrame(collect())
    # print(df)

    # df.to_csv("repos_benchmark.csv", index=False)

    df = pd.read_csv("repos_benchmark.csv")

    test_repo(df)
