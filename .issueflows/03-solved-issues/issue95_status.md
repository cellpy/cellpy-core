# Issue #95 — Status

## Done

- [x] Moved `return df` outside `finally` in `set_col_first` (`legacy/mock_core.py`)
- [x] Added subprocess import test with `-W error::SyntaxWarning`
- [x] Full test suite passes

## Acceptance criteria

- [x] No `SyntaxWarning` when importing `cellpycore` on Python 3.14
- [x] Existing tests for legacy/mock helpers still pass

- [x] Done
