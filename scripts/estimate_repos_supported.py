import re
from pprint import pprint

from py3data import Repositories


def count_repos():
    counts = {
        "dataverse": Repositories().filter(software="Dataverse").count(),
        "dspace": Repositories().filter(software="DSpace").count(),
        "figshare": Repositories().query("figshare").count(),
        "dataone": Repositories().query("dataone").count(),
        "zenodo": 1,
        "mendeley": 1,
        "osf": 1,
        "dryad": 1,
        "github": 1,
        "huggingface": 1,
        "pangaea": 1,
    }

    print(counts)

    return sum([v for k, v in counts.items()])


def _update_docs(file_name, n_total):
    with open(file_name) as f_read:
        readme = f_read.read()

    print(readme)

    readme_updated = re.sub(
        r"\<\!\-\-\scount\s\-\-\>(\d+)\<\!\-\-\scount\s\-\-\>",
        f"<!-- count -->{n_total}<!-- count -->",
        readme,
        flags=re.MULTILINE,
    )

    with open(file_name, "w") as f_write:
        f_write.write(readme_updated)


if __name__ == "__main__":
    n_total = count_repos()
    pprint(n_total)
    print("Number of supported data repositories", n_total)

    _update_docs("README.md", n_total)
    _update_docs("docs/repositories.md", n_total)
