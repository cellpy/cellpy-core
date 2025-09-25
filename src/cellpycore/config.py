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

from enum import StrEnum


class Cols(StrEnum):
    A: str = "col1"
    B: str = "col2"
    C: str = "col3"
    _version: str = "1.0.0"



if __name__ == "__main__":
    import pandas as pd
    import polars as pl

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

    print(f"Cols._version: {Cols._version}")
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


