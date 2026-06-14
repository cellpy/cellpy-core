# Plan for issue #13: Migrate the step/summary compute engine to polars (native schema)

## Goal

Replace the pandas + legacy-schema compute engine (`make_step_table` **and** the summary
path in `summarizers.py` / `selectors.py`) with a **polars-native** engine that operates on
the native `config` schema, while keeping the `cellpy` integration seam
(`OldCellpyCellCore`) byte-stable against the golden oracle in `tests/test_golden.py`.

## Constraints

- **KISS / scope:** this is large. Plan proposes a **phased split** (see Approach) and asks
  the user before implementing past Phase 1.
- **Golden oracle stays green.** `tests/test_golden.py` pins the engine against cellpy's
  published numbers (103 steps / 18 cycles / cyc-1 `data_point` 1457) plus a frozen
  step-table snapshot (`tests/data/arbin_cc_steps_expected.parquet`). Any intentional change
  to step-table output must be a deliberate snapshot regen, not an accident.
- **Legacy headers must not drift.** `legacy.HeadersNormal/Summary/StepTable` are verbatim
  mirrors of cellpy's `internal_settings` and are contract-tested (jepegit/cellpy#378). They
  keep their `*_txt` / `type` / `rate_avr` attribute names and values.
- **Schema-agnostic + thread-safe** engine design (per `config.Schema`, injected per cell)
  is preserved.
- **Units by value** — the engine takes precomputed conversion factors / `nom_cap` /
  `raw_limits` as arguments; no pint in the engine.
- `requires-python >=3.13`; deps already include `polars>=1.29`, `narwhals>=1.38`, `pandas`.
- Project rule: run via `uv run` (`uv run pytest`).

### Prior art

- `summarizers.make_step_table` (`cellpycore.summarizers`) — pandas `groupby().agg([...])`
  on raw, reads schema attrs **by legacy names** (`schema.raw.data_point_txt`,
  `schema.step.type`, `schema.step.rate_avr`, …); emits flattened `<col>_<stat>` columns +
  `type`/`sub_type`/`info`/`rate_avr`. New work: re-implement in polars; decide vocabulary
  (see Open questions).
- Summary path `summarizers.{generate_absolute_summary_columns, end_voltage_to_summary,
  c_rates_to_summary, ir_to_summary, equivalent_cycles_to_summary,
  generate_specific_summary_columns}` + `selectors.{create_selector,
  summary_selector_exluder, get_step_numbers, get_cycle_numbers, get_rates}` — all pandas,
  read legacy schema attrs, operate on `data.raw` / `data.summary` / `data.steps`. New work:
  migrate together (avoid split engine).
- `config.RawCols/StepCols/CycleCols` (`cellpycore.config`) — native names (`potential`,
  `charge_capacity`, `step_type`, `_mean`). Missing raw inputs the engine needs (`step_time`,
  `internal_resistance`, `ref_voltage`, plain non-cumulative capacity). New work: extend
  (Phase 1).
- `CellpyCellCore.schema` / `make_core_step_table` / `make_core_summary`
  (`cellpycore.cell_core`) — the seam that injects the schema and calls the engine. The
  bridge work lands here.
- `tests/test_schema.py`, `tests/test_golden.py` — current behavior pins. Mirror their
  intent for the native path.
- None found for an existing polars step engine in-repo (grep checked) — greenfield rewrite.

## Approach

**Decision pending (Open question 1) on engine vocabulary** — the rest assumes the
recommended option **A** (engine targets native schema; `OldCellpyCellCore` bridges
legacy↔native + pandas↔polars at the seam). Phasing:

**Phase 1 — Extend the native schema (low-risk, unblocks 2 & 3).**
- Add to `config.RawCols` the inputs the engine consumes: `step_time`,
  `internal_resistance`, `ref_voltage`, and a single **cumulative capacity** signal per
  direction (see Capacity finding below). Decide spec stance (Open question 3).

  **Capacity finding (from the real Arbin fixture, verified):** legacy raw
  `charge_capacity` / `discharge_capacity` are **cycle-cumulative, per direction** — they
  accumulate across a cycle's steps for their direction and reset to 0 at each cycle
  boundary. They are *not* per-step. The harmonized spec's `step_cumulative_charge_capacity`
  name is therefore misleading relative to the data. **Per-step** capacity is *derived* by
  the engine (delta = last−first within a step group); **per-cycle** capacity is the
  cycle-end value. So native raw carries one cumulative-capacity column per direction (=
  legacy `charge_capacity`), and the engine computes per-step / per-cycle from it.
- Confirm `config.StepCols` already covers the full output set (it lists
  energy/power stats); add any legacy-equivalent extras the engine produces that have no
  native home (`rate_avr`→? , `step_type`/`sub_step_type` exist; `info`/`ustep`→ decide).
