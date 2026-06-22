# Issue #23: Fix ir_to_summary: internal resistance assigned to the wrong cycle

Source: https://github.com/cellpy/cellpy-core/issues/23

## Original issue text

`summarizers.ir_to_summary` carries a long-standing correctness bug, flagged in-code:

```
# THIS DOES NOT WORK PROPERLY!!!!
# Found a file where it writes IR for cycle n on cycle n+1
# This only picks out the data on the last IR step before
```

It picks the IR value from a single step per cycle and can misattribute it (off-by-one cycle), and only handles one IR step.

### Scope
- [ ] Reproduce with a fixture where charge/discharge IR steps span a cycle boundary.
- [ ] Fix the cycle/step selection so IR lands on the correct cycle.
- [ ] Decide behaviour when a cycle has multiple IR steps (currently takes `[0]`).
- [ ] Do this **as part of (or after) the polars port** of `ir_to_summary` (#21) so it isn't ported twice.

### Caution
The current (buggy) output is frozen in the Phase 3a summary oracle (`arbin_cc_summary_expected.parquet`). Fixing this will require an intentional, reviewed oracle regen via `dev/regenerate_test_data.py`.
