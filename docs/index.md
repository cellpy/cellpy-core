# cellpy-core

The core engine of [cellpy](https://github.com/jepegit/cellpy): fast,
thread-safe processing of battery-cycling raw data. Given a raw data frame
(polars, native schema — or pandas via the legacy bridge), it finds all steps
and cycles and builds per-step and per-cycle summary tables. It is designed to
be small, schema-injected, and easy for cellpy developers to build on and
extend; instrument loaders, file IO, and unit handling stay out of the core.

```python
import polars as pl
from cellpycore import Data, add_step_c_rate, make_step_table, make_summary

data = Data.from_raw_frame(pl.read_parquet("my_native_raw.parquet"))
make_step_table(data)
add_step_c_rate(data, nom_cap_abs=1.0)  # optional: per-step C-rate
make_summary(data)
print(data.steps, data.summary)
```

## Where to go next

- [Getting started](getting-started.md) — install the package and run the
  pipeline for the first time.
- [Examples](examples/index.md) — runnable notebooks demonstrating the full
  pipeline on mock and real cycling data.
- [Standalone use](user-guide/standalone-use.md) — the slim-consumer guide:
  step tables and per-cycle summaries without full cellpy.
- [Harmonized raw format](specifications/harmonized-raw.md) — the
  authoritative input-format specification.
- [Development guide](development/guide.md) — practices and workflows for
  contributors.

## Design in one paragraph

The engine is polars-native, schema-agnostic (column names are injected via a
`Schema` object), and thread-safe (no module-level mutable state). Order
matters: the step table is built before the summary, because `make_summary`
reads `data.steps`. Units are passed by value (plain conversion factors), and
populated cell metadata is never required — see
[the contract the caller must honor](user-guide/standalone-use.md#the-contract-the-caller-must-honor).
