"""cellpy-core: the core summarization engine for battery-cycling raw data.

The public, stable surface is the curated set of names re-exported here:
the cell classes (``CellpyCellCore``, its legacy bridge ``OldCellpyCellCore``),
the ``Data`` container, the engine entry points (``make_step_table``,
``add_step_c_rate``, ``make_summary``), the column-header schema types, and the package
exceptions. Everything else (``units``, ``timestamps``, ``legacy``, ``metadata``,
``testing`` ...) remains importable as submodules but is not part of the
guaranteed top-level API.
"""

from importlib.metadata import PackageNotFoundError, version

from cellpycore.cell_core import (
    CellpyCellCore,
    Data,
    OldCellpyCellCore,
    cast_raw_frame,
    validate_raw_frame,
)
from cellpycore.config import (
    CycleCols,
    RawCols,
    Schema,
    StepCols,
    default_schema,
)
from cellpycore.exceptions import CellpyError, NoDataFound
from cellpycore.merge import merge_data, update_data
from cellpycore.summarizers import add_step_c_rate, make_step_table, make_summary

try:
    __version__ = version("cellpycore")
except PackageNotFoundError:  # not installed (e.g. running from a source tree)
    __version__ = "0.0.0"

__all__ = [
    "CellpyCellCore",
    "CellpyError",
    "CycleCols",
    "Data",
    "NoDataFound",
    "OldCellpyCellCore",
    "RawCols",
    "Schema",
    "StepCols",
    "__version__",
    "add_step_c_rate",
    "cast_raw_frame",
    "default_schema",
    "make_step_table",
    "make_summary",
    "merge_data",
    "update_data",
    "validate_raw_frame",
]
