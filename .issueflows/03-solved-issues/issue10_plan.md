# Plan for issue #10: Make sure column headers make sense

## Goal
Review every place column headers are defined (docs + `config.py`), find what is missing or inconsistent, reconcile the conflicting specs into a single source of truth, and make sure the header set is aligned with the multi-scale platform strategy in `local/data orchestration strategy.md`.

## Constraints
- Follow KISS: this is primarily a **review + documentation** issue. Keep code churn minimal and defer large code restructures to follow-up issues unless the user asks otherwise.
- Header *names* are still DRAFT, but treat doc reconciliation as the deliverable, not a rewrite of the processing engine.
- The durable design decision belongs in `.issueflows/04-designs-and-guides/` (project memory), per AGENTS.md.

### Prior art
- `config.py` `RawCols` / `StepCols` / `CycleCols` (`src/cellpycore/config.py`) — convention: dataclass of `name: str = "name"`, dot + bracket access, `__version__` on `BaseCols`. New work: keep this convention; the doc spec must match these class attributes 1:1.
- Legacy headers `Data` / `*_txt` (`src/cellpycore/legacy.py`) — convention: old cellpy `current_txt`, `sub_step_index_txt`, etc. **The actual processing code (`selectors.py`, `summarizers.py`) still consumes these, NOT the new `Cols` classes.** New work: coexist; note the gap, do not try to migrate the engine in this issue.
- `dev/col_structure_development.py` `SuperDuperCols` — convention: prototype enum carrying `value`/`unit`/`dtype` + `is_aux`. New work: cite as the candidate pattern for header+unit+dtype+versioning (SPEED-30); recommend, do not adopt here.
- `_helpers.py` (`make_raw` synthetic data) — only consumer of `RawCols`; any `RawCols` rename must be reflected here. Low blast radius.

## Approach
Read-only analysis already done; findings to capture:

**A. Conflicting / duplicated specs (pick one source of truth)**
- `docs/data_format_specifications/harmonized_raw.md` (2025-09-08, older) vs `docs/harmonized_raw_definition.md` (2025-09-17, newer, richer). They disagree. Newer adds `mask`, `source_step_num`, `step_mode`, `cycle_type`, `step_cumulative_charge/discharge_energy`, `step_charge/discharge_power`, `aux_*` naming scheme; drops `channel_status` and renames `mode`→`step_mode`. Recommend: make the 2025-09-17 definition authoritative and either delete or mark the older one as superseded.

**B. Code vs doc drift (`config.py` `RawCols`)**
- `RawCols` matches the *older* doc: still has `mode`, `channel_status`, `temperature_cell/chamber`, `pressure`; missing `mask`, `source_step_num`, `step_mode`, `cycle_type`, energy/power cumulative, and the `aux_*` scheme.

**C. Naming / unit inconsistencies**
- `voltage` (data-object-definition.md) vs `potential` (harmonized/config) — pick one.
- `test_time` unit: `millisecond` (data-object-definition.md) vs `second` (harmonized). Pick one.
- `StepCols.power_capacity_*` is a misnomer (power is not a capacity) — should be `power_*`.
- `voltage_efficiency` unit typo in cycle_table.md (`percetange (V)`).

**D. Missing headers vs `functionality.md` requirements**
- `functionality.md` says both StepTable and CycleTable should carry a `mask` (boolean); neither `StepCols` nor `CycleCols` has it.
- Substep type handling (`sub_step_type` = TBD) still undefined.

**E. Malformed doc tables**
- `cycle_table.md`: rows `first/last_epoch_time_utc` (l.15-16) are missing a column cell; `test_net_energy` (l.41) has duplicated/extra cells; header has 5 cols but several rows have 4.
- `step_table.md`: header declares 4 columns but rows carry a 5th (description) with no header; `power_capacity_*` naming.

