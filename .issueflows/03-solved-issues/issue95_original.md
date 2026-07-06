# Issue #95: Fix SyntaxWarning: 'return' in finally block in legacy/mock_core.py

Source: https://github.com/cellpy/cellpy-core/issues/95

## Original issue text

## Context

When importing `cellpycore` in JupyterLab with Python 3.14, a `SyntaxWarning` is emitted:

```
src/cellpycore/legacy/mock_core.py:66: SyntaxWarning: 'return' in a 'finally' block
  return df
```

Source: `SCRATCHPAD.md` (Syntax warning section).

## Problem

`return` inside a `finally` block is deprecated/problematic in Python 3.14+ and triggers a syntax warning at import time.

## Suggested fix

Refactor `set_col_first` (or the surrounding try/finally in `legacy/mock_core.py`) so the return happens outside the `finally` block, preserving behaviour.

## Acceptance criteria

- [ ] No `SyntaxWarning` when importing `cellpycore` on Python 3.14
- [ ] Existing tests for legacy/mock helpers still pass
