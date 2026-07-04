# Issue #91 status

- [ ] Done

## What's done

- Plan confirmed: `cellpycore==0.1.4` pin style; skip #88 in HISTORY.
- Retroactive `[0.1.3]` section in `HISTORY.md` (moved unreleased bullets + #89, #63).
- `[0.1.4]` promoted in `HISTORY.md`; `pyproject.toml` bumped to 0.1.4.
- Preflight green: ruff + 150 pytest passed.
- PR opened for cellpy-core changelog + version bump.

## Remaining work

- Merge PR, run `release` alias on `main`, verify PyPI `cellpycore 0.1.4`.
- cellpy: separate PR — `cellpycore==0.1.4`, `uv lock`, `tests/test_slim.py`.
