# Column headers — review, decisions, and gaps

Durable record from issue #10 ("Make sure column headers make sense"). This is project memory: it captures *why* the column-header docs look the way they do after the issue-#10 cleanup, what is deliberately deferred, and where the next worker should pick up.

Scope of issue #10 was **docs-only**. The `src/cellpycore/config.py` header classes were intentionally **not** changed; the config-vs-doc drift is recorded here as the starting point for a follow-up code issue.

## Where column headers live (the three layers)

1. **Spec docs** (`docs/`) — the human-facing definitions. After issue #10:
   - `docs/harmonized_raw_definition.md` — **authoritative** harmonized-raw spec (single source of truth).
   - `docs/data_format_specifications/cycle_table.md`, `step_table.md` — cycle/step table specs.
   - `docs/data-object-definition.md` — the minimal input contract.
   - (`docs/data_format_specifications/harmonized_raw.md` was **deleted** as a stale duplicate.)
2. **New config classes** (`src/cellpycore/config.py`) — `RawCols`, `StepCols`, `CycleCols`, dataclasses of `name: str = "name"` with dot + bracket access and a `__version__`. **These are DRAFT and not yet wired into the processing engine.** Only `_helpers.py` (synthetic-data `make_raw`) reads `RawCols`.
3. **Legacy headers** (`src/cellpycore/legacy.py`, `*_txt`) — old-cellpy names (`current_txt`, `sub_step_index_txt`, ...). **The live engine (`selectors.py`, `summarizers.py`) still consumes these, not the new `Cols` classes.**

The key structural fact: docs ↔ `config.py` ↔ engine are three out-of-sync representations. Issue #10 aligned the **docs** and made them internally consistent; aligning `config.py` and then the engine is future work.

## Decisions taken in issue #10 (confirmed with the maintainer)

1. **Scope = docs-only.** No `config.py` edits in this issue.
2. **Signal naming = `potential`** (not `voltage`), and **`test_time` is in seconds** (not milliseconds). `data-object-definition.md` was reconciled to match.
3. **`channel_status` is dropped**; the cycler step mode column is **`step_mode`** (not `mode`).
4. **`harmonized_raw.md` (2025-09-08) deleted**; `harmonized_raw_definition.md` (2025-09-17) is the single source of truth.
5. **Header metadata + versioning (SPEED-30) deferred** — documented as a recommendation, not implemented.
6. **Strategy alignment = document gaps only** — no concrete UUID/BattINFO columns added now.

## Findings (gap analysis)

### A. Duplicated / conflicting harmonized-raw specs — RESOLVED
Two specs disagreed. The newer one (richer: `mask`, `source_step_num`, `step_mode`, `cycle_type`, step cumulative energy/power, `aux_*` scheme) is now authoritative; the older one was deleted.

### B. config.py ↔ doc drift — DEFERRED (follow-up issue)
`RawCols` currently mirrors the *old* doc and is out of step with the authoritative spec. To bring `config.py` `RawCols` in line, a follow-up should:
- **Add**: `mask`, `source_step_num`, `step_mode`, `cycle_type`, `step_cumulative_charge_energy`, `step_cumulative_discharge_energy`, `step_charge_power`, `step_discharge_power`, and the `aux_*` columns (`aux_temperature_cell`, `aux_temperature_chamber`, `aux_pressure_cell`, plus the extensible `aux_<quantity>_<name>` scheme).
- **Remove**: `channel_status`; **rename** `mode` → `step_mode`.
- **Rename** the non-aux `temperature_cell` / `temperature_chamber` / `pressure` to the `aux_*` form to match the spec.
- Update the only consumer, `_helpers.py::make_raw`, accordingly (low blast radius — it builds synthetic frames).

### C. Naming / unit inconsistencies — PARTLY RESOLVED
- `voltage` vs `potential` → standardized on **`potential`** (docs reconciled).
- `test_time` ms vs s → standardized on **seconds** (docs reconciled).
- `voltage_efficiency` unit typo (`percetange (V)`) in `cycle_table.md` → fixed to `Percentage (%)`.
- `StepCols.power_capacity_*` is a misnomer (power is not a capacity). Doc (`step_table.md`) now flags the intended `power_*` naming; the actual `config.py` rename is part of the follow-up (decision B).

### D. Missing headers vs `functionality.md` requirements — DOCUMENTED
- `functionality.md` says both StepTable and CycleTable should carry a `mask` (boolean). Neither `StepCols` nor `CycleCols` has it. Add in the follow-up; the table docs note it.
- `sub_step_type` is still "TBD" — left open; needs a product decision on substep semantics.

### E. Malformed doc tables — RESOLVED
- `cycle_table.md`: `first/last_epoch_time_utc` rows were missing the sample-data cell; `test_net_energy` had duplicated/extra cells; column count normalized to the 5-column header.
- `step_table.md`: header declared 4 columns but rows carried a 5th (description). Header normalized to include a Description column.

### F. Strategy alignment (`local/data orchestration strategy.md`) — DOCUMENTED ONLY
The multi-scale platform strategy (Stage 0) calls for things the headers do not yet reflect:
- **UUID strategy** for cells, electrodes, materials, protocols, and test runs. Headers currently expose only `source_uuid` (the source-file identity). A cross-tester/cross-scale schema will need stable cell/test-run identity that the harmonized raw can carry or reference. Out of scope for #10 (Stage-0 platform work).
- **BattINFO / EMMO vocabulary mapping.** No term-mapping is documented for any column. When the schema work starts, each harmonized column should map to a BattINFO/EMMO concept; capture that mapping alongside the spec.
- **Header structure & versioning (SPEED-30).** Today there is only a single `__version__` string on the `Cols` base and no per-column unit/dtype metadata. The prototype in `dev/col_structure_development.py` (`SuperDuperCols`) is the candidate pattern: an enum/Mapping that carries `value` + `unit` + `dtype` (and an `is_aux` helper), works with both Polars and Pandas, and supports versioning. **Recommended** direction; deferred.
- `cycle_type` (Standard / GITT / ICI / Characterization) aligns with the strategy's "type of experiment" need — kept in the authoritative spec.

## Recommended follow-up issues
1. **Align `config.py` `RawCols`/`StepCols`/`CycleCols` with the authoritative docs** (decisions B, C-power, D-mask). Update `_helpers.py`. Add a test asserting config classes match the documented column sets.
2. **Adopt a unit+dtype-carrying, versioned header object** (SPEED-30), based on the `SuperDuperCols` prototype; then migrate the engine off the legacy `*_txt` headers.
3. **BattINFO/EMMO column mapping + UUID/identity fields** as part of the Stage-0 schema work.
