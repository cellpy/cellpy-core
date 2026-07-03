# Issue #66 status: code cleaning and test completion

- [x] Done

Plan: [issue66_plan.md](issue66_plan.md) (confirmed 2026-07-03, deferred items filed as #67–#70)

## What's done

All four plan phases implemented on branch `66-code-cleaning-and-test-completion`
(one commit per phase, suite green after each; 120 passed + 3 opt-in benchmarks):

- **Phase 1 — hygiene** (`chore:` commit): removed unused deps (duckdb,
  duckdb-engine, sqlalchemy, narwhals) + uv-dynamic-versioning; real pyproject
  description/classifier; deleted tracked `scratch.db` / `tmp/*` (+ gitignore);
  module loggers replace root `logging.*` calls; **A3** falsy-override fix
  (explicit `0.0` wins) + regression test; **A5** `DEFAULT_RAW_LIMITS` frozen
  (`MappingProxyType`), `make_step_table` builds fresh limits per call;
  **A6** dead `Data.cycle` / `Data.step` removed; ruff config + CI lint step;
  ruff check --fix + format applied repo-wide.
- **Phase 2 — API truthing** (`feat:` commit): curated public API in
  `cellpycore/__init__.py` + `__version__` (importlib.metadata); `py.typed`;
  **A4** dead `find_end_voltage`/`select_columns` removed from *native*
  `make_core_summary` (legacy bridge keeps them — cellpy passes
  `select_columns`); README description + example; `this-project.md` filled.
- **Phase 3 — engine guards** (`feat:` commit): `NoDataFound` for missing
  `raw`/`steps`, `ValueError` naming every missing required column at
  `make_step_table` / `make_summary`; guard tests.
- **Phase 4 — tests** (`test:` commit): `tests/test_e2e.py` native pipeline
  via public API on the harmonized Arbin fixture (golden counts 103/18/1457,
  exclude-types + scaled-columns variants, empty-frame and discharge-only
  edge cases, thread-safety smoke with parallel schemas);
  `tests/test_benchmarks.py` (pytest-benchmark, opt-in via
  `uv run pytest -m benchmark`). Engine fix: Null-dtype raw signal columns
  skipped in `make_step_table` (all-null placeholders crashed polars).
- Deferred issues filed: #67 (selectors), #68 (units fallback), #69 (CI
  coverage), #70 (B1/B2 design pass).
- graphify graph refreshed.

## Remaining work

- None. Closed via `/iflow-close` 2026-07-03 (HISTORY.md bullet added, no
  version bump requested). Deferred follow-ups live in issues #67–#70.
