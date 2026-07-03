# Issue #67: Selectors: port remaining functions to native schema or make bridge-only

Source: https://github.com/cellpy/cellpy-core/issues/67

## Original issue text

Deferred from #66 (code review 2026-07, item D3/A1).

`selectors.py` is broken with its own default schema: `get_step_numbers`, `get_cycle_numbers`, `get_rates` default to `default_schema()` but dereference legacy-only attribute names (`data_point_txt`, `voltage_txt`, `cycle_index_txt`, ...), so they raise `AttributeError` unless legacy headers are injected. Module is also pandas-only and has zero test coverage.

Decide and implement one of:
- port the functions to the native schema + polars, with tests, or
- move the module next to `legacy.py` and document it as bridge-only until removal.

See `.issueflows/04-designs-and-guides/code-review-2026-07.md` (A1, D3) and `selector-dead-code-deferral.md`.
