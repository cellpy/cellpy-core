# Issue #55 status — validating front door for raw frames

Branch: `55-from-raw-frame`

## Done

- 2026-07-02: Added `validate_raw_frame()` module-level helper and
  `Data.from_raw_frame(raw, validate=True, raw_cols=None)` classmethod in
  `src/cellpycore/cell_core.py` (per confirmed `issue55_plan.md`):
  - `TypeError` on non-polars input (pandas users -> legacy bridge).
  - Single `ValueError` collecting all problems: missing required columns
    (`datapoint_num`, `cycle_num`, `step_num`, `epoch_time_utc`, `test_time`,
    `current`, `potential`, `cumulative_charge_capacity`,
    `cumulative_discharge_capacity`), `epoch_time_utc` must be Int64
    (STEP-11 int64-ns UTC contract named in the message), datapoint/cycle/step
    integer, rest numeric.
  - Optional columns (`test_id`, `internal_resistance`, `ref_potential`,
    `step_time`, `source_*`, `aux_*`, …) allowed absent, not dtype-checked.
  - `validate=False` skips all checks; fresh `Data()` keeps the
    `MockMetaTestDependent` graceful-degradation guarantee.
- 5 new tests in `tests/test_creation.py`: round-trip parity vs plain
  `data.raw = df` through `make_core_step_table` + `make_core_summary`,
  missing columns all named, wrong epoch dtype mentions int64-ns,
  `validate=False` skip, pandas `TypeError`.
- Test suite green: `uv run pytest` -> 100 passed.
- `graphify update .` run after the code change.

## Remaining

- Nothing (ready for `/iflow-close`).

## Status

- [x] Done