**F. Strategy alignment (`local/data orchestration strategy.md`)**
- Stage 0 calls for a **UUID strategy** (cells, electrodes, materials, protocols, test runs) and **BattINFO/EMMO vocabulary mapping**. Today only `source_uuid` exists. Note what header-level provenance/identity fields are missing and that a BattINFO term-mapping column note is absent.
- "Header structure & versioning" (SPEED-30) — only a single `__version__` string exists; no per-column unit/dtype metadata. `SuperDuperCols` is the candidate pattern.
- `cycle_type` (Standard/GITT/ICI/Characterization) aligns with the strategy's "type of experiment" need — confirm it stays.

**Deliverables (proposed, doc-focused):**
1. A gap-analysis / decisions doc under `.issueflows/04-designs-and-guides/` — the durable record of findings A–F and the chosen resolutions.
2. Reconcile harmonized_raw into one authoritative spec; mark/delete the superseded one.
3. Fix malformed/typo'd tables in `cycle_table.md` and `step_table.md`; resolve `voltage`/`potential` and `test_time` unit inconsistency in `data-object-definition.md`.
4. (Pending user call — see Open questions) optionally bring `config.py` `RawCols`/`StepCols`/`CycleCols` in line with the authoritative spec.

## Files to touch
- `.issueflows/04-designs-and-guides/column-headers-review.md` — NEW: gap analysis + decisions (durable).
- `docs/harmonized_raw_definition.md` — promote to authoritative; resolve open follow-up questions where decided.
- `docs/data_format_specifications/harmonized_raw.md` — mark superseded or delete (user call).
- `docs/data_format_specifications/cycle_table.md` — fix malformed rows + unit typo.
- `docs/data_format_specifications/step_table.md` — fix header/row column mismatch; `power_capacity_*` → `power_*` (if approved).
- `docs/data-object-definition.md` — reconcile `voltage`/`potential` + `test_time` units.
- `src/cellpycore/config.py` — ONLY if user approves code alignment in this issue; else defer to follow-up.

## Test strategy
- Mostly docs, so no runtime behavior changes expected.
- If `config.py` is touched: `uv run pytest` to confirm nothing using `RawCols`/`_helpers.make_raw` breaks; check `_helpers.py` still constructs valid frames.
- Sanity-grep that no renamed header is referenced elsewhere before renaming.

## Resolved decisions (confirmed by user)
1. **Scope = docs-only.** Review + reconcile specs + fix tables + write the design doc. **Defer all `config.py` code changes to a follow-up issue** — do NOT edit `src/cellpycore/config.py` in this issue. (Capture the config-vs-doc drift in the design doc as the follow-up's starting point.)
2. **Authoritative naming = `potential` + `test_time` in seconds.** Reconcile `data-object-definition.md` accordingly.
3. **Drop `channel_status`; rename `mode`→`step_mode`** in the authoritative spec.
4. **Older harmonized_raw doc = delete.** Remove `docs/data_format_specifications/harmonized_raw.md`; `docs/harmonized_raw_definition.md` becomes the single source of truth.
5. **Header metadata/versioning (SPEED-30) = defer.** Document the `SuperDuperCols` pattern as the recommendation only.
6. **Strategy alignment = document gaps + recommendations only.** No concrete UUID/BattINFO header columns added now (Stage-0 platform work).

## Files to touch (final, docs-only)
- `.issueflows/04-designs-and-guides/column-headers-review.md` — NEW: gap analysis + decisions (incl. config-vs-doc drift for the follow-up issue).
- `docs/harmonized_raw_definition.md` — authoritative; apply `potential`/seconds, `step_mode`, drop `channel_status`; resolve decided follow-ups.
- `docs/data_format_specifications/harmonized_raw.md` — **delete** (superseded).
- `docs/data_format_specifications/cycle_table.md` — fix malformed rows + `percetange (V)` typo.
- `docs/data_format_specifications/step_table.md` — fix header/row column mismatch; note `power_capacity_*`→`power_*` recommendation (doc only).
- `docs/data-object-definition.md` — reconcile `voltage`→`potential` + `test_time` seconds.
- (NOT touched this issue: `src/cellpycore/config.py`.)
