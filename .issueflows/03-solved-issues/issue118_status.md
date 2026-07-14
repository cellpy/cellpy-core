# Status — issue #118 (Stage 1.17)

- [x] Done

## 2026-07-15

- `cellpycore/curves.py` + `config.CurveCols` / `OcvCurveCols` +
  `docs/specifications/curve-table.md` landed.
- Parity vs the vendored jepegit/cellpy#433 snapshots: **all seven frame cases
  match at rtol 1e-9 across the option matrix** (back-and-forth, labeled
  forth-and-forth, interpolated forth, two-cycle tidy, ccap/dcap, OCV up);
  the two null-cycle cases raise `NoDataFound` as expected.
- Spec-conformance tests added (`test_config_columns.py` pattern); behavioral
  extras for placeholder step lists, empty selections, column reorder.
- Full suite: 239 passed. Release + re-pin next (Stage-1 task 5).
