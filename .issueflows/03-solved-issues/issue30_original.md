# Issue #30: module for handling meta data

Source: https://github.com/cellpy/cellpy-core/issues/30

## Original issue text

add a new module with scaffolding for handling meta-data. It is best to make it into a separate package (i.e. a folder with a __init__.py file inside).

we need to carefully analyse how old cellpy carries meta-data, as well as the available documents within cellpy core and suggest how we should add the key elements into cellpy core. In step one, defining the data structures (enums, dataclasses, etc) would be the goal. In step two, creating some dummy functions that the full future cellpy suite can use, is the goal. We are not yet sure what we need. We need to be able to communicate with a db (through an API / JSONLD most likely). We also need to load cellpy archive files (I think they will be hdf5 as before). And save.

notice that there are (at least) two levels of metadata, cell dependent (those that does not change between tests, for example material specific values and masses) and test-dependent (for example test type, test instrument, uuids, connection/file information)

The overall goal is not to implement a final solution, but to work on the design and scaffolding.
