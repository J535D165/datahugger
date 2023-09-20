# Options

## Skip large files

For most repositories, it is possible to skip files that exceed a certain
number of bytes. For example, you want to skip files larger than 50Mb.


=== "CLI"

    ``` bash
    datahugger 10.5061/dryad.31zcrjdm5 data --max_file_size 50000000
    ```

=== "Python"

    ``` python
    datahugger.get("10.5061/dryad.x3ffbg7m8", "data", max_file_size=50000000)
    ```


## Extract single zip

Some services like [Zenodo](https://zenodo.org) don't offer an option to preserve
folder structures. Therefore, the content is often zipped before being
uploaded to the service. In this case, Datahugger will unzip the file to the
output folder by default.

Disable auto unzip function

=== "CLI"

    Not available at the moment

=== "Python"


    ``` python
    datahugger.get("10.5061/dryad.x3ffbg7m8", "data", unzip=False)
    ```


## Download mode

By default, Datahugger skips the download of files and datasets that are
already available on the local system. The options
are: "skip_if_exists", "force_redownload".


=== "CLI"

    ``` bash
    datahugger 10.5061/dryad.31zcrjdm5 data --download_mode force_redownload
    ```

=== "Python"

    ``` python
    datahugger.get("10.5061/dryad.x3ffbg7m8", "data", download_mode="force_redownload")
    ```


## Progress

By default, Datahugger shows the download progress. You can disable the
progress indicator.


=== "CLI"

    ``` bash
    datahugger 10.5061/dryad.31zcrjdm5 data --no-progress
    ```

=== "Python"

    ``` python
    datahugger.get("10.5061/dryad.x3ffbg7m8", "data", progress=False)
    ```
