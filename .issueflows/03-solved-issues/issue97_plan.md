# Issue #97 — plan: RawCols dtype map and polars cast helpers

## Goal

Single source of truth for the polars dtype of every `RawCols` column, plus a
cast helper next to `validate_raw_frame`, so consumers stop hand-maintaining
dtype maps when converting legacy pandas raw frames to native polars.

## Constraints

- `validate_raw_frame` stays the checker; its checked column set and error
  behavior are unchanged (no new dtype checks — back-compat).
- `config.py` currently imports no polars; keep it that way via lazy
  `import polars as pl` inside the new method (same pattern as
  `validate_raw_frame` in `cell_core.py`).
- Dtypes must match the authoritative spec table in
  [docs/specifications/harmonized-raw.md](../../docs/specifications/harmonized-raw.md)
  (`epoch_time_utc` Int64 ns, `mask` Boolean, ints Int64, floats Float64,
  strings Utf8 — codebase convention is `pl.Utf8`, see
  `testing/mock_data.py`).
- No datetime -> epoch-ns conversion in the cast helper; that stays in
  `cellpycore.timestamps`. The helper does plain strict casts.
- Scope: `RawCols` only. `StepCols` / `CycleCols` dtype maps are deferred
  (issue text says "optionally"; acceptance criteria mention only `RawCols`).

### Prior art

- `Cols.ordered_names()` (`config.py`, issue #96) — classmethod resolving
  attribute names on a fresh instance so `FlexibleCols` renames flow through;
  the dtype map mirrors this convention.
- `validate_raw_frame` (`cell_core.py`) — lazy polars import, `raw_cols`
  injection parameter, collect-all-problems error style; `cast_raw_frame`
  coexists beside it as proposed by the issue.
- SCRATCHPAD.md "Create a dtype map" — full column -> dtype sketch; adopted
  as the map content (verified against the spec table).
- Toolbox (`.issueflows/00-tools/`) empty; graph checked — no other helper
  overlaps.

## Approach

1. **`RawCols.dtype_map()`** (instance method in `config.py`):

   ```python
   def dtype_map(self) -> dict[str, "pl.DataType"]:
       import polars as pl
       return {self.datapoint_num: pl.Int64, self.mask: pl.Boolean, ...}
   ```

   - Covers **all** `RawCols` columns (required and optional).
   - Instance method (not classmethod) so injected renames resolve via
     attribute access, same reasoning as `ordered_names()`.
   - Lives on `RawCols` in `config.py`: dtype knowledge is schema knowledge;
     keeps `RawCols`, the spec comment block, and the dtypes side by side.

2. **`cast_raw_frame(raw, raw_cols=None)`** in `cell_core.py`, beside
   `validate_raw_frame`:

   - Casts every column **present** in the frame that appears in
     `raw_cols.dtype_map()`; missing optional columns are skipped; extra
     columns (e.g. custom `aux_*`) pass through untouched.
   - Strict polars casts (default) — a lossy/failed cast raises
     `polars.exceptions.InvalidOperationError`; fail fast, no silent coercion.
   - Returns a new `DataFrame`; typical use:
     `Data.from_raw_frame(cast_raw_frame(df))`.

3. **Exports**: add `cast_raw_frame` to `cellpycore/__init__.py` (`__all__`).
   `validate_raw_frame` stays unexported (unchanged scope; open question).

4. **Docs**:
   - `docs/user-guide/standalone-use.md`: short "Dtypes" note pointing at
     `RawCols().dtype_map()` + `cast_raw_frame` in the from_raw_frame section.
   - `docs/specifications/harmonized-raw.md`: one line noting the dtype
     column of the spec table now has a code home (`RawCols.dtype_map`).
   - `SCRATCHPAD.md`: mark the #97 entry resolved (same style as #98/#100).

## Files to touch

- `src/cellpycore/config.py` — add `RawCols.dtype_map()`.
- `src/cellpycore/cell_core.py` — add `cast_raw_frame()`.
- `src/cellpycore/__init__.py` — export `cast_raw_frame`.
- `tests/test_config_columns.py` — dtype-map tests: keys == `ordered_names()`
  (guards future column additions), pin `epoch_time_utc` Int64 and `mask`
  Boolean, renamed-schema (`FlexibleCols`) key resolution.
- `tests/test_creation.py` — cast-helper tests: wrong-dtype frame casts then
  validates clean; missing optional / extra columns tolerated; strict-cast
  failure raises; mock-data frame is a no-op round-trip.
- `docs/user-guide/standalone-use.md`, `docs/specifications/harmonized-raw.md`,
  `SCRATCHPAD.md` — references / resolution notes.

## Test strategy

- `uv run pytest` (full suite; benchmarks stay deselected).
- `uv run ruff check && uv run ruff format --check` before push (CI parity).
- New tests as listed above; no golden-fixture changes expected (engine path
  untouched).

## Open questions

1. Also export `validate_raw_frame` at top level while touching `__init__.py`?
   (Docs advertise it via `Data.from_raw_frame`; currently reachable only as
   `cellpycore.cell_core.validate_raw_frame`.) Recommend: yes, cheap and
   consistent with `cast_raw_frame`.
2. Defer `StepCols` / `CycleCols` dtype maps to a follow-up issue, or include
   here? Recommend: defer (acceptance criteria cover `RawCols` only; step/cycle
   output dtypes are produced by the engine, not consumer input).
3. `dtype_map` as instance method on `RawCols` (recommended) vs module-level
   `rawcols_dtype_map()` function as sketched in SCRATCHPAD? Method honors
   renamed schemas for free.
