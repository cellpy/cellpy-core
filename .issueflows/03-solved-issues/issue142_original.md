# Issue #142: Harden cycle_mode unwrapping in OldCellpyCellCore / _cycle_mode_to_test_mode

Source: https://github.com/cellpy/cellpy-core/issues/142

## Original issue text

## Context

Found while working **jepegit/cellpy#668** (v1.x batch notebook): after a custom `update_cell` → `make_step_table()` → `make_summary()`, the legacy bridge crashes with:

```text
AttributeError: 'list' object has no attribute 'strip'
```

in `cellpycore.cell_core._cycle_mode_to_test_mode` when `OldCellpyCellCore.cycle_mode` is still list-shaped (often double-nested from cellpy-file meta, e.g. `[['anode']]`).

### Why this is a core issue (not just v1.x)

- `cellpy` **master** already mitigates on the **consumer load path** via recursive `test_meta._unwrap` after `meta_test_dependent.update(as_list=True, …)` (and has unit tests).
- The **engine/bridge** still assumes a scalar string:
  - `OldCellpyCellCore.cycle_mode` getter only does one-level `m[0]`
  - setter **keeps** list values (`[x.lower() for x in cycle_mode]`) instead of storing a scalar
  - `_cycle_mode_to_test_mode` calls `cycle_mode.strip()` with no list/tuple handling

Any path that skips consumer unwrap (legacy loads, in-memory meta mutation, older cellpy pins) can still hit this. v1.x (#668) will add a consumer-side unwrap backport; core should still be defensive.

## What to do

1. **Getter** (`OldCellpyCellCore.cycle_mode`): recursively unwrap 1-element `list`/`tuple` to a scalar (same semantics as cellpy `test_meta._unwrap`).
2. **Setter**: unwrap first, then store a **scalar** string (or `None`) — do not persist a list of lowered strings.
3. **`_cycle_mode_to_test_mode`**: if given a list/tuple, unwrap before `.strip()`; keep existing string / `None` / unknown-spelling behaviour.
4. **Tests** covering at least:
   - `'anode'` / `'full_cell'`
   - `['anode']`
   - `[['anode']]`
   - `None`
   - make_summary / make_core_summary does not raise on nested list meta

## Acceptance

- Nested list `cycle_mode` no longer crashes summarization through the legacy bridge.
- Existing CE / inverted-convention tests (issue #129 era) stay green.
- No API break for callers that already pass a plain string.

## Links

- Downstream report: https://github.com/jepegit/cellpy/issues/668
- Related consumer mitigation on master: unwrap in `cellpy.readers.cellpy_file.read` / `test_meta._unwrap`
