# Development

## Add new service

Support for repositories can be achieved by implementing a "service". The
file [datahugger/services.py](https://github.com/J535D165/datahugger/blob/main/datahugger/services.py) list various services.
For the new service, one needs to develop a new class, ideally inherited from
the `BaseRepoDownloader` class. The class of Open Science Framework
(`OSFDataset`) is a good example of a simple implementation.

```python
from datahugger.base import DatasetDownloader
from datahugger.base import DatasetResult

class OSFDataset(DatasetDownloader, DatasetResult):
    """Downloader for OSF repository."""

    REGEXP_ID = r"osf\.io\/(.*)/"

    # the base entry point of the REST API
    API_URL = "https://api.osf.io/v2/registrations/"

    # the files and metadata about the dataset
    API_URL_META = API_URL + "{api_record_id}/files/osfstorage/?format=jsonapi"
    META_FILES_JSONPATH = "data"

    # paths to file attributes
    ATTR_FILE_LINK_JSONPATH = "links.download"
    ATTR_NAME_JSONPATH = "attributes.name"
    ATTR_SIZE_JSONPATH = "attributes.size"
    ATTR_HASH_JSONPATH = "attributes.extra.hashes.sha256"
    ATTR_HASH_TYPE_VALUE = "sha256"

```

- The `API_URL` is the entry point for the URL. This URL serves the API.
- The `REGEXP_ID` is used to parse the URL and extract the ID. This ID is passed to the function `_get` with name `record_id`.
- Next, the metadata should be retrieved.
- For every file, download should be called.

## Datahugger for research software

Scientific software rarely offers the options to import datasets from a DOI.
Imagine what it would look like if you could. You can open a statistical
software and you can start working on any published dataset. This is why we
need persistent identifiers.
