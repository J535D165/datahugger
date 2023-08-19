import re
from pprint import pprint

from py3data import Repositories

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
}

n_total = sum([v for k, v in counts.items()])

pprint(counts)
print("Number of supported data repositories", n_total)


if 1:
    with open("README.md") as f_read:
        readme = f_read.read()

    readme_updated = re.sub(
        r"\<\!\-\-\scount\s\-\-\>(\d+)\<\!\-\-\scount\s\-\-\>",
        f"<!-- count -->{n_total}<!-- count -->",
        readme,
        flags=re.MULTILINE,
    )

    with open("README.md", "w") as f_write:
        f_write.write(readme_updated)
