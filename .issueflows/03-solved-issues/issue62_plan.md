# Issue #62 — plan

## Goal

Make the documentation links in `README.md` work when rendered on PyPI.

## Approach

Relative links (`docs/...`) break on PyPI because the docs folder is not part
of the rendered page context. Replace the three relative doc links in the
README with absolute GitHub URLs pointing at `main`
(`https://github.com/cellpy/cellpy-core/blob/main/docs/...`). No packaging
changes — simplest fix, keeps the sdist/wheel lean.

## Files to touch

- `README.md`

## Test strategy

- `uv run pytest` (no code changes, suite must stay green).
- Visual check that the rewritten URLs resolve on GitHub.
