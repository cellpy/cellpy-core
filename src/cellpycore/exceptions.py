"""Cellpy Core exceptions."""


class CellpyError(Exception):
    """Base class for other Cellpy Core exceptions"""

    pass


class NoDataFound(CellpyError):
    """Exception raised when no data is found"""

    pass
