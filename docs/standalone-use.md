# Using cellpy-core standalone (slim-consumer guide)

cellpy-core is designed to be usable on its own: if you can produce a polars
`DataFrame` in the native raw schema (`config.RawCols`), you can get step tables
and per-cycle summaries without pulling in the full
[cellpy](https://github.com/jepegit/cellpy) package.

```bash
pip install cellpycore            # or: uv add cellpycore
pip install "cellpycore[units]"   # optional: pint-backed unit helpers
```

The engine is polars-native, schema-agnostic (column names are injected via a
`Schema` object), and thread-safe (no module-level mutable state).

## The recommended entry point

Use the native `CellpyCellCore` — not the `OldCellpyCellCore` legacy bridge,
which exists only to serve legacy cellpy headers and pandas frames.

```python
from cellpycore.cell_core import CellpyCellCore, Data

core = CellpyCellCore()
core.data = Data.from_raw_frame(my_polars_frame)  # validates against config.RawCols
core.cycle_mode = "standard"                      # see the cycle-mode trap below

data = core.make_core_step_table(
    core.data,
    nom_cap=my_nom_cap_abs,              # absolute (e.g. Ah), for the per-step C-rate
    raw_limits=my_instrument_limits,     # optional; DEFAULT_RAW_LIMITS otherwise
)
data = core.make_core_summary(
    data,
    current_conversion_factor=1.0,       # raw-current -> output-current, by value
)
# optional: specific / normalized columns
data = core.add_scaled_summary_columns(
    data,
    nom_cap_abs=my_nom_cap_abs,
    normalization_cycles=None,
    specific_converters={"gravimetric": f_g, "areal": f_a, "absolute": f_abs},
)

steps, summary = data.steps, data.summary  # polars frames (StepCols / CycleCols)
```

`Data.from_raw_frame` is the validating front door: it checks that the frame is
a polars `DataFrame` carrying the load-bearing `RawCols` columns with sane
dtypes and reports every problem in a single error. Pass `validate=False` to
skip the checks (e.g. in a hot loop after the shape is known-good).

### The cycle-mode trap

`cycle_mode` decides the coulombic-efficiency direction (and which capacity
column "comes first"). For historical cellpy reasons the metadata placeholder
on a fresh `Data` defaults to `"anode"` (anode half-cell, inverted convention)
— **not** `"standard"`. Set it explicitly:

- `"anode"` — anode half-cell (inverted; `CE = 100 * charge / discharge`).
- anything else (`"standard"`, `"cathode"`, `"full_cell"`, …) — normal
  convention (`CE = 100 * discharge / charge`).

### Useful knobs

- `make_core_step_table(..., raw_limits=...)`: instrument resolution thresholds
  for step-type classification (what counts as "constant" / "zero"). Defaults
  to `summarizers.DEFAULT_RAW_LIMITS` (mirrors legacy cellpy's `CellpyLimits`).
- `make_core_summary(..., exclude_step_types=["cv_"])`: subtract the
  capacity contributions of matching step types (prefix match) from the
  summary — e.g. a non-CV summary.
- `make_core_summary(..., find_ir=...)` / `ir_extractor=...`: per-cycle
  internal-resistance columns, when the raw carries `internal_resistance`.
- `add_scaled_summary_columns(...)`: adds `normalized_cycle_index` (equivalent
  cycles) plus `{column}_{gravimetric,areal,absolute}` variants of the
  capacity-like columns (`CycleCols().specific_columns`).

## The class-free alternative

The engine functions in `cellpycore.summarizers` work directly on a `Data`
object with the default native schema — no class required:

```python
from cellpycore.cell_core import Data
from cellpycore import summarizers

data = Data.from_raw_frame(my_polars_frame)
data = summarizers.make_step_table(data)
data = summarizers.make_summary(data)   # test_mode=config.TestMode.INVERTED for anode cells
```

The class is worth it when you want the `cycle_mode` string → `config.TestMode`
handling done for you, and the IR / C-rate orchestration
(`make_core_summary` chains `make_summary` + `ir_to_summary` +
`c_rates_to_summary` in the right order).

## The contract the caller must honor

- **Order matters.** Step table before summary — `make_summary` reads
  `data.steps`.
- **No metadata required.** `Data()` ships a `MockMetaTestDependent`
  placeholder; the engine never needs populated cell metadata. Only
  `cycle_mode` changes the math (CE direction — see the trap above).
- **Units by value.** The core never sees unit objects. The caller precomputes
  plain floats: `nom_cap` / `nom_cap_abs`, `current_conversion_factor`, and the
  `specific_converters` mapping. The pint-backed helpers in `cellpycore.units`
  are an optional fallback (install the `units` extra) — the engine itself does
  not require pint.
- **Raw shape assumptions.**
  - `epoch_time_utc` is int64 nanoseconds since the Unix epoch, UTC (see
    `cellpycore.timestamps` for conversion helpers); `test_time` / `step_time`
    are relative elapsed seconds (float).
  - Capacity / energy columns are **cycle-cumulative per direction** (reset at
    each cycle boundary). If your cycler delivers step-cumulative or
    test-cumulative counters, run
    `summarizers.normalize_capacity_granularity(data, granularity=config.ResetGranularity.STEP)`
    (or `.TEST`) first.
  - `test_id` is optional and defaults to `0`; it only matters for merged
    `Data` objects holding several tests.
- **Legacy cruft is absent by design.** The native summary is the clean
  `CycleCols` subset plus C-rate / IR columns. Cumulated CE, shifted
  capacities, and RIC columns exist only on the legacy bridge
  (`OldCellpyCellCore`).

## Reference

- Raw-format spec (authoritative column list and conventions):
  [`docs/data_format_specifications/harmonized_raw.md`](data_format_specifications/harmonized_raw.md)
- The `Data` object: [`docs/data-object-definition.md`](data-object-definition.md)
- Column names: `cellpycore.config` (`RawCols`, `StepCols`, `CycleCols`)
