import polars as pl
import pytest
from polars.testing import assert_frame_equal

from cellpycore._helpers import create_raw_data
from cellpycore.cell_core import CellpyCellCore, Data
from cellpycore.config import RawCols
from cellpycore.legacy import MockMetaTestDependent


def test_data_creation(mock_data_empty: Data):
    assert mock_data_empty is not None
    assert mock_data_empty.raw is None
    assert mock_data_empty.steps is None
    assert mock_data_empty.summary is None


def test_data_creation_with_raw(mock_data_with_raw: Data):
    assert mock_data_with_raw is not None
    assert mock_data_with_raw.raw is not None
    assert mock_data_with_raw.steps is None
    assert mock_data_with_raw.summary is None


def _run_engine(data: Data) -> Data:
    core = CellpyCellCore()
    data = core.make_core_step_table(data)
    return core.make_core_summary(data)


def test_from_raw_frame_round_trip_matches_plain_assignment():
    df = create_raw_data()

    front_door = _run_engine(Data.from_raw_frame(df))

    plain = Data()
    plain.raw = df
    plain = _run_engine(plain)

    assert isinstance(front_door.meta_test_dependent, MockMetaTestDependent)
    assert_frame_equal(front_door.steps, plain.steps)
    assert_frame_equal(front_door.summary, plain.summary)


def test_from_raw_frame_missing_columns_are_all_named():
    cols = RawCols()
    df = create_raw_data().drop([cols.cycle_num, cols.current])
    with pytest.raises(ValueError) as excinfo:
        Data.from_raw_frame(df)
    assert cols.cycle_num in str(excinfo.value)
    assert cols.current in str(excinfo.value)


def test_from_raw_frame_wrong_epoch_dtype_mentions_contract():
    cols = RawCols()
    df = create_raw_data().with_columns(pl.col(cols.epoch_time_utc).cast(pl.Float64))
    with pytest.raises(ValueError, match="int64 nanoseconds"):
        Data.from_raw_frame(df)


def test_from_raw_frame_validate_false_skips_checks():
    cols = RawCols()
    broken = create_raw_data().drop([cols.cycle_num])
    data = Data.from_raw_frame(broken, validate=False)
    assert data.raw is broken


def test_from_raw_frame_rejects_non_polars_input():
    df = create_raw_data().to_pandas()
    with pytest.raises(TypeError, match="polars.DataFrame"):
        Data.from_raw_frame(df)
