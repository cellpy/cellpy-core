# Issue #56: Document standalone use of cellpy-core (slim-consumer guide)

Source: https://github.com/cellpy/cellpy-core/issues/56

## Original issue text

## Context

cellpy-core is designed to be usable on its own: anyone who can produce a polars DataFrame in the native `config.RawCols` schema should be able to get step tables and per-cycle summaries without pulling in full cellpy. That story currently lives only in design docs and code docstrings — there is no user-facing documentation for it.

## Proposal

Add a "Using cellpy-core standalone" guide to `docs/` covering:

### 1. The recommended entry point

Native `CellpyCellCore` (not the `OldCellpyCellCore` legacy bridge, which exists only to serve legacy cellpy headers):

```python
from cellpycore.cell_core import CellpyCellCore, Data

core = CellpyCellCore(initialize=True)
core.data.raw = my_polars_frame          # native config.RawCols schema
core.cycle_mode = "anode"                # only for half-cells; default "standard"

data = core.make_core_step_table(
    core.data,
    nom_cap=my_nom_cap_abs,              # absolute Ah, for the per-step C-rate
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

Also mention the class-free alternative (`summarizers.make_step_table(data)` + `summarizers.make_summary(data)` with the default schema) and when the class is worth it (cycle-mode -> TestMode handling, IR/C-rate orchestration).

### 2. The contract the caller must honor

- **Order matters:** step table before summary (`make_summary` reads `data.steps`).
- **No metadata required:** `Data()` ships `MockMetaTestDependent`; only `cycle_mode` changes the math (CE direction).
- **Units by value:** core never sees unit objects — the caller precomputes floats (`nom_cap`, `current_conversion_factor`, `specific_converters`); pint fallback only via the optional `units` extra.
- **Raw shape assumptions:** `epoch_time_utc` is int64 ns UTC; capacities are cycle-cumulative per direction (point at `normalize_capacity_granularity` for step-/test-cumulative inputs); `test_id` optional, defaults to 0.
- **Legacy cruft absent by design:** native summary is the clean `CycleCols` subset + C-rate/IR; cumulated CE / shifted / RIC columns exist only on the legacy bridge.

### 3. Housekeeping

- Link the guide from the README.
- Once #55 (`Data.from_raw_frame`) lands, switch the example to use it.

## Links

- Raised together with #55 while discussing the future slim-consumer / cellpy v2 interaction pattern.
- Background: `.issueflows/04-designs-and-guides/cellpy-core-integration-roadmap.md`, `cellpy-core-migration.md` §4 (metadata/units boundaries).
