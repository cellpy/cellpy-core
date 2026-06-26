# Issue 32 — Status

Adopt **int64 nanoseconds since the Unix epoch, UTC** as the canonical
absolute-timestamp dtype (`epoch_time_utc`, `first/last_epoch_time_utc`), with a
small documented conversion module. Implements roadmap STEP-11.

- [x] Done

## What landed (2026-06-25)

Implemented per the confirmed `issue32_plan.md` (defaults accepted on all four open
questions: module named `timestamps.py` with scalar + 2 polars-expr helpers;
scalar `datetime` return; rationale kept in spec + module docstring, no separate
guide doc; fixture regenerated).

- **`src/cellpycore/timestamps.py`** — new module. `NS_PER_SECOND`; scalars
  `epoch_ns_to_seconds` / `seconds_to_epoch_ns` / `datetime_to_epoch_ns`
  (naive == UTC) / `epoch_ns_to_datetime` (tz-aware UTC); polars-expr helpers
  `datetime_to_epoch_ns_expr` (wraps `dt.epoch("ns")`) / `epoch_ns_to_seconds_expr`.
  Pure stdlib + polars, no pint, no new deps.
- **`dev/make_harmonized_raw.py`** — `epoch_time_utc` now emitted via
  `datetime_to_epoch_ns_expr("date_time")` (int64 ns), dropping the lossy
  `dt.epoch("ms")/1000.0` float-seconds narrowing.
- **`tests/data/arbin_cc_harmonized_raw.parquet`** — regenerated; `epoch_time_utc`
  is now `Int64` ns (min ≈ 1.470e18 ns, 2016 era), non-null.
- **`src/cellpycore/_helpers.py`** — mock `create_raw_data` emits `epoch_time_utc`
  as int64 ns (was Int64 *seconds*), resolving the prior spec/code drift.
- **`src/cellpycore/config.py`** — doc comments on `RawCols.epoch_time_utc` and the
  `CycleCols.*_epoch_time_utc` fields stating the int64-ns-UTC convention.
- **Specs** — `harmonized_raw.md` (`epoch_time_utc` row → int64/nanosecond, bullet
  rewritten, the long-standing "float or datetime?" open question **resolved**) and
  `cycle_table.md` (`first/last_epoch_time_utc` → int64/nanosecond; `cycle_duration`
  kept float seconds with a boundary-conversion note).
- **Tests** — new `tests/test_timestamps.py` (11 tests: scalar/expr round-trips,
  naive-as-UTC, microsecond-resolution datetime round-trip, sub-µs truncation,
  Int64/Float64 dtype guards); `tests/test_harmonized_fixture.py` updated to assert
  int64-ns dtype + a ns→seconds sanity check.

## Guardrails honoured

- **Non-breaking / off the hot path.** Summary/step engine untouched; no engine
  output subtracts epoch timestamps today (`first/last_epoch_time_utc` and
  `cycle_duration` are declared headers but not yet populated), so the dtype change
  is isolated.
- **Goldens unchanged** (`test_golden.py`, `check_dtype=False`); `test_config_columns.py`
  is name-only. Full suite: **73 passed** (62 prior + 11 new), no lint errors.
- **`test_time` / `step_time`** confirmed to stay float **seconds** (relative
  elapsed durations, not absolute timestamps) — unchanged.
- No new runtime dependencies.

## Scope / deferred

- Populating `first/last_epoch_time_utc` + `cycle_duration` in the summary engine is
  out of scope (no producer exists yet); any future implementation must convert the
  ns difference to seconds at the boundary, as documented in `cycle_table.md`.
- Full timezone-aware handling beyond the naive-as-UTC convention stays out of scope.

## Next

Ready to ship — run `/iflow-close` (optionally `bump patch`/`minor`).