- Tests: extend `tests/test_config_columns.py`.

**Phase 2 — Polars-native `make_step_table` + bridge.**
- Re-implement `make_step_table` in polars: `group_by([cycle, step, sub_step])` →
  `agg(mean/std/min/max/first/last/delta)`; C-rate; step-type classification masks; emit full
  native `StepCols`, null for absent signals (energy/power/IR when raw lacks them).
- Bridge in `OldCellpyCellCore.make_core_step_table`: pandas(legacy)→polars(native) in,
  run native engine, polars(native)→pandas(legacy) out (rename to legacy columns, restore
  the pandas index/duplicate-column behavior cellpy expects).
- Fix the tiny-fixture blank-`type` edge case (design note calls for it).
- Tests: port `tests/test_schema.py` step assertions to native; keep `tests/test_golden.py`
  green through the bridge (regen snapshot only if a change is intended & approved).

**Phase 3 — Polars-native summary path (`summarizers` summary fns + `selectors`).**
- Migrate `generate_absolute_summary_columns`, `end_voltage_to_summary`,
  `c_rates_to_summary`, `ir_to_summary`, `equivalent_cycles_to_summary`,
  `generate_specific_summary_columns`, and all of `selectors.py` to polars-native.
- Bridge `make_core_summary` / `add_scaled_summary_columns` the same way.

**Phase 4 — Cross-repo parity tests.**
- Parity vs cellpy's `make_step_table` / `make_summary` (the golden parquets are already the
  oracle; extend with summary goldens if needed). Coordinate with jepegit/cellpy#377/#378.

## Files to touch

- `src/cellpycore/config.py` — extend `RawCols` (+ maybe `StepCols`) (Phase 1).
- `docs/data_format_specifications/harmonized_raw.md` — only if we amend the spec (Open q 3).
- `src/cellpycore/summarizers.py` — polars rewrite (Phases 2–3).
- `src/cellpycore/selectors.py` — polars rewrite (Phase 3).
- `src/cellpycore/cell_core.py` — legacy↔native + pandas↔polars bridge in
  `OldCellpyCellCore` / `make_core_*` (Phases 2–3).
- `tests/test_config_columns.py`, `tests/test_schema.py`, `tests/test_golden.py`,
  plus new native/parity tests (all phases).
- Possibly update `.issueflows/04-designs-and-guides/step-table-polars-migration.md` with the
  final vocabulary decision.

## Test strategy

- Re-run `uv run pytest` after each phase; the golden suite is the regression gate.
- New: native-schema step/summary tests mirroring `test_schema.py`; parity tests (Phase 4).
- Snapshot regen (`dev/regenerate_test_data.py`) only on intentional, approved output change.

## Open questions

1. **Engine vocabulary (pivotal).** (A) Engine targets the **native** schema; bridge
   legacy↔native in `OldCellpyCellCore` (recommended; matches the design doc's "extend native
   schema then rewrite"). vs (B) keep the engine reading whatever attr names are injected and
   add native aliases so current legacy attr names resolve on native too (less rewrite, but
   muddies the native schema). Which one?
2. **polars vs narwhals.** Issue says "polars-native"; repo also ships `narwhals`. Pure
   polars in the engine, or narwhals for dataframe-agnosticism? (Recommend pure polars per the
   issue title.)
3. **RawCols vs the authoritative spec (capacity naming).** Verified finding above: legacy
   raw capacity is **cycle-cumulative per direction**, so the spec's
   `step_cumulative_charge_capacity` / `step_cumulative_discharge_capacity` names are
   misleading. Resolution options for the native raw capacity column:
   - **(3a, recommended)** Rename the spec columns to `cumulative_charge_capacity` /
     `cumulative_discharge_capacity` (drop the misleading `step_`), map the bridge
     legacy `charge_capacity` ↔ native `cumulative_charge_capacity`, and have the engine
     derive per-step (delta) and per-cycle (cycle-end) capacities. Amends
     `harmonized_raw.md`.
   - **(3b)** Leave the spec names as-is and just map legacy `charge_capacity` ↔ native
     `step_cumulative_charge_capacity` in the bridge (no doc change, but the name stays
     misleading).
   Also still needed in raw: `step_time`, `internal_resistance`, `ref_voltage` — add as
   optional input columns (derive `step_time` from `test_time` per step if a cycler omits it;
   IR/ref_voltage null when absent). Confirm spec stance.
4. **Scope / sequencing.** OK to land this as **separate PRs per phase** (1→4), or do you
   want it as one branch? (Recommend phased PRs; Phase 1 is safe to start immediately.)
5. **Bridge return contract.** Confirm the seam must keep returning **pandas + legacy
   column names** (so cellpy and the golden tests are unaffected), with the native polars path
   used internally only.
```
