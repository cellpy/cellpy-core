# Status — issue #115 (Stage 1.13)

- [x] Done

## 2026-07-14

- Implemented `convert_value`, `calculate_scaler`, `validate_units` in
  `src/cellpycore/units/converters.py`; exported from `cellpycore.units`.
- Recorded the label decision: `temperature="C"` means Celsius (validated as
  `degC`, never coulomb); `frequency="hz"` accepted as hertz — handled by
  `_PINT_LABEL_ALIASES`, spec labels preserved.
- Tests: 17 new cases in `tests/test_units_converters.py`; pint-optional guard
  extended in `tests/test_units_optional.py`. Full suite: 196 passed.
- Follow-up (not this issue): cellpy #451 wraps these after release + re-pin.
