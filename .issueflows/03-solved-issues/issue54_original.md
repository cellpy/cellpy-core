# Issue #54: Native exclude-types summary support (replace removed create_selector exclusion feature)

Source: https://github.com/cellpy/cellpy-core/issues/54

## Original issue text

## Context

Issue #45 removed the legacy pandas selector pair (`create_selector` / `summary_selector_exluder`). The default row selection (one cycle-end datapoint per cycle) was already native in `summarizers.make_summary`, so nothing was lost there.

But the old selector had a second, distinct capability that was never ported to the polars engine (and has been silently a no-op since the core seam landed): **exclude-types summaries** (`selector_type="non-cv" / "non-rest" / "non-ocv" / "only-cv"`). Because capacities are cycle-cumulative, this is not row selection — it subtracts the excluded steps' deltas (`last - first` per step, summed per cycle) from the cycle-end values, producing a summary "as if" those steps never happened.

cellpy's `make_summary(selector_type=...)` kwargs currently emit a `DeprecationWarning` and do nothing.

## Proposed design (concrete first, KISS)

Add an option to the native engine:

```python
summarizers.make_summary(data, schema, exclude_step_types=["cv_"], ...)
```

Implementation sketch:

1. Filter the step table by excluded `step_type` prefix(es).
2. Compute per-step deltas from the existing `*_first` / `*_last` stat columns (charge, discharge, current, voltage).
3. Group by cycle (and `test_id` when present), sum.
4. Subtract the per-cycle correction from the selected cycle-end summary rows.

No new protocol/abstraction yet. If a second variant appears (custom exclusion logic, different correction policy), promote it to a pluggable `SummaryAdjuster` mirroring `extractors.SummaryExtractor` — giving the clean vocabulary: *selectors* pick rows, *extractors* derive columns, *adjusters* correct values.

## Testing

- Parity test against the removed pandas implementation (resurrect `summary_selector_exluder` from git history as a test oracle on a fixture with CV steps).
- Guard: `exclude_step_types=None` must stay byte-identical to the current summary (golden fixtures).

## Follow-up on the cellpy side

Once this lands, cellpy can wire `selector_type` / `exclude_types` / `exclude_steps` to the new argument instead of warning, or keep the deprecation and expose the new API directly.

## Links

- #45 (dead-code removal that surfaced this)
- #13 (polars summary rewrite that deliberately skipped the exclusion machinery)
- `.issueflows/04-designs-and-guides/selector-dead-code-deferral.md`
