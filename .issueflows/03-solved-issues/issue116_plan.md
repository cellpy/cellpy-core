# Plan — issue #116 (Stage 1.14)

1. **`expand_specific_columns(rename, specific_columns, modes)`** — lift the
   bridge's inline postfix loop verbatim into `mapping.py` as a pure,
   non-mutating function (`legacy_col` falls back to the native name when
   unmapped, exactly as before); re-point
   `OldCellpyCellCore.add_scaled_summary_columns` at it. Behavior guarded by
   the existing bridge byte-parity goldens.
2. **`LEGACY_ATTR_TO_SCHEMA`** — three sub-tables keyed by Schema frame
   (`raw` / `step` / `cycle`), legacy dataclass *attribute* name → native
   field name (`raw`/`cycle`) or base-signal name (`step`, combined with
   `STAT_SUFFIXES` for statistic columns). Companion `LEGACY_ATTR_UNMAPPED`
   exception sets (mirroring the `LEGACY_ONLY_*` value sets) give the same
   totality discipline: an uncategorized attribute fails the build.
3. **Duplicate-value pairs** (`charge_capacity`/`charge_capacity_raw`,
   `discharge_capacity`/`discharge_capacity_raw`) mapped on both sides and
   declared in `DUPLICATE_VALUE_ATTRS`; the shim owns the disambiguation
   warning (native-headers plan D6).
4. **`legacy_attr_to_native(frame, attr)`** — small resolver with clear
   KeyErrors distinguishing legacy-only vs unknown attributes.
5. **Tests** — six new cases in `tests/test_header_mapping.py`: attribute
   totality per class, targets exist on native classes, attribute table agrees
   with the value-based pair tables, duplicate pairs coincide, resolver raise
   behavior, and expansion equivalence (mapped, unmapped, non-mutating).
