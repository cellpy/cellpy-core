# Issue #136 — status

- [x] Done

## What's done

- Plan confirmed (2026-07-17): carry `test_id` on steps+summary; window cruft;
  hard-error legacy schema on merge/update; regenerate goldens.
- Implemented on `136-legacy-bridge-preserve-test-id`.
- Version bumped `0.2.1` → `0.2.2` (static `pyproject.toml`); HISTORY promoted.
- `uv run pytest` 261 passed; ruff clean.
- Close: commit + PR; PyPI release via `release` from `main` after merge
  (see `release-procedure.md`).

## Remaining work

- None for the code issue. Post-merge: `iflow cleanup` + cut GitHub/PyPI
  release for `0.2.2`, then re-pin cellpy.
