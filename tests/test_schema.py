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
from cellpycore import config
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


def _build_cumulative_raw(nhdr: RawCols) -> pd.DataFrame:
    """2 cycles, each charge then discharge, with cycle-cumulative capacities held.

    Unlike ``_build_raw`` (which ends each cycle on a zero-capacity rest step), the
    cycle-end datapoint here has non-zero charge/discharge capacities (cc=0.5,
    dc=0.4), so the per-cycle summary capacities and efficiencies are meaningful.
    """
    records = []
    dp = 0
    for cyc in (1, 2):
        for k in range(5):  # charge: cc 0.1..0.5, dc 0
            records.append({
                nhdr.datapoint_num: dp, nhdr.test_time: float(dp),
                nhdr.step_time: float(k), nhdr.step_num: 1, nhdr.cycle_num: cyc,
                nhdr.current: 1.0, nhdr.potential: 3.5 + 0.01 * k,
                nhdr.cumulative_charge_capacity: 0.1 * (k + 1),
                nhdr.cumulative_discharge_capacity: 0.0,
                nhdr.internal_resistance: 0.0,
            })
            dp += 1
        for k in range(5):  # discharge: cc held 0.5, dc 0.08..0.4
            records.append({
                nhdr.datapoint_num: dp, nhdr.test_time: float(dp),
                nhdr.step_time: float(k), nhdr.step_num: 2, nhdr.cycle_num: cyc,
                nhdr.current: -1.0, nhdr.potential: 3.9 - 0.01 * k,
                nhdr.cumulative_charge_capacity: 0.5,
                nhdr.cumulative_discharge_capacity: 0.08 * (k + 1),
                nhdr.internal_resistance: 0.0,
            })
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


def test_make_summary_native_schema():
    """The native polars summary engine emits the clean CycleCols subset only."""
    nhdr = RawCols()
    schema = _native_schema()
    chdr = schema.cycle

    data = _data_with_raw(nhdr)
    summarizers.make_step_table(data, schema=schema, nom_cap=1.0)
    summarizers.make_summary(data, schema=schema)
    s = data.summary

    assert s.height == 2  # one row per cycle
    for col in (
        chdr.cycle_num, chdr.charge_capacity, chdr.discharge_capacity,
        chdr.coulombic_efficiency, chdr.coulombic_difference,
        chdr.test_cumulated_charge_capacity, chdr.potential_end_charge,
    ):
        assert col in s.columns

    # legacy-only cruft must NOT leak into the native summary (it lives in the bridge)
    for col in (
        "cumulated_ric", "shifted_charge_capacity", "charge_c_rate",
        "normalized_cycle_index", "cumulated_coulombic_efficiency", "ir_charge",
    ):
        assert col not in s.columns


def test_generate_specific_columns_takes_factor_by_value():
    """generate_specific_summary_columns multiplies by the given factor (no pint)."""
    data = Data()
    data.summary = pl.DataFrame({"charge_capacity": [1.0, 2.0, 4.0]})
    data = summarizers.generate_specific_summary_columns(
        data, mode="gravimetric", specific_columns=["charge_capacity"],
        specific_converter=10.0,
    )
    assert data.summary["charge_capacity_gravimetric"].to_list() == [10.0, 20.0, 40.0]


def test_make_summary_anode_flips_coulombic_columns():
    """TestMode.INVERTED (anode) flips CE and coulombic_difference references."""
    nhdr = RawCols()
    schema = _native_schema()
    chdr = schema.cycle

    def _summ(test_mode):
        data = Data()
        data.raw = _build_cumulative_raw(nhdr)
        summarizers.make_step_table(data, schema=schema, nom_cap=1.0)
        summarizers.make_summary(data, schema=schema, test_mode=test_mode)
        return data.summary

    s_n = _summ(config.TestMode.NORMAL)
    s_a = _summ(config.TestMode.INVERTED)

    cc = s_n[chdr.charge_capacity].to_list()
    dc = s_n[chdr.discharge_capacity].to_list()
    ce_normal = s_n[chdr.coulombic_efficiency].to_list()
    ce_anode = s_a[chdr.coulombic_efficiency].to_list()
    cd_normal = s_n[chdr.coulombic_difference].to_list()
    cd_anode = s_a[chdr.coulombic_difference].to_list()

    assert cc == pytest.approx([0.5, 0.5])
    assert dc == pytest.approx([0.4, 0.4])
    for i in range(len(cc)):
        assert ce_normal[i] == pytest.approx(100.0 * dc[i] / cc[i])
        assert ce_anode[i] == pytest.approx(100.0 * cc[i] / dc[i])
        assert cd_normal[i] == pytest.approx(cc[i] - dc[i])
        assert cd_anode[i] == pytest.approx(dc[i] - cc[i])


def test_c_rates_to_summary_native():
    """c_rates_to_summary joins per-cycle first charge/discharge C-rates (native)."""
    nhdr = RawCols()
    schema = _native_schema()
    chdr = schema.cycle

    data = _data_with_raw(nhdr)
    summarizers.make_step_table(data, schema=schema, nom_cap=2.0)
    summarizers.make_summary(data, schema=schema)
    summarizers.c_rates_to_summary(data, schema, nom_cap=1.0)

    assert chdr.charge_c_rate in data.summary.columns
    assert chdr.discharge_c_rate in data.summary.columns
    # both directions present in every cycle of the fixture -> no nulls
    assert data.summary[chdr.charge_c_rate].null_count() == 0
    assert data.summary[chdr.discharge_c_rate].null_count() == 0


