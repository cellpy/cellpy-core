# Plan for issue #32: int64-nanosecond timestamps (with documented seconds-UTC conversion)

## Goal

Make the canonical internal representation of **absolute** timestamps
(`epoch_time_utc` in raw; `first_epoch_time_utc` / `last_epoch_time_utc` in the cycle
table) **int64 nanoseconds since the Unix epoch, UTC**, and provide a small, documented
conversion module (ns ↔ float seconds UTC, ns ↔ native datetime). Remove the existing
float-vs-int drift between spec, converter, and mock helper.

## Constraints

- **KISS / no new deps.** Conversions are pure stdlib + `polars` (no `pint`, no new
  third-party packages). int64 ns is exactly what polars `Datetime` / Arrow use, so the
  helpers are thin.
- **Non-breaking & off the hot path.** The summary/step engine is untouched; this is a
  dtype + scaffolding change. Goldens must stay green.
- **Scope = absolute epoch timestamps only.** `test_time` / `step_time` are *relative
  elapsed seconds* and **stay float seconds** (confirmed below). Durations
  (`cycle_duration`, `*_duration`) are documented in **seconds**; any future
  implementation converts the ns difference to seconds *at the boundary* rather than
  storing ns durations.
- Google-style docstrings; follow `this-project.mdc` (run via `uv`/venv, not bare python).

### Prior art

- `dev/make_harmonized_raw.py` (`build_harmonized`) — converts native `date_time`
  (polars `Datetime`) to `epoch_time_utc` via `dt.epoch("ms") / 1000.0` → float seconds.
  *New work:* switch to `dt.epoch("ns")` → int64 ns (lossless, no narrowing); reuse the
  new module's polars helper so the magic constant lives in one place.
- `cellpycore._helpers.create_raw_data` — already emits `epoch_time_utc` as **Int64
  seconds** (range starting `1609459200`), i.e. *neither* the spec's float-seconds nor
  the target ns. *New work:* emit int64 **ns** (`* 1_000_000_000`), making it the
  canonical dtype and resolving the drift.
