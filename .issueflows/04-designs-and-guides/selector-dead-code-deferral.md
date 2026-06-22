# Selector dead-code deferral: keep `create_selector` until cellpy migrates

**Context.** Issue #22 (follow-up to #13) proposed removing four "superseded" pandas
summary/selector helpers from cellpy-core after the polars summary rewrite:

- `summarizers.generate_absolute_summary_columns`
- `summarizers.end_voltage_to_summary`
- `selectors.create_selector`
- `selectors.summary_selector_exluder`

**Findings (June 2026).**

- The two `summarizers.*` functions were **already removed in issue #24** (see
  `03-solved-issues/issue24_status.md`, "Dead-code cleanup"). They are absent from
  `src/cellpycore/` today. (cellpy's own `_generate_absolute_summary_columns` /
  `_end_voltage_to_summary` are private methods on its reader, not imports from the core.)
- `selectors.create_selector` is **still imported by the external cellpy repo**:
  `cellpy/readers/cellreader.py` (`core_selectors.create_selector(...)`) and
  `cellpy/tests/test_slim.py`. cellpy pins `cellpycore @ git+...@main`, so removing it would
  break cellpy at its next core-pin resolution.
- `selectors.summary_selector_exluder` is the pandas engine that `create_selector` wraps
  (`functools.partial`), so it must live as long as `create_selector` does.

**Decision.** Keep `create_selector` and `summary_selector_exluder` in cellpy-core for now.
They are **not** dead code from the consumer's point of view. The issue's own guard applies:
"If still needed externally, coordinate a deprecation rather than a hard removal."

**Removal trigger (future work).** Remove both functions only after cellpy stops importing
`core_selectors.create_selector` (i.e. cellpy moves its summary selection onto the native
`make_summary` path, or replaces it with its own helper). At that point this can be done as a
small dead-code deletion in cellpy-core.

**Alternatives considered.**

- *Hard-remove now* — rejected: breaks cellpy's pinned `@main` dependency.
- *Add a deprecation warning now + open a cellpy-side issue* — viable but deferred; spans two
  repos and adds churn for no immediate benefit. Revisit when cellpy work touches that path.

**Links.** Issues #22 (this), #24 (removed the summarizer pair), #13 (polars summary rewrite).
