# Plan — Issue #54: Native exclude-types summary support

## Goal

Add native exclude-types summary support to the polars engine: `summarizers.make_summary(..., exclude_step_types=["cv_"])` subtracts the excluded steps' per-cycle deltas from the cycle-end summary values, replacing the capability lost when `create_selector` / `summary_selector_exluder` were removed (issue #45).

## Constraints

- KISS: concrete kwarg first, no `SummaryAdjuster` protocol yet (issue explicitly defers it until a second variant appears).
- `exclude_step_types=None` (default) must be **byte-identical** to today's summary — no join, no extra columns, golden fixtures untouched.
- Engine stays schema-injected, polars-native, thread-safe; no module-level state.
- cellpy-side wiring (`selector_type` → this kwarg) is a follow-up in the cellpy repo, out of scope here (per migration guide: core PR first).
- Google-style docstrings.

### Prior art

- **Oracle:** removed pandas `summary_selector_exluder` recovered from `git show 2da165e^:src/cellpycore/selectors.py`. Math: filter steps whose `step_type` starts with any excluded prefix; per step compute `last - first` for current, voltage, charge, discharge; group by cycle, sum; left-merge onto selected cycle-end raw rows, `fillna(0.0)`, subtract.
- **Deviations to document:** (1) old code also corrected current and voltage on the raw rows — the native summary's base subset carries only capacities (end potentials come from step-table joins), so the native correction targets `charge_capacity` / `discharge_capacity` only; (2) old `exclude_steps` matched step *numbers* against the step **type** column (`steps[t_st_txt].isin(exclude_steps)`) — a latent bug; we do not port `exclude_steps` at all; (3) old `create_selector` mapped `"non-rest"` → prefix `"rest_"` which never matched label `"rest"` — mapping strings stay in cellpy's follow-up, core takes explicit prefixes.
- **Siblings/conventions to mirror:** `_group_keys` / `use_tid` composite-key handling and `join ... how="left"` + `fill_null` pattern already used by `_add_end_potentials`, `c_rates_to_summary`, `ir_to_summary` in [summarizers.py](../../src/cellpycore/summarizers.py). Step table provides `charge_capacity_first/_last`, `discharge_capacity_first/_last` stat columns (native names). Do **not** reuse `_delta_expr` (it is percent-based); the correction needs plain `last - first`.
- Toolbox `.issueflows/00-tools/`: empty — nothing to reuse.
- Graph: Community 50 (`make_summary`, `_group_keys`, `_add_end_potentials`) and 53 (step table) confirm the touch points; no surprises.

## Approach

1. **`summarizers.make_summary`** gains `exclude_step_types: Optional[Sequence[str]] = None`.
   - When `None`: current code path, untouched.
   - Else, right after the base `summary = selected.select(...)` and **before** the CE / coulombic-difference / loss / cumulated `with_columns` (so every derived column reflects corrected capacities, mirroring the oracle which corrected raw rows before summary derivation):
     - Filter steps: `pl.any_horizontal(pl.col(shdr.step_type).str.starts_with(p) for p in exclude_step_types)`.
     - Aggregate per `(test_id?, cycle)` (via `_group_keys`): `(charge_capacity_last - charge_capacity_first).sum()` and same for discharge, into temp `__excl_charge` / `__excl_discharge` columns.
     - Left-join onto summary (same `use_tid` join-key logic as `_add_end_potentials`), `fill_null(0.0)` (oracle's `replace_nan=True`), subtract from `chdr.charge_capacity` / `chdr.discharge_capacity`, drop temp columns.
2. **`CellpyCellCore.make_core_summary`** in [cell_core.py](../../src/cellpycore/cell_core.py) gains the same kwarg and passes it through (native entry point). Legacy bridge `OldCellpyCellCore` untouched for now — see open questions.
3. Docstrings updated; short note added to `.issueflows/04-designs-and-guides/selector-dead-code-deferral.md` marking #54 resolved once merged (done at close, not plan).

## Files to touch

- `src/cellpycore/summarizers.py` — new kwarg + correction block in `make_summary` (~30 lines).
- `src/cellpycore/cell_core.py` — pass-through kwarg on `CellpyCellCore.make_core_summary`.
- `tests/test_schema.py` (or new `tests/test_exclude_types.py` if cleaner) — new tests, see below.

## Test strategy

Command: `uv run pytest` (project venv).

- **Parity vs oracle:** synthetic native-named raw with CV steps (extend the `_build_cumulative_raw`-style builders; golden Arbin fixture has *no* CV steps, so it can't drive parity). Inline a small pandas oracle in the test file — the resurrected `summary_selector_exluder` math ported to native column names, capacities only — and assert the native `exclude_step_types=["cv_"]` summary capacities match.
- **Guard:** `exclude_step_types=None` output equals current summary frame exactly (and existing golden tests `test_golden.py` stay green).
- **Edge:** cycle without any excluded step gets zero correction (fill_null path); merged two-test frame keeps corrections isolated per `test_id` (reuse `_build_merged_raw` pattern).
- **`only-cv` analogue:** `exclude_step_types=["charge", "discharge"]` excludes the plain `charge` / `discharge` steps but keeps `cv_charge` / `cv_discharge` (neither starts with those prefixes) — a test locks this `startswith` semantics, matching the oracle.

## Open questions

1. **Legacy bridge:** should `OldCellpyCellCore.make_core_summary` also accept/forward `exclude_step_types` now (making cellpy's follow-up wiring trivial), or stay untouched until the cellpy-side issue? Recommendation: add the pass-through now — it is ~3 lines and the bridge is the path cellpy actually calls.
2. **Correction scope:** confirm capacities-only is acceptable (old code also adjusted the raw current/voltage of the selected row; those adjusted values fed nothing that survives in the native summary). Recommendation: capacities only, documented.
3. Branch: create `54-exclude-types-summary` off up-to-date `main` at `/iflow-start`.
