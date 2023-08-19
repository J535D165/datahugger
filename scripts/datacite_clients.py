import pandas as pd
import requests

url_datacite_clients = (
    "https://api.datacite.org/clients?page%5Bnumber%5D=1&page%5Bsize%5D=1000"
)

data = []
while url_datacite_clients:
    r = requests.get(url_datacite_clients)
    res = r.json()
    data.extend(res["data"])
    url_datacite_clients = res["links"]["next"] if "next" in res["links"] else None


print(len(data))

result = []

for client in data:
    result.append(
        {
            "datacite_id": client["id"],
            "name": client["attributes"]["name"],
            "url": client["attributes"]["url"],
            "re3data": client["attributes"]["re3data"],
        }
    )

df = pd.DataFrame(result)

print(df)
breakpoint()
