# Status — issue #116 (Stage 1.14)

- [x] Done

## 2026-07-14

- Added `LEGACY_ATTR_TO_SCHEMA` (10 raw + 14 step + 25 cycle attributes),
  `LEGACY_ATTR_UNMAPPED`, `DUPLICATE_VALUE_ATTRS`, `legacy_attr_to_native`,
  and `expand_specific_columns` to `cellpycore/legacy/mapping.py`.
- Re-pointed `OldCellpyCellCore.add_scaled_summary_columns` at
  `expand_specific_columns` (behavior-preserving; bridge goldens green).
- The new attribute-totality test caught one omission during development
  (`discharge_capacity_loss`) — the discipline works.
- Full suite: 202 passed. Consumed by cellpy Stage 1.15 (#458) after
  release + re-pin.
