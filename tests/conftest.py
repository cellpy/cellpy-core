import pytest
from cellpycore.cell_core import Data


@pytest.fixture
def mock_data() -> Data:
    return Data()
