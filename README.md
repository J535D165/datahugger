[![datahugger_repo.png](https://github.com/J535D165/datahugger/raw/main/docs/images/datahugger_repo.png)](github.com/j535d165/datahugger)

# Datahugger - Where DOI :open_hands: Data

Datahugger is a tool to download scientific datasets, software, and code from a large number of repositories based on their DOI [(wiki)](https://en.wikipedia.org/wiki/Digital_object_identifier) or URL. With Datahugger, you can automate the downloading of data and improve the reproducibility of your research. Datahugger provides a straightforward [Python interface](#download-with-python) as well as an intuitive [Command Line Interface](#download-with-command-line) (CLI).

## Supported repositories

Datahugger offers support for more than [150 generic and specific (scientific) repositories](https://github.com/J535D165/datahugger/blob/main/docs/repositories.md) (and more to come!).

[![Datahugger support Zenodo, Dataverse, DataOne, GitHub, FigShare, HuggingFace, Mendeley Data, Dryad, OSF, and many more](https://github.com/J535D165/datahugger/raw/main/docs/images/logos.png)](https://github.com/J535D165/datahugger/blob/main/docs/repositories.md)

We are still expanding Datahugger with support for more repositories. You can
help by [requesting support for a repository](https://github.com/J535D165/datahugger/issues/new/choose) in the issue tracker. Pull Requests are very
welcome as well.

## Installation

Datahugger requires Python 3.6 or later.

```
pip install datahugger
```

## Getting started

### Download with Python

Load a dataset (or any digital asset) from a repository with the `datahugger.load_repository` function. The first
argument is the DOI or URL and the second argument the name of the folder to store the dataset (will be
created if it does not exist).

```python
import datahugger

# download the data to your device
datahugger.load_repository("10.5061/dryad.x3ffbg7m8", "data")
```

The data from DOI [10.5061/dryad.x3ffbg7m8](https://doi.org/10.5061/dryad.x3ffbg7m8) is now stored in the folder `data`. The data can now be accessed and analyzed. For example:

```python

import pandas as pd

df = pd.read_csv("data/Pfaller_Robinson_2022_Global_Sea_Turtle_Epibiont_Database.csv")
print(df["Higher Taxon"].value_counts())
```


### Download with command line

The command line function `datahugger` provides an easy interface to download data. The first
argument is the DOI or URL and the second argument the name of the folder to store the dataset (will be
created if it does not exist).

```bash
datahugger 10.5061/dryad.31zcrjdm5 data
```

```bash
% datahugger 10.5061/dryad.x3ffbg7m8 data
README_Pfaller_Robinson_20[...].txt: 100%|█████████████████████████████████████| 17.1k/17.1k [00:00<00:00, 2.62MB/s]
Pfaller_Robinson_2022_Glob[...].csv: 100%|████████████████████████████████████████| 709k/709k [00:00<00:00, 904kB/s]
Repository content succesfully downloaded.
```

**Tip:** On some systems, you have to quote the DOI or URL. For example: `datahugger "10.5061/dryad.31zcrjdm5" data`. 

## Options

### Skip large files

For most repositories, it is possible to skip files that exceed a certain
number of bytes. For `load_repositories` use the argument `max_file_size`
(in bytes). For example, you want to skip files larger than 50Mb, use
`max_file_size=50000000`. For the command line interface, use
`--max_file_size`.

### Extract single zip

Some services like [Zenodo](zenodo.org) don't offer an option to preserve
folder structures. Therefore, the content is often zipped before being
uploaded to the service. In this case, Datahugger will unzip the file to the
output folder by default. Set this option to False to disable(`unzip`).

### Download mode

By default, Datahugger skips the download of files and datasets that are already 
available on the local system. To change this behavior, use the argument 
`download_mode`. The options are: "skip_if_exists", "force_redownload".

## Tips and tricks

- No need to struggle with DOIs versus DOI URLs. They both work (and more). Example: The values `10.5061/dryad.x3ffbg7m8`, `doi:10.5061/dryad.x3ffbg7m8`, [`https://doi.org/10.5061/dryad.x3ffbg7m8`](https://doi.org/10.5061/dryad.x3ffbg7m8), and [`https://datadryad.org/stash/dataset/doi:10.5061/dryad.x3ffbg7m8`](https://datadryad.org/stash/dataset/doi:10.5061/dryad.x3ffbg7m8) all point to the same dataset.
- Do not repuplish the dataset when you are uploading your data to an scientific data repository. These storages resources can be used better :)
- Are you using git? Add the folder to the `.gitignore` file. This prevents committing all results to the repo.

## Interesting reads

- https://www.crossref.org/blog/urls-and-dois-a-complicated-relationship/
- *Harvey MJ, Mason NJ, McLean A, Rzepa HS. Standards-based metadata procedures for retrieving data for display or mining utilizing persistent (data-DOI) identifiers. J Cheminform. 2015 Aug 8;7:37. doi: [10.1186/s13321-015-0081-7](https://doi.org/10.1186%2Fs13321-015-0081-7). PMID: 26257829; PMCID: PMC4528360.*
- [DOI Content Negotiation (Crosscite.org](https://citation.crosscite.org/docs.html) 

## License

[MIT](/LICENSE)

## Contact

Datahugger is developed and maintained by Jonathan de Bruin ([jonathandebruinos@gmail.com](email:jonathandebruinos@gmail.com)).
This project received support from the Utrecht University Open Science Programme and the Utrecht University
Research IT Programme.  
