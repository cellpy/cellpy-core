# Issue #118 — Stage 1.17: cellpycore.curves — spec'd capacity/OCV curve extraction

GitHub: https://github.com/cellpy/cellpy-core/issues/118
Labels: cellpy2-stage1

## Goal

Gated on the #438 decision (curve-schema home): a `curves.py` module + `CurveCols`
schema + curve-table spec doc, porting `get_cap` / `get_ccap` / `get_dcap` /
`get_ocv` selection logic (interpolation, taper trimming, forth-and-forth,
steptable override) polars-native and schema-injected — the `extractors.py`
introduction pattern (issue #23) applied to curves.

## Acceptance

- Spec doc + `CurveCols` + spec-conformance test (the `test_config_columns.py` pattern).
- Parity vs the #433 snapshots across the option matrix; intentional differences
  documented, not silent.
- Release tagged for cellpy re-pin.
