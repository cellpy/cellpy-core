# Issue #148: update_data: gap-append keeps the partial trailing step (step spanning the cut is split)

Source: https://github.com/cellpy/cellpy-core/issues/148

## Original issue text

Found by the cellpy L6 golden-equality oracle (jepegit/cellpy#778).

When `new_raw` starts strictly after the existing `datapoint_num` max (`gap_append=True`), `merge.update_data` keeps *all* existing step rows and rebuilds only from the first new datapoint. If the existing raw ends mid-step (the tester step continues in the new rows), that step ends up as two rows: the kept partial row and a new partial row. Downstream the per-cycle summary C-rate drifts (e.g. `discharge_c_rate` 248.6919 vs 248.68871 on `neware_uio.csv` cut at row 4000).

With any overlap (>= 1 already-seen row) `_trim_steps_for_overlap` rebuilds from the start of the spanning step and the result is identical to a full load.

Expected: gap-append should also trim the trailing step of `kept_steps` when the first new row continues the same (cycle, step) and rebuild from that step's `datapoint_num_first`; alternatively document that callers must re-read from the start of the last step.

Repro: `tests/test_incremental_update.py::test_gap_append_mid_step_equals_full_load` in jepegit/cellpy (strict xfail until fixed).