- `cellpycore.units` (`units.py`) — pint-based physical-unit conversion behind the
  optional `units` extra. *New work:* deliberately **coexist, do not merge** — epoch↔ns
  is dimensionless integer arithmetic, not a pint quantity, so it lives in its own
  module (mirrors the issue's guidance to keep it out of the pint machinery).
- `CycleCols.first/last_epoch_time_utc` + `cycle_duration` (`config.py`) and
  `header_mapping.NATIVE_ONLY_CYCLE` — declared headers, **but no engine code populates
  them today** (grep: only declarations + mapping membership, no producer). *New work:*
  update their doc/units only; do not implement population here.

## Approach

1. **New module `src/cellpycore/timestamps.py`** (small, documented, polars + stdlib).
   Proposed surface (refine during start; see Open questions):
   - `NS_PER_SECOND = 1_000_000_000`
   - Scalars: `epoch_ns_to_seconds(ns: int) -> float`,
     `seconds_to_epoch_ns(seconds: float) -> int`,
     `epoch_ns_to_datetime(ns: int) -> datetime` (tz-aware UTC),
     `datetime_to_epoch_ns(dt: datetime) -> int` (naive treated as UTC).
   - polars expr helpers for column work:
     `datetime_to_epoch_ns_expr(col) -> pl.Expr` (wraps `dt.epoch("ns")`),
     `epoch_ns_to_seconds_expr(col) -> pl.Expr`.
   The module documents the convention (int64 ns since Unix epoch, UTC; naive-source ==
   UTC at import) in its docstring.

2. **Converter** `dev/make_harmonized_raw.py`: replace the float-seconds line with the
   ns expr helper (`datetime_to_epoch_ns_expr("date_time")`), dropping the lossy
   `/1000.0` + `Float64` cast. Regenerate `tests/data/arbin_cc_harmonized_raw.parquet`.

3. **Mock helper** `_helpers.create_raw_data`: emit `epoch_time_utc` as int64 ns
   (multiply the current second-based range by `NS_PER_SECOND`), keeping `pl.Int64`.

4. **Specs**:
   - `harmonized_raw.md`: `epoch_time_utc` row → `int64 | nanosecond | <ns example>`;
     rewrite the `epoch_time_utc` bullet to state int64-ns-UTC + how to get seconds;
     **resolve** the "float or datetime?" open question (answer: int64 ns UTC, with
     documented conversion helpers).
   - `cycle_table.md`: `first/last_epoch_time_utc` rows → `int64 | nanosecond`; keep
     `cycle_duration` (and `*_duration`) as **float seconds**, noting the boundary
     conversion.

5. **`config.py` docs**: add brief comments on `RawCols.epoch_time_utc` and the
   `CycleCols.*_epoch_time_utc` fields stating the int64-ns-UTC convention and pointing
   at `cellpycore.timestamps` (names/values unchanged — dataclasses carry no dtype).

6. **Confirm derived quantities**: document (no code) that no current engine output
   subtracts epoch timestamps, so there is no seconds/ns regression risk today; future
   `cycle_duration` work must convert at the boundary.

## Files to touch

- `src/cellpycore/timestamps.py` — **new** module with conversion helpers (+ docstrings).
- `dev/make_harmonized_raw.py` — emit int64 ns via the helper.
- `tests/data/arbin_cc_harmonized_raw.parquet` — **regenerated** (no manual edit).
- `src/cellpycore/_helpers.py` — mock `epoch_time_utc` → int64 ns.
- `src/cellpycore/config.py` — doc/comment notes on the epoch fields.
- `docs/data_format_specifications/harmonized_raw.md` — dtype/unit + bullet + resolve open question.
- `docs/data_format_specifications/cycle_table.md` — dtype/unit for the epoch columns.
- `tests/test_timestamps.py` — **new** unit tests for the conversion helpers.
- `tests/test_harmonized_fixture.py` — update `epoch_time_utc` assertions for int64 ns
  (+ a round-trip ns↔seconds check).
- (optional) `.issueflows/04-designs-and-guides/` — short decision note on the timestamp
  representation, if we want a durable record.

## Test strategy

- **New** `tests/test_timestamps.py`: scalar round-trips (`seconds_to_epoch_ns` ↔
  `epoch_ns_to_seconds`), datetime round-trips (tz-aware UTC; naive-as-UTC), and the
  polars expr helpers on a tiny frame; assert int64 dtype and losslessness vs float
  seconds across the fixture's time range (~2016–2026).
- **Update** `tests/test_harmonized_fixture.py`: assert `epoch_time_utc` dtype is
  `Int64`, non-null, and `min` is in the ns range (`> 1.4e18`); add a ns→seconds sanity
  check landing in the 2016 era.
- **Regression**: `uv run pytest` (full suite). Expect goldens (`test_golden.py`,
  `check_dtype=False`) and step/cycle parity **unchanged**, since epoch timestamps feed
  no derived engine column. `test_config_columns.py` is name-only, so it is unaffected.

## Open questions

1. **Module name & surface.** `timestamps.py` (proposed) vs `time_utils.py`; and the
   exact helper set — do we want the polars-expr helpers now, or scalars-only until a
   second caller appears? (Default: `timestamps.py` with the small scalar + 2 expr
   helpers above.)
2. **Datetime helper return type.** Native `datetime` (tz-aware UTC) only, or also a
   polars `Datetime` expr? (Default: scalar `datetime` + the two polars exprs; skip a
   ns→Datetime expr until needed.)
3. **Durable design note.** Add a `.issueflows/04-designs-and-guides/` decision record
   for the timestamp convention, or keep the rationale in the spec + module docstring
   only? (Default: spec + docstring; add a short guide note only if you prefer.)
4. **Fixture churn.** Regenerating the parquet changes one committed binary column
   (float→int64 ns). Confirm that's acceptable (it is the point of the issue).
