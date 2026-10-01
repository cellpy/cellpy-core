# Plan — Issue #359: cycle counter for discharge-first full cells

Upstream: [jepegit/cellpy#359](https://github.com/jepegit/cellpy/issues/359) (Stage 5 S3,
`to core`). Provisional local number `359`; rename the group when the `cellpy-core`
mirror issue exists (see "Mirror issue (to create)" at the end).

## Goal

Give cellpy-core an explicit, opt-in way to repair a cycler's cycle counter so that every
cycle opens with a chosen direction (charge for full/cathode cells, discharge for anode
half-cells), with a lone leading step of the other direction kept as its own first cycle.
Raw cycle-cumulative capacities/energies, the step table and the summary must all follow
the new cycle boundaries, so coulombic efficiency and curve extraction pair the right
half-cycles.

## Constraints

- Core-first, additive, default behaviour unchanged: nothing is renumbered unless the
  caller asks. Golden parquet fixtures and e2e tests stay byte-identical.
- `TestMode` stays binary (polarity only; `config.py` docstring). Cycle *ordering* is a
  separate concern and must not be folded into `TestMode`.
- Harmonized raw mandates cycle-cumulative capacity (`docs/specifications/harmonized-raw.md`
  §Capacity convention); the raw spec already lists "do we need an updated cycle number?"
  as an open question for `cycle_num` — this issue answers it with a post-processing step,
  not a new raw column.
- Metadata boundary: the engine must not require populated metadata (`cellpy-core-migration.md`).
  `cycle_mode` on `meta_test_dependent` is read, never required.
- Polars-native; accept pandas in / pandas out like `normalize_capacity_granularity`.
- Per-step stat column names are a fixed contract — no new step columns needed here.
- KISS: one public function, one shared private helper, one test module, one design note.

### Prior art

- `summarizers.normalize_capacity_granularity` — reconstructs per-row increments inside a
  source reset group and re-accumulates over `(test_id, cycle_num)`. Exactly the math a
  renumbering needs (source = *old* cycle keys, target = *new* cycle keys). **Migrate** the
  two-pass body into a shared private helper and call it from both.
- `summarizers._ensure_test_id`, `_group_keys`, `_CUMULATIVE_ATTRS` — reuse as-is.
- `make_step_table` — classification depends on current/potential stats only, never on
  `cycle_num`, so rebuilding steps after renumbering re-derives identical step types.
- `make_summary(test_mode=...)` — CE direction already keyed on `TestMode`; untouched.
- `merge.update_data` — incremental append keyed on cycler cycle numbers. Coexist: renumber
  is a post-processing step a consumer applies after the raw is complete (documented
  limitation; no change to merge).
- Toolbox `.issueflows/00-tools/` — empty. Graph report stale (2026-07); grep used.

## Approach

### Public API

```python
def renumber_cycles(
    data: Data,
    schema: Optional[Schema] = None,
    opening: StepDirection = StepDirection.CHARGE,   # or test_mode -> derive
    **step_table_kwargs,
) -> Data
```

- Lives in `summarizers.py` next to `normalize_capacity_granularity`; exported from
  `cellpycore/__init__.py`.
- `opening` says which direction starts a cycle. Default charge (matches `TestMode.NORMAL`).
  Anode half-cells pass `discharge`. Implementation: a tiny `StrEnum` in `config.py`
  (`StepDirection.CHARGE / DISCHARGE`) so the value is validated, mirroring the existing
  enums. Convenience: `opening=None` -> derive from `TestMode` passed as keyword
  (`test_mode=TestMode.INVERTED` -> discharge). Keep only one of these two knobs if it
  feels like two ways to say the same thing — see Open questions.
- Requires `data.raw` and a classified `data.steps` (`NoDataFound` otherwise). Raises
  `ValueError` if the step table carries `ustep` rows (ambiguous raw mapping) or if a
  `(test_id, cycle, step)` key is not unique.

### Algorithm (polars, per `test_id`)

