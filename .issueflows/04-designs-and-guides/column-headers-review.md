# Column headers — review, decisions, and gaps

Durable record from issue #10 ("Make sure column headers make sense"). This is project memory: it captures *why* the column-header docs look the way they do after the issue-#10 cleanup, what is deliberately deferred, and where the next worker should pick up.

Scope of issue #10 was **docs-only**. The `src/cellpycore/config.py` header classes were intentionally **not** changed; the config-vs-doc drift is recorded here as the starting point for a follow-up code issue.

## Where column headers live (the three layers)

1. **Spec docs** (`docs/`) — the human-facing definitions. After issue #10:
   - `docs/data_format_specifications/harmonized_raw.md` — **authoritative** harmonized-raw spec (single source of truth; moved here from `docs/harmonized_raw_definition.md` in PR #14).
   - `docs/data_format_specifications/cycle_table.md`, `step_table.md` — cycle/step table specs.
   - `docs/data-object-definition.md` — the minimal input contract.
   - (The stale 2025-09-08 duplicate that previously sat at this path was deleted in issue #10; the authoritative file was later moved back to this path in PR #14.)
2. **New config classes** (`src/cellpycore/config.py`) — `RawCols`, `StepCols`, `CycleCols`, dataclasses of `name: str = "name"` with dot + bracket access and a `__version__`. **These are DRAFT and not yet wired into the processing engine.** Only `_helpers.py` (synthetic-data `make_raw`) reads `RawCols`.
3. **Legacy headers** (`src/cellpycore/legacy.py`, `*_txt`) — old-cellpy names (`current_txt`, `sub_step_index_txt`, ...). **The live engine (`selectors.py`, `summarizers.py`) still consumes these, not the new `Cols` classes.**

The key structural fact: docs ↔ `config.py` ↔ engine are three out-of-sync representations. Issue #10 aligned the **docs** and made them internally consistent; aligning `config.py` and then the engine is future work.

## Decisions taken in issue #10 (confirmed with the maintainer)

1. **Scope = docs-only.** No `config.py` edits in this issue.
2. **Signal naming = `potential`** (not `voltage`), and **`test_time` is in seconds** (not milliseconds). `data-object-definition.md` was reconciled to match.
3. **`channel_status` is dropped**; the cycler step mode column is **`step_mode`** (not `mode`).
4. **`harmonized_raw.md` (2025-09-08) deleted**; the 2025-09-17 spec is the single source of truth (now at `docs/data_format_specifications/harmonized_raw.md` after the PR #14 move).
5. **Header metadata + versioning (SPEED-30) deferred** — documented as a recommendation, not implemented.
6. **Strategy alignment = document gaps only** — no concrete UUID/BattINFO columns added now.

## Findings (gap analysis)

### A. Duplicated / conflicting harmonized-raw specs — RESOLVED
Two specs disagreed. The newer one (richer: `mask`, `source_step_num`, `step_mode`, `cycle_type`, step cumulative energy/power, `aux_*` scheme) is now authoritative; the older one was deleted.

### B. config.py ↔ doc drift — DONE (PR #14, on the #12 branch)
`RawCols` mirrored the *old* doc and was out of step with the authoritative spec. **Resolved:**
`config.py` `RawCols`/`StepCols` were aligned to the authoritative specs and `_helpers.py`
updated; `tests/test_config_columns.py` now locks all three column classes to the spec
tables. `CycleCols` already matched `cycle_table.md`. The original deferral plan was:
- **Add**: `mask`, `source_step_num`, `step_mode`, `cycle_type`, `step_cumulative_charge_energy`, `step_cumulative_discharge_energy`, `step_charge_power`, `step_discharge_power`, and the `aux_*` columns (`aux_temperature_cell`, `aux_temperature_chamber`, `aux_pressure_cell`, plus the extensible `aux_<quantity>_<name>` scheme).
- **Remove**: `channel_status`; **rename** `mode` → `step_mode`.
- **Rename** the non-aux `temperature_cell` / `temperature_chamber` / `pressure` to the `aux_*` form to match the spec.
- Update the only consumer, `_helpers.py::make_raw`, accordingly (low blast radius — it builds synthetic frames).

### C. Naming / unit inconsistencies — PARTLY RESOLVED
- `voltage` vs `potential` → standardized on **`potential`** (docs reconciled).
- `test_time` ms vs s → standardized on **seconds** (docs reconciled).
- `voltage_efficiency` unit typo (`percetange (V)`) in `cycle_table.md` → fixed to `Percentage (%)`.
- `StepCols.power_capacity_*` is a misnomer (power is not a capacity). Doc (`step_table.md`) flagged the intended `power_*` naming; **the `config.py` rename to `power_*` is now done** (PR #14, with decision B).

### D. Missing headers vs `functionality.md` requirements — RESOLVED (mask)
- `mask` (boolean) is now present in all three tables: `RawCols` (from `harmonized_raw.md`),
  and `StepCols` / `CycleCols` (PR #14 added a `mask` row to `step_table.md` /
  `cycle_table.md` and the matching field to `config.py`, placed right after each table's
  identity block, before `datapoint_num_first`). Default semantics: True = row selected/used.
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

## Issue #24 — categorical-column enums (decisions)

Continuation of the header review. Added typed vocabularies for the categorical
columns in `src/cellpycore/config.py`, alongside the existing `TestMode` enum.

1. **Reference, not validating.** All these enums (`TestMode`, `StepType`,
   `StepMode`, `CycleType`) are `StrEnum`s used as *reference vocabularies*:
   tables keep storing plain strings, the engine does **not** validate against
   them, and unknown values stay allowed. Extend by adding members rather than
   reintroducing free-form strings. (Chosen over closed/validated vocabularies
   to match the reality that we cannot enumerate every value yet.)
2. **`StepType` is the single source of truth.** It holds the canonical 13
   labels (mirroring old cellpy's `list_of_step_types`). The previously
   duplicated `STEP_TYPES` lists in `selectors.py` and `legacy.py` are now both
   `from cellpycore.config import STEP_TYPES`, where
   `STEP_TYPES = [m.value for m in StepType]`. Values/order are unchanged, so
   `test_limits` (classifier labels ⊆ `STEP_TYPES`) and golden parity hold.
3. **Known `StepType` gaps (not fixed here, to preserve golden parity):**
   - `_classify_steps` emits only a subset (`charge`, `discharge`, `cv_charge`,
     `cv_discharge`, `ocvrlx_up`, `ocvrlx_down`, `ir`, `rest`); `taper_*`,
     `charge_cv`, `discharge_cv`, `not_known` come from specs/overrides/legacy.
   - The classifier uses `""` for uncategorized, not `not_known`. **Follow-up:**
     unify `""` and `NOT_KNOWN`.
4. **`StepMode` = `CC`/`CV`/`CP`.** Absence is a null value, **not** the literal
   string `"None"` shown in the spec table (documentation shorthand). Not
   produced by the engine yet.
5. **`CycleType` = `Standard`/`GITT`/`ICI`/`Characterization`** (spec
   capitalization kept). Not used by the engine yet. **Follow-up:** likely
   migrates to per-test metadata as `test_type`; `GITT` overlaps the `test_type`
   examples, so `cycle_type` and `test_type` may be unified.
6. **`sub_step_type` still TBD** (consistent with finding D). Documented in
   `StepCols` as reserved/unpopulated (engine writes null); when used it is
   expected to draw from the `StepType` vocabulary.

Deliberately **out of scope** for this pass (deferred): metadata-level enums
(`TestFamily`/`TestType`, `SourceKind`) and cross-cutting descriptors (capacity
specifics `gravimetric`/`areal`/`absolute`; batbase-aligned `CellConfiguration`
/ `FormFactor`).

## Issue #34 — authoritative header mapping (STEP-09)

Settled the `config.Cols` <-> legacy `Headers*` story. Decisions:

1. **One source of truth.** The native <-> legacy correspondence now lives in
   `src/cellpycore/header_mapping.py` (per-family `RAW_PAIRS`, `STEP_BASE_PAIRS`
   + `STEP_SCALAR_PAIRS` + `STAT_SUFFIXES`, `CYCLE_PAIRS`). The four rename dicts
   that used to be hand-maintained inside `OldCellpyCellCore` (`cell_core.py`)
   now derive from it; the bridge keeps no literal column maps. Behaviour is
   byte-identical (golden + schema tests unchanged).
2. **Mapping is over column-name strings**, not attribute names — that is what
   DataFrame renames act on, and legacy `HeadersSummary` has two attributes that
   share a value (`discharge_capacity` / `discharge_capacity_raw`).
3. **Identity pass-throughs are declared.** Summary `ir_charge`, `ir_discharge`,
   `charge_c_rate`, `discharge_c_rate`, `normalized_cycle_index` already share a
   name across native/legacy; they are listed as (identity) pairs so the totality
   claim holds. As bridge renames they are harmless no-ops.
4. **"Lossless/total" is modulo documented exceptions.** Each side declares
   explicit exception sets (`LEGACY_ONLY_*` / `NATIVE_ONLY_*`) for columns with
   no counterpart — legacy-only cruft (`shifted_*`, `cumulated_ric*`,
   `cumulated_coulombic_efficiency`, `ocv_*`, temperatures, `aux_` prefix, the
   step-table `info` / `ustep` / `ir_pct_change` / `test`) and native-only
   columns (raw `aux_*` / `cumulative_*_energy` / identity & source fields, the
   step `power_*` / `*_energy` statistics and `mask`, and the rich native cycle
   statistics). `tests/test_header_mapping.py` asserts, per family, that declared
   columns == mapped ∪ exceptions (disjoint), so adding a column on either side
   fails the test until it is deliberately categorised — no silent rename drift.
5. **`test_id` is intentionally not bridged.** `RawCols.test_id` and
   `HeadersNormal.test_id_txt` are both `"test_id"`, but the raw bridge does not
   translate it today; it is recorded as an exception on both sides rather than
   added to `RAW_PAIRS` (behaviour-preserving). Revisit if/when the bridge needs
   to carry `test_id` through.
6. **Step granularity.** The native/legacy step correspondence is declared at
   *base-signal* level and expanded with `STAT_SUFFIXES` (`mean` -> `avr`, the
   rest identical). `datapoint_num` / `test_time` participate as base signals but
   `StepCols` only declares their `_first` / `_last` variants (the engine emits
   just those two stats), so the step totality test compares at base-signal
   granularity.
