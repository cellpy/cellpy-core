# Issue #95 — Plan

## Goal

Eliminate `SyntaxWarning: 'return' in a 'finally' block` from `legacy/mock_core.py` on Python 3.14+ import.

## Approach

Move `return df` out of the `finally` block in `set_col_first`. Keep `df.reindex(columns=column_headings)` in `finally` so column reorder still runs even if the loop raises.

## Files to touch

- `src/cellpycore/legacy/mock_core.py` — refactor `set_col_first`
- `tests/test_import.py` — optional import-with-warnings check (if trivial)

## Test strategy

- `uv run pytest` (full suite)
- `uv run python -W error::SyntaxWarning -c "import cellpycore"` to assert no warning
