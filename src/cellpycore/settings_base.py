"""Generic dict-like settings base classes shared across cellpy-core.

These were originally defined in :mod:`cellpycore.legacy`. They are kept in a
neutral, dependency-free module so that both the unit-spec (:mod:`cellpycore.units`)
and the legacy mirror (:mod:`cellpycore.legacy`) can build on them without forming
an import cycle. ``cellpycore.legacy`` re-exports both names for backwards
compatibility.
"""

from dataclasses import asdict, dataclass, fields
import logging


@dataclass
class DictLikeClass:
    """Add some dunder-methods so that it does not break old code that used
    dictionaries for storing settings

    Remarks: it is not a complete dictionary experience - for example,
    setting new attributes (new keys) is not supported (raises ``KeyError``
    if using the typical dict setting method) since it uses the
    ``dataclasses.fields`` method to find its members.

    """

    def __getitem__(self, key):
        if key not in self._field_names:
            logging.debug(f"{key} not in fields")
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(f"missing key: {key}")

    def __setitem__(self, key, value):
        if key not in self._field_names:
            raise KeyError(f"creating new key not allowed: {key}")
        setattr(self, key, value)

    def __missing__(self, key):
        raise KeyError

    @property
    def _field_names(self):
        return [field.name for field in fields(self)]

    def __iter__(self):
        for field in self._field_names:
            yield field

    def _value_iter(self):
        for field in self._field_names:
            yield getattr(self, field)

    def keys(self):
        return [key for key in self.__iter__()]

    def values(self):
        return [v for v in self._value_iter()]

    def items(self):
        return zip(self.keys(), self.values())


@dataclass
class BaseSettings(DictLikeClass):
    """Base class for internal cellpy settings.

    Usage::

         @dataclass
         class MyCoolCellpySetting(BaseSetting):
             var1: str = "first var"
             var2: int = 12

    """

    def get(self, key):
        """Get the value (postfixes not supported)."""
        if key not in self.keys():
            logging.critical(f"the column header '{key}' not found")
            return
        else:
            return self[key]

    def to_frame(self):
        """Converts to pandas dataframe"""
        import pandas

        df = pandas.DataFrame.from_dict(asdict(self), orient="index")
        df.index.name = "key"
        _, n_cols = df.shape
        if n_cols == 1:
            columns = ["value"]
        else:
            columns = [f"value_{i:02}" for i in range(n_cols)]
        df.columns = columns

        return df
