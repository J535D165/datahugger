<p align="center">
  <img width="360px" alt="Datahugger - Where DOI hugs Data" src="https://github.com/J535D165/datahugger/raw/main/datahugger_logo.svg">
</p>

# Datahugger - Where DOI :open_hands: Data

Datahugger is a tool to download scientific datasets, software, and code from a large number of repositories based on their DOI [(wiki)](https://en.wikipedia.org/wiki/Digital_object_identifier) or URL. With Datahugger, you can automate the downloading of data and improve the reproducibility of your research. Datahugger provides a straightforward [Python interface](#download-with-python) as well as an intuitive [Command Line Interface](#download-with-command-line) (CLI).

## Supported repositories

Datahugger offers support for more than [<!-- count -->377<!-- count --> generic and specific (scientific) repositories](https://j535d165.github.io/datahugger/repositories) (and more to come!).

[![Datahugger support Zenodo, Dataverse, DataOne, GitHub, FigShare, HuggingFace, Mendeley Data, Dryad, OSF, and many more](https://github.com/J535D165/datahugger/raw/main/docs/images/logos.png)](https://j535d165.github.io/datahugger/repositories)

We are still expanding Datahugger with support for more repositories. You can
help by [requesting support for a repository](https://github.com/J535D165/datahugger/issues/new/choose) in the issue
tracker. Pull Requests are very welcome as well.

## Installation

[![PyPI](https://img.shields.io/pypi/v/datahugger)](https://pypi.org/project/datahugger/)

Datahugger requires Python 3.6 or later.

```
pip install datahugger
```

## Getting started

### Datahugger with Python

Load a dataset (or any digital asset) from a repository with the
`datahugger.get()` function. The first argument is the DOI or URL,
and the second is the folder name to store the dataset (it will be
created if it does not exist).

The following code loads dataset [10.5061/dryad.mj8m0](https://doi.org/10.5061/dryad.mj8m0) into
the folder `data`.

```python
import datahugger

# download the dataset to the folder "data"
datahugger.get("10.5061/dryad.mj8m0", "data")
```

For an example of how this can integrate with your work, see the
[example workflow notebook](https://github.com/J535D165/datahugger/blob/main/examples/example_datahugger_in_workflow.ipynb) or
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/J535D165/datahugger/blob/main/examples/example_datahugger_in_workflow.ipynb)


### Datahugger with command line

The command line function `datahugger` provides an easy interface to download data. The first
argument is the DOI or URL, and the second argument is the name of the folder to store the dataset (will be
created if it does not exist).

```bash
datahugger 10.5061/dryad.mj8m0 data
```

```bash
% datahugger 10.5061/dryad.mj8m0 data
Collecting...
NestTemperatureData.csv            : 100%|████████████████████████████████████████| 607k/607k
README_for_NestTemperatureData.txt : 100%|██████████████████████████████████████| 2.82k/2.82k
ExternalTemps.csv                  : 100%|██████████████████████████████████████| 1.06k/1.06k
README_for_ExternalTemps.txt       : 100%|██████████████████████████████████████| 2.82k/2.82k
InternalEggTempData.csv            : 100%|██████████████████████████████████████████| 664/664
README_for_InternalEggTempData.txt : 100%|██████████████████████████████████████| 2.82k/2.82k
SoilSimulation_Output.csv          : 100%|████████████████████████████████████████| 229M/229M
README_for_SoilSimulation_[...].txt: 100%|██████████████████████████████████████| 2.82k/2.82k
Dataset successfully downloaded.
```

**Tip:** On some systems, you have to quote the DOI or URL. For example: `datahugger "10.5061/dryad.mj8m0" data`.

## Tips and tricks

- No need to struggle with DOIs versus DOI URLs. They both work (and more). Example: The values `10.5061/dryad.x3ffbg7m8`, `doi:10.5061/dryad.x3ffbg7m8`, [`https://doi.org/10.5061/dryad.x3ffbg7m8`](https://doi.org/10.5061/dryad.x3ffbg7m8), and [`https://datadryad.org/stash/dataset/doi:10.5061/dryad.x3ffbg7m8`](https://datadryad.org/stash/dataset/doi:10.5061/dryad.x3ffbg7m8) all point to the same dataset.
- Do not republish the dataset when uploading your data to a scientific data repository. These storage resources can be used better :)

## License

[MIT](/LICENSE)

## Contact

Please feel free to reach out with questions, comments, and suggestions. The
[issue tracker](/issues) is a good starting point. You can also email me at
[jonathandebruinos@gmail.com](mailto:jonathandebruinos@gmail.com).
