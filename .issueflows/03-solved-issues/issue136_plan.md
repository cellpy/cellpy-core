# Issue #136 — plan

Source: https://github.com/cellpy/cellpy-core/issues/136

## Goal

Legacy bridge keeps `test_id` on outbound steps (and summary when present) so
campaign-merged multi-test objects get per-test summary windowing through the
bridge — no cellpy #507 re-stamp workaround. Also fix legacy-cruft cumsums and
clarify `merge_data` + legacy schema.

## Constraints

- Back-compat: single-test objects already have `test_id=0` on raw; emitting
  `test_id` on steps/summary is **additive** (extra column). Goldens that pin
  exact column sets may need updates.
- Mapping totality (`NATIVE_ONLY_*` / attr maps) must stay consistent.
- Do not change native engine behaviour; bridge-only (+ headers/mapping).
- Unblocks cellpy #510 V2-15 pin after a **new** cellpycore PyPI release.

### Prior art

| Hit | Role | Plan |
|-----|------|------|
| [`OldCellpyCellCore._native_steps_to_legacy`](../../src/cellpycore/cell_core.py) / `_legacy_step_column_order` | Drops unknown cols via fixed order | **Extend** order with `test_id` when present |
| [`make_core_summary`](../../src/cellpycore/cell_core.py) rebuilds native steps from legacy `data.steps` | `use_tid` false after strip | Fixed once steps carry `test_id` through rename |
| [`_add_legacy_summary_cruft`](../../src/cellpycore/cell_core.py) | Global pandas cumsums | **Window** by `test_id` when column present |
| [`NATIVE_ONLY_STEP` / `NATIVE_ONLY_CYCLE`](../../src/cellpycore/legacy/mapping.py) | Declares `test_id` intentionally unbridged | **Remove** `test_id`; add identity scalar/cycle pairs |
| [`HeadersStepTable` / `HeadersSummary`](../../src/cellpycore/legacy/headers.py) | No `test_id` field today | **Add** `test_id: str = "test_id"` |
| cellpy [`cellreader.make_step_table` re-stamp](../../../cellpy/cellpy/readers/cellreader.py) (~2293) | Workaround | Becomes redundant after this; leave for a cellpy follow-up |
| [`merge_data`](../../src/cellpycore/merge.py) | Expects native `Schema` attrs | **Document + hard error** on legacy header schema (cellpy already uses pandas merge) |
| Toolbox `00-tools/` | Empty | None |
| Graph | Bridge / mapping communities | Touch `cell_core` + `legacy/mapping` + `legacy/headers` |

## Approach

1. **Steps outbound:** Add `HeadersStepTable.test_id`. Put `test_id` early in
   `_legacy_step_column_order` (before cycle/step). Add identity
   `STEP_SCALAR_PAIRS` entry `("test_id", "test_id")`; drop `test_id` from
   `NATIVE_ONLY_STEP`. Update attr maps (`LEGACY_ATTR_TO_SCHEMA` /
   `LEGACY_ATTR_UNMAPPED`) for the new header field.
2. **Summary outbound:** Add `HeadersSummary.test_id`. Include in
   `_legacy_summary_column_order` (near `cycle_index`) when present after rename.
   Add identity `CYCLE_PAIRS` entry; drop `test_id` from `NATIVE_ONLY_CYCLE`.
   No flag — always pass through when the native summary has it (single-test →
   all `0`).
3. **Cruft:** In `_add_legacy_summary_cruft`, if `test_id` in summary columns and
   `nunique > 1` (or always when column present): compute cumsums / shifted /
   ric **per group**; else keep today's global behaviour.
4. **`merge_data` + legacy schema:** At entry, if `schema.raw` is
   `HeadersNormal` (or lacks `datapoint_num` / `cycle_num` / `test_id`), raise
   `TypeError` with a clear message: use `config.default_schema()` / native
   `Schema`. Document in `merge_data` docstring. No full legacy-schema merge
   implementation in this issue (cellpy does not call it).
5. **Tests:** Bridge multi-test fixture (or reuse schema/e2e multi-test raw) →
   `make_core_step_table` / `make_core_summary` → assert `test_id` on steps and
   summary `{0,1}`; assert summary cumulatives restart per test. Mapping
   totality tests update with the exception-set moves. One test that
   `merge_data(..., schema=legacy.schema)` raises the new TypeError.

## Files to touch

| Path | Change |
|------|--------|
| `src/cellpycore/legacy/headers.py` | `test_id` on step + summary headers |
| `src/cellpycore/legacy/mapping.py` | pairs / `NATIVE_ONLY_*` / attr maps + comments |
| `src/cellpycore/cell_core.py` | column order, cruft windowing |
| `tests/test_*.py` (bridge / mapping / merge) | new + update totality |
| `CHANGELOG` / HISTORY if present | note for 0.2.2 release |

## Test strategy

```bash
uv run pytest
uv run ruff check && uv run ruff format --check
```

Focus: new bridge multi-test test + `tests/test_header_mapping.py` totality +
`tests/test_merge.py` legacy-schema error.

## Decisions (confirmed 2026-07-17)

1. **Summary `test_id`:** always when present (no flag).
2. **`merge_data` legacy schema:** hard `TypeError` + docstring (also
   `update_data`).
3. **Cruft windowing:** when `test_id` column exists (groupby).
4. **Goldens:** regenerate stage-B step/summary snapshots (additive `test_id`).
