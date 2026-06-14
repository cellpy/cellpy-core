# Issue #12: Port make_step_table into cellpy-core (bring CellpyLimits with it)

Source: https://github.com/cellpy/cellpy-core/issues/12

## Original issue text

## Goal

Port the **step-table generation** (`make_step_table`) into `cellpy-core`. This is the
remaining half of the "find all steps and cycles" core: the summary / per-cycle half is
already in `cellpy-core` (`summarizers.py`, `selectors.py`, `CellpyCellCore.make_core_summary`),
but step-table building still lives only in the legacy `cellpy` repo
(`cellpy/readers/cellreader.py::make_step_table`).

Currently both `src/cellpycore/cell_core.py` and the ancestor `cellpy/slim/cell_core.py`
carry the marker `# TODO: implement make step table`.

## Why this matters

Until the step table is in core, `cellpy` can only delegate its *summary* processing to
`cellpy-core` (see jepegit/cellpy#377) and must keep `make_step_table` in the monolith.
Porting it completes the core processing surface and lets `cellpy` delegate both halves.

## Tasks

- [ ] Port `make_step_table` logic from `cellpy/readers/cellreader.py` into `cellpy-core`
      (likely a new function/method that consumes `data.raw` and produces `data.step`),
      reusing `selectors.py` / `summarizers.py` patterns where possible.
- [ ] **Bring `CellpyLimits` along.** `cellpy`'s `cellpy/parameters/internal_settings.py`
      defines `CellpyLimits` (step-type detection thresholds: `current_hard`,
      `stable_voltage_hard`, `ir_change`, ...). It is NOT yet present in `cellpy-core`
      (`legacy.py` copies headers + `CellpyUnits` only). Step-type detection depends on it.
- [ ] Decide where the step-type constants live (the `STEP_TYPES` /
      `CAPACITY_MODIFIERS` lists currently in `legacy.py` are marked "NOT USED (YET?)").
- [ ] Add tests against existing testdata to verify parity with legacy `make_step_table`
      output (column names per `docs/data_format_specifications/step_table.md`).

## References

- Header/limits source of truth: `cellpy/parameters/internal_settings.py`.
- Step-table spec: `docs/data_format_specifications/step_table.md`.
- Integration tracking issue (consumer side): jepegit/cellpy#377.
- Design note: `.issueflows/04-designs-and-guides/cellpy-core-integration-into-cellpy.md`.

## Comments (curated summary)

- **Additional tasks**: The cellpy-core step-summary / step-table implementation should use **polars** (not pandas) as its compute engine.
- **Clarifications / constraints**: The intermediate bridge (letting today's pandas-based cellpy use cellpy-core) will need a pandas → polars → pandas round-trip, which is not straightforward — pandas relies on an index and tolerates duplicate column names, whereas polars has no index and disallows duplicate column names.

_Note: this section is an interpretive summary of the comment thread, not a verbatim dump. Source comments: 1, last comment by @jepegit on 2026-06-14._
