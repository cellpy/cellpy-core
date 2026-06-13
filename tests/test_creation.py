import pytest

from cellpycore.cell_core import Data

def test_data_creation(mock_data_empty: Data):
    assert mock_data_empty is not None
    assert mock_data_empty.raw is None
    assert mock_data_empty.cycle is None
    assert mock_data_empty.step is None

def test_data_creation_with_raw(mock_data_with_raw: Data):
    assert mock_data_with_raw is not None
    assert mock_data_with_raw.raw is not None
    assert mock_data_with_raw.cycle is None
    assert mock_data_with_raw.step is None

