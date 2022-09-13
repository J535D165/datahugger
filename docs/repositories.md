# Supported repositories

Datahugger offers support for more than [150 generic and specific (scientific) repositories](https://github.com/J535D165/datahugger/blob/main/docs/repositories.md) (and more to come!).

[![Datahugger support Zenodo, Dataverse, DataOne, GitHub, FigShare, HuggingFace, Mendeley Data, Dryad, OSF, and many more](images/logos.png)](https://github.com/J535D165/datahugger/blob/main/docs/repositories.md)

We are still expanding Datahugger with support for more repositories. You can
help by [requesting support for a repository](https://github.com/J535D165/datahugger/issues/new/choose) in the issue tracker. Pull Requests are very
welcome as well.

The following list gives an (non-exclusive) overview of repositories supported
by Datahugger.


## Supported repositories

### Single implementations

- [zenodo.org](https://zenodo.org)
- [figshare.com](https://figshare.com)
- [github.com](https://github.com)
- [datadryad.org](https://datadryad.org)
- [huggingface.co](https://huggingface.co)
- [osf.io](https://osf.io)
- [data.mendeley.com](https://data.mendeley.com)


### DataOne repositories

The following repositories make use of DataOne software. DataOne software is
supported by Datahugger.

- [arcticdata.io](https://arcticdata.io)
- [knb.ecoinformatics.org](https://knb.ecoinformatics.org)
- [data.pndb.fr](https://data.pndb.fr)
- [opc.dataone.org](https://opc.dataone.org)
- [portal.edirepository.org](https://portal.edirepository.org)
- [goa.nceas.ucsb.edu](https://goa.nceas.ucsb.edu)
- [data.piscoweb.org](https://data.piscoweb.org)
- [adc.arm.gov](https://adc.arm.gov)
- [scidb.cn](https://scidb.cn)
- [data.ess-dive.lbl.gov](https://data.ess-dive.lbl.gov)
- [hydroshare.org](https://hydroshare.org)
- [ecl.earthchem.org](https://ecl.earthchem.org)
- [get.iedadata.org](https://get.iedadata.org)
- [usap-dc.org](https://usap-dc.org)
- [iys.hakai.org](https://iys.hakai.org)
- [doi.pangaea.de](https://doi.pangaea.de)
- [rvdata.us](https://rvdata.us)
- [sead-published.ncsa.illinois.edu](https://sead-published.ncsa.illinois.edu)

### DataVerse repositories

See [https://dataverse.org/institutions](https://dataverse.org/institutions) and [DataVerse on Re3data.org](https://www.re3data.org/search?query=&software%5B%5D=DataVerse) for an overview of DataVerse repositories.

## Not supported

When a repository is not supported, the following is returned.

=== "CLI"

    ``` bash
    datahugger 10.5061/dryad.31zcrjdm5 data
    ```

=== "Python"

    ``` python
    datahugger.load_repository("10.5061/dryad.x3ffbg7m8", "data")
    ```
