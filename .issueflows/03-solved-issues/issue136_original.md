# Issue #136: Legacy bridge: preserve test_id through steps/summary output; legacy-schema support for merge_data

Source: https://github.com/cellpy/cellpy-core/issues/136

## Original issue text

## Summary

The `OldCellpyCellCore` legacy bridge strips `test_id` from the outbound
step/summary frames, which degrades multi-test (campaign-merged) objects to
cycle-only summary grouping. cellpy #507 works around it; these requests make
the workaround unnecessary and unblock campaign merges that keep original
per-test cycle numbers.

## Details

1. **Outbound `test_id` stripping.** `_native_steps_to_legacy` re-projects to a
   fixed legacy column order (cell_core.py ~781-815) and the summary path
   filters to `_legacy_summary_column_order` (~928-1065); `test_id` is in
   `NATIVE_ONLY_STEP` / `NATIVE_ONLY_CYCLE` (mapping.py ~191-196, 227-231). The
   inbound side is fine: a raw `test_id` column passes through (exception
   lists, mapping.py ~129-144) and `make_step_table` groups on
   `(test_id, cycle_num, step_num)` (proven by the cycler_small golden).
2. **Bridge summary rebuilds native steps from the stripped legacy steps**
   (`make_core_summary`, cell_core.py ~1010-1012), so
   `use_tid` (summarizers.py ~792) is always False through the bridge â€”
   cycle-only grouping, no per-test windowing, and cross-test collision when
   cycle numbers overlap. cellpy #507's workaround: re-stamp `test_id` onto the
   legacy steps frame post-bridge (depends on the inbound step rename staying
   rename-only with no column filtering â€” please treat that as a contract or
   provide the fix below).
3. **`_add_legacy_summary_cruft`** (cell_core.py ~960-978) does global pandas
   cumsums (cumulated CE, shifted_*, cumulated_ric*) even when the engine
   windowed per test â€” these columns are wrong for multi-test objects.
4. **`merge_data(schema=<legacy Schema>)` raises `AttributeError`** â€”
   `HeadersNormal` lacks the native attribute names (`datapoint_num`,
   `cycle_num`, `test_id`), and passing the native schema instead silently
   skips offsets on legacy-named frames (`_max_column` returns 0 for missing
   columns). Either document legacy schemas as unsupported for merge/update, or
   add attribute aliases so bridge consumers can call
   `merge_data`/`update_data` directly (cellpy #507 mirrors the semantics in
   pandas instead).

## Requests

- [ ] Carry `test_id` through the legacy step output (or have
      `make_core_summary` reuse the native steps it already computed instead of
      rebuilding from the stripped legacy frame).
- [ ] Optionally expose `test_id` in the legacy summary output behind a flag.
- [ ] Window `_add_legacy_summary_cruft` per `test_id` when present.
- [ ] Resolve the `merge_data` legacy-schema story (docs or aliases).
- [ ] Together these unblock `renumber_cycles=False` (original per-test cycle
      numbers) for cellpy's campaign merge ahead of the native-schema path
      (cellpy #511).

## Refs

cellpy jepegit/cellpy#507 (campaign merge + workaround), jepegit/cellpy#511
(native schema opt-in), core tests test_golden.py (cycler_small composite-key
golden), test_merge.py / test_e2e.py (native multi-test invariants).
