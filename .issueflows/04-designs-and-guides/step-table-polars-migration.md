# Step/summary engine: polars-native migration (deferred)

Durable record of why the cellpy-core compute engine is still pandas, what blocks the
polars rewrite, and the design decisions to honour when it is done. Spun out of issue #12;
tracked in **issue #13**.

## Context

- `make_step_table` was ported to core in PR #9 and is driven by `cellpy` across the seam
  (`cellreader.py::make_step_table` → `OldCellpyCellCore.make_core_step_table` →
  `summarizers.make_step_table`). It works and is tested (`tests/test_schema.py`).
- Issue #12 also asked to "bring `CellpyLimits`" and (per a later comment) to move the
  engine to **polars**. Phase 1 of #12 brought `CellpyLimits` (in `legacy.py`) and derived
  `DEFAULT_RAW_LIMITS` from it. The polars rewrite was **descoped** to this follow-up.

## Why the polars rewrite is non-trivial (blockers)

1. **The whole engine is pandas + legacy-schema only.** Both `summarizers.py` and
   `selectors.py` use `pandas.groupby` and read legacy `*_txt` names
   (`charge_capacity_txt`, `cycle_index_txt`, …) that exist only on `HeadersNormal`. They
   operate on pandas `data.raw` / `data.summary`. There is no working native polars path
   today to "make consistent" — it must be written from scratch while keeping the legacy
   seam byte-stable for cellpy.
2. **Native `RawCols` lacks columns the step engine needs:** no `step_time`,
   `internal_resistance`, `ref_voltage`; capacity is only `step_cumulative_charge_capacity`
   / `step_cumulative_discharge_capacity` (no plain `charge_capacity`); no energy/power.
3. **Native `StepCols` ≠ legacy `HeadersStepTable`:** native uses `_mean`/`potential`/
   `charge_capacity`; legacy uses `_avr`/`voltage`/`charge` and additionally has
   `rate_avr`, `ir`, `ir_pct_change`, `type`, `info`, `ustep` (produced by the engine and
   consumed by cellpy). Native `StepCols` also lists `power_capacity_*` / `*_energy_*` that
   the native raw cannot supply.

## Decisions to honour in the follow-up

- **Engine consistency:** migrate step *and* summary paths together (avoid a split engine).
- **Column policy:** the native step table should always emit the full `StepCols` set,
  filling null/NaN where the source signal is absent from `data.raw`.
- **Keep the cellpy seam working:** either a pandas↔polars + legacy↔native bridge in
  `OldCellpyCellCore`, or extend the native schema first (preferred — resolves the gaps in
  blockers 2 & 3) and then rewrite.
- **Limits:** step-detection thresholds come from `CellpyLimits` (already in `legacy.py`);
  cellpy passes its own `raw_limits` by value.

## Prep done (de-risks this rewrite)

- **Real-data regression oracle in place** (`tests/test_golden.py`): the engine is
  pinned against cellpy's published goldens (103 steps / 18 cycles / cycle-1
  `data_point` 1457) on a real Arbin frame, plus a frozen step-table snapshot. The
  polars rewrite must keep these green. Fixtures + regen script + best-practice are
  described in `test-data-and-fixtures.md`.
- **Edge case to fix during the rewrite:** on the tiny 47-row fixture the engine
  leaves one step's `type` blank (`''`) — revisit step-type classification.

## Decisions taken in issue #13 (the follow-up itself)

- **Engine vocabulary:** Option A — the polars engine targets the **native** schema;
  `OldCellpyCellCore` bridges legacy↔native (column rename) + pandas↔polars at the seam.
  Confirmed 2026-06-14.
- **Dataframe lib:** pure **polars** in the engine (not narwhals).
- **Sequencing:** phased PRs — (1) extend native schema, (2) polars step engine + bridge,
  (3) polars summary path, (4) cross-repo parity.
