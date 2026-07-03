"""Legacy cellpy mock helpers (migration scaffolding)."""

import logging
import numbers

from cellpycore.units import CellpyUnits, Q

logger = logging.getLogger(__name__)


class MockCore:
    def __init__(self):
        self.cellpy_units = CellpyUnits()

    # Candidates for cellpy core extension.
    def _dump_cellpy_unit(self, value, parameter):
        """Parse for unit, update cellpy_units class, and return magnitude."""
        import numpy as np

        c_value, c_unit = self._check_value_unit(value, parameter)
        if not isinstance(c_value, numbers.Number) or np.isnan(c_value):
            logger.critical(f"Could not parse {parameter} ({value})")
            logger.critical("Setting it to 1.0")
            return 1.0
        if c_unit is not None:
            self.cellpy_units[parameter] = f"{c_unit}"
            logger.debug(f"Updated your cellpy_units['{parameter}'] to '{c_unit}'")

        return c_value

    @staticmethod
    def _check_value_unit(value, parameter) -> tuple:
        """Check if value is a valid number, or a quantity with units."""
        if isinstance(value, numbers.Number):
            return value, None
        logger.critical(f"Parsing {parameter} ({value})")

        try:
            c = Q(value)
            c_unit = c.units
            c_value = c.magnitude
        except ValueError:
            logger.debug(f"Could not parse {value}")
            return None, None
        return c_value, c_unit


# NOT USED
def set_col_first(df, col_names):
    """Set selected columns first in a pandas.DataFrame.

    This function sets cols with names given in  col_names (a list) first in
    the DataFrame. The last col in col_name will come first (processed last)

    """

    column_headings = df.columns
    column_headings = column_headings.tolist()
    try:
        for col_name in col_names:
            column_headings.pop(column_headings.index(col_name))
            column_headings.insert(0, col_name)

    finally:
        df = df.reindex(columns=column_headings)
        return df
