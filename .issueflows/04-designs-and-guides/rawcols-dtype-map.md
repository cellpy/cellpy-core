# RawCols dtype map and cast helper (issue #97)

**Context.** Consumers converting foreign raw data (e.g. legacy pandas frames)
to native polars had to hand-maintain a column -> dtype map; no single source
of truth existed next to `config.RawCols` and `validate_raw_frame()`.

**Decision.**

- The authoritative map is `RawCols.dtype_map()` in `config.py` — an
  **instance method** (not classmethod / module function) so renamed schemas
  (subclass overrides, `FlexibleCols` transforms) resolve through attribute
  access, mirroring `Cols.ordered_names()`. Lazy `import polars` keeps
  `config.py` polars-free at import time.
- Casting is a separate helper, `cell_core.cast_raw_frame()`, beside
  `validate_raw_frame()`: strict casts (fail fast, no silent coercion), skips
  absent optional columns, passes extra columns (custom `aux_*`) through.
  `validate_raw_frame()` stays the checker, unchanged.
- Both `cast_raw_frame` and `validate_raw_frame` are exported top-level.
- A test pins `list(dtype_map()) == ordered_names()` so new columns cannot be
  added without a dtype.

**Alternatives considered.** Module-level `rawcols_dtype_map()` (SCRATCHPAD
sketch) — rejected: does not honor renamed schemas. Dtype-checking all
optional columns in `validate_raw_frame` — rejected: back-compat, validator
scope unchanged.

**Deferred.** `StepCols` / `CycleCols` dtype maps: engine-produced outputs,
not consumer input; open a follow-up issue if a concrete need appears.

Link: [issue #97](https://github.com/cellpy/cellpy-core/issues/97), PR #106.
