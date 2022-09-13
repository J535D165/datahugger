# Getting started

## Options

### Skip large files

For most repositories, it is possible to skip files that exceed a certain
number of bytes. For example, you want to skip files larger than 50Mb.


=== "CLI"

    ``` bash
    datahugger 10.5061/dryad.31zcrjdm5 data --max_file_size 50000000
    ```

=== "Python"

    ``` python
    datahugger.load_repository("10.5061/dryad.x3ffbg7m8", "data", max_file_size=50000000)
    ```


### Download mode

By default, Datahugger skips the download of files and datasets that are
already available on the local system. The options
are: "skip_if_exists", "force_redownload".


=== "CLI"

    ``` bash
    datahugger 10.5061/dryad.31zcrjdm5 data --download_mode force_redownload
    ```

=== "Python"

    ``` python
    datahugger.load_repository("10.5061/dryad.x3ffbg7m8", "data", download_mode="force_redownload")
    ```
