# Issue #40: Finalize STEP-12 (core): promote CellpyUnits to a unit-spec module + converter-parity tests

Source: https://github.com/cellpy/cellpy-core/issues/40

## Original issue text

Finalizes the cellpy-core side of **STEP-12 (unit-handling boundary)** from the integration roadmap (`.issueflows/04-designs-and-guides/cellpy-core-integration-roadmap.md`). The cellpy-side delegation of its duplicate converters is tracked separately on jepegit/cellpy and is out of scope here.

## Scope (cellpy-core only)

- Promote `CellpyUnits` out of `legacy.py` into a first-class core **unit-spec module** (e.g. `cellpycore.units` or a dedicated spec module). Keep the `legacy.py` mirror/re-export so the STEP-05 contract test (`cellpy/tests/test_core_settings_parity.py`) and `CellpyUnits` field parity stay intact.
- Add a **converter-parity test**: assert `cellpycore.units.get_converter_to_specific` and `nominal_capacity_as_absolute` reproduce cellpy's legacy converter outputs on fixture data for gravimetric / areal / absolute modes, so the upstream duplicates can later be retired without drift.
- Add an **optional-extra guard test**: importing `cellpycore` and running the step/summary engine must work with `pint` **not** installed; the unit helpers raise a clear `ModuleNotFoundError` only when actually called.
- Goldens (STEP-06, `tests/test_golden.py`) must be unchanged.

## Notes / anchors

- Design: roadmap STEP-12; `cellpy-core-integration-into-cellpy.md`, `cellpy-core-migration.md` §4 (boundary analogue of metadata STEP-10).
- Current state: schema + pint tooling already exist behind the optional `units` extra and attach to `OldCellpyCellCore`; factors cross the seam by value. Remaining core work is the module promotion + the parity/optional guard tests.
