# Datahugger result object

After you have downloaded the contents of a dataset, you can inspect the
result of the download. Assign the returned object to a variable.

*This is Python API only.*


## Scitree

:octicons-beaker-24: Experimental

The Datahugger result object has a method tree to print the tree. The tree
is optimized for scientific use (see [scitree](https://github.com/J535D165/scitree) and [scisort](https://github.com/J535D165/scisort)).

=== "Python"

```python
import datahugger

dh_data = datahugger.get("10.5061/dryad.x3ffbg7m8", "data")

dh_data.tree()
```

```
data/
├── README_Pfaller_Robinson_2022_Global_Sea_Turtle_Epibiont_Database.txt
└── Pfaller_Robinson_2022_Global_Sea_Turtle_Epibiont_Database.csv

0 directories, 2 files
README Data Code
```
