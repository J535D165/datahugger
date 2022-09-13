# Datahugger - Where DOI 👐 Data

Datahugger is a tool to download scientific datasets, software, and code from
a large number of repositories based on their DOI [(wiki)](https://en.wikipedia.org/wiki/Digital_object_identifier) or URL. With
Datahugger, you can automate the downloading of data and improve the
reproducibility of your research. Datahugger provides a straightforward
[Python interface](#download-with-python) as well as an intuitive
[Command Line Interface](#download-with-command-line) (CLI).

[![datahugger_repo.png](../images/datahugger_repo.png)](github.com/j535d165/datahugger)


## Installation

Datahugger requires Python 3.6 or later.

```
pip install datahugger
```


## Download dataset

The following example downloads the data of dataset
[10.5061/dryad.x3ffbg7m8](https://doi.org/10.5061/dryad.x3ffbg7m8) to the
folder `data`.

###  Download dataset from DOI

=== "CLI"

    ``` bash
    datahugger 10.5061/dryad.31zcrjdm5 data
    ```

    In some situations, you might have to quote the number the DOI (e.g. `datahugger "10.5061/dryad.31zcrjdm5" data`)

=== "Python"

    ``` python
    import datahugger

    datahugger.load_repository("10.5061/dryad.x3ffbg7m8", "data")
    ```

###  Download dataset from URL

=== "CLI"

    ``` bash
    datahugger 10.5061/dryad.31zcrjdm5 data
    ```

    In some situations, you might have to quote the number the DOI (e.g. `datahugger "10.5061/dryad.31zcrjdm5" data`)

=== "Python"

    ``` python
    import datahugger

    datahugger.load_repository("10.5061/dryad.x3ffbg7m8", "data")
    ```
