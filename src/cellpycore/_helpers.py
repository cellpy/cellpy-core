"""Helper functions only intended for development purposes  (e.g. for creating mock data)."""

from typing import TypeVar

DataFrame = TypeVar("DataFrame")


def create_raw_data() -> DataFrame:
    """Create mock raw battery testing data with realistic values.

    TODO: This function was generated using AI and has not been checked for correctness!

    Note that this function is called separately for each test that uses the mock_data_with_raw fixture.
    If the test-suite is getting slow, consider caching the result of this function or using a different approach.
    """
    import polars as pl
    from cellpycore.config import RawCols

    # Create a RawCols instance to get column names
    raw_cols = RawCols()

    # Generate realistic battery testing data
    n_points = 1000  # Number of data points

    # Create time series data
    test_time = pl.Series(raw_cols.test_time, range(n_points), dtype=pl.Float64)
    epoch_time_utc = pl.Series(
        raw_cols.epoch_time_utc,
        range(1609459200, 1609459200 + n_points),
        dtype=pl.Int64,
    )

    # Generate cycle and step data
    cycle_num = pl.Series(
        raw_cols.cycle_num, [i // 100 for i in range(n_points)], dtype=pl.Int64
    )
    step_num = pl.Series(
        raw_cols.step_num, [(i % 100) // 10 for i in range(n_points)], dtype=pl.Int64
    )
    datapoint_num = pl.Series(raw_cols.datapoint_num, range(n_points), dtype=pl.Int64)
    source_datapoint_num = pl.Series(
        raw_cols.source_datapoint_num, range(n_points), dtype=pl.Int64
    )

    # Generate step types (charge, discharge, rest)
    step_types = []
    for i in range(n_points):
        step_idx = i % 10
        if step_idx < 3:
            step_types.append("charge")
        elif step_idx < 6:
            step_types.append("discharge")
        else:
            step_types.append("rest")

    step_type = pl.Series(raw_cols.step_type, step_types, dtype=pl.Utf8)
    step_type_detail = pl.Series(
        raw_cols.step_type_detail, [f"{t}_cc" for t in step_types], dtype=pl.Utf8
    )

    # Generate current data (charge: positive, discharge: negative, rest: 0)
    current = []
    for i, st in enumerate(step_types):
        if st == "charge":
            current.append(1.0 + (i % 5) * 0.1)  # 1.0 to 1.4 A
        elif st == "discharge":
            current.append(-1.0 - (i % 5) * 0.1)  # -1.0 to -1.4 A
        else:
            current.append(0.0)

    current = pl.Series(raw_cols.current, current, dtype=pl.Float64)

    # Generate potential data (voltage)
    potential = []
    base_voltage = 3.7  # Typical Li-ion voltage
    for i, st in enumerate(step_types):
        if st == "charge":
            # Voltage increases during charge
            potential.append(base_voltage + (i % 100) * 0.01)
        elif st == "discharge":
            # Voltage decreases during discharge
            potential.append(base_voltage - (i % 100) * 0.01)
        else:
            # Rest voltage
            potential.append(base_voltage + (i % 10) * 0.001)

    potential = pl.Series(raw_cols.potential, potential, dtype=pl.Float64)

    # Generate cumulative capacities
    step_cumulative_charge_capacity = []
    step_cumulative_discharge_capacity = []
    charge_cap = 0.0
    discharge_cap = 0.0

    for i, (curr, st) in enumerate(zip(current, step_types)):
        if st == "charge":
            charge_cap += abs(curr) * 0.1  # Assuming 0.1 hour time step
        elif st == "discharge":
            discharge_cap += abs(curr) * 0.1
        step_cumulative_charge_capacity.append(charge_cap)
        step_cumulative_discharge_capacity.append(discharge_cap)

    step_cumulative_charge_capacity = pl.Series(
        raw_cols.step_cumulative_charge_capacity,
        step_cumulative_charge_capacity,
        dtype=pl.Float64,
    )
    step_cumulative_discharge_capacity = pl.Series(
        raw_cols.step_cumulative_discharge_capacity,
        step_cumulative_discharge_capacity,
        dtype=pl.Float64,
    )

    # Generate temperature data
    temperature_cell = pl.Series(
        raw_cols.temperature_cell,
        [25.0 + (i % 20) * 0.5 for i in range(n_points)],
        dtype=pl.Float64,
    )
    temperature_chamber = pl.Series(
        raw_cols.temperature_chamber,
        [25.0 + (i % 10) * 0.2 for i in range(n_points)],
        dtype=pl.Float64,
    )

    # Generate other metadata
    source_type = pl.Series(raw_cols.source_type, ["maccor"] * n_points, dtype=pl.Utf8)
    source_uuid = pl.Series(
        raw_cols.source_uuid, [f"test_{i:06d}" for i in range(n_points)], dtype=pl.Utf8
    )
    mode = pl.Series(raw_cols.mode, ["galvanostatic"] * n_points, dtype=pl.Utf8)
    channel_status = pl.Series(
        raw_cols.channel_status, ["active"] * n_points, dtype=pl.Utf8
    )
    pressure = pl.Series(
        raw_cols.pressure,
        [101325.0 + (i % 100) * 10 for i in range(n_points)],
        dtype=pl.Float64,
    )

    # Create the DataFrame using the column names from RawCols
    data = {
        raw_cols.source_type: source_type,
        raw_cols.source_uuid: source_uuid,
        raw_cols.source_datapoint_num: source_datapoint_num,
        raw_cols.datapoint_num: datapoint_num,
        raw_cols.step_num: step_num,
        raw_cols.cycle_num: cycle_num,
        raw_cols.epoch_time_utc: epoch_time_utc,
        raw_cols.test_time: test_time,
        raw_cols.mode: mode,
        raw_cols.channel_status: channel_status,
        raw_cols.step_type: step_type,
        raw_cols.step_type_detail: step_type_detail,
        raw_cols.potential: potential,
        raw_cols.current: current,
        raw_cols.temperature_cell: temperature_cell,
        raw_cols.temperature_chamber: temperature_chamber,
        raw_cols.pressure: pressure,
        raw_cols.step_cumulative_charge_capacity: step_cumulative_charge_capacity,
        raw_cols.step_cumulative_discharge_capacity: step_cumulative_discharge_capacity,
    }

    return pl.DataFrame(data)
