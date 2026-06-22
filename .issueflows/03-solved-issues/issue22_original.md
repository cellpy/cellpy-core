# Issue #22: Remove superseded pandas summary/selector functions

Source: https://github.com/cellpy/cellpy-core/issues/22

## Original issue text

Follow-up to #13. After the polars summary rewrite these functions are no longer used inside cellpy-core — they were superseded by the native `make_summary` / `_add_end_potentials` engine and the legacy extras computed in `OldCellpyCellCore._add_legacy_summary_extras`. They were kept only because the external `jepegit/cellpy` repo *might* still import them.

### Candidates for removal
- [ ] `summarizers.generate_absolute_summary_columns` (superseded by `make_summary` + bridge extras)
- [ ] `summarizers.end_voltage_to_summary` (superseded by `_add_end_potentials`)
- [ ] `selectors.create_selector` (native `make_summary` does cycle-end selection inline)
- [ ] `selectors.summary_selector_exluder` (legacy-only; relies on `StepCols.point/.voltage/.type`)

### Before deleting
- [ ] Confirm `jepegit/cellpy` (current pinned version) does not import these names. (`cellreader.py` and `tests/test_slim.py` referenced some of them historically — verify.)
- [ ] If still needed externally, coordinate a deprecation rather than a hard removal.

### Acceptance
- Dead code removed; `uv run pytest` green; no import breakage in cellpy after its core pin is bumped.
