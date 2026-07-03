from typing import TypeVar

import pytest

from cellpycore._helpers import create_raw_data
from cellpycore.cell_core import Data

DataFrame = TypeVar("DataFrame")


@pytest.fixture
def mock_data_empty() -> Data:
    data = Data()
    return data


@pytest.fixture
def mock_data_with_raw() -> Data:
    data = Data()
    data.raw = create_raw_data()
    return data
