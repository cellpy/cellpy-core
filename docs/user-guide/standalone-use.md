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
core.cycle_mode = "anode"                          # half-cells only; unset = normal

data = core.make_core_step_table(
    core.data,
    nom_cap_abs=my_nom_cap_abs,          # absolute (e.g. Ah), for the per-step C-rate
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
    specific_conversion_factors={"gravimetric": f_g, "areal": f_a, "absolute": f_abs},
) # Note, f_abs should always be 1.0 in standalone mode if charge units match

steps, summary = data.steps, data.summary  # polars frames (StepCols / CycleCols)
```

`Data.from_raw_frame` is the validating front door: it checks that the frame is
a polars `DataFrame` carrying the load-bearing `RawCols` columns with sane
dtypes and reports every problem in a single error. Pass `validate=False` to
skip the checks (e.g. in a hot loop after the shape is known-good).


### Unit conversion

If you have `pint` installed, you can use `cellpy-core` to help calculate the
conversion factors.

```python
from cellpycore import units

# Absolute nominal capacity
my_nom_cap_abs = units.calculate_nom_cap_abs_from_specific(nom_cap_gravimetric, mass)
# or
my_nom_cap_abs = units.calculate_nom_cap_abs_from_specific(
    nom_cap_areal, area, specific_type="areal"
)

# Current conversion factor
my_current_conversion_factor = units.calculate_current_conversion_factor("mA")

# Specific conversion factors
my_specific_conversion_factors = units.calculate_specific_conversion_factors(
    mass=mass, area=area
)
# {"gravimetric": f_g, "areal": f_a, "absolute": 1.0} when charge units match
```


### Dtypes

The authoritative column -> polars dtype map lives on the schema:
`RawCols().dtype_map()` (one entry per column; `epoch_time_utc` is `Int64`
nanoseconds, `mask` is `Boolean`, and so on — matching the
[harmonized raw spec](../specifications/harmonized-raw.md)). When converting
foreign raw data (e.g. a legacy pandas frame turned into polars), don't
hand-maintain dtypes — cast through the helper first:

```python
from cellpycore import cast_raw_frame

data = Data.from_raw_frame(cast_raw_frame(df))
```

`cast_raw_frame` strictly casts every mapped column present in the frame,
skips absent optional columns, and passes extra columns (e.g. custom `aux_*`
columns) through untouched.

### The cycle-mode default

`cycle_mode` decides the coulombic-efficiency direction (and which capacity
column "comes first"). A fresh ``Data`` leaves ``cycle_mode`` unset
(``None``), which the engine treats as **normal** convention — set it
explicitly for half-cells:

- unset / `"standard"` / `"cathode"` / `"full_cell"` / … — normal convention
  (`CE = 100 * discharge / charge`).
- `"anode"` — anode half-cell (inverted; `CE = 100 * charge / discharge`).

Legacy cellpy historically defaulted to `"anode"`; the cellpy bridge must set
that when loading real cells. Do not rely on implicit defaults across layers.

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
data = summarizers.add_step_c_rate(data, nom_cap_abs=my_nom_cap_abs)  # optional
data = summarizers.make_summary(data)   # test_mode=config.TestMode.INVERTED for anode cells
```

The base step table carries no C-rate; `add_step_c_rate` is the separate
opt-in step that appends `c_rate` (legacy `rate_avr`) — required before
`c_rates_to_summary`. The class is worth it when you want the `cycle_mode`
string → `config.TestMode` handling done for you, and the C-rate / IR
orchestration (`make_core_step_table` chains `make_step_table` +
`add_step_c_rate`; `make_core_summary` chains `make_summary` +
`ir_to_summary` + `c_rates_to_summary` in the right order).

## The contract the caller must honor

- **Order matters.** Step table before summary — `make_summary` reads
  `data.steps`.
- **No metadata required.** `Data()` ships a `MockMetaTestDependent`
  placeholder; the engine never needs populated cell metadata. Only an
  explicit `cycle_mode` (e.g. `"anode"`) changes the math (CE direction — see
  above).
- **Units by value.** The core never sees unit objects. The caller precomputes
  plain floats; the pint-backed helpers in `cellpycore.units` are an optional
  fallback (install the `units` extra) — the engine itself does not require
  pint. Glossary of the by-value knobs:
  - `nom_cap_abs` — the **absolute** nominal capacity, in the same unit as the
    raw capacity columns (e.g. Ah). One value, used everywhere it appears:
    the per-step C-rate (`add_step_c_rate` / `make_core_step_table`) and the
    summary normalization (`add_scaled_summary_columns`,
    `equivalent_cycles_to_summary`, `c_rates_to_summary`). The old `nom_cap`
    keyword is a deprecated alias (warns since #99). Not to be confused with
    the *metadata field* `CellMeta.nom_cap`, which may be specific (qualified
    by `nom_cap_specifics`).
  - `current_conversion_factor` — converts the raw **current** unit to the
    output current unit for the per-cycle `charge_c_rate` / `discharge_c_rate`
    columns (`make_core_summary` / `c_rates_to_summary`). Default 1.0 = no
    conversion.
  - `specific_conversion_factors` — mapping `mode -> factor` (e.g.
    `{"gravimetric": 1/mass}`) that scales the **capacity-like** summary
    columns into their specific variants in `add_scaled_summary_columns`.
    Pairs with `current_conversion_factor` (current vs capacity scaling).
    The old name `specific_converters` is a deprecated alias.
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
  [Harmonized raw format](../specifications/harmonized-raw.md)
- [The Data object](data-object.md)
- Column names: `cellpycore.config` (`RawCols`, `StepCols`, `CycleCols`)
