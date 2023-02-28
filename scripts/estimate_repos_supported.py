import re
import xml.etree.ElementTree as ET

import requests


def get_count(url):

    r = requests.get(url)
    tree = ET.fromstring(r.content)

    return len(tree)


n_dataverse = get_count(
    "https://www.re3data.org/api/beta/repositories?software%5B%5D=DataVerse"
)
# print("DataVerse", n_dataverse)

n_dspace = get_count(
    "https://www.re3data.org/api/beta/repositories?software%5B%5D=DSpace"
)
# print("DSpace", n_dspace)

n_figshare = get_count("https://www.re3data.org/api/beta/repositories?query=figshare")
# print("FigShare", n_figshare)

n_dataone = get_count("https://www.re3data.org/api/beta/repositories?query=dataone")
# print("DataOne", n_dataone)

single_instance_repos = ["zenodo", "mendeley", "osf", "dryad", "github", "huggingface"]

n_total = n_dataverse + n_figshare + n_dspace + n_dataone + len(single_instance_repos)
print("Number of supported data repositories", n_total)


if 1:

    with open("README.md") as f_read:
        readme = f_read.read()

    readme_updated = re.sub(
        r"\<\!\-\-\scount\s\-\-\>(\d+)\<\!\-\-\scount\s\-\-\>",
        f"<!-- count -->{n_total}<!-- count -->",
        readme,
        re.MULTILINE,
    )

    with open("README.md", "w") as f_write:
        f_write.write(readme_updated)
