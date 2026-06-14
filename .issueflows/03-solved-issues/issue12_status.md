# Status — issue #12: Port `make_step_table` into cellpy-core (bring `CellpyLimits`)

- [x] Done (descoped to Phase 1 — see "Decision" below)

## Decision (2026-06-14)

`make_step_table` was already ported to core in PR #9. Reading the full engine showed the
remaining "polars + native schema" work is a large rewrite blocked on native-schema gaps
(see "Blockers" below). We **descoped #12 to Phase 1** (bring `CellpyLimits`, settle the
step-type constants) and moved the polars engine rewrite + parity tests to a **dedicated
follow-up issue (#13)**. Decision recorded in
`.issueflows/04-designs-and-guides/step-table-polars-migration.md`.

## Landed so far (Phase 1 — safe, green)

- Added `CellpyLimits` dataclass to `src/cellpycore/legacy.py` (verbatim mirror of
  `cellpy.parameters.internal_settings.CellpyLimits`).
- `summarizers.DEFAULT_RAW_LIMITS` now derived from `asdict(CellpyLimits())` — standalone
  defaults match legacy (keys verified identical to the previous dict).
- Settled step-type constants in `legacy.py` (`STEP_TYPES` / `CAPACITY_MODIFIERS` no longer
  flagged "NOT USED"; documented as canonical).
- Removed the stale `# TODO: implement make step table` marker in `cell_core.py`.
- Added `tests/test_limits.py` (CellpyLimits values/keys, DEFAULT_RAW_LIMITS derivation,
  dict-like behaviour, canonical step-type labels).
- `uv run pytest`: **18 passed**; no lint errors.

## Paused for design re-confirmation (before the polars rewrite)

Reading the full engine surfaced blockers the plan's high-level choices don't resolve:

1. **There is no working native polars engine to "make consistent" with.** Both the step
   *and* summary functions reference legacy `*_txt` names (`charge_capacity_txt`,
   `cycle_index_txt`, …) that exist only on `HeadersNormal`, and operate on pandas
   `data.raw` / `data.summary`. The engine today is **pandas + legacy-schema only**, driven
   solely by cellpy via `OldCellpyCellCore`.
2. **Native `RawCols` lacks columns the step engine needs.** No `step_time`,
   `internal_resistance`, `ref_voltage`, `charge_capacity`/`discharge_capacity` (only
   `step_cumulative_charge_capacity` / `_discharge_capacity`), no energy/power. A native
   `make_step_table` would have to map cumulative→capacity and leave ir/energy/power empty.
3. **Native `StepCols` vs legacy `HeadersStepTable` mismatch.** Native uses `_mean` (not
   `_avr`), `potential` (not `voltage`), `charge_capacity` (not `charge`), and has **no**
   `rate_avr` / `ir` / `ir_pct_change` / `type` / `info` / `ustep` — which the engine
   produces and the cellpy seam consumes. "Always emit full `StepCols`" and "keep the
   legacy seam byte-stable" therefore need an explicit reconciliation.

Resolution: descoped (see Decision). Column policy for the future native engine: emit the
full `StepCols` set with null/NaN for signals absent from `data.raw` (user choice).

## Moved to a dedicated follow-up issue (#13)

- [ ] Polars-native `make_step_table` + summary path (`summarizers` + `selectors`).
- [ ] Extend native `RawCols`/`StepCols` (step_time, internal_resistance, capacity vs
      cumulative, rate/type/ir columns) so the native schema can represent the output.
- [ ] pandas↔polars / legacy↔native bridge in `OldCellpyCellCore`.
- [ ] Cross-repo parity vs cellpy step/summary tests.

See `.issueflows/04-designs-and-guides/step-table-polars-migration.md`.
