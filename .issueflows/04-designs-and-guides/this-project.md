# cellpycore

## What this project is

`cellpy-core` is the core processing engine of
[cellpy](https://github.com/jepegit/cellpy): it takes battery-cycling raw data
(one row per logged datapoint) and finds all steps and cycles, classifies step
types (charge / discharge / rest / cv / ir), and builds per-step and per-cycle
summary tables. It is consumed by cellpy through the legacy bridge
(`OldCellpyCellCore`) and by slim standalone consumers through the native API
(`Data.from_raw_frame` + `make_step_table` / `make_summary`). Goals: fast,
thread-safe, schema-injected, easy to extend.

## Stack / runtime

- Python >= 3.13, managed with `uv` (`.venv` in the repo root).
- Engine is polars-native; pandas + pyarrow only for the legacy bridge and
  parquet fixtures. `pint` is an optional extra (`units`) for the unit helpers.
- Lint/format: `ruff` (checked in CI — same commands as the workflow). Tests: `pytest`.

## How to run / test

```bash
uv sync                      # install / sync dependencies
uv run pytest                # full test suite (benchmarks excluded by default)
uv run pytest -m benchmark   # opt-in performance benchmarks

# Lint / format — run before push (matches CI)
uv run ruff check && uv run ruff format --check

# Auto-fix what ruff can (unused imports, format, etc.)
uv run ruff check --fix && uv run ruff format
```

Run **both** check and format before opening a PR. CI runs `ruff check` and
`ruff format --check` with no `--fix`; autofix locally, then re-run the check
commands to confirm green.

Optional: install [pre-commit](https://pre-commit.com/) and add a local hook that
runs the same ruff commands — not configured in-repo yet, but a good guard if
you commit often without running CI locally.

## Conventions

- Issue work on `<N>-<short-slug>` branches; Conventional Commits; squash
  merges on GitHub. Issue tracking lives under `.issueflows/`.
- Google-style docstrings everywhere.
- Column names for raw / cycle / step **group keys** and summary aliases come
  from an injected ``config.Schema``. Per-step stat column stems
  (``<signal>_<stat>``) are a **fixed engine contract**, not schema-injected
  (see issue #70 / ``StepCols`` docstring).
- Parity with legacy cellpy is enforced by tests (golden parquet fixtures in
  `tests/data/`, see `tests/data/README.md`), not by vigilance.
- Metadata boundary: core ships metadata *scaffolding* (`cellpycore.metadata`)
  but never requires populated metadata on `Data` (see
  `cellpy-core-migration.md`).

## Entry points

- Public API: `cellpycore/__init__.py` (curated exports + `__version__`).
- Engine: `src/cellpycore/summarizers.py` (`make_step_table`, `make_summary`),
  helpers in `extractors.py`.
- Cell classes / data container: `src/cellpycore/cell_core.py`
  (`CellpyCellCore`, `OldCellpyCellCore`, `Data`).
- Schemas: `src/cellpycore/config.py`; legacy headers: `legacy.py`;
  legacy<->native mapping: `header_mapping.py`.
- Read first: `.issueflows/04-designs-and-guides/code-review-2026-07.md` and
  `cellpy-core-migration.md`.

## Non-goals / known limitations

- No instrument loaders, no file IO beyond test fixtures, no unit conversion
  on the hot path (conversion factors are passed by value).
- `legacy_selectors.py` is bridge-only (pandas + `legacy_schema()`); not part of
  the public API.
- Per-step stat column names (`<signal>_<stat>`) are a fixed engine contract,
  not schema-injected (issue #70).
