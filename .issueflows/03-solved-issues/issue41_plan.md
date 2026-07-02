# Issue #41 plan — `test_id` in StepCols/CycleCols + composite group keys

## Goal

Thread `test_id` into the per-step (`StepCols`) and per-cycle (`CycleCols`) table
schemas and make every per-step / per-cycle aggregation, cumulation and join key
on the composite `(test_id, cycle_num, step_num, …)` instead of `cycle_num`
alone, so a single merged `Data` holding many tests never mixes cycles across
tests. Single-test behaviour (and all goldens) stay byte-identical.

## Constraints

- **Goldens byte-identical** (`tests/test_golden.py`): the arbin fixture has a
  single `test_id == 1`, so grouping / `over` / joins that add `test_id` as a
  constant leading key produce identical rows, order and values. The legacy
  bridge output column-order lists (`_legacy_step_column_order`,
  `_legacy_summary_column_order`) do **not** include `test_id`, so even though the
  native frames now carry it, it is dropped from the legacy pandas output.
- **Graceful default** (`test-metadata-and-merging.md`): when `raw` has no
  `test_id` column, materialize it as constant `0` at engine entry so the step /
  cycle tables always carry `test_id` (behaviour-preserving; equivalent to a
  single unmerged test).
- **Cross-frame consistency**: cross-frame joins (summary↔steps↔raw) key on
  `test_id` **only when every frame involved carries it**. This keeps the legacy
  *summary* bridge correct: there the rebuilt native `steps` lack `test_id`
  (dropped by the step bridge) while native `raw` has it — so those joins fall
  back to `cycle_num` only, exactly as today.
- KISS: single cohesive feature, one PR. No metadata-class work (v2.0 tail is
  explicitly deferred by the issue).

### Prior art

- `.issueflows/04-designs-and-guides/test-metadata-and-merging.md` — the decision
  record (hybrid compact `raw.test_id` key + composite group keys). Directly drives
  this plan.
- `src/cellpycore/header_mapping.py` — `test_id` already declared `NATIVE_ONLY_RAW`
  / `LEGACY_ONLY_RAW` (intentionally *not* raw-bridged). Same pattern reused for
  step/cycle: add `test_id` to `NATIVE_ONLY_STEP` / `NATIVE_ONLY_CYCLE` (no legacy
  counterpart), keeping the totality tests balanced.
- `config.RawCols.test_id` (`config.py:519`) already exists — mirror its naming.
- `.issueflows/00-tools/` — empty toolbox, nothing reusable. (toolbox + grep +
  graph checked.)

## Approach

Add a tiny presence helper in `summarizers.py`:

```python
def _group_keys(frame, base_keys, test_id_col):
    """Prepend test_id when the frame carries it, else the base keys unchanged."""
    return ([test_id_col, *base_keys]
            if test_id_col in frame.columns else list(base_keys))
```

and a `_ensure_test_id(raw, col)` that adds `pl.lit(0).alias(col)` when absent.

Composite-key each stage:

- **`make_step_table`** — `_ensure_test_id` on `raw`; prepend `nhdr.test_id` to the
  group-by `by` list; extend the group-key rename to map `nhdr.test_id →
  shdr.test_id` (no-op for native names). Result: native step table always carries
  `test_id` as its leading column. `sort(by)` with a constant/single-value leading
  key preserves current row order.
- **`make_summary`** — `_ensure_test_id` on `raw`; compute
  `use_tid = nhdr.test_id in raw and shdr.test_id in steps`.
  - `finals` groups `steps` by `_group_keys(steps, [cycle], test_id)`.
  - `selected` sorts by `[test_id, cycle]` when `use_tid`.
  - carry `chdr.test_id` onto the summary (from raw) when `use_tid`.
  - `charge_capacity_loss` / `discharge_capacity_loss` (`shift(1)`) and all
    `test_cumulated_*` (`cum_sum`) become `.over(chdr.test_id)` when `use_tid`.
  - `_add_end_potentials` groups steps and joins on
    `[test_id, cycle]` when both frames carry `test_id`, else `cycle` only.
- **`c_rates_to_summary`** — `_first_rate` groups `steps` by composite; join to
  summary on the keys present in both (`[test_id, cycle]` or `[cycle]`).
- **`extractors.LastIRExtractor` / `ir_to_summary`** — group `raw` by
  `[test_id, cycle, step]` and `steps` by `[test_id, cycle]` when present; the
  per-cycle frame carries `test_id` when the inputs do; `ir_to_summary` joins onto
  the summary on the keys common to both the extractor output and the summary
  (so custom extractors returning only `cycle_num`, e.g. the test `ConstIR`, still
  work).

Because the legacy step bridge drops `test_id` from its pandas output, the legacy
*summary* bridge sees `steps` without `test_id` → `use_tid = False` everywhere →
identical to today. Native callers get full per-test isolation.

## Files to touch

- `src/cellpycore/config.py` — add `test_id: str = "test_id"` as the **first**
  field of `StepCols` and of `CycleCols`.
- `src/cellpycore/summarizers.py` — `_ensure_test_id` + `_group_keys` helpers;
  composite keys in `make_step_table`, `make_summary`, `_add_end_potentials`,
  `c_rates_to_summary`.
- `src/cellpycore/extractors.py` — composite grouping in `LastIRExtractor`;
  presence-aware join in `ir_to_summary` (in `summarizers.py`).
- `src/cellpycore/header_mapping.py` — add `"test_id"` to `NATIVE_ONLY_STEP` and
  `NATIVE_ONLY_CYCLE` (keeps totality tests balanced).
- `tests/test_config_columns.py` — prepend `test_id` to `STEP_EXPECTED` and
  `CYCLE_EXPECTED`.
- `docs/data_format_specifications/step_table.md`, `cycle_table.md` — add a
  `test_id` row (first) to the column-header tables.
- `tests/test_schema.py` — new merged-object isolation test (below).

## Test strategy

Command: activate the venv then `pytest` (or `uv run pytest`) from the repo root.

- **Regression / parity (must stay green, unchanged):** `tests/test_golden.py`
  (step + summary snapshots, cellpy cross-repo step-types), `test_header_mapping.py`
  (totality), `test_config_columns.py`, `test_harmonized_fixture.py`,
  `test_schema.py` (native no-`test_id` fixtures exercise the graceful fallback).
- **New — cross-test isolation** (`test_schema.py`): build a native raw of two
  `test_id`s (e.g. `0` and `1`) with **overlapping** `cycle_num`/`step_num`, run
  `make_step_table` + `make_summary` (+ `c_rates` + `ir`). Assert:
  - step-table row count == sum of both tests' step counts (no collapse across
    tests sharing `(cycle_num, step_num)`);
  - summary row count == sum of both tests' cycle counts;
  - `test_cumulated_charge_capacity` restarts per `test_id` (test 1's first cycle
    equals its own charge_capacity, not continuing test 0's cumulation);
  - `charge_capacity_loss` first row of each test is null/independent.
- **New — default fallback**: assert a raw *without* `test_id` yields tables whose
  `test_id` column is all `0` (graceful default).

## Open questions

1. **Position of `test_id`** in `StepCols`/`CycleCols`: plan puts it **first**
   (leading composite key, mirrors the `(test_id, cycle_num, …)` ordering in the
   design doc). This fixes the spec-doc and `*_EXPECTED` ordering. OK? (Recommended.)
2. **Always materialize `test_id=0`** when `raw` lacks it (so tables always carry
   the column) vs. only carry it when present. Plan chooses **always materialize**
   per the design doc ("tables should carry `test_id`", "default 0"). OK?
