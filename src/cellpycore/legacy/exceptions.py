"""Legacy cellpy exceptions (mirrored for bridge parity)."""


class CellpyError(Exception):
    """Base class for other exceptions"""

    pass


class NoDataFound(CellpyError):
    """Exception raised when no data is found"""

    pass
