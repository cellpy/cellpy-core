# Plan for issue #21: Complete the native polars summary path (port remaining helpers + anode mode + native add_scaled)

## Goal

Make the native `CellpyCellCore` summary path stand on its own (no legacy bridge
needed) by porting the five remaining pandas summary helpers to polars-native,
adding anode (discharge-first) handling to `make_summary`, and making
`add_scaled_summary_columns` work on the native polars `summary` — all while
keeping the `tests/test_golden.py` summary oracle byte-green through the bridge.

## Constraints

- **Oracle stays byte-green.** `tests/test_golden.py::test_arbin_summary_matches_snapshot`
  (and `..._matches_cellpy_goldens`) must keep passing unchanged. The legacy bridge
  (`OldCellpyCellCore.make_core_summary`) output is the contract.
- **Polars-only engine, schema-injected, thread-safe** (project rule + `step-table-polars-migration.md`).
- **`ir_to_summary` correctness bug is out of scope.** It currently writes IR for
  cycle *n* on *n+1* ("DOES NOT WORK PROPERLY"). Preserve current behaviour exactly
  (oracle-locked); the real fix is a separate issue.
- **KISS / dead-code:** avoid duplicating a pandas + a polars copy of each helper.
  One polars-native implementation; the bridge converts at the seam.
- Google-style docstrings; double-backtick code tokens.

### Prior art

- `summarizers.make_summary` (`cellpycore.summarizers`) — already polars-native on the
  native schema (the model to mirror: read names off injected `Schema`, `pl.col(...).with_columns`,
  `cum_sum`/`shift` parity verified against pandas). New work: **mirror** its style.
- `summarizers._add_end_potentials` (`cellpycore.summarizers`) — polars per-cycle join helper
  (group_by cycle → join onto summary). New work: **mirror** for the c-rate/IR joins.
- `OldCellpyCellCore._add_legacy_summary_extras` / `_native_to_legacy_summary_rename`
  (`cellpycore.legacy`) — the existing bridge that today computes the legacy-only extras
  in pandas (`cumulated_coulombic_efficiency`, `shifted_*`, `cumulated_ric*`) and calls the
  pandas `ir_to_summary` / `c_rates_to_summary`. New work: **migrate** these to run on the
  native polars frame before the final →pandas rename.
- Legacy cellpy `_generate_absolute_summary_columns` / `_equivalent_cycles_to_summary`
  (`cellpy/readers/cellreader.py` ~line 6093) — the authoritative anode-mode reference:
  `coulombic_efficiency = 100*second/first`, `coulombic_difference = first - second`, where
  normal: first=charge,second=discharge; anode: first=discharge,second=charge. New work:
  **mirror** the first/second flip in native `make_summary`.
- `cellpycore.config.TestMode` (`NORMAL`/`INVERTED`) — the typed replacement for cellpy's
  loose `cycle_mode` string, already defined but not wired up. New work: candidate to drive
  the anode flag (see Open questions).

## Approach

Four work-items. Recommend landing as **phased PRs** (see Scope check).

### A. Anode (discharge-first) mode in `make_summary`  — via `config.TestMode`

In `summarizers.make_summary`, the only mode-dependent values are
`coulombic_efficiency` and `coulombic_difference` (capacity-loss and cumulated
columns are direction-independent). Add a `test_mode: TestMode = TestMode.NORMAL`
parameter and compute:

- `NORMAL`:   `CE = 100*dc/cc`, `coul_diff = cc - dc`  (current behaviour)
- `INVERTED` (anode): `CE = 100*cc/dc`, `coul_diff = dc - cc`

Wire up `config.TestMode` (currently defined but unused): `CellpyCellCore.make_core_summary`
maps `self.cycle_mode == "anode"` → `TestMode.INVERTED`, else `TestMode.NORMAL`, and passes
it down (also threaded through `equivalent_cycles_to_summary` / `c_rates_to_summary` for the
first-step capacity choice). The bridge keeps passing `NORMAL` (oracle is full-cell), so the
oracle is unaffected.

### B. Port the 5 helpers to polars-native (native schema)

Rewrite these to operate on a polars `data.summary` / `data.steps` using injected
`Schema` names (mirroring `make_summary`):

1. `generate_specific_summary_columns` — `summary.with_columns((factor*pl.col(col)).alias(f"{col}_{mode}"))`.
2. `_calculate_nominal_capacity_from_cycles` — polars `filter(cycle.is_in(...))` + `mean()`; native cycle-num + capacity column.
3. `equivalent_cycles_to_summary` — `normalized_cycle_index = test_cumulated_charge_capacity / nom_cap`.
4. `c_rates_to_summary` — per-cycle first charge/discharge `c_rate` from the step table joined onto summary (mirror `_add_end_potentials`).
5. `ir_to_summary` — **behaviour-preserving** port (keep the off-by-one), via `selectors.get_step_numbers`.

