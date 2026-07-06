# Issue #100 — status

- [ ] Done

## What's done

- Issue captured (`issue100_original.md`) and plan confirmed (`issue100_plan.md`).
- Decision recorded in `.issueflows/04-designs-and-guides/bdf-io-placement.md`;
  ROADMAP links it; stale SCRATCHPAD entry marked resolved.
- Prototype package `scripts/bdf/` (`cellpy_bdf`): declarative
  harmonized-raw <-> BDF mapping (`mapping.py`), `export_bdf` /
  `to_bdf_frame` (`export.py`), `read_bdf` / `from_bdf_frame` (`read.py`),
  README, nested `pyproject.toml` (path source on in-repo `cellpycore`),
  committed `uv.lock`.
- Round-trip tests (7) in `scripts/bdf/tests/test_roundtrip.py`; run via
  `uv run --directory scripts/bdf pytest` — all pass.
- Nested-pyproject interference check: root `uv run pytest` (150 passed),
  `uv lock --check` clean, root `uv.lock` untouched, `uv run ruff check` and
  `uv run ruff format --check` green. PEP 723 fallback not needed.

## Remaining work

- `/iflow-close`: final checks, commit/push, PR review + merge.
