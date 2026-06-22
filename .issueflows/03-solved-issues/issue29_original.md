# Issue #29: create a test harmonized raw file

Source: https://github.com/cellpy/cellpy-core/issues/29

## Original issue text


Create a helper script (put it in dev/) that converts the arbin_cc_raw.parquet file into a harmonized raw file (also parquet) with the harmonized raw headers that we can use for testing.

The renaming of the headers should ideally be obvious (if not, the documentation for cellpy core needs to be amended).

If we later on modify cellpy core's RawCols in some way, we should ideally only need to re-run our script and get an appropriate harmonized raw file.
