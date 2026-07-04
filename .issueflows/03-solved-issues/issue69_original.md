# Issue #69: Add coverage reporting to CI

Source: https://github.com/cellpy/cellpy-core/issues/69

## Original issue text

Deferred from #66 (code review 2026-07, section C).

CI currently runs tests only (plus ruff after #66). Add coverage reporting: `pytest-cov` in the dev group, coverage step in `.github/workflows/simpletest.yml`, and optionally a threshold or badge.

See `.issueflows/04-designs-and-guides/code-review-2026-07.md` (section C, CI bullet).
