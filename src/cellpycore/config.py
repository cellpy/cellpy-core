# Definitions of headers and other constants

"""
This module contains definitions of headers and other constants.

Planned features:
- It should also contain a custom dict-like object that can be used to store
the settings. It should allow for both "dot notation" and "bracket notation" to access the keys.
- It should work well with both Polars and Pandas.
- It should be extendable in case we want to add new features in the future.

"""

from dataclasses import dataclass
from enum import StrEnum


class CyclingMode(StrEnum):
    ANODE = "anode"
    OTHER = "other"


@dataclass
class BaseCols:
    __version__: str = "0.1.0"

    def __getitem__(self, key: str) -> str:
        """Allow for bracket notation"""
        return getattr(self, key)


class FlexibleCols(BaseCols):
    def __getattribute__(self, key: str) -> str:
        """Modification of the attribute can be done here.

        When implemented in the actual column classes (e.g. CycleCols), you have to add
        a comment in this docstring to show the version of the implementation.

        version 0.1.0:
        - uses the default getattr method, implemented only for showing future us
          where to put code.

        Example: adding a suffix to the attribute name.

            >> original_item = super().__getattribute__(key)
            >> # Since __getattribute__ is used for all attributes (not only the ones we defined in the class)
            >> # we need to check the type of the attribute before we can modify it.
            >> if isinstance(original_item, str):
            >>     modified_item = original_item + "_modified"
            >> else:
            >>     modified_item = original_item
            >> return modified_item

        """

        return super().__getattribute__(key)


class Cols(BaseCols):
    # Implement common additonal functionality here (e.g. to_json method).
    #
    # If we chose to use custom getattr method, swap the
    # class inheritance to FlexibleCols (will encure some performance loss).
    pass


class CycleCols(Cols):
    cycle_num: str = "cycle_num"
    datapoint_num_first: str = "datapoint_num_first"
    datapoint_num_last: str = "datapoint_num_last"
    first_epoch_time_utc: str = "first_epoch_time_utc"
    last_epoch_time_utc: str = "last_epoch_time_utc"
    first_test_time: str = "first_test_time"
    last_test_time: str = "last_test_time"
    cycle_duration: str = "cycle_duration"
    charge_duration: str = "charge_duration"
    discharge_duration: str = "discharge_duration"
    rest_duration: str = "rest_duration"
    charge_capacity: str = "charge_capacity"
    discharge_capacity: str = "discharge_capacity"
    charge_capacity_loss: str = "charge_capacity_loss"
    discharge_capacity_loss: str = "discharge_capacity_loss"
    coulombic_difference: str = "coulombic_difference"
    coulombic_efficiency: str = "coulombic_efficiency"
    test_cumulated_charge_capacity: str = "test_cumulated_charge_capacity"
    test_cumulated_discharge_capacity: str = "test_cumulated_discharge_capacity"
    test_cumulated_coulombic_difference: str = "test_cumulated_coulombic_difference"
    test_cumulated_charge_capacity_loss: str = "test_cumulated_charge_capacity_loss"
    test_cumulated_discharge_capacity_loss: str = "test_cumulated_discharge_capacity_loss"
    test_net_capacity: str = "test_net_capacity"
    charge_energy: str = "charge_energy"
    discharge_energy: str = "discharge_energy"
    cycle_net_energy: str = "cycle_net_energy"
    energy_efficiency: str = "energy_efficiency"
    test_cumulated_charge_energy: str = "test_cumulated_charge_energy"
    test_cumulated_discharge_energy: str = "test_cumulated_discharge_energy"
    test_net_energy: str = "test_net_energy"
    current_charge_mean: str = "current_charge_mean"
    current_charge_mean_tw: str = "current_charge_mean_tw"
    current_charge_mean_cw: str = "current_charge_mean_cw"
    current_charge_max: str = "current_charge_max"
    current_charge_min: str = "current_charge_min"
    current_discharge_mean: str = "current_discharge_mean"
    current_discharge_mean_tw: str = "current_discharge_mean_tw"
    current_discharge_mean_cw: str = "current_discharge_mean_cw"
    current_discharge_max: str = "current_discharge_max"
    current_discharge_min: str = "current_discharge_min"
    potential_charge_mean: str = "potential_charge_mean"
    potential_charge_mean_tw: str = "potential_charge_mean_tw"
    potential_charge_mean_cw: str = "potential_charge_mean_cw"
    potential_charge_max: str = "potential_charge_max"
    potential_charge_min: str = "potential_charge_min"
    potential_discharge_mean: str = "potential_discharge_mean"
    potential_discharge_mean_tw: str = "potential_discharge_mean_tw"
    potential_discharge_mean_cw: str = "potential_discharge_mean_cw"
    potential_discharge_max: str = "potential_discharge_max"
    potential_discharge_min: str = "potential_discharge_min"
    potential_start_charge: str = "potential_start_charge"
    potential_end_charge: str = "potential_end_charge"
    potential_start_discharge: str = "potential_start_discharge"
    potential_end_discharge: str = "potential_end_discharge"
    voltage_efficiency: str = "voltage_efficiency"
    power_charge_mean: str = "power_charge_mean"
    power_charge_mean_tw: str = "power_charge_mean_tw"
    power_charge_mean_cw: str = "power_charge_mean_cw"
    power_charge_max: str = "power_charge_max"
    power_charge_min: str = "power_charge_min"
    power_discharge_mean: str = "power_discharge_mean"
    power_discharge_mean_tw: str = "power_discharge_mean_tw"
    power_discharge_mean_cw: str = "power_discharge_mean_cw"
    power_discharge_max: str = "power_discharge_max"
    power_discharge_min: str = "power_discharge_min"
    ir_start_charge: str = "ir_start_charge"
    ir_end_charge: str = "ir_end_charge"
    ir_start_discharge: str = "ir_start_discharge"
    ir_end_discharge: str = "ir_end_discharge"
    relaxation_potential_charge: str = "relaxation_potential_charge"
    relaxation_potential_discharge: str = "relaxation_potential_discharge"
    open_circuit_potential_charge: str = "open_circuit_potential_charge"
    open_circuit_potential_discharge: str = "open_circuit_potential_discharge"
    cv_share: str = "cv_share"
    cv_charge_capacity: str = "cv_charge_capacity"
    cv_charge_energy: str = "cv_charge_energy"
    cv_charge_time: str = "cv_charge_time"
    cc_charge_capacity: str = "cc_charge_capacity"
    cc_charge_energy: str = "cc_charge_energy"
    cc_charge_time: str = "cc_charge_time"


