# Definitions of headers and other constants

"""
This module contains definitions of headers and other constants.

Planned features:
- It should also contain a custom dict-like object that can be used to store
the settings. It should allow for both "dot notation" and "bracket notation" to access the keys.
- It should work well with both Polars and Pandas.

Other ideas:
- Also include the units used by cellpycore. Could be a good idea to have a object that
has convenient methods for converting between units, or make using e.g. pint easier for the coders.

COMMENT: this file can most likely be deleted.

"""

from dataclasses import dataclass, field
from enum import StrEnum, Enum
import polars as pl


@dataclass
class Cols:
    __version__: str = "1.0.0"
    

class CycleCols(Cols):
    cycle_num: str = "cycle_num"
    step_num: str = "step_num"
    sub_step_num: str = "sub_step_num"
    step_type: str = "step_type"
    step_mode: str = "step_mode"
    charge_capacity: str = "charge_capacity"



class SimpleCols(StrEnum):
    __version__: str = "1.0.0"
    A: str = "col1"
    B: str = "col2"
    C: str = "col3"


class SuperDuperColsBase(str, Enum):
    # problems with this: not clear how to extend the class with new members programmatically
    def __new__(
        cls, value: str, unit: str | None = None, dtype: pl.DataType | None = None
    ):
        obj = str.__new__(cls, value)
        obj._value_ = value
        # consider converting unit to a pint unit object:
        obj.unit = unit
        # consider converting to pl.DataType object if it is a string:
        obj.dtype = dtype
        return obj

    @property
    def value(self) -> str:
        return self._value_

    @property
    def is_aux(self) -> bool:
        if self._name_.lower().startswith("aux_"):
            return True
        return False

    @classmethod
    def to_dict(self) -> dict:
        d = {}
        for label, member in self.__members__.items():
            value = str(member.value)
            unit = str(member.unit) if member.unit is not None else None
            dtype = str(member.dtype) if member.dtype is not None else None
            d[label] = {
                "value": value,
                "unit": unit,
                "dtype": dtype,
            }
        return d


class SuperDuperCols(SuperDuperColsBase):
    __version__: str = "0.0.1"

    # TODO: dtype should be a python native "dtype object" if it exists, or a pl.DataType? Using str for now.
    #       It is also possible to convert from str to pl.DataType in the __new__ method, I guess.
    A: list[str, str | None, pl.DataType | None] = "col1", "V", pl.Float64
    B: list[str, str | None, pl.DataType | None] = "col2", "mAh/g", pl.Float64
    C: list[str, str | None, pl.DataType | None] = "col3", "s", pl.Float64
    # Does it work if we don't provide the unit and dtype? YES!
    D = "col4"


def super_duper_cols_check():
    import pandas as pd
    import polars as pl

    print(80 * "-")
    print("CHECKING SuperDuperCols")
    print(f"SuperDuperCols.__version__: {SuperDuperCols.__version__}")
    print(80 * "-")

    print(f"{SuperDuperCols.to_dict()=}")
    print(80 * "-")

    print("Proper one:")
    print(f"{SuperDuperCols.A=}")
    print(f"{SuperDuperCols.A.value=}")
    print(f"{SuperDuperCols.A.unit=}")
    print(f"{SuperDuperCols.A.dtype=}")
    print(f"{SuperDuperCols.A.is_aux=}")

    print("Not so proper one:")
    print(f"{SuperDuperCols.D=}")
    print(f"{SuperDuperCols.D.value=}")
    print(f"{SuperDuperCols.D.unit=}")
    print(f"{SuperDuperCols.D.dtype=}")

    test_data = {
        "col1": [1, 2, 3],
        "col2": [4, 5, 6],
        "col3": [7, 8, 9],
    }

    df = pl.DataFrame(test_data)
    df_pandas = pd.DataFrame(test_data)

    print(df)
    print(df.schema)

    print(f"{SuperDuperCols.__annotations__=}")
    print(f"{SuperDuperCols.A.__annotations__=}")
    print(f"{SuperDuperCols.A.__annotations__['A']=}")

    v_enum = df.select(pl.col(SuperDuperCols.A).min()).item()
    v_enum_str = df.select(pl.col(SuperDuperCols["A"]).min()).item()
    v_str = df.select(pl.col("col1").min()).item()

    print(f"v_enum: {v_enum}")
    print(f"v_enum_str: {v_enum_str}")
    print(f"v_str: {v_str}")

    assert v_enum == v_str
    assert v_enum == v_enum_str

    print("All tests passed for polars")

    v_enum_pandas = df_pandas.loc[:, SuperDuperCols.A].min()
    v_str_pandas = df_pandas.loc[:, "col1"].min()
    v_enum_str_pandas = df_pandas.loc[:, SuperDuperCols["A"]].min()
    print(f"v_str: {v_str_pandas}")
    print(f"v_enum: {v_enum_pandas}")
    print(f"v_enum_str: {v_enum_str_pandas}")
    assert v_str_pandas == v_str
    assert v_enum_pandas == v_str_pandas
    assert v_enum_pandas == v_enum_str_pandas

    print("All tests passed for pandas")
    print()
    print(80 * "-")
    for var in SuperDuperCols.__members__:
        print(var)

    print(80 * "-")
    print(vars(SuperDuperCols.A))
    print(SuperDuperCols.A._name_)


def simple_cols_check():
    import pandas as pd
    import polars as pl

    print(80 * "-")
    print("CHECKING Cols")
    print(f"Cols.__version__: {SimpleCols.__version__}")
    print(80 * "-")

    test_data = {
        "col1": [1, 2, 3],
        "col2": [4, 5, 6],
        "col3": [7, 8, 9],
    }

    print(f"{SimpleCols["A"]=}")
    print(f"{SimpleCols.A=}")
    print(f"{SimpleCols("col1")=}")

    df = pl.DataFrame(test_data)
    df_pandas = pd.DataFrame(test_data)

    print(df)
    print(df.schema)

    print(f"Cols.__version__: {SimpleCols.__version__}")
    print(f"{SimpleCols.__annotations__=}")
    print(f"{SimpleCols.A.__annotations__=}")
    print(f"{SimpleCols.A.__annotations__['A']=}")

    v_enum = df.select(pl.col(SimpleCols.A).min()).item()
    v_enum_str = df.select(pl.col(SimpleCols["A"]).min()).item()
    v_str = df.select(pl.col("col1").min()).item()

    print(f"v_enum: {v_enum}")
    print(f"v_enum_str: {v_enum_str}")
    print(f"v_str: {v_str}")

    assert v_enum == v_str
    assert v_enum == v_enum_str

    v_key = df.select(pl.col(SimpleCols("col1")).min()).item()

    print(f"v_key: {v_key}")

    assert v_key == v_str

    print("All tests passed for polars")

    v_enum_pandas = df_pandas.loc[:, SimpleCols.A].min()
    v_str_pandas = df_pandas.loc[:, "col1"].min()
    v_enum_str_pandas = df_pandas.loc[:, SimpleCols["A"]].min()
    print(f"v_str: {v_str_pandas}")
    print(f"v_enum: {v_enum_pandas}")
    print(f"v_enum_str: {v_enum_str_pandas}")
    assert v_str_pandas == v_str
    assert v_enum_pandas == v_str_pandas
    assert v_enum_pandas == v_enum_str_pandas

    print("All tests passed for pandas")


if __name__ == "__main__":
    # simple_cols_check()
    super_duper_cols_check()
