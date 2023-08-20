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
    datahugger https://hdl.handle.net/10622/NHJZUD data
    ```

    ```
    Error: Data protocol for https://hdl.handle.net/10622/NHJZUD not found.

    Do you think this is a data repository that needs to be supported?
    Please request support in the issue tracker:

      https://github.com/J535D165/datahugger/issues/new/choose

    ```

=== "Python"

    ``` python
    datahugger.get("10.5061/dryad.x3ffbg7m8", "data")
    ```

    ```
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/Users/User/projects/datahugger/api.py", line 263, in get
        return _base_request(
      File "/Users/User/projects/datahugger/api.py", line 205, in _base_request
        raise ValueError(f"Data protocol for {url} not found.")
    ValueError: Data protocol for https://hdl.handle.net/10622/NHJZUD not found.
    ```

## Request support

If a repository is not supported by Datahugger, you can open an issue in the
GitHub issue tracker.
