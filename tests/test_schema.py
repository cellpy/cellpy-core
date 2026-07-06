"""Tests for the injected Schema bundle and the step-table port.

These prove the engine reads its column names from an injected ``Schema`` object
(no module-level header globals), so it is schema-agnostic and thread-safe, and
that the per-step C-rate / classification respond to the by-value ``nom_cap`` and
the injected ``raw_limits``.
"""

import pandas as pd
import polars as pl
import pytest

from cellpycore import config, summarizers
from cellpycore.cell_core import CellpyCellCore, Data, OldCellpyCellCore
from cellpycore.config import (
    CycleCols,
    RawCols,
    ResetGranularity,
    Schema,
    StepCols,
    default_schema,
)
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
            records.append(
                {
                    nhdr.datapoint_num: dp,
                    nhdr.test_time: float(dp),
                    nhdr.step_time: float(k),
                    nhdr.step_num: 1,
                    nhdr.cycle_num: cyc,
                    nhdr.current: 1.0,
                    nhdr.potential: 3.5 + 0.01 * k,
                    nhdr.cumulative_charge_capacity: 0.1 * (k + 1),
                    nhdr.cumulative_discharge_capacity: 0.0,
                    nhdr.internal_resistance: 0.0,
                }
            )
            dp += 1
        for k in range(5):  # discharge: cc held 0.5, dc 0.08..0.4
            records.append(
                {
                    nhdr.datapoint_num: dp,
                    nhdr.test_time: float(dp),
                    nhdr.step_time: float(k),
                    nhdr.step_num: 2,
                    nhdr.cycle_num: cyc,
                    nhdr.current: -1.0,
                    nhdr.potential: 3.9 - 0.01 * k,
                    nhdr.cumulative_charge_capacity: 0.5,
                    nhdr.cumulative_discharge_capacity: 0.08 * (k + 1),
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
    for name in (
        "headers_steps",
        "headers_summary",
        "headers_raw",
        "cellpy_units",
        "output_units",
        "units",
    ):
        assert not hasattr(summarizers, name), f"summarizers.{name} should not exist"


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
    result = summarizers.make_step_table(data, schema=schema)

    assert "CYCLE_MARKER" in result.steps.columns
    assert "charge" in set(result.steps[shdr.step_type].to_list())


def test_two_schemas_do_not_share_state():
    """Two cells with different schemas each emit their own column names."""
    nhdr = RawCols()

    shdr_a = StepCols()
    shdr_a.cycle_num = "CYCLE_A"
    res_a = summarizers.make_step_table(
        _data_with_raw(nhdr), schema=Schema(nhdr, CycleCols(), shdr_a)
    )

    shdr_b = StepCols()
    shdr_b.cycle_num = "CYCLE_B"
    res_b = summarizers.make_step_table(
        _data_with_raw(nhdr), schema=Schema(nhdr, CycleCols(), shdr_b)
    )

    assert "CYCLE_A" in res_a.steps.columns and "CYCLE_A" not in res_b.steps.columns
    assert "CYCLE_B" in res_b.steps.columns and "CYCLE_B" not in res_a.steps.columns


def test_make_step_table_emits_no_c_rate():
    """The base step builder emits no ``c_rate``; that is add_step_c_rate's job."""
    nhdr = RawCols()
    schema = _native_schema()

    res = summarizers.make_step_table(_data_with_raw(nhdr), schema=schema)
    assert StepCols.c_rate not in res.steps.columns


def test_nom_cap_scales_c_rate_by_value():
    """c_rate = abs(current_mean / nom_cap_abs): doubling nom_cap_abs halves the rate."""
    nhdr = RawCols()
    schema = _native_schema()

    res1 = summarizers.make_step_table(_data_with_raw(nhdr), schema=schema)
    res1 = summarizers.add_step_c_rate(res1, schema, nom_cap_abs=1.0)
    res2 = summarizers.make_step_table(_data_with_raw(nhdr), schema=schema)
    res2 = summarizers.add_step_c_rate(res2, schema, nom_cap_abs=2.0)

    def _charge_rate(steps):
        return steps.filter(pl.col(StepCols.step_type) == "charge")[
            StepCols.c_rate
        ].to_list()[0]

    assert _charge_rate(res1.steps) == pytest.approx(2 * _charge_rate(res2.steps))


def test_add_step_c_rate_uses_injected_schema():
    """add_step_c_rate honours the injected StepCols rename for ``c_rate``."""
    nhdr = RawCols()
    shdr = StepCols()
    shdr.c_rate = "RATE_MARKER"
    schema = Schema(raw=nhdr, cycle=CycleCols(), step=shdr)

    data = summarizers.make_step_table(_data_with_raw(nhdr), schema=schema)
    data = summarizers.add_step_c_rate(data, schema, nom_cap_abs=1.0)

    assert "RATE_MARKER" in data.steps.columns
    assert StepCols.c_rate not in data.steps.columns


def test_add_step_c_rate_missing_steps_raises_no_data_found():
    from cellpycore.legacy import NoDataFound

    with pytest.raises(NoDataFound, match="steps"):
        summarizers.add_step_c_rate(Data(), schema=_native_schema())


def test_deprecated_nom_cap_kwarg_warns_and_scales():
    """Old ``nom_cap=`` keyword still works but emits a DeprecationWarning (#99)."""
    nhdr = RawCols()
    schema = _native_schema()

    res_new = summarizers.make_step_table(_data_with_raw(nhdr), schema=schema)
    res_new = summarizers.add_step_c_rate(res_new, schema, nom_cap_abs=2.0)

    res_old = summarizers.make_step_table(_data_with_raw(nhdr), schema=schema)
    with pytest.warns(DeprecationWarning, match="nom_cap_abs"):
        res_old = summarizers.add_step_c_rate(res_old, schema, nom_cap=2.0)

    assert (
        res_old.steps[StepCols.c_rate].to_list()
        == res_new.steps[StepCols.c_rate].to_list()
    )


def test_deprecated_nom_cap_kwarg_on_make_core_step_table():
    """Native ``make_core_step_table`` accepts the deprecated ``nom_cap=`` (#99)."""
    core = CellpyCellCore(initialize=False)
    data = _data_with_raw(core.schema.raw)

    with pytest.warns(DeprecationWarning, match="nom_cap_abs"):
        data = core.make_core_step_table(data, nom_cap=1.0)

    assert core.schema.step.c_rate in data.steps.columns


def test_raw_limits_affect_classification():
    """Step-type classification uses the supplied raw_limits, not a fixed default."""
    nhdr = RawCols()
    schema = _native_schema()

    res_default = summarizers.make_step_table(_data_with_raw(nhdr), schema=schema)
    assert "charge" in _types(res_default.steps)

    huge_current_limit = dict(summarizers.DEFAULT_RAW_LIMITS)
    huge_current_limit["current_hard"] = 1.0e6
    res_huge = summarizers.make_step_table(
        _data_with_raw(nhdr), schema=schema, raw_limits=huge_current_limit
    )
    # with a huge current limit, the charge/discharge steps are no longer detected
    assert "charge" not in _types(res_huge.steps)


def test_make_step_table_missing_raw_raises_no_data_found():
    from cellpycore.legacy import NoDataFound

    with pytest.raises(NoDataFound, match="raw"):
        summarizers.make_step_table(Data(), schema=_native_schema())


def test_make_step_table_missing_columns_are_all_named():
    nhdr = RawCols()
    data = Data()
    data.raw = _build_raw(nhdr).drop(columns=[nhdr.cycle_num, nhdr.step_num])
    with pytest.raises(ValueError) as excinfo:
        summarizers.make_step_table(data, schema=_native_schema())
    assert nhdr.cycle_num in str(excinfo.value)
    assert nhdr.step_num in str(excinfo.value)


def test_make_summary_missing_steps_raises_no_data_found():
    from cellpycore.legacy import NoDataFound

    data = _data_with_raw(RawCols())
    with pytest.raises(NoDataFound, match="steps"):
        summarizers.make_summary(data, schema=_native_schema())


def test_make_summary_missing_raw_columns_are_named():
    nhdr = RawCols()
    schema = _native_schema()
    data = _data_with_raw(nhdr)
    summarizers.make_step_table(data, schema=schema)
    data.raw = data.raw.drop(columns=[nhdr.cumulative_charge_capacity])
    with pytest.raises(ValueError, match=nhdr.cumulative_charge_capacity):
        summarizers.make_summary(data, schema=schema)


def test_override_raw_limits_zero_is_honoured():
    """Regression for the falsy-override bug: an explicit 0.0 override must win.

    With ``current_hard=0.0`` the no-current mask ``(|max| + |min|) < 0`` is
    always false, so a zero-current step with slight potential drift can no
    longer be classified as ``rest`` (and the drift keeps the ``ir`` no-change
    rule out of play), leaving it uncategorized.
    """
    nhdr = RawCols()
    schema = _native_schema()

    # One zero-current step with a slight potential drift: "rest" under the
    # default current_hard, but neither "rest" nor "ir" when current_hard=0.0.
    records = [
        {
            nhdr.datapoint_num: k,
            nhdr.test_time: float(k),
            nhdr.step_time: float(k),
            nhdr.step_num: 1,
            nhdr.cycle_num: 1,
            nhdr.current: 0.0,
            nhdr.potential: 3.7 + 0.001 * k,
            nhdr.cumulative_charge_capacity: 0.0,
            nhdr.cumulative_discharge_capacity: 0.0,
            nhdr.internal_resistance: 0.0,
        }
        for k in range(5)
    ]

    def _fresh_data() -> Data:
        data = Data()
        data.raw = pd.DataFrame(records)
        return data

    res_default = summarizers.make_step_table(_fresh_data(), schema=schema)
    assert _types(res_default.steps) == {"rest"}

    res_zero = summarizers.make_step_table(
        _fresh_data(),
        schema=schema,
        override_raw_limits={"current_hard": 0.0},
    )
    assert "rest" not in _types(res_zero.steps)


def test_make_summary_native_schema():
    """The native polars summary engine emits the clean CycleCols subset only."""
    nhdr = RawCols()
    schema = _native_schema()
    chdr = schema.cycle

    data = _data_with_raw(nhdr)
    summarizers.make_step_table(data, schema=schema)
    summarizers.make_summary(data, schema=schema)
    s = data.summary

    assert s.height == 2  # one row per cycle
    for col in (
        chdr.cycle_num,
        chdr.charge_capacity,
        chdr.discharge_capacity,
        chdr.coulombic_efficiency,
        chdr.coulombic_difference,
        chdr.test_cumulated_charge_capacity,
        chdr.potential_end_charge,
    ):
        assert col in s.columns

    # legacy-only cruft must NOT leak into the native summary (it lives in the bridge)
    for col in (
        "cumulated_ric",
        "shifted_charge_capacity",
        "charge_c_rate",
        "normalized_cycle_index",
        "cumulated_coulombic_efficiency",
        "ir_charge",
    ):
        assert col not in s.columns


def test_generate_specific_columns_takes_factor_by_value():
    """generate_specific_summary_columns multiplies by the given factor (no pint)."""
    data = Data()
    data.summary = pl.DataFrame({"charge_capacity": [1.0, 2.0, 4.0]})
    data = summarizers.generate_specific_summary_columns(
        data,
        mode="gravimetric",
        specific_columns=["charge_capacity"],
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
        summarizers.make_step_table(data, schema=schema)
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


# --- issue #70: stat-column contract + cycle_mode default --------------------
_STAT_SUFFIXES = ("mean", "std", "min", "max", "first", "last", "delta")

_STEP_TABLE_BASES = (
    "datapoint_num",
    "test_time",
    "step_time",
    "current",
    "potential",
    "charge_capacity",
    "discharge_capacity",
    "internal_resistance",
)


def test_step_table_stat_columns_match_stepcols_defaults():
    """Per-step stat columns follow the fixed ``<base>_<stat>`` engine contract."""
    schema = default_schema()
    shdr = schema.step
    data = Data()
    data.raw = _build_raw(RawCols())

    summarizers.make_step_table(data, schema=schema)
    steps = data.steps

    for base in _STEP_TABLE_BASES:
        for stat in _STAT_SUFFIXES:
            col = f"{base}_{stat}"
            assert col in steps.columns
            attr = f"{base}_{stat}"
            if hasattr(shdr, attr):
                assert getattr(shdr, attr) == col


def test_default_cycle_mode_is_normal_convention():
    """Fresh Data() with unset cycle_mode uses NORMAL CE via CellpyCellCore."""
    nhdr = RawCols()
    chdr = default_schema().cycle
    data = Data()
    data.raw = _build_cumulative_raw(nhdr)

    core = CellpyCellCore()
    core.data = data
    assert core.cycle_mode is None

    data = core.make_core_step_table(data, nom_cap_abs=1.0)
    data = core.make_core_summary(data)
    s = data.summary

    cc = s[chdr.charge_capacity].to_list()
    dc = s[chdr.discharge_capacity].to_list()
    ce = s[chdr.coulombic_efficiency].to_list()
    cd = s[chdr.coulombic_difference].to_list()
    for i in range(len(cc)):
        assert ce[i] == pytest.approx(100.0 * dc[i] / cc[i])
        assert cd[i] == pytest.approx(cc[i] - dc[i])


def test_cycle_mode_anode_via_cellpy_cell_core():
    """Explicit cycle_mode='anode' still selects INVERTED CE direction."""
    nhdr = RawCols()
    chdr = default_schema().cycle
    data = Data()
    data.raw = _build_cumulative_raw(nhdr)

    core = CellpyCellCore()
    core.data = data
    core.cycle_mode = "anode"

    data = core.make_core_step_table(data, nom_cap_abs=1.0)
    data = core.make_core_summary(data)
    s = data.summary

    cc = s[chdr.charge_capacity].to_list()
    dc = s[chdr.discharge_capacity].to_list()
    ce = s[chdr.coulombic_efficiency].to_list()
    cd = s[chdr.coulombic_difference].to_list()
    for i in range(len(cc)):
        assert ce[i] == pytest.approx(100.0 * cc[i] / dc[i])
        assert cd[i] == pytest.approx(dc[i] - cc[i])


def test_initialized_and_uninitialized_core_share_cycle_mode_default():
    """initialize=True vs False must not diverge on default polarity."""
    assert CellpyCellCore(initialize=False).cycle_mode is None
    assert CellpyCellCore(initialize=True).cycle_mode is None


def test_c_rates_to_summary_native():
    """c_rates_to_summary joins per-cycle first charge/discharge C-rates (native)."""
    nhdr = RawCols()
    schema = _native_schema()
    chdr = schema.cycle

    data = _data_with_raw(nhdr)
    summarizers.make_step_table(data, schema=schema)
    summarizers.add_step_c_rate(data, schema, nom_cap_abs=2.0)
    summarizers.make_summary(data, schema=schema)
    summarizers.c_rates_to_summary(data, schema, nom_cap_abs=1.0)

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
    summarizers.make_step_table(data, schema=schema)
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
    cell.make_core_step_table(data, nom_cap_abs=1.0)
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


def test_native_add_scaled_summary_columns_with_cell_meta():
    """Units fallback via ``cell_meta`` works without ``specific_converters``."""
    pytest.importorskip("pint")

    from cellpycore.metadata.models import CellMeta

    cell = CellpyCellCore(initialize=False)
    nhdr = cell.schema.raw
    chdr = cell.schema.cycle

    data = _data_with_raw(nhdr)
    cell.make_core_step_table(data, nom_cap_abs=1.0)
    cell.make_core_summary(data)
    cell.add_scaled_summary_columns(
        data,
        nom_cap_abs=1.0,
        normalization_cycles=None,
        specifics=["gravimetric"],
        cell_meta=CellMeta(mass=2.0),
    )

    base = data.summary[chdr.charge_capacity].to_list()
    grav = data.summary[f"{chdr.charge_capacity}_gravimetric"].to_list()
    for b, g in zip(base, grav):
        assert g == pytest.approx(500.0 * b)


# --- issue #41: per-test key + composite group keys -------------------------
def _build_merged_raw(nhdr: RawCols) -> pd.DataFrame:
    """Two tests (test_id 0 and 1) with **overlapping** cycle_num/step_num.

    Each test has 2 cycles; each cycle is charge (step 1, cc 0.1..0.5) then
    discharge (step 2, dc 0.08..0.4, cc held 0.5). ``datapoint_num`` stays globally
    unique across the merged object; ``(cycle_num, step_num)`` collide across
    tests, so anything keyed on cycle alone would mix them.
    """
    records = []
    dp = 0
    for test_id in (0, 1):
        # slightly different capacities per test so cross-test leakage is visible
        scale = 1.0 if test_id == 0 else 2.0
        for cyc in (1, 2):
            for k in range(5):  # charge
                records.append(
                    {
                        nhdr.test_id: test_id,
                        nhdr.datapoint_num: dp,
                        nhdr.test_time: float(dp),
                        nhdr.step_time: float(k),
                        nhdr.step_num: 1,
                        nhdr.cycle_num: cyc,
                        nhdr.current: 1.0,
                        nhdr.potential: 3.5 + 0.01 * k,
                        nhdr.cumulative_charge_capacity: scale * 0.1 * (k + 1),
                        nhdr.cumulative_discharge_capacity: 0.0,
                        nhdr.internal_resistance: 0.0,
                    }
                )
                dp += 1
            for k in range(5):  # discharge
                records.append(
                    {
                        nhdr.test_id: test_id,
                        nhdr.datapoint_num: dp,
                        nhdr.test_time: float(dp),
                        nhdr.step_time: float(k),
                        nhdr.step_num: 2,
                        nhdr.cycle_num: cyc,
                        nhdr.current: -1.0,
                        nhdr.potential: 3.9 - 0.01 * k,
                        nhdr.cumulative_charge_capacity: scale * 0.5,
                        nhdr.cumulative_discharge_capacity: scale * 0.08 * (k + 1),
                        nhdr.internal_resistance: 0.0,
                    }
                )
                dp += 1
    return pd.DataFrame(records)


def test_merged_object_step_table_isolated_per_test():
    """A merged object (2 tests, overlapping cycle/step) keeps every step row.

    Without the composite ``(test_id, cycle_num, step_num)`` key the four
    colliding (cycle, step) pairs shared by the two tests would collapse.
    """
    nhdr = RawCols()
    schema = _native_schema()
    shdr = schema.step

    data = Data()
    data.raw = _build_merged_raw(nhdr)
    summarizers.make_step_table(data, schema=schema)
    steps = data.steps

    # 2 tests * 2 cycles * 2 steps = 8 rows, and test_id present with both tests.
    assert steps.height == 8
    assert set(steps[shdr.test_id].to_list()) == {0, 1}
    # each (test_id, cycle_num, step_num) triple is unique (no cross-test collapse)
    key = steps.select(shdr.test_id, shdr.cycle_num, shdr.step_num)
    assert key.n_unique() == 8


def test_merged_object_summary_cumulation_resets_per_test():
    """Per-cycle cumulations restart at each test; no capacity leaks across tests."""
    nhdr = RawCols()
    schema = _native_schema()
    chdr = schema.cycle

    data = Data()
    data.raw = _build_merged_raw(nhdr)
    summarizers.make_step_table(data, schema=schema)
    summarizers.make_summary(data, schema=schema)
    s = data.summary.sort([chdr.test_id, chdr.cycle_num])

    # 2 tests * 2 cycles = 4 rows.
    assert s.height == 4
    assert s[chdr.test_id].to_list() == [0, 0, 1, 1]

    cc = s[chdr.charge_capacity].to_list()
    cum = s[chdr.test_cumulated_charge_capacity].to_list()
    loss = s[chdr.charge_capacity_loss].to_list()

    # test 0: cc = [0.5, 0.5]; test 1: cc = [1.0, 1.0] (scale 2x)
    assert cc == pytest.approx([0.5, 0.5, 1.0, 1.0])
    # cumulation restarts per test: first cycle of each test == its own cc
    assert cum[0] == pytest.approx(cc[0])  # test 0, cycle 1
    assert cum[1] == pytest.approx(cc[0] + cc[1])  # test 0, cycle 2
    assert cum[2] == pytest.approx(cc[2])  # test 1, cycle 1 -> RESET
    assert cum[3] == pytest.approx(cc[2] + cc[3])  # test 1, cycle 2
    # first-cycle capacity loss is null within each test (shift is per-test)
    import math

    assert loss[0] is None or math.isnan(loss[0])
    assert loss[2] is None or math.isnan(loss[2])


def test_single_test_defaults_test_id_to_zero():
    """A raw frame without test_id yields tables whose test_id column is all 0."""
    nhdr = RawCols()
    schema = _native_schema()
    shdr, chdr = schema.step, schema.cycle

    data = _data_with_raw(nhdr)  # _build_raw has no test_id column
    assert nhdr.test_id not in data.raw.columns

    summarizers.make_step_table(data, schema=schema)
    summarizers.make_summary(data, schema=schema)

    assert set(data.steps[shdr.test_id].to_list()) == {0}
    assert set(data.summary[chdr.test_id].to_list()) == {0}


# --- issue #42: reset-granularity normalization ----------------------------
def _build_step_cumulative_raw(nhdr: RawCols) -> pd.DataFrame:
    """Same increments as ``_build_cumulative_raw`` but counters reset per step.

    Each capacity column restarts at the start of every step, so within the
    discharge step the (inactive) charge capacity is 0 rather than the held
    cycle-cumulative 0.5. Normalizing this to cycle-cumulative must reproduce
    ``_build_cumulative_raw``.
    """
    records = []
    dp = 0
    for cyc in (1, 2):
        for k in range(5):  # charge step: cc restarts at 0 -> 0.1..0.5, dc 0
            records.append(
                {
                    nhdr.datapoint_num: dp,
                    nhdr.test_time: float(dp),
                    nhdr.step_time: float(k),
                    nhdr.step_num: 1,
                    nhdr.cycle_num: cyc,
                    nhdr.current: 1.0,
                    nhdr.potential: 3.5 + 0.01 * k,
                    nhdr.cumulative_charge_capacity: 0.1 * (k + 1),
                    nhdr.cumulative_discharge_capacity: 0.0,
                    nhdr.internal_resistance: 0.0,
                }
            )
            dp += 1
        for k in range(5):  # discharge step: cc restarts at 0, dc 0.08..0.4
            records.append(
                {
                    nhdr.datapoint_num: dp,
                    nhdr.test_time: float(dp),
                    nhdr.step_time: float(k),
                    nhdr.step_num: 2,
                    nhdr.cycle_num: cyc,
                    nhdr.current: -1.0,
                    nhdr.potential: 3.9 - 0.01 * k,
                    nhdr.cumulative_charge_capacity: 0.0,
                    nhdr.cumulative_discharge_capacity: 0.08 * (k + 1),
                    nhdr.internal_resistance: 0.0,
                }
            )
            dp += 1
    return pd.DataFrame(records)


def _build_test_cumulative_raw(nhdr: RawCols) -> pd.DataFrame:
    """Same increments as ``_build_cumulative_raw`` but counters never reset.

    Capacities accumulate across the whole test (cycle 2 charge continues from
    cycle 1's 0.5, etc.). Normalizing to cycle-cumulative must reproduce
    ``_build_cumulative_raw``.
    """
    records = []
    dp = 0
    cc = 0.0  # running test-cumulative charge capacity
    dc = 0.0  # running test-cumulative discharge capacity
    for cyc in (1, 2):
        for k in range(5):  # charge: cc grows by 0.1/row, dc held
            cc += 0.1
            records.append(
                {
                    nhdr.datapoint_num: dp,
                    nhdr.test_time: float(dp),
                    nhdr.step_time: float(k),
                    nhdr.step_num: 1,
                    nhdr.cycle_num: cyc,
                    nhdr.current: 1.0,
                    nhdr.potential: 3.5 + 0.01 * k,
                    nhdr.cumulative_charge_capacity: cc,
                    nhdr.cumulative_discharge_capacity: dc,
                    nhdr.internal_resistance: 0.0,
                }
            )
            dp += 1
        for k in range(5):  # discharge: dc grows by 0.08/row, cc held
            dc += 0.08
            records.append(
                {
                    nhdr.datapoint_num: dp,
                    nhdr.test_time: float(dp),
                    nhdr.step_time: float(k),
                    nhdr.step_num: 2,
                    nhdr.cycle_num: cyc,
                    nhdr.current: -1.0,
                    nhdr.potential: 3.9 - 0.01 * k,
                    nhdr.cumulative_charge_capacity: cc,
                    nhdr.cumulative_discharge_capacity: dc,
                    nhdr.internal_resistance: 0.0,
                }
            )
            dp += 1
    return pd.DataFrame(records)


def _cap_lists(raw) -> tuple:
    """Return the (charge, discharge) cumulative capacity lists, datapoint-ordered."""
    nhdr = RawCols()
    if not isinstance(raw, pl.DataFrame):
        raw = pl.from_pandas(raw)
    raw = raw.sort(nhdr.datapoint_num)
    return (
        raw[nhdr.cumulative_charge_capacity].to_list(),
        raw[nhdr.cumulative_discharge_capacity].to_list(),
    )


@pytest.mark.parametrize(
    "builder, granularity",
    [
        (_build_step_cumulative_raw, ResetGranularity.STEP),
        (_build_test_cumulative_raw, ResetGranularity.TEST),
    ],
)
def test_normalize_capacity_granularity_matches_cycle_oracle(builder, granularity):
    """STEP / TEST cumulative raw normalizes to the cycle-cumulative oracle."""
    nhdr = RawCols()
    schema = _native_schema()

    data = Data()
    data.raw = builder(nhdr)
    summarizers.normalize_capacity_granularity(data, schema, granularity)

    got_cc, got_dc = _cap_lists(data.raw)
    exp_cc, exp_dc = _cap_lists(_build_cumulative_raw(nhdr))
    assert got_cc == pytest.approx(exp_cc)
    assert got_dc == pytest.approx(exp_dc)


# --- issue #43: ref_potential (reference electrode) --------------------------
def _ref_stat_columns(shdr: StepCols) -> list:
    return [
        shdr.ref_potential_mean,
        shdr.ref_potential_std,
        shdr.ref_potential_min,
        shdr.ref_potential_max,
        shdr.ref_potential_first,
        shdr.ref_potential_last,
        shdr.ref_potential_delta,
    ]


def test_step_table_aggregates_ref_potential_when_present():
    """Raw with ref_potential yields all seven ref_potential_* step aggregates."""
    nhdr = RawCols()
    schema = _native_schema()
    shdr = schema.step

    data = Data()
    raw = _build_raw(nhdr)
    raw[nhdr.ref_potential] = raw[nhdr.potential] - 0.2
    data.raw = raw

    summarizers.make_step_table(data, schema=schema)
    steps = data.steps

    for col in _ref_stat_columns(shdr):
        assert col in steps.columns

    # sanity: min <= mean <= max, and first/last match the raw step boundaries
    first_step = steps.sort([shdr.cycle_num, shdr.step_num]).head(1)
    mean = first_step[shdr.ref_potential_mean][0]
    assert first_step[shdr.ref_potential_min][0] <= mean
    assert mean <= first_step[shdr.ref_potential_max][0]
    ref_step1 = raw.loc[
        (raw[nhdr.cycle_num] == 1) & (raw[nhdr.step_num] == 1), nhdr.ref_potential
    ]
    assert first_step[shdr.ref_potential_first][0] == pytest.approx(ref_step1.iloc[0])
    assert first_step[shdr.ref_potential_last][0] == pytest.approx(ref_step1.iloc[-1])


def test_step_table_skips_ref_potential_when_absent():
    """Raw without ref_potential yields no ref_potential_* columns, engine unaffected."""
    nhdr = RawCols()
    schema = _native_schema()
    shdr = schema.step

    data = _data_with_raw(nhdr)  # _build_raw carries no ref_potential
    assert nhdr.ref_potential not in data.raw.columns

    summarizers.make_step_table(data, schema=schema)
    steps = data.steps

    for col in _ref_stat_columns(shdr):
        assert col not in steps.columns
    # the rest of the engine output is unaffected
    assert "charge" in _types(steps)


def test_mock_raw_data_carries_ref_potential():
    """The synthetic mock raw fixture exercises the ref_potential column."""
    from cellpycore.testing.mock_data import create_raw_data

    nhdr = RawCols()
    raw = create_raw_data()
    assert nhdr.ref_potential in raw.columns
    # constant offset vs the cell potential (see testing.mock_data.create_raw_data)
    diff = (raw[nhdr.potential] - raw[nhdr.ref_potential]).unique().to_list()
    assert diff == pytest.approx([0.2])


def test_normalize_capacity_granularity_cycle_is_noop():
    """A CYCLE input is returned untouched (goldens stay byte-stable)."""
    nhdr = RawCols()
    schema = _native_schema()

    original = _build_cumulative_raw(nhdr)
    data = Data()
    data.raw = original
    result = summarizers.normalize_capacity_granularity(
        data, schema, ResetGranularity.CYCLE
    )

    # untouched: same object, unchanged values
    assert result.raw is original
    got_cc, got_dc = _cap_lists(result.raw)
    exp_cc, exp_dc = _cap_lists(original)
    assert got_cc == pytest.approx(exp_cc)
    assert got_dc == pytest.approx(exp_dc)
