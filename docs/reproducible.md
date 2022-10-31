# Work reproducible with Datahugger

By downloading a dataset directly from a DOI, you can improve the
reproducibility of your (scientific) work. It also saves manual work and
time. Because of this, sharing work is easier. In the following sections, we
discuss possible ways to integrate Datahugger in your workflow.

## Publish a project with datahugger

### Find a dataset

First, find a dataset you want to use in your analysis. You can use dataset
search engines like [Google Dataset Search](https://datasetsearch.research.google.com/) or look for references in
scientific publications. Once you found the dataset, copy the DOI. If there
is no DOI available, use the URL to the dataset.

### Option 1: Create project

### Option 2: Embed in project

### Tips for git users

#### Add download folder to `.gitignore`

Are you using git for version control? Add the download folder to the
`.gitignore` file. This prevents you from adding the new dataset to the
history. As you can redownload the same dataset, there is no need to track
the dataset (it's disposable).

#### Download without progress indicators

A redownload of the data will likely result in different progress output as
download times will vary. For some applications, like [Jupyter Notebooks](https://jupyter.org/), this will result in changes in the output, where
there are no changes in the actual results. To prevent this, you can disable
the progress indicator.

=== "CLI"

    ``` bash
    datahugger 10.5061/dryad.31zcrjdm5 data --no-progress
    ```

=== "Python"

    ``` python
    datahugger.load_repository("10.5061/dryad.x3ffbg7m8", "data", progress=False)
    ```

### Share your project

After publishing your project in a data repository or alike, others can start
reusing it. Ideally, your downloaded data is not republished. This implies
that the user of your project needs to download the assets with datahugger as
well. This means that `datahugger` needs to be added to the installation
dependencies.

## Reuse a project with datahugger

### Install datahugger

Ideally, the installation instructions of the project you want to
(re)use provide installation instructions or automates the installation of
dependencies. If not, please install datahugger.
