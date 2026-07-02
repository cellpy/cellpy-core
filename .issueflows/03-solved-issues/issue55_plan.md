# Plan — Issue #55: Add validating front door for raw frames (`Data.from_raw_frame`)

## Goal

Give slim consumers a validating entry point for native-schema polars raw frames:
`Data.from_raw_frame(df, validate=True)` fails fast with one actionable error
instead of a deep polars stack trace inside `summarizers`.

## Constraints

- KISS (per issue): one classmethod + one module-level validation helper in
  `src/cellpycore/cell_core.py`. No schema-validation framework, no new deps.
- Graceful-degradation metadata guarantee untouched: `Data()` already attaches
  `MockMetaTestDependent`; `from_raw_frame` reuses the plain constructor.
- `validate=False` must skip all checks entirely (zero cost).
- Google-style docstrings.

### Prior art

- `tests/test_harmonized_fixture.py::_rawcols_names()` — derives the full
  `RawCols` name set via `vars(RawCols)`; the helper mirrors the idea but only
  needs the explicit required subset (coexist, no migration).
- `summarizers._ensure_test_id` — engine already auto-adds `test_id`; validator
  must therefore treat `test_id` as optional.
- `summarizers.make_step_table` signal resolution (lines ~360-375) — engine
  skips absent `internal_resistance` / `ref_potential` / `step_time`; validator
  treats these as optional too.
- `_helpers.create_raw_data()` + `mock_data_with_raw` fixture — valid native
  frame for tests (reuse, no new fixture needed).
- Toolbox (`.issueflows/00-tools/`) empty; graph report checked — nothing else relevant.

## Approach

1. **Module-level helper** `validate_raw_frame(raw, raw_cols=None)` in
   `cell_core.py` (public, so cellpy v2 can call it directly later):
   - `raw_cols` defaults to `config.RawCols()`.
   - Type check: must be a `polars.DataFrame` (the slim-consumer story is
     polars-native) — clear `TypeError` otherwise.
   - **Required columns** (the engine's load-bearing set):
     `datapoint_num`, `cycle_num`, `step_num`, `epoch_time_utc`, `test_time`,
     `current`, `potential`, `cumulative_charge_capacity`,
     `cumulative_discharge_capacity`. Missing ones → single `ValueError`
     listing all of them.
   - **Dtype sanity** (collected, reported together with missing-column errors
     in one message):
     - `epoch_time_utc` must be exactly `pl.Int64` — error text mentions the
       int64 nanoseconds-since-epoch UTC (STEP-11) contract.
     - `datapoint_num`, `cycle_num`, `step_num` must be integer dtypes.
     - `test_time`, `current`, `potential`, `cumulative_*_capacity` must be
       numeric.
   - **Optional columns** (`test_id`, `internal_resistance`, `ref_potential`,
     `step_time`, `mask`, `source_*`, aux columns, …): allowed absent, not
     dtype-checked (KISS).
2. **Classmethod** on `Data`:

   ```python
   @classmethod
   def from_raw_frame(cls, raw, validate=True, raw_cols=None) -> "Data":
       if validate:
           validate_raw_frame(raw, raw_cols)
       data = cls()
       data.raw = raw
       return data
   ```

3. Run `graphify update .` after the code change (project rule).

## Files to touch

- [src/cellpycore/cell_core.py](c:\scripting\cellpy-core\src\cellpycore\cell_core.py)
  — add `validate_raw_frame()` helper + `Data.from_raw_frame()` classmethod
  (imports `polars` lazily inside the helper, matching module style).
- [tests/test_creation.py](c:\scripting\cellpy-core\tests\test_creation.py)
  — add the new tests (creation-themed file already exists; no new test module).

## Test strategy

Command: `uv run pytest` (project default).

New tests in `tests/test_creation.py`:

- **Happy path / round-trip**: `Data.from_raw_frame(create_raw_data())` runs
  through `CellpyCellCore.make_core_step_table` + `make_core_summary` and the
  resulting steps/summary frames equal those from plain `data.raw = df`.
- **Missing columns**: drop e.g. `cycle_num` + `current` → `ValueError` naming
  both.
- **Wrong dtype**: cast `epoch_time_utc` to `pl.Float64` → error mentioning
  int64-ns contract.
- **`validate=False`**: same broken frame passes without error.
- **Not a polars frame**: pandas frame → `TypeError`.

## Open questions

- None — polars-only input is assumed (the issue's slim-consumer story);
  pandas users go through the legacy bridge instead.