- **Capacity semantics (verified on the real Arbin fixture):** legacy raw
  `charge_capacity` / `discharge_capacity` are **cycle-cumulative, per direction** (accumulate
  across a cycle's steps for their direction, reset to 0 at each cycle boundary). They are
  *not* per-step. The summary path depends on this: `selectors.summary_selector_exluder`
  reads the cycle's **last** raw datapoint as that cycle's capacity, which is only correct for
  cycle-cumulative raw. Taking the harmonized spec's `step_cumulative_*` name literally
  (step-cumulative values) would **break** the summary.
  - **Decision:** the harmonized raw capacity column **mandates cycle-cumulative** (per
    cycle, per direction). Renamed the native columns
    `step_cumulative_charge_capacity`→`cumulative_charge_capacity` and
    `step_cumulative_discharge_capacity`→`cumulative_discharge_capacity` (energy renamed the
    same way). The bridge maps legacy `charge_capacity` ↔ native `cumulative_charge_capacity`
    (pure rename, no value transform). Per-step capacity is **derived** by the engine
    (delta = last−first within a step); per-cycle is the cycle-end cumulative value.
  - Reset-granularity normalization in the engine (to also accept step-/test-cumulative raw
    from other cyclers) is a deliberate **future follow-up**, not done now.

### Phase 2 step engine + bridge (done)

- `summarizers.make_step_table` is now **polars-native** and operates on the **native**
  schema. It aggregates every present native raw signal (`datapoint_num`, `test_time`,
  `step_time`, `current`, `potential`, `cumulative_charge_*capacity`, `internal_resistance`)
  with the full mean/std/min/max/first/last/delta set, derives the per-step `c_rate`, and
  classifies step types via the same threshold logic as legacy (later rules win; helper
  `_classify_steps`). Output is a polars `data.steps` frame.
- `OldCellpyCellCore.make_core_step_table` is the **legacy↔native + pandas↔polars bridge**:
  legacy pandas raw → rename to native → polars → engine → native polars steps → rename to
  legacy → pandas, reproducing the legacy `HeadersStepTable` 64-column frame **byte-for-byte**
  (incl. the leading `index` column and the `test_time_first` sort). This keeps
  `tests/test_golden.py` green against the existing cellpy-parity snapshot **without
  regenerating it** — the strongest parity guarantee.
- Parity decision: the bridge reproduces the exact legacy frame (Path P), chosen over
  adopting the native StepCols shape + regenerating the golden (Path N). The native step
  frame is a *superset* of `StepCols` (it also carries full `test_time`/`datapoint_num`
  aggregates needed for legacy parity); `StepCols` remains the canonical/guaranteed set.
- `tests/test_schema.py` step tests rewritten to the native schema/raw (the engine is
  native-only now). The summary-path test is unchanged (Phase 3 still pandas).
- **Blank step-type "edge case" — resolved as a non-bug.** The tiny fixture's `step 2` is a
  degenerate synthetic slice (non-monotonic/duplicated `data_point`, mixed current signs,
  zero capacity-delta); leaving it blank matches legacy cellpy and is a fixture artifact, not
  a defect. Classification logic was deliberately **not** changed (changing it would diverge
  from cellpy and break the parity guarantee). A holistic classification review, if wanted,
  belongs in its own issue.

### Phase 4 cross-repo parity (done)

- **Key finding:** the cellpy→cellpy-core integration *already happened* — cellpy 1.0.3
  delegates `make_step_table`/`make_summary` to `self.core.make_core_*`. So comparing
  cellpy-core against a synced cellpy is circular; the meaningful references are cellpy's
  **pre-integration committed goldens**.
- **Steps:** cellpy's `testdata/data/steps.csv` (cycle/step/type/info, 103 rows) is an
  independent classifier oracle. Vendored as `tests/data/arbin_cc_steptypes_cellpy.csv`;
  cellpy-core reproduces it byte-for-byte (`test_arbin_step_types_match_cellpy_reference`).
- **Summary (decision `steps_sufficient`):** the summary stays gated by the Phase 3a oracle +
  cellpy's cyc-1 `data_point` golden (1457). A full byte-parity against cellpy's independent
  `old=True` legacy summary needs cellpy run with the current core in its venv (stale install);
  deferred to cellpy#377/#378 rather than doing env surgery.
- Note for the future: once cellpy's pinned core is bumped to include this work, an end-to-end
  cellpy run is the integration test; the `steps.csv` golden remains the non-circular unit check.

### Phase 3b polars-native summary engine + bridge (done)

- **Key finding:** the native per-cycle vocabulary (`config.CycleCols` / `cycle_table.md`) is a
  curated, forward-looking design — **not** a renamed legacy summary. ~14 legacy summary columns
  map cleanly to native concepts (e.g. legacy `cumulated_charge_capacity` → native
  `test_cumulated_charge_capacity`; `end_voltage_charge` → `potential_end_charge`), but ~11 are
  legacy cruft the native design intentionally drops (`cumulated_coulombic_efficiency`,
  `shifted_charge/discharge_capacity`, `cumulated_ric/_sei/_disconnect`,
  `charge_c_rate/discharge_c_rate`, `ir_charge/ir_discharge`, `normalized_cycle_index`).
- **Decision: `bridge_extras`** (over extending `CycleCols`, and over a separate clean impl).
  The native polars engine (`summarizers.make_summary`) produces **only** the clean native
  subset; the `OldCellpyCellCore` bridge renames native→legacy and **computes the legacy-only
  extras** to reproduce the Phase 3a oracle byte-for-byte. Keeps `cycle_table.md`/`CycleCols`/
  `CYCLE_EXPECTED` untouched; legacy cruft lives only in the legacy bridge (reusing the legacy
  pandas `ir_to_summary` / `c_rates_to_summary` helpers — appropriate, they *are* legacy).
- **Selection:** `make_summary` does the cycle-end raw-row selection inline (last step's last
  datapoint per cycle); the advanced `selectors.create_selector` exclude-types machinery is
  legacy-only and now unused.
- **Parity semantics:** verified polars `cum_sum` (skips nulls like pandas), `shift` (null fill),
  and ÷-by-zero (inf/NaN) match pandas exactly, so the polars rewrite is byte-faithful.
- **Cell convention:** native `make_summary` assumes full-/cathode (charge = first); anode mode
  (discharge-first) is not yet handled in the native engine (legacy bridge default is full, which
  the oracle uses). Add when an anode consumer needs it.
- **Superseded but kept (transitional):** `generate_absolute_summary_columns`,
  `end_voltage_to_summary`, `selectors.create_selector`, `selectors.summary_selector_exluder` —
  no longer used inside cellpy-core but may be imported by the external `cellpy` repo; prune in a
  later cleanup once cross-repo usage is confirmed.

### Phase 3a data-model fix + summary oracle (done)

- Phase 3 is **split**: 3a = make the summary path runnable + freeze a regression oracle;
  3b = polars-native rewrite of `selectors.py` + summary functions + bridge.
- **Data-model fix (decision: `add_attrs`).** `Data` declared only `raw`/`cycle`/`step`, but
  the engine reads/writes `data.steps`/`data.summary`/`data.has_steps`. `has_steps` was never
  defined, so the summary path raised `AttributeError` and had never run. `Data` now declares
  `steps`/`summary` and exposes `has_steps`/`has_summary` properties (`cycle`/`step` kept as
  legacy aliases). Once fixed, the legacy pandas summary runs and reproduces the cellpy golden
  cyc-1 `data_point` (1457).
- **Oracle (decision: `freeze_now`).** Froze cellpy-core's *current* pandas summary output as
  `arbin_cc_summary_expected.parquet` (18×27) via the legacy bridge. This locks the upcoming
  3b refactor; **cross-library byte-parity with cellpy is deferred to Phase 4** (the snapshot
  is cellpy-core's own output, not a cellpy reference, though cyc-1 datapoint already matches).
- `dev/regenerate_test_data.py` stage B was rewritten to drive the step table through the
  bridge (its old direct `make_step_table(schema=legacy)` call broke after Phase 2) and to emit
  the summary snapshot.

### Phase 1 native-schema changes (PR #16, merged)

- `RawCols`: rename the 4 `step_cumulative_*` capacity/energy columns to `cumulative_*`;
  add `step_time` and `internal_resistance` (engine inputs present in legacy raw / needed for
  parity). `ref_potential` deferred — **not present** in the golden Arbin data, so not needed
  for parity yet (note kept here so the gap is tracked).
- `StepCols`: add `step_time` and `internal_resistance` aggregate sets (mean/std/min/max/
  first/last/delta) and a per-step `c_rate` (native name for legacy `rate_avr`).
- The legacy `Headers*` mirrors in `legacy.py` are **unchanged** (cellpy contract); the
  legacy/golden path is unaffected by these native-schema edits.

## Related

- Issue #12 (this work's origin): `.issueflows/03-solved-issues/issue12_*` once closed.
- Test-data strategy & oracle: `test-data-and-fixtures.md`.
- Integration design: `cellpy-core-integration-into-cellpy.md`.
- Header harmonization: `column-headers-review.md`, cellpy/cellpy-core#4 (SPEED-30).
- Contract tests for the legacy mirrors: jepegit/cellpy#378.
