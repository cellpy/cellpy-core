# Issue #70: Design pass: schema-agnostic step-stat columns (B1) and cycle_mode default polarity (B2)

Source: https://github.com/cellpy/cellpy-core/issues/70

## Original issue text

Deferred from #66 (code review 2026-07, items B1 + B2).

**B1 — schema-agnosticism is only partial in the step engine.** Per-step statistic columns are hardcoded as `f"{base}_{stat}"` and the classifier reads `pl.col("current_mean")` etc.; injected `StepCols` values apply only to group keys, `step_type` and `c_rate`. Either derive stat column names from the schema, or (cheaper, recommended by the review) document the `<signal>_<stat>` names as a fixed engine contract.

**B2 — default-polarity inconsistency in `cycle_mode`.** `MockMetaTestDependent.cycle_mode = "anode"` means an initialized `Data` defaults to INVERTED mode, while an uninitialized cell (`_cycle_mode = None`) resolves to NORMAL — the exact "default-polarity trap" the `config.TestMode` docstring warns about.

Decide document-vs-fix for each and implement.

See `.issueflows/04-designs-and-guides/code-review-2026-07.md` (B1, B2).
