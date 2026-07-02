# Issue #45: Cleanup (blocked): remove create_selector/summary_selector_exluder once cellpy migrates off them

Source: https://github.com/cellpy/cellpy-core/issues/45

## Original issue text

Tracking issue for the deferred dead-code removal documented in `.issueflows/04-designs-and-guides/selector-dead-code-deferral.md`.

## Status: blocked (do not remove yet)

`selectors.create_selector` is **still imported by the external cellpy repo** (`cellpy/readers/cellreader.py` via `core_selectors.create_selector(...)`, and `cellpy/tests/test_slim.py`). `selectors.summary_selector_exluder` is the pandas engine it wraps, so it must live as long as `create_selector` does. cellpy pins `cellpycore @ ...@main`, so removing now breaks cellpy at its next pin resolution.

## Removal trigger (future work)

Remove **both** functions only after cellpy stops importing `core_selectors.create_selector` (i.e. cellpy moves its summary selection onto the native `make_summary` path or its own helper). Then this is a small dead-code deletion in `src/cellpycore/selectors.py`.

(The sibling pair `generate_absolute_summary_columns` / `end_voltage_to_summary` was already removed in issue #24.)
