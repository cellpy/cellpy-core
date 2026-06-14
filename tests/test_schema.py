"""Tests for the injected Schema bundle and the step-table port.

These prove the engine reads its column names from an injected ``Schema`` object
(no module-level header globals), so it is schema-agnostic and thread-safe, and
that the per-step C-rate / classification respond to the by-value ``nom_cap`` and
the injected ``raw_limits``.
"""

import pandas as pd
import pytest

from cellpycore import selectors, summarizers
from cellpycore.cell_core import CellpyCellCore, OldCellpyCellCore, Data
from cellpycore.config import RawCols, CycleCols, StepCols, Schema, default_schema
from cellpycore.legacy import HeadersNormal, HeadersSummary, HeadersStepTable


def _build_raw(nhdr: HeadersNormal) -> pd.DataFrame:
    """Build a minimal legacy-named raw DataFrame (2 cycles x charge/discharge/rest)."""
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
                        nhdr.data_point_txt: dp,
                        nhdr.test_time_txt: float(dp),
                        nhdr.step_time_txt: float(k),
                        nhdr.step_index_txt: step,
                        nhdr.cycle_index_txt: cyc,
                        nhdr.current_txt: cur,
                        nhdr.voltage_txt: volt,
                        nhdr.ref_voltage_txt: 0.0,
                        nhdr.charge_capacity_txt: ch,
                        nhdr.discharge_capacity_txt: dch,
                        nhdr.internal_resistance_txt: 0.0,
                    }
                )
                dp += 1
    return pd.DataFrame(records)


def _legacy_schema(step: HeadersStepTable = None) -> Schema:
    return Schema(
        raw=HeadersNormal(),
        cycle=HeadersSummary(),
        step=step or HeadersStepTable(),
    )


def _data_with_raw(nhdr: HeadersNormal) -> Data:
    data = Data()
    data.raw = _build_raw(nhdr)
    return data


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
    """The output column names follow the injected schema, not any global."""
    nhdr = HeadersNormal()
    shdr = HeadersStepTable()
    shdr.cycle = "CYCLE_MARKER"  # custom step-table column name
    schema = Schema(raw=nhdr, cycle=HeadersSummary(), step=shdr)

    data = _data_with_raw(nhdr)
    result = summarizers.make_step_table(data, schema=schema, nom_cap=1.0)

    assert "CYCLE_MARKER" in result.steps.columns
    assert "charge" in set(result.steps["type"])


def test_two_schemas_do_not_share_state():
    """Two cells with different schemas each emit their own column names."""
    nhdr = HeadersNormal()

    shdr_a = HeadersStepTable()
    shdr_a.cycle = "CYCLE_A"
    res_a = summarizers.make_step_table(
        _data_with_raw(nhdr), schema=Schema(nhdr, HeadersSummary(), shdr_a), nom_cap=1.0
    )

    shdr_b = HeadersStepTable()
    shdr_b.cycle = "CYCLE_B"
    res_b = summarizers.make_step_table(
        _data_with_raw(nhdr), schema=Schema(nhdr, HeadersSummary(), shdr_b), nom_cap=1.0
    )

    assert "CYCLE_A" in res_a.steps.columns and "CYCLE_A" not in res_b.steps.columns
    assert "CYCLE_B" in res_b.steps.columns and "CYCLE_B" not in res_a.steps.columns


def test_nom_cap_scales_c_rate_by_value():
    """rate_avr = abs(current_avr / nom_cap): doubling nom_cap halves the rate."""
    nhdr = HeadersNormal()
    schema = _legacy_schema()

    res1 = summarizers.make_step_table(_data_with_raw(nhdr), schema=schema, nom_cap=1.0)
    res2 = summarizers.make_step_table(_data_with_raw(nhdr), schema=schema, nom_cap=2.0)

    charge1 = res1.steps.loc[res1.steps["type"] == "charge", "rate_avr"].iloc[0]
    charge2 = res2.steps.loc[res2.steps["type"] == "charge", "rate_avr"].iloc[0]
    assert charge1 == pytest.approx(2 * charge2)


def test_raw_limits_affect_classification():
    """Step-type classification uses the supplied raw_limits, not a fixed default."""
    nhdr = HeadersNormal()
    schema = _legacy_schema()

    res_default = summarizers.make_step_table(
        _data_with_raw(nhdr), schema=schema, nom_cap=1.0
    )
    assert "charge" in set(res_default.steps["type"])

    huge_current_limit = dict(summarizers.DEFAULT_RAW_LIMITS)
    huge_current_limit["current_hard"] = 1.0e6
    res_huge = summarizers.make_step_table(
        _data_with_raw(nhdr), schema=schema, nom_cap=1.0, raw_limits=huge_current_limit
    )
    # with a huge current limit, the charge/discharge steps are no longer detected
    assert "charge" not in set(res_huge.steps["type"])


def test_generate_specific_columns_takes_factor_by_value():
    """generate_specific_summary_columns multiplies by the given factor (no pint)."""
    data = Data()
    data.summary = pd.DataFrame({"charge_capacity": [1.0, 2.0, 4.0]})
    data = summarizers.generate_specific_summary_columns(
        data, mode="gravimetric", specific_columns=["charge_capacity"],
        specific_converter=10.0,
    )
    assert list(data.summary["charge_capacity_gravimetric"]) == [10.0, 20.0, 40.0]