### C. Make the legacy bridge feed polars (keep oracle byte-green)

Move `OldCellpyCellCore._add_legacy_summary_extras` to compute the extras on the
**native polars** frame (reuse the ported helpers + polars `cum_sum` for
`cumulated_coulombic_efficiency` / `shifted_*` / `cumulated_ric*`), then do the
single native→legacy rename →pandas at the end. The golden oracle proves parity.

### D. Native `add_scaled_summary_columns` + extend `CycleCols` (Option A)

Once B lands, the existing `CellpyCellCore.add_scaled_summary_columns` already calls
`equivalent_cycles_to_summary` + `generate_specific_summary_columns`; it will work on
the native polars summary.

**Decision (confirmed): Option A — fully extend native `CycleCols`** so the native path
is completely standalone (revises the Phase 3b "drop legacy-only columns" decision; record
this in `step-table-polars-migration.md`). Add to `CycleCols`:

- `normalized_cycle_index` (for `equivalent_cycles_to_summary` / `add_scaled`)
- `charge_c_rate`, `discharge_c_rate` (for `c_rates_to_summary`)
- `ir_charge`, `ir_discharge` (behaviour-preserving native targets for `ir_to_summary`;
  the existing `ir_start/end_*` stay reserved/unpopulated — adding the legacy-shaped pair
  keeps `ir_to_summary` oracle-locked rather than forcing a semantically wrong start/end split)
- a `specific_columns` accessor (which columns get `_gravimetric/_areal/_absolute` variants)

Then update `docs/data_format_specifications/cycle_table.md` and
`tests/test_config_columns.py::CYCLE_EXPECTED` to match the new column set.

## Files to touch

- `src/cellpycore/summarizers.py` — anode mode in `make_summary`; port the 5 helpers to polars.
- `src/cellpycore/legacy.py` — `OldCellpyCellCore` bridge: feed polars to the extras path.
- `src/cellpycore/cell_core.py` — pass anode flag in `make_core_summary`; verify `add_scaled_summary_columns` native path.
- `src/cellpycore/config.py` — add `normalized_cycle_index`, `charge_c_rate`, `discharge_c_rate`, `ir_charge`, `ir_discharge`, and a `specific_columns` accessor to `CycleCols` (Option A); wire `TestMode` into the summary path.
- `docs/data_format_specifications/cycle_table.md` + `tests/test_config_columns.py` (`CYCLE_EXPECTED`) — sync with the extended `CycleCols`.
- `tests/test_schema.py` — new native-schema tests mirroring `test_make_summary_native_schema` (anode CE/diff flip; native `add_scaled`; ported helpers).
- `.issueflows/04-designs-and-guides/step-table-polars-migration.md` — record the Phase-3b follow-up decision (esp. the CycleCols question).

## Test strategy

- `uv run pytest tests/test_golden.py` — oracle must stay green (byte-parity through the bridge).
- `uv run pytest tests/test_schema.py tests/test_config_columns.py` — native schema + spec parity.
- New tests: anode CE/coul_diff flip vs normal; native `add_scaled_summary_columns`
  end-to-end on polars (normalized_cycle_index + `*_gravimetric/_areal/_absolute`);
  each ported helper on a tiny native frame.
- `uv run pytest` — full suite green before close.

## Resolved decisions (confirmed by user)

1. **Native `CycleCols`: Option A — fully extend** (`normalized_cycle_index`,
   `charge_c_rate`, `discharge_c_rate`, `ir_charge`, `ir_discharge`, `specific_columns`),
   updating `cycle_table.md` + `CYCLE_EXPECTED`. This revises the Phase 3b "drop legacy-only
   columns" decision; record the revision in `step-table-polars-migration.md`.
2. **IR native targets:** add `ir_charge`/`ir_discharge` to `CycleCols` (behaviour-preserving;
   keeps `ir_to_summary` oracle-locked). Existing `ir_start/end_*` stay reserved.
3. **Anode flag:** wire up the existing `config.TestMode` enum (`NORMAL`/`INVERTED`) now.

## Scope check

This issue bundles 4 deliverables (anode mode, 5 helper ports, bridge migration, native
add_scaled) + the `CycleCols` extension. **Confirmed: deliver as a single PR.** The golden
oracle (`test_golden.py`) is the safety net for the bridge migration; new native-schema tests
cover anode mode and `add_scaled`.
