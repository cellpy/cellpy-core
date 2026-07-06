# Issue #97 — status

- [x] Done

## What's done

- Issue captured (`issue97_original.md`) and plan confirmed (`issue97_plan.md`).
- `RawCols.dtype_map()` added in `config.py` — all 29 columns, lazy polars
  import, instance method so renamed schemas resolve (mirrors `ordered_names`).
- `cast_raw_frame()` added in `cell_core.py` beside `validate_raw_frame` —
  strict casts, skips absent optional columns, extra columns pass through.
- Top-level exports: `cast_raw_frame` and `validate_raw_frame` in
  `cellpycore/__init__.py` (`__all__`).
- Tests: dtype-map coverage/order + key-dtype pins + renamed-schema resolution
  (`test_config_columns.py`); cast-then-validate, skip/pass-through, no-op
  round-trip, strict-failure, non-polars rejection (`test_creation.py`).
- Docs: `standalone-use.md` Dtypes section, `harmonized-raw.md` code-home note,
  SCRATCHPAD #97 marked resolved.
- `uv run pytest` green (163 passed), `ruff check` + `ruff format --check`
  clean; end-to-end demo (sloppy dtypes -> cast -> validate -> step table ->
  summary) verified.

- Closed via `/iflow-close`: `HISTORY.md` bullet under `[Unreleased]` (no
  version bump requested), design note added
  (`04-designs-and-guides/rawcols-dtype-map.md`), PR #106 open against `main`.

## Remaining work

- None for this issue. Deferred (per plan, by design): `StepCols` /
  `CycleCols` dtype maps (engine outputs, not consumer input) — open a
  follow-up issue if a concrete need appears.
