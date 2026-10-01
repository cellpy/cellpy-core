# Cycle renumbering for discharge-first cells

Issue: [jepegit/cellpy#359](https://github.com/jepegit/cellpy/issues/359) (Stage 5 S3,
`to core`); core PR [#153](https://github.com/cellpy/cellpy-core/pull/153).

## Context

Full / commercial cells are often started with a lone discharge. The cycler's cycle counter
then disagrees with the "charge opens a cycle" convention (`[D C D][C D]…` or
`[D C][D C]…`), so coulombic efficiency and curve extraction pair the wrong half-cycles.
Core took `cycle_num` as-is and only knew about polarity (`TestMode`).

## Decision

- **Explicit opt-in post-processing step** `summarizers.renumber_cycles(data, schema=None,
  opening=StepDirection.CHARGE, **step_table_kwargs)`, exported top-level. Default engine
  behaviour unchanged; golden fixtures untouched.
- **New enum `config.StepDirection`** (`CHARGE` / `DISCHARGE`) for the opening direction.
  `TestMode` stays binary (polarity only); half-cycle *ordering* is a separate axis.
- **Algorithm** (per `test_id`, steps sorted by `datapoint_num_first`): direction from
  `step_type` (charge-ish / discharge-ish / neutral); a boundary opens where an `opening`
  step follows the last non-neutral step of the other direction; the first step is never a
  boundary (a leading run of closing steps becomes cycle 1). Numbering restarts from the
  test's original first cycle number.
- **Raw capacities follow**: the cycle-cumulative capacity / energy columns are
  re-accumulated from old to new cycle keys with `_reaccumulate_cumulative` (the body
  extracted from `normalize_capacity_granularity`). Exact no-op (early return) when the
  mapping is the identity.
- **Steps are rebuilt** with `make_step_table(**step_table_kwargs)` (per-step cumulative
  `*_first/last` stats shift; classification is cycle-independent). **Summary is dropped**
  (`data.summary = None`) — caller reruns `make_summary` with its own `test_mode`.
- A lone first discharge yields `CE = inf` under `NORMAL`; left as-is (honest value).

## Alternatives considered

- New `TestMode` member (e.g. `FULL_DISCHARGE_FIRST`) — conflates polarity with ordering;
  `TestMode` docstring explicitly wants it binary. Rejected.
- Keyword on `make_summary` only — cannot fix raw cumulative capacities or the step table,
  so curves / steps would still be mis-paired. Rejected.
- New raw column (`corrected_cycle_num`) — spec answer: no; keep one `cycle_num`, repair it.
- Mapping-only update of `steps.cycle_num` instead of rebuild — leaves cumulative-capacity
  step stats stale. Rejected (rebuild is one extra group_by).

## Limitations / follow-ups

- `usteps=True` step tables are rejected (ustep rows cannot be mapped back onto raw).
- Apply after the raw is complete — `merge.update_data` keys on the cycler counter.
- Owner's two solutions ([comment](https://github.com/jepegit/cellpy/issues/359)): core
  delivers "Solution 2" (explicit control); cellpy wires "Solution 1" on top — a
  `cycle_mode` variant (e.g. `"full_cell_discharge_first"`) that maps to `TestMode.NORMAL`
  + `renumber_cycles(opening=CHARGE)` after the step table. User-visible convention change
  → release note + comparator exception on the cellpy side (stage5 §S3).
