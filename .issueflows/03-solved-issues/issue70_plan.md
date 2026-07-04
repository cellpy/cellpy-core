# Issue #70 — plan

## Goal

Close code-review items **B1** and **B2**: make the step-engine stat-column naming
contract explicit, and remove the `cycle_mode` default-polarity trap inside
cellpy-core so an initialized vs uninitialized `CellpyCellCore` behaves the same
unless the caller sets `cycle_mode` explicitly.

## Constraints

- **B1: document, not refactor.** The 2026-07 review recommends documenting
  `<signal>_<stat>` as a fixed engine contract rather than deriving names from
  injected `StepCols`. Issue #43 already followed that pattern for
  `ref_potential`. No change to aggregation or classifier logic.
- **B2: fix the inconsistency, keep cellpy bridge path explicit.** Changing the
  core default to “unset → NORMAL” is intentional: it matches `TestMode` /
  batbase and the uninitialized `_cycle_mode = None` path. Legacy cellpy’s
  historical `"anode"` default remains the bridge’s job when loading real cells
  (document, do not silently reintroduce `"anode"` in core).
- **Parity:** golden / legacy-bridge tests must stay green. Native API tests may
  need CE-direction updates only if they implicitly relied on the old anode
  default (grep shows none beyond round-trip self-consistency).
- **Scope:** docs + small defaults/helper only. No schema-derived stat rename,
  no metadata wiring, no `make_step_table` refactor.

### Prior art