class StepCols(Cols):
    cycle_num: str = "cycle_num"
    step_num: str = "step_num"
    sub_step_num: str = "sub_step_num"
    step_type: str = "step_type"
    sub_step_type: str = "sub_step_type"
    datapoint_num_first: str = "datapoint_num_first"
    datapoint_num_last: str = "datapoint_num_last"
    test_time_first: str = "test_time_first"
    test_time_last: str = "test_time_last"
    current_mean: str = "current_mean"
    current_std: str = "current_std"
    current_min: str = "current_min"
    current_max: str = "current_max"
    current_first: str = "current_first"
    current_last: str = "current_last"
    current_delta: str = "current_delta"
    potential_mean: str = "potential_mean"
    potential_std: str = "potential_std"
    potential_min: str = "potential_min"
    potential_max: str = "potential_max"
    potential_first: str = "potential_first"
    potential_last: str = "potential_last"
    potential_delta: str = "potential_delta"
    charge_capacity_mean: str = "charge_capacity_mean"
    charge_capacity_std: str = "charge_capacity_std"
    charge_capacity_min: str = "charge_capacity_min"
    charge_capacity_max: str = "charge_capacity_max"
    charge_capacity_first: str = "charge_capacity_first"
    charge_capacity_last: str = "charge_capacity_last"
    charge_capacity_delta: str = "charge_capacity_delta"
    discharge_capacity_mean: str = "discharge_capacity_mean"
    discharge_capacity_std: str = "discharge_capacity_std"
    discharge_capacity_min: str = "discharge_capacity_min"
    discharge_capacity_max: str = "discharge_capacity_max"
    discharge_capacity_first: str = "discharge_capacity_first"
    discharge_capacity_last: str = "discharge_capacity_last"
    discharge_capacity_delta: str = "discharge_capacity_delta"
    power_capacity_mean: str = "power_capacity_mean"
    power_capacity_std: str = "power_capacity_std"
    power_capacity_min: str = "power_capacity_min"
    power_capacity_max: str = "power_capacity_max"
    power_capacity_first: str = "power_capacity_first"
    power_capacity_last: str = "power_capacity_last"
    power_capacity_delta: str = "power_capacity_delta"
    charge_energy_mean: str = "charge_energy_mean"
    charge_energy_std: str = "charge_energy_std"
    charge_energy_min: str = "charge_energy_min"
    charge_energy_max: str = "charge_energy_max"
    charge_energy_first: str = "charge_energy_first"
    charge_energy_last: str = "charge_energy_last"
    charge_energy_delta: str = "charge_energy_delta"
    discharge_energy_mean: str = "discharge_energy_mean"
    discharge_energy_std: str = "discharge_energy_std"
    discharge_energy_min: str = "discharge_energy_min"
    discharge_energy_max: str = "discharge_energy_max"
    discharge_energy_first: str = "discharge_energy_first"
    discharge_energy_last: str = "discharge_energy_last"
    discharge_energy_delta: str = "discharge_energy_delta"


