# Download dataset

The following example downloads dataset
[10.5061/dryad.x3ffbg7m8](https://doi.org/10.5061/dryad.x3ffbg7m8) to the
folder `data`.

##  Download dataset from DOI

=== "CLI"

    ``` bash
    datahugger 10.5061/dryad.31zcrjdm5 data
    ```

    In some situations, you might have to quote the number the DOI (e.g. `datahugger "10.5061/dryad.31zcrjdm5" data`)

=== "Python"

    ``` python
    import datahugger

    datahugger.get("10.5061/dryad.x3ffbg7m8", "data")
    ```

##  Download dataset from URL

=== "CLI"

    ``` bash
    datahugger https://datadryad.org/stash/dataset/doi:10.5061/dryad.x3ffbg7m8 data
    ```

    In some situations, you might have to quote the number the DOI (e.g. `datahugger "https://datadryad.org/stash/dataset/doi:10.5061/dryad.x3ffbg7m8" data`)

=== "Python"

    ``` python
    import datahugger

    datahugger.get("https://datadryad.org/stash/dataset/doi:10.5061/dryad.x3ffbg7m8", "data")
    ```