- [`code-review-2026-07.md`](../04-designs-and-guides/code-review-2026-07.md) §B1, §B2 — source findings; review recommends document for B1.
- [`issue43_plan.md`](../03-solved-issues/issue43_plan.md) — “Engine stat-column contract: hardcoded `f"{base}_{stat}"`”; mirror that decision.
- [`this-project.md`](../04-designs-and-guides/this-project.md) — already notes stat columns as fixed contract (issue #70); line 48 still overclaims full schema injection — update in same PR.
- [`docs/standalone-use.md`](../../docs/standalone-use.md) — “cycle-mode trap” section documents old `"anode"` default; must be updated if B2 fix lands.
- `summarizers.make_step_table` — aggregation at `f"{base}_{stat}"` (lines 454–457); classifier hardcodes `pl.col("current_mean")` etc. (lines 273–279); only group keys + `step_type` / `c_rate` use injected `StepCols` (lines 498–506).
- `header_mapping.STAT_SUFFIXES` + `OldCellpyCellCore._legacy_step_column_order` — legacy rename path; unchanged by B1 docs.
- `config.TestMode` docstring — already warns about batbase NORMAL vs cellpy `"anode"`; extend cross-link to `MockMetaTestDependent`.
- `tests/test_schema.py::test_make_summary_anode_flips_coulombic_columns` — explicit `TestMode` test; reuse pattern for default-mode test.
- Graph communities 0 / engine hub (`summarizers.py`, `config.py`, `cell_core.py`) — confirms touch surface.
- `.issueflows/00-tools/` — nothing relevant.

## Approach

### B1 — document the stat-column engine contract

1. **`config.StepCols` docstring** — add a `Note:` block: attributes name the
   **native output columns** for the default contract; the step engine builds
   intermediate aggregates as `<base>_<stat>` where `<base>` comes from
   `_SIGNAL_BASES` / raw column stems (`current`, `potential`, …) and `<stat>`
   is one of `mean|std|min|max|first|last|delta`. Custom `StepCols.current_mean`
   (etc.) does **not** retarget aggregation or classification today; only group
   keys, `step_type`, and `c_rate` honour injected renames. Legacy bridge renames
   via `header_mapping.native_to_legacy_step()` after the engine runs.
2. **`summarizers.make_step_table` docstring** — same `Note:` (shorter); point
   readers to `StepCols`.
3. **`summarizers.py` module comment** (lines 20–23) — nuance “schema-agnostic”:
   raw/cycle/step *keys* and summary column aliases are injected; per-step stat
   column stems are a fixed contract.
4. **`this-project.md`** — tighten conventions bullet: group keys and summary
   headers are schema-injected; per-step stat stems are not.
5. **`code-review-2026-07.md`** — mark B1 resolved (documented, 2026-07-03).

**Optional guard test** (recommended, ~15 lines): after `make_step_table` on
synthetic raw data, assert every `StepCols` `*_mean|*_delta|…` default name that
corresponds to a present signal exists as a column. Documents the contract in
tests without custom-schema rename coverage.

### B2 — align default polarity to NORMAL (unset)

**Decision:** `None` / unset → `TestMode.NORMAL`; only explicit `"anode"` →
`TestMode.INVERTED`. Fixes the initialize=True vs initialize=False split.

1. **`legacy.MockMetaTestDependent`**
   - Change `cycle_mode: str = "anode"` → `cycle_mode: Optional[str] = None`.
   - Docstring: placeholder for graceful degradation; `None` means normal
     convention; cellpy bridge / caller must set `"anode"` for half-cells.
2. **`cell_core.py`**
   - Add small helper `_cycle_mode_to_test_mode(cycle_mode: str | None) -> TestMode`
     (or method on `CellpyCellCore`): `"anode"` → `INVERTED`, else `NORMAL`
     (including `None`).
   - Use it in `make_core_summary` (and anywhere else the same
     `if self.cycle_mode == "anode"` pattern appears: `add_scaled_summary_columns`,
     `OldCellpyCellCore.add_scaled_summary_columns`) so logic is single-sourced.
   - Annotate `cycle_mode` property return as `Optional[str]`; no behaviour change
     to getter/setter beyond the new default on fresh `Data`.
3. **Docs**
   - Update [`docs/standalone-use.md`](../../docs/standalone-use.md) trap section:
     fresh `Data` now defaults to normal convention; set `core.cycle_mode = "anode"`
     for half-cells. Keep explicit mapping table.
   - Cross-link from `config.TestMode` docstring to `MockMetaTestDependent`.
4. **`code-review-2026-07.md`** — mark B2 resolved.

## Files to touch

| File | Change |
| --- | --- |
| [`src/cellpycore/config.py`](../../src/cellpycore/config.py) | `StepCols` contract `Note:`; optional `TestMode` cross-link |
| [`src/cellpycore/summarizers.py`](../../src/cellpycore/summarizers.py) | Module comment + `make_step_table` `Note:` |
| [`src/cellpycore/legacy.py`](../../src/cellpycore/legacy.py) | `MockMetaTestDependent.cycle_mode = None` + docstring |
| [`src/cellpycore/cell_core.py`](../../src/cellpycore/cell_core.py) | `_cycle_mode_to_test_mode` helper; replace inline `"anode"` checks |
| [`docs/standalone-use.md`](../../docs/standalone-use.md) | Updated default-polarity guidance |
| [`.issueflows/04-designs-and-guides/this-project.md`](../04-designs-and-guides/this-project.md) | Nuance schema-injection convention |
| [`.issueflows/04-designs-and-guides/code-review-2026-07.md`](../04-designs-and-guides/code-review-2026-07.md) | Mark B1 + B2 resolved |
| [`tests/test_schema.py`](../../tests/test_schema.py) or new small test file | Contract column test (B1); default `cycle_mode` → NORMAL summary test (B2) |

## Test strategy

```bash
uv run pytest tests/test_schema.py tests/test_creation.py -q
uv run pytest -q   # full suite before close
uv run ruff check && uv run ruff format --check
```

**New tests**

- **B1:** `test_step_table_stat_columns_match_stepcols_defaults` — default schema,
  synthetic raw with core signals → step columns include expected stat names.
- **B2:** `test_default_cycle_mode_is_normal_convention` — fresh `Data()` +
  `CellpyCellCore.make_core_summary` CE direction matches
  `TestMode.NORMAL`; separate assert that `cycle_mode="anode"` still flips
  (can extend existing anode test or add integration via `CellpyCellCore`).

## Open questions

1. **Breaking-change notice:** default CE direction changes for callers who never
   set `cycle_mode` on native `Data()` / `CellpyCellCore`. Acceptable for
   pre-release core? (Recommend yes — fixes the documented trap; note in PR body.)
2. **B1 guard test:** include the optional contract assertion test, or docs-only?
   (Recommend include — cheap, prevents doc drift.)