1. Sort steps by `test_id`, `test_time_first` (fallback `datapoint_num_first`).
2. Direction per step from `step_type`: charge-ish = `charge, cv_charge, taper_charge,
   charge_cv`; discharge-ish = `discharge, cv_discharge, taper_discharge, discharge_cv`;
   everything else (`rest, ir, ocvrlx_*, not_known, ""`) is neutral and attaches to the
   current cycle.
3. `prev` = forward-filled last non-neutral direction *before* this step (`shift(1)` over
   `test_id` on the forward-filled series). New cycle boundary iff
   `dir == opening and prev == closing`. First step of a test is never a boundary, so a
   lone leading discharge becomes cycle 1 on its own.
4. `new_cycle = base + cum_sum(boundary)` over `test_id`, with `base` = the test's original
   first `cycle_num` (keeps 0- vs 1-based numbering of the source).
5. Build the mapping `(test_id, old_cycle, step_num) -> new_cycle`; join onto raw. Raw rows
   with no step row (e.g. `skip_steps`) forward-fill the new cycle in datapoint order,
   remaining nulls keep the old value.
6. Re-accumulate `_CUMULATIVE_ATTRS` columns via the shared helper: increments over
   `(test_id, old_cycle)`, cum_sum over `(test_id, new_cycle)`. Identity wherever the
   boundaries did not move, so an already-correct file is a no-op (test for it).
7. Replace raw `cycle_num`, drop helper columns, restore frame type (pandas/polars).
8. Rebuild steps with `make_step_table(data, schema=schema, **step_table_kwargs)` so the
   per-step cumulative-capacity stats follow the new boundaries (deltas are invariant, but
   `*_first/last/avg/...` of cumulative columns are not). Classification is unchanged by
   construction.
9. `data.summary = None` and log at info that the summary must be rebuilt
   (`make_summary(...)`); the function does not know the caller's `test_mode` /
   `exclude_step_types`.

Expected outcomes (charge opening):

- cycler `[D][C D][C D]` -> unchanged (no-op).
- cycler `[D C D][C D]`   -> `[D][C D][C D]`.
- cycler `[D C][D C][D C]` -> `[D][C D][C D][C]`.

Cycle 1 (lone discharge) gets `CE = discharge/0 = inf` under `NORMAL`; left as-is and
documented — CE math is out of scope.

### cellpy wiring (not in this PR, recorded for the design note)

cellpy adds a `cycle_mode` variant (e.g. `"full_cell_discharge_first"`) that maps to
`TestMode.NORMAL` + `renumber_cycles(opening="charge")` after the step table is built. This
is owner "Solution 1" at the cellpy layer backed by owner "Solution 2" (explicit control)
at the core layer. Convention delta -> release note + comparator exception on the cellpy
side (stage5 §S3).

## Files to touch

- `src/cellpycore/config.py` — add `StepDirection` StrEnum (CHARGE / DISCHARGE) with
  Google-style docstring.
- `src/cellpycore/summarizers.py` — extract `_reaccumulate_cumulative(raw, cols,
  source_keys, target_keys)` from `normalize_capacity_granularity`; add
  `_step_direction_expr(shdr)` and public `renumber_cycles(...)`.
- `src/cellpycore/__init__.py` — export `renumber_cycles` (and `StepDirection`), extend
  `__all__` and module docstring.
- `tests/test_renumber_cycles.py` — new (see Test strategy).
- `docs/specifications/harmonized-raw.md` — resolve the `cycle_num` open question with a
  one-line pointer to `renumber_cycles`.
- `docs/user-guide/` (or `docs/api/public.md`) — short "repairing the cycle counter"
  section with the three patterns above.
- `.issueflows/04-designs-and-guides/cycle-renumbering.md` — new design note (context,
  decision, alternatives: new `TestMode` member / kwarg on `make_summary` / raw column;
  cellpy wiring; limitations: usteps, incremental `update_data`).
- `docs/changelog.md` — entry at close (feature -> `uv version --bump minor`, `0.2.6` ->
  `0.3.0`, decided at `/iflow-close`).

