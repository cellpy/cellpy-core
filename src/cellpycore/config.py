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
    step_num: str = "step_num"
    sub_step_num: str = "sub_step_num"
    step_type: str = "step_type"
    step_mode: str = "step_mode"
    charge_capacity: str = "charge_capacity"


class StepCols(Cols):
    step_num: str = "step_num"
    sub_step_num: str = "sub_step_num"
    step_type: str = "step_type"
    step_mode: str = "step_mode"
    charge_capacity: str = "charge_capacity"
    discharge_capacity: str = "discharge_capacity"


class RawCols(Cols):
    source_type: str = "source_type"
    source_uuid: str = "source_uuid"
    source_datapoint_num: str = "source_datapoint_num"
    datapoint_num: str = "datapoint_num"
    step_num: str = "step_num"
    cycle_num: str = "cycle_num"


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
