# Issue #97: Add RawCols dtype map and polars cast helpers

Source: https://github.com/cellpy/cellpy-core/issues/97

## Original issue text

## Context

Consumers converting legacy pandas raw frames to native polars must hand-maintain a dtype map (`Int64` for `epoch_time_utc`, `Boolean` for `mask`, etc.). There is no single source of truth alongside `config.RawCols` and `validate_raw_frame()`.

Source: `SCRATCHPAD.md` (Create a dtype map section).

## Proposal

- Add an authoritative dtype map for `RawCols` (and optionally `StepCols` / `CycleCols`) in or near `config.py`, aligned with `docs/specifications/harmonized-raw.md`.
- Add helper(s) alongside `validate_raw_frame()` — e.g. `rawcols_dtype_map() -> dict[str, pl.DataType]` and optionally `cast_raw_frame(df) -> pl.DataFrame`.
- Keep `validate_raw_frame()` as the checker; casting helpers enforce dtypes before validation.

## Open design questions

- Should dtypes live on `RawCols` as a classmethod, a module-level constant, or next to `validate_raw_frame` in `cell_core.py`?
- How much of the optional-column set should be dtype-checked vs cast-only?

## Acceptance criteria

- [ ] Single maintained dtype map for all `RawCols` columns
- [ ] Tests pin key dtypes (especially `epoch_time_utc` Int64, `mask` Boolean)
- [ ] Standalone-use / harmonized-raw docs reference the helper
