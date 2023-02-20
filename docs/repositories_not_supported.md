# Not supported repositories


## Reasons of failure

There are several reasons why Datahugger can't download the contents of a DOI.
Besides internet and network errors, reasons for failure include (but not limited to):

- Not a valid DOI or URL
- DOI doesn't point to a data repository
- Data repository isn't in the list of [supported repositories](repositories.md).
- DOI is no longer available in the repository.

## Not supported error message

When a repository is not supported, an error is returned (exit 1).

=== "CLI"

    ``` bash
    datahugger 10.5061/dryad.31zcrjdm5 data
    ```

    ```
    Traceback (most recent call last):
      File "/Users/Bruin056/.pyenv/versions/sra-dev/bin/datahugger", line 8, in <module>
        sys.exit(main())
      File "/Users/Bruin056/Documents/GitHub/datahugger/datahugger/__main__.py", line 65, in main
        get(
      File "/Users/Bruin056/Documents/GitHub/datahugger/datahugger/api.py", line 185, in load_repository
        return get(
      File "/Users/Bruin056/Documents/GitHub/datahugger/datahugger/api.py", line 197, in load_repository
        service_class = _resolve_service(url, doi)
      File "/Users/Bruin056/Documents/GitHub/datahugger/datahugger/api.py", line 226, in _resolve_service
        service_class = _resolve_service_with_re3data(doi)
      File "/Users/Bruin056/Documents/GitHub/datahugger/datahugger/api.py", line 246, in _resolve_service_with_re3data
        publisher = get_datapublisher_from_doi(doi)
      File "/Users/Bruin056/Documents/GitHub/datahugger/datahugger/utils.py", line 93, in get_datapublisher_from_doi
        raise ValueError("DOI not found")
    ValueError: DOI not found
    ```

=== "Python"

    ``` python
    datahugger.get("10.5061/dryad.x3ffbg7m8", "data")
    ```

    ```
    Traceback (most recent call last):
      File "/Users/Bruin056/.pyenv/versions/sra-dev/bin/datahugger", line 8, in <module>
        sys.exit(main())
      File "/Users/Bruin056/Documents/GitHub/datahugger/datahugger/__main__.py", line 65, in main
        get(
      File "/Users/Bruin056/Documents/GitHub/datahugger/datahugger/api.py", line 185, in load_repository
        return get(
      File "/Users/Bruin056/Documents/GitHub/datahugger/datahugger/api.py", line 197, in load_repository
        service_class = _resolve_service(url, doi)
      File "/Users/Bruin056/Documents/GitHub/datahugger/datahugger/api.py", line 226, in _resolve_service
        service_class = _resolve_service_with_re3data(doi)
      File "/Users/Bruin056/Documents/GitHub/datahugger/datahugger/api.py", line 246, in _resolve_service_with_re3data
        publisher = get_datapublisher_from_doi(doi)
      File "/Users/Bruin056/Documents/GitHub/datahugger/datahugger/utils.py", line 93, in get_datapublisher_from_doi
        raise ValueError("DOI not found")
    ValueError: DOI not found
    ```

## Request support

If a repository is not supported by Datahugger, you can open an issue in the
GitHub issue tracker.
