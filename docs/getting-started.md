# Getting started

## Install

cellpy-core is available on PyPI as
[`cellpycore`](https://pypi.org/project/cellpycore/) (Python 3.13+):

```bash
pip install cellpycore            # or: uv add cellpycore
pip install "cellpycore[units]"   # optional: pint-backed unit helpers
```

The core engine only depends on `polars`, `pandas`, and `pyarrow`. The `units`
extra adds `pint` for the optional unit-conversion helpers in
`cellpycore.units`; the engine itself takes conversion factors by value and
never needs unit objects.

## The pipeline in three calls

The whole point of cellpy-core is one short pipeline: validate the raw frame,
find the steps, summarize the cycles.

```python
import polars as pl
from cellpycore import Data, make_step_table, make_summary

raw = pl.read_parquet("my_native_raw.parquet")  # harmonized-raw schema

data = Data.from_raw_frame(raw)   # 1. validating front door
make_step_table(data, nom_cap=1.0)  # 2. per-step table -> data.steps
make_summary(data)                  # 3. per-cycle summary -> data.summary

print(data.steps)
print(data.summary)
```

`Data.from_raw_frame` checks that the frame is a polars `DataFrame` carrying
the load-bearing [harmonized-raw](specifications/harmonized-raw.md) columns
with sane dtypes, and reports every problem in a single error. Pass
`validate=False` to skip the checks in a hot loop.

!!! note "Order matters"
    Build the step table before the summary — `make_summary` reads
    `data.steps` and raises if it is missing.

## Trying it without instrument data

You don't need a cycler file to explore the API; the package ships a mock-data
helper:

```python
from cellpycore.testing.mock_data import create_raw_data
from cellpycore import Data, make_step_table, make_summary

data = Data.from_raw_frame(create_raw_data())
make_step_table(data, nom_cap=1.0)
make_summary(data)
```

See the [Quickstart notebook](examples/quickstart.md) for a full walkthrough
with plots, and the
[real-data walkthrough](examples/real_data_walkthrough.md) for the same
pipeline on genuine cycling data.

## Going further

- Class-based orchestration (`CellpyCellCore`), cycle modes for half-cells,
  C-rates, internal resistance, and specific/normalized columns:
  [Standalone use](user-guide/standalone-use.md).
- The shape of the input and output tables:
  [Harmonized raw](specifications/harmonized-raw.md),
  [Step table](specifications/step-table.md),
  [Cycle table](specifications/cycle-table.md).
