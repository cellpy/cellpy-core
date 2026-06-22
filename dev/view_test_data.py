import marimo

__generated_with = "0.23.10"
app = marimo.App(width="medium")


@app.cell
def _():
    from pathlib import Path

    import marimo as mo
    import polars as pl

    return Path, mo, pl


@app.cell
def _(Path):
    # Resolve tests/data relative to this notebook (dev/ is a sibling of tests/).
    DATA_DIR = Path(__file__).resolve().parent.parent / "tests" / "data"
    parquet_files = sorted(DATA_DIR.glob("*.parquet"))
    return (parquet_files,)


@app.cell
def _(mo, parquet_files):
    file_selector = mo.ui.dropdown(
        options={p.name: str(p) for p in parquet_files},
        value=parquet_files[0].name if parquet_files else None,
        label="Parquet file",
    )
    file_selector
    return (file_selector,)


@app.cell
def _(file_selector, mo, pl):
    mo.stop(file_selector.value is None, mo.md("No parquet files found in `tests/data`."))

    df = pl.read_parquet(file_selector.value)
    return (df,)


@app.cell
def _(df, mo):
    mo.md(f"""
    **{df.height:,} rows × {df.width} columns**
    """)
    return


@app.cell
def _(df, mo):
    # Schema overview: column name + dtype.
    mo.ui.table(
        [{"column": name, "dtype": str(dtype)} for name, dtype in df.schema.items()],
        label="Schema",
        selection=None,
    )
    return


@app.cell
def _(df, mo):
    # Interactive view of the full frame.
    mo.ui.dataframe(df.to_pandas())
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
