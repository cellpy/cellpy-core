"""Tests for the injected Schema bundle and the step-table port.

These prove the engine reads its column names from an injected ``Schema`` object
(no module-level header globals), so it is schema-agnostic and thread-safe, and
that the per-step C-rate / classification respond to the by-value ``nom_cap`` and
the injected ``raw_limits``.
"""

import pandas as pd
import polars as pl
import pytest

from cellpycore import selectors, summarizers
from cellpycore.cell_core import CellpyCellCore, OldCellpyCellCore, Data
from cellpycore.config import RawCols, CycleCols, StepCols, Schema, default_schema
from cellpycore.legacy import HeadersNormal


def _build_raw(nhdr: RawCols) -> pd.DataFrame:
    """Build a minimal native-named raw DataFrame (2 cycles x charge/discharge/rest)."""
    records = []
    dp = 0
    for cyc in (1, 2):
        for step, stype in ((1, "charge"), (2, "discharge"), (3, "rest")):
            for k in range(5):
                if stype == "charge":
                    cur, volt = 1.0, 3.5 + 0.01 * k
                    ch, dch = 0.1 * k, 0.0
                elif stype == "discharge":
                    cur, volt = -1.0, 3.9 - 0.01 * k
                    ch, dch = 0.0, 0.1 * k
                else:
                    cur, volt = 0.0, 3.7
                    ch, dch = 0.0, 0.0
                records.append(
                    {
                        nhdr.datapoint_num: dp,
                        nhdr.test_time: float(dp),
                        nhdr.step_time: float(k),
                        nhdr.step_num: step,
                        nhdr.cycle_num: cyc,
                        nhdr.current: cur,
                        nhdr.potential: volt,
                        nhdr.cumulative_charge_capacity: ch,
                        nhdr.cumulative_discharge_capacity: dch,
                        nhdr.internal_resistance: 0.0,
                    }
                )
                dp += 1
    return pd.DataFrame(records)


def _native_schema(step: StepCols = None) -> Schema:
    return Schema(raw=RawCols(), cycle=CycleCols(), step=step or StepCols())


def _data_with_raw(nhdr: RawCols) -> Data:
    data = Data()
    data.raw = _build_raw(nhdr)
    return data


def _types(steps) -> set:
    """Distinct step-type labels from a (polars) native step table."""
    return set(steps[StepCols.step_type].to_list())


def test_no_module_header_globals():
    """The globals bridge is gone: no module-level header/unit globals remain."""
    for name in ("headers_steps", "headers_summary", "headers_raw",
                 "cellpy_units", "output_units", "units"):
        assert not hasattr(summarizers, name), f"summarizers.{name} should not exist"
    for name in ("headers_step_table", "headers_summary", "headers_normal"):
        assert not hasattr(selectors, name), f"selectors.{name} should not exist"


def test_schema_property_reflects_headers():
    """CellpyCellCore.schema bundles the (possibly overridden) header instances."""
    native = CellpyCellCore(initialize=False)
    assert isinstance(native.schema.raw, RawCols)
    assert isinstance(native.schema.cycle, CycleCols)
    assert isinstance(native.schema.step, StepCols)

    legacy = OldCellpyCellCore(initialize=False)
    assert isinstance(legacy.schema.raw, HeadersNormal)
    assert legacy.schema.raw is legacy.raw_cols
    assert legacy.schema.step is legacy.step_cols

    # overriding an attribute is reflected by the property (built on access)
    legacy.raw_cols = HeadersNormal(charge_capacity_txt="CUSTOM_CHARGE")
    assert legacy.schema.raw.charge_capacity_txt == "CUSTOM_CHARGE"


def test_default_schema_is_native():
    schema = default_schema()
    assert isinstance(schema.raw, RawCols)
    assert isinstance(schema.cycle, CycleCols)
    assert isinstance(schema.step, StepCols)


def test_make_step_table_uses_injected_schema():
    """The output column names follow the injected (native) schema, not any global."""
    nhdr = RawCols()
    shdr = StepCols()
    shdr.cycle_num = "CYCLE_MARKER"  # custom step-table column name
    schema = Schema(raw=nhdr, cycle=CycleCols(), step=shdr)

    data = _data_with_raw(nhdr)
    result = summarizers.make_step_table(data, schema=schema, nom_cap=1.0)

    assert "CYCLE_MARKER" in result.steps.columns
    assert "charge" in set(result.steps[shdr.step_type].to_list())


def test_two_schemas_do_not_share_state():
    """Two cells with different schemas each emit their own column names."""
    nhdr = RawCols()

    shdr_a = StepCols()
    shdr_a.cycle_num = "CYCLE_A"
    res_a = summarizers.make_step_table(
        _data_with_raw(nhdr), schema=Schema(nhdr, CycleCols(), shdr_a), nom_cap=1.0
    )

    shdr_b = StepCols()
    shdr_b.cycle_num = "CYCLE_B"
    res_b = summarizers.make_step_table(
        _data_with_raw(nhdr), schema=Schema(nhdr, CycleCols(), shdr_b), nom_cap=1.0
    )

    assert "CYCLE_A" in res_a.steps.columns and "CYCLE_A" not in res_b.steps.columns
    assert "CYCLE_B" in res_b.steps.columns and "CYCLE_B" not in res_a.steps.columns


def test_nom_cap_scales_c_rate_by_value():
    """c_rate = abs(current_mean / nom_cap): doubling nom_cap halves the rate."""
    nhdr = RawCols()
    schema = _native_schema()

    res1 = summarizers.make_step_table(_data_with_raw(nhdr), schema=schema, nom_cap=1.0)
    res2 = summarizers.make_step_table(_data_with_raw(nhdr), schema=schema, nom_cap=2.0)

    def _charge_rate(steps):
        return (
            steps.filter(pl.col(StepCols.step_type) == "charge")[StepCols.c_rate]
            .to_list()[0]
        )

    assert _charge_rate(res1.steps) == pytest.approx(2 * _charge_rate(res2.steps))


def test_raw_limits_affect_classification():
    """Step-type classification uses the supplied raw_limits, not a fixed default."""
    nhdr = RawCols()
    schema = _native_schema()

    res_default = summarizers.make_step_table(
        _data_with_raw(nhdr), schema=schema, nom_cap=1.0
    )
    assert "charge" in _types(res_default.steps)

    huge_current_limit = dict(summarizers.DEFAULT_RAW_LIMITS)
    huge_current_limit["current_hard"] = 1.0e6
    res_huge = summarizers.make_step_table(
        _data_with_raw(nhdr), schema=schema, nom_cap=1.0, raw_limits=huge_current_limit
    )
    # with a huge current limit, the charge/discharge steps are no longer detected
    assert "charge" not in _types(res_huge.steps)


def test_generate_specific_columns_takes_factor_by_value():
    """generate_specific_summary_columns multiplies by the given factor (no pint)."""
    data = Data()
    data.summary = pd.DataFrame({"charge_capacity": [1.0, 2.0, 4.0]})
    data = summarizers.generate_specific_summary_columns(
        data, mode="gravimetric", specific_columns=["charge_capacity"],
        specific_converter=10.0,
    )
    assert list(data.summary["charge_capacity_gravimetric"]) == [10.0, 20.0, 40.0]
