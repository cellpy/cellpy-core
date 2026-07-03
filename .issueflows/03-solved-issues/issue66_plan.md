# Issue #66 plan: code cleaning and test completion

Source issue: [issue66_original.md](issue66_original.md)
Driving doc: [code-review-2026-07.md](../04-designs-and-guides/code-review-2026-07.md)
Branch: `66-code-cleaning-and-test-completion`

## Goal

Land the mechanical cleanup from the 2026-07 code review (hygiene, API truthing,
engine guards) and close the test gaps with native-path e2e tests and opt-in
profiling benchmarks.

## Constraints

- **In scope (grilled + confirmed):** review-doc items D1 (hygiene), D2 (API
  truthing), D5 (engine guards), D7 (test gaps) + e2e + profiling tests.
- **Out of scope (deferred, filed):** D3 selectors decision (#67, see
  `selector-dead-code-deferral.md`), D4 units fallback (A2, #68), CI coverage
  reporting (#69), B1/B2 design pass (#70), structural refactors (no module
  splits/moves — review verdict: engine is healthy; avoid churn before cellpy
  pins a tag).
- Parity is enforced by tests (migration doc): golden tests must stay green
  byte-for-byte; no changes to computed values.
- Legacy bridge (`OldCellpyCellCore`) behavior unchanged — cellpy imports only
  this (verified: `cellpy/readers/cellreader.py:72` is the sole entry).
- Google-style docstrings; project loggers, not root `logging` calls.

### Prior art

- `tests/test_golden.py` — legacy-bridge e2e on vendored Arbin parquet with
  golden numbers (`ARBIN_N_STEPS=103`, `ARBIN_N_CYCLES=18`); new native e2e
  mirrors this oracle, does not duplicate the legacy path.
- `tests/test_harmonized_fixture.py` + `tests/data/arbin_cc_harmonized_raw.parquet`
  — harmonized (native-naming) fixture already vendored; reuse for native e2e.
- `Data.from_raw_frame` (issue #55) — existing validating front door; native
  e2e drives through it, engine guards (B3) extend the same validation spirit
  into `make_step_table` / `make_summary`.
- Exclude-types support (issue #54) — covered by `tests/test_exclude_types.py`;
  e2e exercises it as a pipeline variant only.
- `.issueflows/00-tools/` — only README, no reusable helper applies.
- graphify: not installed for this repo state (no `graphify-out/` consulted
  beyond rules; grep-based discovery used).

## Approach

Phased commits on the issue branch, one concern per commit (Conventional
Commits), tests green after each phase.

### Phase 1 — hygiene (D1)

1. `pyproject.toml`: remove `duckdb`, `duckdb-engine`, `sqlalchemy`, `narwhals`
   (keep `pyarrow`); drop `uv-dynamic-versioning` from `[build-system]`; real
   description; fix wrong classifier; `uv sync` to refresh lock.
2. Delete tracked junk: `scratch.db`, `tmp/simple.csv`, `tmp/simple.parquet`
   (+ `.gitignore` entries for `scratch.db`, `tmp/`).
3. Replace root-logger calls with module loggers (`logger = logging.getLogger(__name__)`)
   in `summarizers.py`, `settings_base.py`, `units.py`.
4. **A3 falsy-override fix** in `summarizers._classify_steps`: membership test
   (`key in orl`) instead of `or`-fallback for all four override keys +
   regression test with `0.0` override.
5. **A5**: `make_step_table(raw_limits=None)` → build fresh
   `asdict(CellpyLimits())` per call; keep `DEFAULT_RAW_LIMITS` as a frozen
   `MappingProxyType` for introspection/back-compat (`test_limits.py` uses it).
6. **A6**: delete `Data.cycle` / `Data.step` dead fields (verified unused in
   cellpy).
7. CI: add ruff step (`ruff check` + `ruff format --check`) to
   `.github/workflows/simpletest.yml`; minimal `[tool.ruff]` config.

### Phase 2 — API truthing (D2)

1. `src/cellpycore/__init__.py`: minimal curated exports —
   `CellpyCellCore`, `OldCellpyCellCore`, `Data`, `make_step_table`,
   `make_summary`, `default_schema` + schema types, `NoDataFound`;
   `__version__` via `importlib.metadata.version("cellpy-core")` with
   `PackageNotFoundError` fallback. `metadata` stays a submodule import.
2. **A4**: delete unused `selector` / `select_columns` / `find_end_voltage`
   params from native `make_core_summary` (legacy bridge keeps its
   `find_end_voltage`).
3. Add `py.typed` marker (+ ensure hatch includes it).
4. Docs: fill `this-project.md` stubs; README project description.

### Phase 3 — engine guards (D5/B3)

- `make_step_table` / `make_summary`: raise `NoDataFound` when `data.raw`
  (resp. `data.steps`) is `None`/missing; raise `ValueError` naming the missing
  required columns. Tests for both.

### Phase 4 — tests (D7 + e2e + profiling)

1. `tests/test_e2e.py` — native pipeline via public API only
   (`from cellpycore import ...`): harmonized raw parquet →
   `Data.from_raw_frame` → `make_step_table` → `make_summary` →
   exclude-types and scaled-columns variants; assert golden cycle/step counts
   and spot values. Edge cases: empty raw frame, cycle without charge step,
   `override_raw_limits={"current_hard": 0.0}`; thread-safety smoke (two
   schemas, parallel `make_step_table` via `ThreadPoolExecutor`).
2. `tests/test_benchmarks.py` — `pytest-benchmark` (new dev dep):
   `make_step_table` + `make_summary` on Arbin fixture + small fixture;
   `@pytest.mark.benchmark`, excluded from default run via addopts
   (`-m "not benchmark"`); run manually: `uv run pytest -m benchmark`.

## Files to touch

- `pyproject.toml` — deps, build-system, metadata, ruff config, addopts, dev dep
- `uv.lock` — regenerated
- `scratch.db`, `tmp/` — deleted; `.gitignore` — updated
- `.github/workflows/simpletest.yml` — ruff step
- `src/cellpycore/__init__.py` — public API + `__version__`
- `src/cellpycore/py.typed` — new marker
- `src/cellpycore/summarizers.py` — A3, A5, logger, guards
- `src/cellpycore/cell_core.py` — A6, A4
- `src/cellpycore/settings_base.py`, `src/cellpycore/units.py` — logger only
- `tests/test_e2e.py`, `tests/test_benchmarks.py` — new
- `tests/test_limits.py` — adjust for frozen `DEFAULT_RAW_LIMITS`
- `README.md`, `.issueflows/04-designs-and-guides/this-project.md` — docs

## Test strategy

- Full suite: `uv run pytest` (must stay green after every phase; golden tests
  are the parity gate).
- New: A3 regression (`0.0` override), guard tests (`NoDataFound`,
  missing-column `ValueError`), native e2e, thread-safety smoke.
- Benchmarks opt-in: `uv run pytest -m benchmark` (not in CI).
- Lint locally before push: `uv run ruff check` + `uv run ruff format --check`.

## Open questions

- None — resolved via grilling 2026-07-03 (scope split, minimal public API,
  native-path e2e, pytest-benchmark opt-in, no structural refactor).

## Follow-ups (filed as GitHub issues, not this issue)

- [#67](https://github.com/cellpy/cellpy-core/issues/67) — D3: selectors module
  decision (port vs bridge-only).
- [#68](https://github.com/cellpy/cellpy-core/issues/68) — D4/A2: units
  fallback → explicit values or `metadata.CellMeta`.
- [#69](https://github.com/cellpy/cellpy-core/issues/69) — CI coverage
  reporting.
- [#70](https://github.com/cellpy/cellpy-core/issues/70) — B1/B2 design pass
  (schema-agnostic stat columns; cycle_mode polarity default).
