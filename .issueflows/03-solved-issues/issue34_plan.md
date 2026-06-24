# Plan for issue #34: Finalize config.Cols <-> legacy Headers* mapping

## Goal
Replace the four scattered, hand-maintained rename dicts in `OldCellpyCellCore` with a single declared `config.Cols` <-> legacy `Headers*` mapping (a new module), and prove by test that the translation is **lossless and total** over the declared header classes, modulo explicitly listed exception sets (legacy-only / native-only columns). Behavior must stay identical (goldens green).

## Constraints
- Behavior-preserving: `tests/test_golden.py`, `tests/test_schema.py`, `tests/test_config_columns.py` must stay green; the STEP-05 contract tests live in the `cellpy` repo and rely on the legacy frame layout being byte-identical, so no observable rename change.
- KISS: one new module + one new test + a focused refactor; no new deps.
- Mapping is defined over **column-name strings** (the dataclass field *values*), not attribute names, because that is what DataFrame renames act on and because legacy `HeadersSummary` has duplicate values (e.g. `discharge_capacity` and `discharge_capacity_raw`).
- The mapping must distinguish **renamed pairs** (native string != legacy string) from **identity pass-through** (native == legacy, intentionally unrenamed, e.g. summary `ir_charge`, `charge_c_rate`, `normalized_cycle_index`). A correct totality claim depends on capturing identity pass-throughs.

### Prior art
- `OldCellpyCellCore._NATIVE_STAT_TO_LEGACY`, `_legacy_to_native_raw_rename`, `_native_to_legacy_step_rename`, `_native_to_legacy_summary_rename` (`cellpycore.cell_core`) — the current ad-hoc maps; convention: per-family dicts, step uses base-signal + stat-suffix expansion + scalar columns. New work: **migrate** these to derive from the new module (single source of truth), preserving exact output.
- `tests/test_config_columns.py` — convention: transcribe spec tables to expected lists, assert `list(declared) == EXPECTED` and value==name. New work: **mirror** this style for the mapping/round-trip test.
- `config.CycleCols.specific_columns` / `legacy.HeadersSummary.specific_columns` — convention: native list deliberately drops legacy-only `shifted_*`. New work: reuse this as the canonical example of a documented native-vs-legacy gap.
- `.issueflows/04-designs-and-guides/column-headers-review.md` — durable header-decision memory; new work appends an issue-#34 decision section.

## Approach
1. **New module `src/cellpycore/header_mapping.py`** — the single authoritative declaration:
   - `STAT_SUFFIXES`: native->legacy stat map (`mean->avr`, `std`, `min`, `max`, `first`, `last`, `delta`) (moved from `_NATIVE_STAT_TO_LEGACY`).
   - `RAW_PAIRS`: list of `(native, legacy)` tuples for the raw frame (the 10 current pairs, e.g. `("cumulative_charge_capacity", "charge_capacity")`).
   - `STEP_BASE_PAIRS` (base signals: `step_time`/`current`/`potential`<->`voltage`/`charge_capacity`<->`charge`/`discharge_capacity`<->`discharge`/`internal_resistance`<->`ir`/`datapoint_num`<->`point`/`test_time`) + `STEP_SCALAR_PAIRS` (`cycle_num`<->`cycle`, `step_num`<->`step`, `sub_step_num`<->`sub_step`, `step_type`<->`type`, `sub_step_type`<->`sub_type`, `c_rate`<->`rate_avr`).
   - `CYCLE_PAIRS`: the 16 current summary pairs **plus** the identity pass-throughs (`ir_charge`, `ir_discharge`, `charge_c_rate`, `discharge_c_rate`, `normalized_cycle_index`) so totality holds.
   - Documented exception constants per family: `LEGACY_ONLY_RAW/STEP/CYCLE` and `NATIVE_ONLY_RAW/STEP/CYCLE` (sets of column-name strings with short comments explaining why they have no counterpart, e.g. raw `aci_phase_angle`, summary `shifted_*` / `cumulated_ric*` / `cumulated_coulombic_efficiency` / `ocv_*`, native `aux_*` / `cumulative_*_energy`).
   - Small derivation helpers used by the bridge: `legacy_to_native_raw()`, `native_to_legacy_step()`, `native_to_legacy_summary()` (build the dicts the bridge needs, incl. step base x stat expansion), and their inverses where needed.
2. **Refactor `OldCellpyCellCore`** so the four helpers delegate to `header_mapping` (no literal dicts left in `cell_core.py`); keep method names/signatures so the rest of the class is untouched. Output frames must be identical.
3. **Document exceptions** as the module-level constants above (single source) + a concise decision section appended to `column-headers-review.md`.

## Files to touch
- `src/cellpycore/header_mapping.py` (new) — authoritative pairs, stat map, exception sets, derivation helpers.
- `src/cellpycore/cell_core.py` — back the 4 rename helpers with `header_mapping`; drop the inline literals.
- `tests/test_header_mapping.py` (new) — round-trip + totality + no-drift tests.
- `.issueflows/04-designs-and-guides/column-headers-review.md` — append "Issue #34 — authoritative header mapping" decision note.
- `.issueflows/01-current-issues/issue34_plan.md` — write this plan (first step of /iflow-start).

## Test strategy
`tests/test_header_mapping.py` (run with `uv run pytest`), per family (raw / step / cycle):
- **Round-trip / bijection:** mapping is injective both ways; native->legacy->native is identity on the declared domain; `STAT_SUFFIXES` is bijective.
- **Native totality:** every declared `config.Cols` column value is either in the mapping (directly, or via base x stat expansion for step) or in `NATIVE_ONLY_*`; the two are disjoint and cover the class exactly.
- **Legacy totality:** every declared `Headers*` column value is either mapped or in `LEGACY_ONLY_*`; disjoint and exact cover.
- **No stale drift:** every name in the exception sets and pairs actually exists on the relevant class.
- **Bridge parity:** assert `OldCellpyCellCore`'s helper outputs equal the `header_mapping`-derived dicts (guards the refactor).
- Document the known step quirk: `datapoint_num`/`test_time` base signals yield runtime stat columns beyond the `*_first`/`*_last` declared in `StepCols`; the step totality check is asserted at base-signal granularity with this noted.
- Re-run full suite: `uv run pytest` (esp. `test_golden.py`, `test_schema.py`, `test_config_columns.py`).

## Open questions
- `RawCols.test_id` and legacy `HeadersNormal.test_id_txt` are both `"test_id"` but the raw bridge does **not** translate `test_id` today. Plan: document it as an exception on both sides (behavior-preserving) rather than adding it to `RAW_PAIRS`. Flag if you'd prefer it added to the mapping instead.
- STEP-05 contract tests live in `cellpy` (sibling repo); they are not run from `cellpy-core` CI. Plan treats "no observable rename change" as the guarantee; a manual cross-repo `pytest` run in `cellpy` can confirm if desired.

## Status
- [x] Done

Implemented: `src/cellpycore/header_mapping.py` (authoritative pairs + exception
sets + derivation helpers), refactored `OldCellpyCellCore` to derive its four
rename dicts from it, added `tests/test_header_mapping.py` (12 tests), and
recorded the decisions in `column-headers-review.md`. Full suite green (50
passed), including `test_golden.py` / `test_schema.py` / `test_config_columns.py`
— no rename drift.
