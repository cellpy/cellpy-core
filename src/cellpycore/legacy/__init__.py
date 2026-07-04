"""Legacy cellpy bridge: headers, mapping, selectors, and migration helpers.

Mocks and verbatim mirrors of cellpy types used by ``OldCellpyCellCore`` and
the cellpy<->core parity contract tests. Not part of the slim native API.
"""

from cellpycore.config import STEP_TYPES  # noqa: F401  (re-exported; see note below)
from cellpycore.exceptions import CellpyError, NoDataFound
from cellpycore.legacy.headers import (
    BaseHeaders,
    HeadersNormal,
    HeadersStepTable,
    HeadersSummary,
)
from cellpycore.legacy.limits import CAPACITY_MODIFIERS, CellpyLimits
from cellpycore.legacy.meta import Meta, MockMetaTestDependent
from cellpycore.legacy.mock_core import MockCore, set_col_first
from cellpycore.settings_base import BaseSettings, DictLikeClass  # noqa: F401
from cellpycore.units import CellpyUnits  # noqa: F401

from . import mapping

__all__ = [
    "CAPACITY_MODIFIERS",
    "BaseHeaders",
    "BaseSettings",
    "CellpyError",
    "CellpyLimits",
    "CellpyUnits",
    "DictLikeClass",
    "HeadersNormal",
    "HeadersStepTable",
    "HeadersSummary",
    "Meta",
    "MockCore",
    "MockMetaTestDependent",
    "NoDataFound",
    "STEP_TYPES",
    "mapping",
    "set_col_first",
]
