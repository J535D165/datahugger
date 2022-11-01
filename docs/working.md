# How Datahugger works

Datahugger solves both a conceptual and technical issue. The main challenge
for datahugger is to connect the DOI to the machine-to-machine interface of
the repository (the API). For humans, it is often clear to click the download
button. However computers like to interact with the API. Unfortunately, there
is no metadata describing the API entry point and protocol. Datahugger tries
to solve this issue by creating this metadata or by doing an educated guess.
The following flowchart provides an overview of the working of datahugger.

<p align="center">
  <img alt="Datahugger - Architecture" src="../images/datahugger_architecture.drawio.svg">
</p>
