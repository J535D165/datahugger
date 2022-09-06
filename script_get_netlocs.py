from datahugger.utils import get_re3data_repositories, get_base_url
import requests
import xml.etree.ElementTree as ET

SOFTWARE = "DataVerse"
URL = f"https://www.re3data.org/api/beta/repositories?query=&software%5B%5D={SOFTWARE}"


x = get_re3data_repositories(URL)

def get_re3data_repository(re3data_id):

    namespaces = {"r3d": "http://www.re3data.org/schema/2-2"}
    r = requests.get(f"https://www.re3data.org/api/v1/repository/{re3data_id}")

    tree = ET.fromstring(r.content)

    return (
        tree[0]
        .find("r3d:repositoryURL", namespaces)
        .text
    )


base_urls = set()

for v in list(x):

	z = get_re3data_repository(v["id"])
	base_urls.add(get_base_url(z))

base_urls = sorted(list(base_urls))

for url in base_urls:
    print(url)
