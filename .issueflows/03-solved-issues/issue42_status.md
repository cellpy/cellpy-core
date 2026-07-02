# Issue #42 status — reset-granularity normalization

- [x] Done

## What's done

- Plan confirmed (`issue42_plan.md`); open questions resolved: ship engine fn + tests now,
  defer pipeline/bridge wiring; include energy columns; assume clean monotonic-within-group raw.
- `config.ResetGranularity` StrEnum (`CYCLE`/`STEP`/`TEST`), CYCLE = mandated default.
- `summarizers.normalize_capacity_granularity(data, schema, granularity)`: reconstructs the
  per-row increment within the source reset group and re-accumulates over `(test_id, cycle_num)`.
  Two-pass polars window impl (nested windows disallowed). Normalizes the present
  `cumulative_*_capacity` / `cumulative_*_energy` columns; polars-in→polars-out /
  pandas-in→pandas-out. CYCLE returns the object untouched.
- Tests in `tests/test_schema.py`: parametrized STEP/TEST→cycle equivalence vs the
  `_build_cumulative_raw` oracle, plus CYCLE no-op (same object + unchanged values).
- Full suite green: `uv run pytest` → 91 passed (goldens byte-stable).

## Remaining work

- None for this issue. Deferred (separate follow-up if a real non-cycle consumer appears):
  wiring the normalizer into `make_step_table`/`make_summary` or a `CellpyCellCore` method,
  and the legacy bridge.

## Notes

- Pipeline/bridge wiring intentionally deferred (issue is "lower priority"; default no-op
  keeps the exercised cycle-cumulative Arbin path untouched).
