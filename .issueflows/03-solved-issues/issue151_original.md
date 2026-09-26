# Issue #151: CellMeta.uuid: cell-level join key for external metadata sources

Source: https://github.com/cellpy/cellpy-core/issues/151
Labels: enhancement
Captured: 2026-09-26

---

## Context

jepegit/cellpy#784 (Epic M, external metadata sources) adds a `MetadataSource` Protocol and a persisted back-link (`ExternalLink`: `source_name`, `external_id`, `source_uri`) on the cellpy side. The design (cellpy-design-and-development `active/cellpy2-metadata-source-integration.md` §3.3, metadata-plan OQ6) also parks a **cell-level** id — `CellMeta.uuid` — next to the existing `TestMeta.uuid`, so a physical cell can be linked to a lab database record independently of any one test run.

`CellMeta` lives in `cellpycore.metadata.models`, so this is a core-first change (then PyPI release, then cellpy re-pin per jepegit/cellpy Epic S).

## Spec

- Add `uuid: Optional[str] = None` to `CellMeta` (same conventions as `TestMeta.uuid`: minted by the consumer, never required, round-trips through `to_dict` / `from_dict` and the legacy mapping tables as a core-only field).
- Add `"uuid"` to `meta_mapping.CORE_ONLY_CELL` so `apply_test_meta_to_legacy` in cellpy skips it.
- Update `docs/specifications/harmonized-raw.md` CellMeta table.

## Acceptance

- `CellMeta(uuid="…")` round-trips through the metadata archive helpers.
- Existing cellpy tests that build `CellMeta()` are unaffected (default `None`).
- Release note entry; cellpy re-pin tracked in jepegit/cellpy.
