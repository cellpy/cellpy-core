import polars as pl
import datetime as dt


def main():
    df = pl.DataFrame(
        {
            "name": ["Alice Archer", "Ben Brown", "Chloe Cooper", "Daniel Donovan"],
            "birthdate": [
                dt.date(1997, 1, 10),
                dt.date(1985, 2, 15),
                dt.date(1983, 3, 22),
                dt.date(1981, 4, 30),
            ],
            "weight": [57.9, 72.5, 53.6, 83.1],  # (kg)
            "height": [1.56, 1.77, 1.65, 1.75],  # (m)
        }
    )

    print("DataFrame:")
    print(df)

    print("Writing to parquet...")
    df.write_parquet("tmp/simple.parquet")

    print("Reading from parquet...")
    df_read = pl.read_parquet("tmp/simple.parquet")
    print(df_read)

    print("Writing to csv...")
    df.write_csv("tmp/simple.csv")

    print("Reading from csv...")
    df_read = pl.read_csv("tmp/simple.csv")
    print(df_read)

    # reading to and from duckdb using polara is not solved yet, and maybe it is not needed.


if __name__ == "__main__":
    main()
