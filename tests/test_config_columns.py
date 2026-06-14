"""Conformance tests: config.py column classes match docs/data_format_specifications.

These lock `RawCols` / `StepCols` / `CycleCols` to the authoritative spec tables
(`harmonized_raw.md`, `step_table.md`, `cycle_table.md`) so the three
representations cannot silently drift again. The expected column sets below are
transcribed from those specs.
"""

from cellpycore.config import RawCols, StepCols, CycleCols


def _declared_columns(cols_cls) -> dict:
    """Map declared column attribute -> its string value for a Cols subclass."""
    return {name: getattr(cols_cls, name) for name in cols_cls.__annotations__}


def _aggregates(signal: str) -> list:
    return [f"{signal}_{stat}" for stat in
            ("mean", "std", "min", "max", "first", "last", "delta")]


# --- harmonized_raw.md (authoritative, 2025-09-17) ---------------------------
RAW_EXPECTED = [
    "datapoint_num", "source_datapoint_num", "mask", "epoch_time_utc",
    "test_time", "step_time", "source_type", "source_uuid", "test_id", "step_num",
    "source_step_num",
    "step_type", "step_type_detail", "step_mode", "cycle_num", "cycle_type",
    "potential", "current", "cumulative_charge_capacity",
    "cumulative_discharge_capacity", "cumulative_charge_energy",
    "cumulative_discharge_energy", "step_charge_power", "step_discharge_power",
    "internal_resistance",
    "aux_temperature_cell", "aux_temperature_chamber", "aux_pressure_cell",
]

# --- step_table.md ----------------------------------------------------------
STEP_EXPECTED = [
    "cycle_num", "step_num", "sub_step_num", "step_type", "sub_step_type", "mask",
    "datapoint_num_first", "datapoint_num_last", "test_time_first", "test_time_last",
    *_aggregates("step_time"),
    *_aggregates("current"), *_aggregates("potential"),
    *_aggregates("charge_capacity"), *_aggregates("discharge_capacity"),
    *_aggregates("power"), *_aggregates("charge_energy"),
    *_aggregates("discharge_energy"), *_aggregates("internal_resistance"),
    "c_rate",
]

# --- cycle_table.md ---------------------------------------------------------
CYCLE_EXPECTED = [
    "cycle_num", "mask", "datapoint_num_first", "datapoint_num_last",
    "first_epoch_time_utc", "last_epoch_time_utc", "first_test_time",
    "last_test_time", "cycle_duration", "charge_duration", "discharge_duration",
    "rest_duration", "charge_capacity", "discharge_capacity",
    "charge_capacity_loss", "discharge_capacity_loss", "coulombic_difference",
    "coulombic_efficiency", "test_cumulated_charge_capacity",
    "test_cumulated_discharge_capacity", "test_cumulated_coulombic_difference",
    "test_cumulated_charge_capacity_loss", "test_cumulated_discharge_capacity_loss",
    "test_net_capacity", "charge_energy", "discharge_energy", "cycle_net_energy",
    "energy_efficiency", "test_cumulated_charge_energy",
    "test_cumulated_discharge_energy", "test_net_energy",
    "current_charge_mean", "current_charge_mean_tw", "current_charge_mean_cw",
    "current_charge_max", "current_charge_min", "current_discharge_mean",
    "current_discharge_mean_tw", "current_discharge_mean_cw",
    "current_discharge_max", "current_discharge_min",
    "potential_charge_mean", "potential_charge_mean_tw", "potential_charge_mean_cw",
    "potential_charge_max", "potential_charge_min", "potential_discharge_mean",
    "potential_discharge_mean_tw", "potential_discharge_mean_cw",
    "potential_discharge_max", "potential_discharge_min",
    "potential_start_charge", "potential_end_charge", "potential_start_discharge",
    "potential_end_discharge", "voltage_efficiency",
    "power_charge_mean", "power_charge_mean_tw", "power_charge_mean_cw",
    "power_charge_max", "power_charge_min", "power_discharge_mean",
    "power_discharge_mean_tw", "power_discharge_mean_cw", "power_discharge_max",
    "power_discharge_min", "ir_start_charge", "ir_end_charge", "ir_start_discharge",
    "ir_end_discharge", "relaxation_potential_charge",
    "relaxation_potential_discharge", "open_circuit_potential_charge",
    "open_circuit_potential_discharge", "cv_share", "cv_charge_capacity",
    "cv_charge_energy", "cv_charge_time", "cc_charge_capacity", "cc_charge_energy",
    "cc_charge_time",
]


def test_raw_cols_match_spec():
    declared = _declared_columns(RawCols)
    assert list(declared) == RAW_EXPECTED
    # each column attribute value equals its name
    assert all(declared[name] == name for name in declared)


def test_step_cols_match_spec():
    declared = _declared_columns(StepCols)
    assert list(declared) == STEP_EXPECTED
    assert all(declared[name] == name for name in declared)


def test_cycle_cols_match_spec():
    declared = _declared_columns(CycleCols)
    assert list(declared) == CYCLE_EXPECTED
    assert all(declared[name] == name for name in declared)


def test_no_legacy_raw_names():
    """The renamed/removed legacy names are gone from RawCols."""
    for gone in ("mode", "channel_status", "temperature_cell",
                 "temperature_chamber", "pressure"):
        assert gone not in RawCols.__annotations__


def test_power_not_power_capacity_in_step():
    for gone in ("power_capacity_mean", "power_capacity_delta"):
        assert gone not in StepCols.__annotations__
