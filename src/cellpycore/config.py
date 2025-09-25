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

"""

from dataclasses import dataclass
from enum import StrEnum, Enum


@dataclass
class ColsItem(str):
    value: str
    unit: str
    dtype: str
    def __str__(self) -> str:
        return self.value
    def __repr__(self) -> str:
        return self.value
    def __eq__(self, other: str) -> bool:
        return self.value == other
    def __hash__(self) -> int:
        return hash(self.value)

    



class Cols(StrEnum):
    __version__: str = "1.0.0"
    A: str = "col1"
    B: str = "col2"
    C: str = "col3"

    def is_valid(self, value: str) -> bool:
        return value in self.__members__


class SuperDuperCols(Enum):

    __version__: str = "1.0.0"

    def __new__(cls, value: str, unit: str, dtype: str):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.unit = unit
        obj.dtype = dtype
        return obj

    # TODO: dtype should be a python native "dtype object" if it exists, or a pl.DataType? Using str for now.
    A: list[str, str, str] = "col1", "V", "Float64"
    B: list[str, str, str] = "col2", "mAh/g", "Float64"
    C: list[str, str, str] = "col3", "s", "Float64"

    @property
    def value(self) -> str:
        return self._value_



def super_duper_cols_check():
    import pandas as pd
    import polars as pl
    
    print(80*"-")
    print("CHECKING SuperDuperCols")
    print(f"SuperDuperCols.__version__: {SuperDuperCols.__version__}")
    print(80*"-")

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
    
    v_enum = df.select(pl.col(SuperDuperCols.A.value).min()).item()
    v_enum_str = df.select(pl.col(SuperDuperCols["A"].value).min()).item()
    v_str = df.select(pl.col("col1").min()).item()
    
    print(f"v_enum: {v_enum}")
    print(f"v_enum_str: {v_enum_str}")
    print(f"v_str: {v_str}")
    
    assert v_enum == v_str
    assert v_enum == v_enum_str
        
    print("All tests passed for polars")
    
    v_enum_pandas = df_pandas.loc[:, SuperDuperCols.A.value].min()
    v_str_pandas = df_pandas.loc[:, "col1"].min()
    v_enum_str_pandas = df_pandas.loc[:, SuperDuperCols["A"].value].min()
    print(f"v_str: {v_str_pandas}")
    print(f"v_enum: {v_enum_pandas}")
    print(f"v_enum_str: {v_enum_str_pandas}")
    assert v_str_pandas == v_str
    assert v_enum_pandas == v_str_pandas
    assert v_enum_pandas == v_enum_str_pandas
    
    print("All tests passed for pandas")


def simple_cols_check():
    import pandas as pd
    import polars as pl

    print(80*"-")
    print("CHECKING Cols")
    print(f"Cols.__version__: {Cols.__version__}")
    print(80*"-")

    test_data = {
    "col1": [1, 2, 3],
    "col2": [4, 5, 6],
    "col3": [7, 8, 9],
}



    print(f"{Cols["A"]=}")
    print(f"{Cols.A=}")
    print(f"{Cols("col1")=}")

    df = pl.DataFrame(test_data)
    df_pandas = pd.DataFrame(test_data)

    print(df)
    print(df.schema)

    print(f"Cols.__version__: {Cols.__version__}")
    print(f"{Cols.__annotations__=}")
    print(f"{Cols.A.__annotations__=}")
    print(f"{Cols.A.__annotations__['A']=}")

    v_enum = df.select(pl.col(Cols.A).min()).item()
    v_enum_str = df.select(pl.col(Cols["A"]).min()).item()
    v_str = df.select(pl.col("col1").min()).item()

    print(f"v_enum: {v_enum}")
    print(f"v_enum_str: {v_enum_str}")
    print(f"v_str: {v_str}")

    assert v_enum == v_str
    assert v_enum == v_enum_str

    v_key = df.select(pl.col(Cols("col1")).min()).item()

    print(f"v_key: {v_key}")

    assert v_key == v_str

    print("All tests passed for polars")

    v_enum_pandas = df_pandas.loc[:, Cols.A].min()
    v_str_pandas = df_pandas.loc[:, "col1"].min()
    v_enum_str_pandas = df_pandas.loc[:, Cols["A"]].min()
    print(f"v_str: {v_str_pandas}")
    print(f"v_enum: {v_enum_pandas}")
    print(f"v_enum_str: {v_enum_str_pandas}")
    assert v_str_pandas == v_str
    assert v_enum_pandas == v_str_pandas
    assert v_enum_pandas == v_enum_str_pandas

    print("All tests passed for pandas")


if __name__ == "__main__":
    simple_cols_check()
    super_duper_cols_check()