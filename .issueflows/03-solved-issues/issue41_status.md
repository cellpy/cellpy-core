# Issue #41 status — test_id + composite group keys

- [x] Done

## What's done

- `config.py`: added `test_id` as the leading field of `StepCols` and `CycleCols`.
- `summarizers.py`: `_ensure_test_id` (default 0) + `_group_keys` helpers;
  composite keys in `make_step_table` (group `by`), `make_summary` (finals,
  sort, per-test `cum_sum`/`shift` via `.over(test_id)`, summary `test_id` col),
  `_add_end_potentials`, `c_rates_to_summary`, and the `ir_to_summary` join.
- `extractors.py`: `LastIRExtractor` groups/joins per `(test_id, cycle, step)`
  when present, gracefully falling back to cycle-only otherwise.
- `header_mapping.py`: `test_id` added to `NATIVE_ONLY_STEP` / `NATIVE_ONLY_CYCLE`
  (kept out of the legacy step/summary bridge, mirroring the raw `test_id`).
- Specs updated: `step_table.md`, `cycle_table.md` (leading `test_id` row).
- Tests: `test_config_columns.py` expected lists updated; new `test_schema.py`
  cases for merged-object step/summary isolation and the default-0 fallback.

### Design note (cross-frame consistency)

Cross-frame joins use `test_id` only when **all** involved frames carry it. This
keeps the legacy *summary* bridge (rebuilt native steps lack `test_id`) on the
cycle-only path = byte-identical to before. The single-test goldens
(`arbin_cc`, `test_id == 1`) are unchanged.

### Behaviour change caught by a fixture

`arbin_small_raw.parquet` is actually a merged object with three `test_id`s
(1, 2, 3) sharing `(cycle, step)`. The old engine collapsed them to 3 steps; the
composite key correctly yields 7. `test_small_step_table_runs_on_real_data`
updated accordingly (this is the bug the issue fixes, on real data).

## Remaining work

- None. Full suite green (88 passed). Ready for `/iflow-close`.
