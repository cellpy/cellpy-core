# Issue #32: Use int64 nanoseconds for timestamps internally (with documented conversion to epoch-seconds UTC)

Source: https://github.com/cellpy/cellpy-core/issues/32

## Original issue text

## Summary

Standardize how cellpy-core represents absolute timestamps. Today `epoch_time_utc`
(raw) and `first_epoch_time_utc` / `last_epoch_time_utc` (cycle table) are specced
as **float seconds since the Unix epoch, UTC**. We should instead use **int64
nanoseconds since the Unix epoch, UTC** as the canonical internal representation,
and provide easy, well-documented conversion helpers to/from **float seconds UTC**
(and ideally a native datetime).

This also resolves the long-standing open question in the harmonized-raw spec:
*"epoch_time_utc — should this be a float or a datetime object?"*

## Why

- **Precision.** float64 epoch-seconds only has ~0.24 µs resolution near 2026 (the
  ~1.7e9 magnitude consumes most of the 52-bit mantissa), so it cannot represent
  nanoseconds and silently rounds sub-microsecond values. int64 ns is exact and is
  exactly what `pandas` `datetime64[ns]` / `polars Datetime` / Arrow timestamps use
  internally, so round-trips to native timestamp types are lossless.
- **Consistency.** There is already drift between the spec and the code:
  - spec (`docs/data_format_specifications/harmonized_raw.md`, `cycle_table.md`) and
    `RawCols.epoch_time_utc` / `CycleCols.first_epoch_time_utc` describe **float seconds**;
  - the mock-data helper `cellpycore._helpers.create_raw_data` actually emits
    `epoch_time_utc` as **Int64 seconds**;
  - the issue #29 converter `dev/make_harmonized_raw.py` takes a native `Datetime`
    (`date_time`) and **narrows it to float seconds** (`dt.epoch("ms")/1000`).
  A single canonical dtype removes this ambiguity.
- **Interop.** int64 ns is the lingua franca of the Arrow/pandas/polars ecosystem.

## Goal / desired outcome

1. Canonical internal timestamp dtype = **int64, nanoseconds since Unix epoch, UTC**.
2. A small, well-documented set of conversion helpers, e.g.:
   - `epoch_ns -> float seconds UTC` and back,
   - `epoch_ns <-> native datetime / polars Datetime`,
   - kept out of the physical-unit (`pint`) machinery in `units.py` — likely a new
     tiny `time` utility module (decision to be made in planning).
3. Docs that make the representation and the seconds-UTC conversion obvious to
   downstream cellpy developers.

## Scope (proposed — refine in planning)

- [ ] Decide & document the canonical dtype (int64 ns UTC) and the conversion API.
- [ ] Update the spec tables: `harmonized_raw.md` (`epoch_time_utc`) and
      `cycle_table.md` (`first_epoch_time_utc` / `last_epoch_time_utc`) — dtype, unit,
      and a note on converting to seconds UTC. Resolve the float-vs-datetime follow-up.
- [ ] Add conversion helpers (ns <-> seconds float, ns <-> datetime) in a central,
      documented place, with tests.
- [ ] Update `RawCols` / `CycleCols` documentation/comments to match.
- [ ] Update `dev/make_harmonized_raw.py` to emit int64 ns (no lossy narrowing) and
      regenerate `tests/data/arbin_cc_harmonized_raw.parquet`.
- [ ] Fix `cellpycore._helpers.create_raw_data` to emit int64 ns consistently.
- [ ] Confirm derived quantities that subtract timestamps (e.g. `cycle_duration`,
      `*_test_time`) still produce their documented units (seconds) — convert at the
      boundary rather than storing durations in ns.

## Out of scope / open questions

- Full timezone-aware handling beyond the UTC convention (naive-source tz inference
  stays a separate concern; we still assume source-naive == UTC at import).
- Whether `test_time` / `step_time` (elapsed seconds, not absolute epoch) should also
  change — they are relative durations and probably stay float seconds; confirm.

## References

- Precision analysis and trade-offs were discussed alongside issue #29 (harmonized
  raw test fixture), which introduced the current float-seconds conversion.
- Affected code: `src/cellpycore/config.py` (`RawCols`, `CycleCols`),
  `src/cellpycore/_helpers.py`, `dev/make_harmonized_raw.py`.