## Test strategy

Command: `uv run pytest` plus `uv run ruff check && uv run ruff format --check`.

New `tests/test_renumber_cycles.py` with a small synthetic-raw builder (same style as
`tests/test_exclude_types.py::_build_cv_raw`; override step types via
`override_step_types` so classification is deterministic):

- no-op on an already charge-first file (raw, steps, summary unchanged).
- `[D C D][C D]` -> `[D][C D][C D]`; per-cycle `charge_capacity` / `discharge_capacity`
  in `make_summary` equal the hand-computed per-half-cycle totals.
- `[D C][D C][D C]` -> four cycles, trailing lone charge kept.
- rest / ir steps attach to the current cycle; CC + CV charge stay in one cycle.
- `opening=DISCHARGE` (anode) mirrors the above with roles swapped.
- two `test_id`s in one frame are renumbered independently (base per test preserved).
- pandas in -> pandas out.
- `ustep` step table -> `ValueError`; missing steps -> `NoDataFound`.
- regression: `renumber_cycles` on the harmonized/golden fixture (if present) leaves raw
  byte-identical and `normalize_capacity_granularity` still passes its existing tests
  after the helper extraction.

## Open questions

1. **Mirror issue number** — I cannot create issues with this token. Please create the
   `cellpy/cellpy-core` issue (body below) and tell me the number; I rename the
   `.issueflows` group and reference it in commits/PR. Until then everything is tracked
   as `359`.
2. **Name**: `renumber_cycles` (recommended; verb is unambiguous) vs the issue's
   `update_cycle_counter`.
3. **Knob**: `opening: StepDirection` only (recommended; one knob) vs also accepting
   `test_mode: TestMode` and deriving it. cellpy can do the derivation in its thin surface.
4. **Numbering base**: keep the source's first cycle number per test (recommended) vs
   always restart at 1.
5. **`CellpyCellCore.renumber_core_cycles(...)` wrapper**: skip for now (recommended,
   YAGNI; cellpy calls the function) vs add a 10-line passthrough like `make_core_summary`.

## Mirror issue (to create)

Title: `Cycle counter for discharge-first full cells (cellpy#359 / Stage 5 S3)` — label
`enhancement`. Body:

> Mirrors [jepegit/cellpy#359](https://github.com/jepegit/cellpy/issues/359) (Stage 5, S3 — labelled `to core`).
>
> **Problem.** Commercial / full cells are often tested starting with a discharge (cycle 1 = discharge only), followed by charge–discharge cycles. Cyclers then assign an "erroneous" cycle counter: either cycle 1 becomes discharge–charge–discharge, or every cycle ends up discharge–charge. Downstream, coulombic efficiency (charge/discharge for full cells) and charge/discharge curve extraction pair the wrong half-cycles.
>
> **Current state in core.** `cycle_index` is taken as-is from the harmonized raw frame; core never renumbers cycles. Polarity is handled only via `TestMode` (`NORMAL` / `INVERTED`, from legacy `cycle_mode`) in `cell_core.py`, `curves.py` and `summarizers.py`. There is no notion of "discharge-first" ordering within a cycle.
>
> **Scope (core-first; cellpy gets a thin surface later).**
> - Add an explicit `renumber_cycles(...)` post-processing step that renumbers `cycle_num` so each cycle opens with a chosen direction (charge for full/cathode cells, discharge for anode half-cells), keeping a leading lone step of the other direction as its own cycle. Raw cycle-cumulative capacities/energies, the step table and the summary follow the new boundaries.
> - Additive only; default behaviour unchanged (cycler counter kept). Golden/e2e fixtures stay green.
> - Tests: synthetic raw frames with discharge-first patterns (lone first discharge; all-cycles discharge–charge), plus a design note under `.issueflows/04-designs-and-guides/` since this is a user-visible convention change (release note needed in cellpy).
>
> **Out of scope.** cellpy-side `cycle_mode` plumbing / CLI; S1 (#313) and S2 (#312).
