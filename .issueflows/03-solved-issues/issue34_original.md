# Issue #34: STEP-09: Finalize config.Cols <-> legacy Headers* mapping (lossless/total round-trip + test)

Source: https://github.com/cellpy/cellpy-core/issues/34

## Original issue text

## Context

Roadmap **STEP-09 (Harmonize column headers)** — see
`.issueflows/04-designs-and-guides/cellpy-core-integration-roadmap.md`.

The integration delegates `cellpy`'s core processing to `cellpy-core` while keeping
legacy behaviour. Native column names live in `config.Cols`
(`RawCols` / `StepCols` / `CycleCols`); the legacy-named headers cellpy still expects
live in `cellpycore.legacy` (`HeadersNormal` / `HeadersSummary` / `HeadersStepTable`).

## Current state

- `config.Cols` and `legacy.Headers*` both exist, each with spec-conformance tests
  (`tests/test_config_columns.py`).
- The `OldCellpyCellCore` bridge in `src/cellpycore/cell_core.py` already translates
  native <-> legacy column names, but **ad hoc**: e.g. `_NATIVE_STAT_TO_LEGACY` and the
  inline native->legacy rename map in the summary bridge.
- There is **no single, declared, tested** `config.Cols` <-> legacy `Headers*` mapping,
  and no round-trip test proving the translation is lossless and total.

## Goal

Settle the column-header story: provide one authoritative `config.Cols` <-> legacy
`Headers*` mapping and prove (by test) that the translation is **lossless and total** —
every legacy header maps to a native column and back, with no silent rename drift.

## Scope / tasks

- Define the authoritative mapping in one place (native <-> legacy), replacing or backing
  the ad-hoc rename dicts currently scattered in `cell_core.py`.
- Document any legacy headers that intentionally have **no** native counterpart (legacy-only
  "extras" such as `shifted_*`, RIC, cumulated-CE) and any native columns with no legacy
  counterpart, so "lossless/total" is well-defined rather than aspirational.
- Add a round-trip / mapping test (e.g. `tests/test_header_mapping.py`).

## Success criteria (from roadmap STEP-09)

- Spec-conformance tests continue to pin `RawCols` / `StepCols` / `CycleCols` to the
  authoritative spec tables (`tests/test_config_columns.py` — exists).
- A round-trip / mapping test proves `config.Cols` <-> legacy `Headers*` translation is
  lossless and total (every legacy header maps and back, documented exceptions aside).
- The STEP-05 contract tests (in `cellpy`) and STEP-06 goldens (`tests/test_golden.py`)
  still pass — no silent rename drift.

## Out of scope

- Porting further engine behaviour (STEP-08 cleanup, STEP-10/11/12) — tracked separately.
- Changing the harmonized raw spec itself.

## References

- `.issueflows/04-designs-and-guides/cellpy-core-integration-roadmap.md` (STEP-09)
- `src/cellpycore/config.py`, `src/cellpycore/legacy.py`, `src/cellpycore/cell_core.py`
- `tests/test_config_columns.py`, `tests/test_golden.py`