def test_ir_to_summary_native():
    """ir_to_summary adds ir_charge/ir_discharge (native, default extractor)."""
    nhdr = RawCols()
    schema = _native_schema()
    chdr = schema.cycle

    data = _data_with_raw(nhdr)
    summarizers.make_step_table(data, schema=schema, nom_cap=1.0)
    summarizers.make_summary(data, schema=schema)
    summarizers.ir_to_summary(data, schema)

    assert chdr.ir_charge in data.summary.columns
    assert chdr.ir_discharge in data.summary.columns
    # the fixture has a zero internal_resistance column and every cycle has a
    # charge + discharge step -> all zeros, no missing values.
    assert data.summary[chdr.ir_charge].null_count() == 0
    assert set(data.summary[chdr.ir_charge].to_list()) == {0.0}


def _ir_raw_steps(nhdr: RawCols, shdr: StepCols):
    """Hand-built native raw + steps exercising the IR-extraction rules.

    cycle 1: charge step 1 (ir 10->11), discharge step 2 (ir 5->6),
             charge step 3 (ir 20->22)  -> last charge step is 3, last dp 22.
    cycle 2: discharge step 1 (ir 30->33) only -> no charge step (ir_charge NaN).
    """
    rows = [
        (1, 1, "charge", [10.0, 11.0]),
        (1, 2, "discharge", [5.0, 6.0]),
        (1, 3, "charge", [20.0, 22.0]),
        (2, 1, "discharge", [30.0, 33.0]),
    ]
    raw_records, step_records = [], []
    dp = 0
    for cyc, step, stype, irs in rows:
        step_records.append(
            {shdr.cycle_num: cyc, shdr.step_num: step, shdr.step_type: stype}
        )
        for ir in irs:
            raw_records.append(
                {
                    nhdr.cycle_num: cyc,
                    nhdr.step_num: step,
                    nhdr.datapoint_num: dp,
                    nhdr.internal_resistance: ir,
                }
            )
            dp += 1
    return pl.DataFrame(raw_records), pl.DataFrame(step_records)


def test_ir_to_summary_last_step_and_nan():
    """Default extractor picks the last datapoint of the last charge/discharge
    step per cycle and yields NaN when a direction's step is absent."""
    import math

    nhdr, shdr, chdr = RawCols(), StepCols(), CycleCols()
    schema = Schema(raw=nhdr, cycle=chdr, step=shdr)
    raw, steps = _ir_raw_steps(nhdr, shdr)

    data = Data()
    data.raw = raw
    data.steps = steps
    data.summary = pl.DataFrame({chdr.cycle_num: [1, 2]})

    summarizers.ir_to_summary(data, schema)
    out = data.summary.sort(chdr.cycle_num)

    charge = out[chdr.ir_charge].to_list()
    discharge = out[chdr.ir_discharge].to_list()
    assert charge[0] == 22.0  # last datapoint of the last charge step (step 3)
    assert math.isnan(charge[1])  # cycle 2 has no charge step -> NaN, not 0.0
    assert discharge[0] == 6.0  # last datapoint of the (only) discharge step
    assert discharge[1] == 33.0


def test_ir_to_summary_accepts_custom_extractor():
    """A custom SummaryExtractor passed via ir_extractor overrides the default."""
    from cellpycore.extractors import SummaryExtractor

    nhdr, shdr, chdr = RawCols(), StepCols(), CycleCols()
    schema = Schema(raw=nhdr, cycle=chdr, step=shdr)
    raw, steps = _ir_raw_steps(nhdr, shdr)

    class ConstIR(SummaryExtractor):
        def __call__(self, *, raw, steps, summary, schema):
            return pl.DataFrame(
                {
                    schema.cycle.cycle_num: [1, 2],
                    schema.cycle.ir_charge: [1.5, 2.5],
                    schema.cycle.ir_discharge: [3.5, 4.5],
                }
            )

    data = Data()
    data.raw = raw
    data.steps = steps
    data.summary = pl.DataFrame({chdr.cycle_num: [1, 2]})

    summarizers.ir_to_summary(data, schema, ir_extractor=ConstIR())
    out = data.summary.sort(chdr.cycle_num)
    assert out[chdr.ir_charge].to_list() == [1.5, 2.5]
    assert out[chdr.ir_discharge].to_list() == [3.5, 4.5]


def test_native_add_scaled_summary_columns_end_to_end():
    """The native CellpyCellCore add_scaled path runs on the polars summary."""
    cell = CellpyCellCore(initialize=False)
    nhdr = cell.schema.raw
    chdr = cell.schema.cycle

    data = _data_with_raw(nhdr)
    cell.make_core_step_table(data, nom_cap=1.0)
    cell.make_core_summary(data)
    cell.add_scaled_summary_columns(
        data,
        nom_cap_abs=1.0,
        normalization_cycles=None,
        specific_converters={"gravimetric": 10.0, "areal": 2.0, "absolute": 1.0},
    )

    assert chdr.normalized_cycle_index in data.summary.columns
    assert f"{chdr.charge_capacity}_gravimetric" in data.summary.columns
    assert f"{chdr.charge_capacity}_areal" in data.summary.columns
    # gravimetric variant is 10x the absolute charge_capacity
    base = data.summary[chdr.charge_capacity].to_list()
    grav = data.summary[f"{chdr.charge_capacity}_gravimetric"].to_list()
    for b, g in zip(base, grav):
        assert g == pytest.approx(10.0 * b)
