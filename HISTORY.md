# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

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
