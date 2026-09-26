# Status: #151 CellMeta.uuid

- [x] Done

## What was done (2026-09-26)

- `CellMeta.uuid: Optional[str] = None` (docstring: cell-level id, consumer-minted,
  distinct from `TestMeta.uuid`).
- `legacy.meta_mapping.CORE_ONLY_CELL` gains `"uuid"` so totality tests hold and
  cellpy's `apply_test_meta_to_legacy` skips it.
- Spec table in `docs/specifications/harmonized-raw.md` (core-only CellMeta fields).
- Tests: JSON round-trip + core-only mapping; suite 289 passed, ruff clean.
- HISTORY.md `[Unreleased]` entry.

## Follow-up (not here)

PyPI release of cellpy-core and cellpy re-pin (jepegit/cellpy Epic S); cellpy's
BatBase adapter can then set `cell.uuid` from the journal row.
