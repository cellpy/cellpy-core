import pytest

from cellpycore.cell_core import Data

def test_data_creation(mock_data: Data):
    assert mock_data is not None
    assert mock_data.raw is not None
    assert mock_data.cycle is not None
    assert mock_data.step is not None