# Issue #142 — plan: harden `cycle_mode` unwrapping

## Goal

Stop nested list-shaped `cycle_mode` (e.g. `[['anode']]`) from crashing
`_cycle_mode_to_test_mode` / summarization on the legacy bridge; store and
expose a scalar string (or `None`) from the `cycle_mode` property.

## Constraints

- Back-compat: plain string callers unchanged; issue #127 spelling tables and
  issue #129 bridge CE polarity tests stay green.
- KISS: no new package/module; private helper next to existing translator in
  `cell_core.py`. No numpy dependency (cellpy’s `_unwrap` also peels numpy
  scalars / NaN — out of scope here; meta on the bridge is Python
  `list`/`tuple`/`str`/`None`).
- Metadata boundary unchanged: still optional; only normalize this one field
  at the property / translator edge.
- Scope: getter, setter, `_cycle_mode_to_test_mode` (+ tests). No cellpy
  consumer changes (jepegit/cellpy#668 stays separate).

### Prior art

- `cellpy.readers.test_meta._unwrap` — recursive peel of 1-element
  `list`/`tuple`; multi-element left as-is. **Mirror** that rule in core
  (list/tuple only).
- `_cycle_mode_to_test_mode` + `#127` tests in `tests/test_schema.py` —
  spelling / warning contract; **extend**, don’t rewrite.
- `CellpyCellCore.cycle_mode` getter already does one-level `m[0]`; setter
  wrongly keeps a lowered **list**. `OldCellpyCellCore` inherits this
  property (no override).
- `test_bridge_summary_respects_cycle_mode` (`tests/test_golden.py`) — CE
  polarity regression for string `"anode"`; keep green; add a nested-list
  smoke if cheap.
- Toolbox: empty (nothing reusable). Graph: `cycle_mode` /
  `_cycle_mode_to_test_mode` / `OldCellpyCellCore` communities confirm the
  change set is `cell_core.py` + `test_schema.py`.

## Approach

1. Add `_unwrap_meta_scalar(value)` in `cell_core.py` (module-private):
   while `list`/`tuple` and `len == 1`, recurse; else return value.
2. **Getter:** unwrap `meta_test_dependent.cycle_mode`; if still
   `list`/`tuple`, take `[0]` when non-empty else `None` (preserves today’s
   first-element behaviour for multi-element placeholders).
3. **Setter:** unwrap first; if still sequence, take first or `None`; then
   store **scalar** `str.lower()` or `None` on both meta and `_cycle_mode`
   (never a list of lowered strings). Handle `None` without calling `.lower()`.
4. **`_cycle_mode_to_test_mode`:** unwrap (+ first-element if still sequence)
   before `.strip()`; keep existing `None` / empty / known / unknown+warn
   behaviour. Type hint can widen to `Optional[str | list | tuple]` or stay
   loose — behaviour matters more than the annotation.
5. No public API export of the helper.

Multi-element lists (`['anode','cathode']`) are not a real cellpy-file shape
today; taking `[0]` matches the old getter and avoids a new failure mode.

## Files to touch

| Path | Change |
|------|--------|
| [`src/cellpycore/cell_core.py`](../../src/cellpycore/cell_core.py) | `_unwrap_meta_scalar`; harden getter / setter / `_cycle_mode_to_test_mode` |
| [`tests/test_schema.py`](../../tests/test_schema.py) | Parametrize unwrap cases next to `#127` block; nested-list → INVERTED; setter stores scalar; optional `make_core_summary` / `make_summary` smoke with nested meta |

## Test strategy

```bash
uv run pytest tests/test_schema.py -k cycle_mode
uv run pytest   # full suite before close
uv run ruff check && uv run ruff format --check
```

New coverage (minimum from issue):

- `_cycle_mode_to_test_mode`: `'anode'`, `'full_cell'`, `['anode']`,
  `[['anode']]`, `None` (and keep existing spelling params green).
- Getter/setter: set `[['anode']]` or assign list → property returns
  `"anode"`; stored meta is a `str`, not a list.
- Smoke: `OldCellpyCellCore` (or `CellpyCellCore`) with nested list on
  `meta_test_dependent.cycle_mode` → `make_core_summary` / `make_summary`
  does not raise.

## Open questions

None blocking — defaults above match the issue + cellpy `_unwrap`. Say if
you want multi-element lists to warn instead of silently taking `[0]`.
