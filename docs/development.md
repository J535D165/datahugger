# Development

## Add new service

Support for repositories can be achieved by implementing a "service". The
file [datahugger/services.py](datahugger/services.py) list various services.
For the new service, one needs to develop a new class, ideally inherited from
the `BaseRepoDownloader` class. The class of Open Science Framework
(`OSFDownload`) is a good example of a simple implementation.

```python
class OSFDownload(BaseRepoDownloader):
    """Downloader for OSF repositories."""

    API_URL = "https://api.osf.io/v2/registrations/"
    REGEXP_ID = r"osf\.io\/(.*)/"

    def _get(
        self,
        record_id: Union[str, int],
        output_folder: Union[Path, str],
        **kwargs,
    ):

        r_meta = requests.get(
            self.API_URL + record_id + "/files/osfstorage/?format=jsonapi")
        dataset_metadata = r_meta.json()

        for f in dataset_metadata["data"]:
            self.download(
                f["links"]["download"],
                output_folder,
                f["attributes"]["name"],
                file_size=f["attributes"]["size"],
            )

```

- The `API_URL` is the entry point for the URL. This URL serves the API.
- The `REGEXP_ID` is used to parse the URL and extract the ID. This ID is passed to the function `_get` with name `record_id`.
- Next, the metadata should be retrieved.
- For every file, download should be called.
