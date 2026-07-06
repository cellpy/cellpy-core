# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

- Fix `SyntaxWarning` from `return` in `finally` block in `legacy/mock_core.py` on Python 3.14+ import. (#95)

## [0.1.4] - 2026-07-04

- Migrate documentation to Zensical with Read the Docs hosting
  (`.readthedocs.yaml`, `zensical.toml`, optional `docs` dependency group).
  Restructure the docs tree (`getting-started`, `user-guide/`, `specifications/`,
  `examples/`, `development/`); `changelog.md` and `development/roadmap.md`
  snippet-include root `HISTORY.md` and `ROADMAP.md`. Add executable example
  notebooks with committed markdown and plot outputs under `docs/examples/`. (#90)
- Backfill `HISTORY.md` for the 0.1.3 release and bump to 0.1.4. (#91)

## [0.1.3] - 2026-07-04

- Add in-repo pre-commit hooks (`ruff check --fix`, `ruff format`) via
  `.pre-commit-config.yaml` and document one-time `uv run pre-commit install`
  setup. (#84)
- Add `merge_data` and `update_data` for combining processed `Data` objects and
  incrementally appending new raw rows (with `CellpyCellCore` wrappers and tests).
  (#86)
- Add merge/update end-to-end test coverage for the public merge and incremental
  update pipeline. (#89)
- Move `CellpyError` / `NoDataFound` from `legacy/` to top-level
  `cellpycore.exceptions` (legacy re-export kept); expand the `CellpyCellCore`
  class docstring; add `ROADMAP.md` for planned features and open design
  questions. (#82)
- Reorganise legacy bridge, units, and test mock helpers into dedicated
  subpackages (`legacy/`, `units/`, `testing/`): split implementation into
  focused modules, update importers, and remove the old top-level modules. (#77)
- Add pytest coverage reporting to CI: `pytest-cov` in the dev group,
  `[tool.coverage.run]` config, and `--cov=cellpycore` in the test workflow. (#69)
- Document the per-step `<signal>_<stat>` engine contract (B1) and default unset
  `cycle_mode` to NORMAL via `_cycle_mode_to_test_mode`, so initialized and
  uninitialized `CellpyCellCore` share the same polarity unless `"anode"` is set
  explicitly. (#70)
- Fix units fallback so `get_converter_to_specific` and
  `nominal_capacity_as_absolute` accept explicit values or `CellMeta` instead of
  crashing on bare `Data`; thread optional `cell_meta` through
  `add_scaled_summary_columns`. (#68)
- Move broken `selectors.py` helpers to bridge-only `legacy_selectors.py` with
  `legacy_schema()` default and unit + golden tests. (#67)
- Rename test-data fixture prefix from vendor-specific `arbin` to generic `cycler`
  (files, tests, regen scripts, harmonized `source_type`, and docs). (#72)
- Code-review cleanup and test completion (#66): drop unused dependencies
  (duckdb, duckdb-engine, sqlalchemy, narwhals) and the unconfigured
  uv-dynamic-versioning; fix the falsy-override bug so an explicit `0.0` in
  `override_raw_limits` wins; freeze `DEFAULT_RAW_LIMITS` and build fresh
  limits per call (thread safety); remove the dead `Data.cycle`/`Data.step`
  fields and the dead `find_end_voltage`/`select_columns` params on the native
  `make_core_summary`; declare the public API in `cellpycore/__init__.py`
  (curated exports + `__version__`) with a `py.typed` marker; validate engine
  inputs (`NoDataFound` / missing-column `ValueError`) at `make_step_table` /
  `make_summary`; add ruff lint to CI, native-path e2e tests via the public
  API, and an opt-in pytest-benchmark suite (`uv run pytest -m benchmark`).
- Update the README developer section to uv's project workflow: `uv sync` after
  cloning, `uv add` for new dependencies, `uv run pytest` for tests (#64).
- Use absolute GitHub URLs for README documentation links so they resolve on PyPI.
  (#62)

## [0.1.2] - 2026-07-02

- Add `summarizers.normalize_capacity_granularity` + `config.ResetGranularity`
  (`CYCLE`/`STEP`/`TEST`) to normalize step-cumulative or test-cumulative raw capacity /
  energy columns to the mandated cycle-cumulative convention before aggregation; a
  cycle-cumulative input is an exact no-op so the exercised path stays byte-stable (#42).
- Add `test_id` to `StepCols`/`CycleCols` and key all per-step/per-cycle aggregation,
  cumulation, and joins on the composite `(test_id, cycle_num, step_num, …)` so a
  merged `Data` holding many tests never mixes cycles across tests (default `test_id=0`
  for a single unmerged test; single-test goldens stay byte-identical) (#41).
- Promote `CellpyUnits` into `cellpycore.units` (first-class unit-spec module) with a
  `legacy.py` re-export, plus converter-parity and pint-optional guard tests (STEP-12, #40).
- Add native `ref_potential` (reference-electrode potential) to `RawCols` with the full
  `StepCols` aggregate set, wired through the polars step engine (aggregated when
  present, skipped when absent); legacy `reference_voltage` stays unbridged to preserve
  the legacy step-frame parity (#43).
- Add a PyPI release workflow (`.github/workflows/release.yml`: release publish → ruff +
  pytest → `uv build` → trusted PyPI publish) and fix the ruff F401 failure that blocked
  the `v0.1.0` release CI (#44).
- Remove the superseded pandas selector pair (`selectors.create_selector` /
  `selectors.summary_selector_exluder`) and the never-used `selector` parameter on both
  `make_core_summary` signatures, now that cellpy has migrated off them; the exclude-types
  summary feature they carried is tracked for native reimplementation in #54 (#45).
- Establish and verify the release/PyPI pipeline end-to-end (`release` alias +
  `release.yml` trusted publishing; `cellpycore` 0.1.1 live on PyPI), document the
  procedure and the cellpy re-pin checklist in
  `.issueflows/04-designs-and-guides/release-procedure.md`, and re-pin cellpy from
  `git+…@main` to the PyPI release (jepegit/cellpy#400) (#44).
- Add a validating front door for raw frames: `Data.from_raw_frame(df, validate=True)`
  plus module-level `validate_raw_frame` check a native polars frame against
  `config.RawCols` (required columns, `epoch_time_utc` int64-ns UTC contract, integer
  datapoint/cycle/step numbers) and fail fast with one actionable error;
  `validate=False` skips all checks (#55).
- Add native exclude-types summary support: `summarizers.make_summary(exclude_step_types=[...])`
  subtracts the excluded steps' per-cycle capacity deltas from the cycle-end summary values
  before any derived column (prefix match on step type, e.g. `["cv_"]` for a non-CV summary),
  forwarded by both `make_core_summary` signatures — natively replacing the exclusion feature
  lost with the removed pandas selector pair; parity locked by a pandas-oracle test (#54).
- Document standalone use of cellpy-core: new slim-consumer guide
  (`docs/standalone-use.md`) covering the native `CellpyCellCore` +
  `Data.from_raw_frame` pipeline, the class-free `summarizers` alternative, and the
  caller contract; linked from the README together with a fixed PyPI install note (#56).