class RawCols(Cols):
    source_type: str = "source_type"
    source_uuid: str = "source_uuid"
    source_datapoint_num: str = "source_datapoint_num"
    datapoint_num: str = "datapoint_num"
    step_num: str = "step_num"
    cycle_num: str = "cycle_num"
    epoch_time_utc: str = "epoch_time_utc"
    test_time: str = "test_time"
    mode: str = "mode"
    channel_status: str = "channel_status"
    step_type: str = "step_type"
    step_type_detail: str = "step_type_detail"
    potential: str = "potential"
    current: str = "current"
    temperature_cell: str = "temperature_cell"
    temperature_chamber: str = "temperature_chamber"
    pressure: str = "pressure"
    step_cumulative_charge_capacity: str = "step_cumulative_charge_capacity"
    step_cumulative_discharge_capacity: str = "step_cumulative_discharge_capacity"


def cols_check():
    import pandas as pd
    import polars as pl

    print(80 * "-")
    print("CHECKING CycleCols")
    print(f"CycleCols.__version__: {CycleCols.__version__}")
    print(80 * "-")

    test_data = {
        "cycle_num": [1, 2, 3],
        "step_num": [4, 5, 6],
        "charge_capacity": [7, 8, 9],
    }

    cycle_cols = CycleCols()
    df = pl.DataFrame(test_data)
    df_pandas = pd.DataFrame(test_data)

    print("pandas:")
    print(df_pandas)
    print(df_pandas.columns)
    print(df_pandas.dtypes)

    print("polars:")
    print(df)
    print(df.schema)

    print(80 * "-")
    print(cycle_cols)
    print(cycle_cols.cycle_num)
    print(cycle_cols.step_num)
    print(cycle_cols.charge_capacity)
    print(80 * "-")
    print(f"{cycle_cols.cycle_num=}")
    print(f"{cycle_cols.step_num=}")
    print(f"{cycle_cols.charge_capacity=}")
    print(80 * "-")
    print(f"{cycle_cols['cycle_num']=}")
    print(f"{cycle_cols['step_num']=}")
    print(f"{cycle_cols['charge_capacity']=}")
    print(80 * "-")

    print(80 * "=")
    print("using Cols for polars")
    print(80 * "=")
    print(df.select(pl.col(cycle_cols.cycle_num)))
    print(df.select(pl.col(cycle_cols.step_num)))
    print(df.select(pl.col(cycle_cols.charge_capacity)))
    print(80 * "-")
    print(df.select(pl.col(cycle_cols["cycle_num"])))
    print(df.select(pl.col(cycle_cols["step_num"])))
    print(df.select(pl.col(cycle_cols["charge_capacity"])))

    print(80 * "=")
    print("using Cols for pandas")
    print(80 * "=")
    print(df_pandas.loc[:, cycle_cols.cycle_num])
    print(df_pandas.loc[:, cycle_cols.step_num])
    print(df_pandas.loc[:, cycle_cols.charge_capacity])
    print(80 * "-")
    print(df_pandas.loc[:, cycle_cols["cycle_num"]])
    print(df_pandas.loc[:, cycle_cols["step_num"]])
    print(df_pandas.loc[:, cycle_cols["charge_capacity"]])


if __name__ == "__main__":
    cols_check()
