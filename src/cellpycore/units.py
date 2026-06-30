from __future__ import annotations

import functools
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, TypeVar

from cellpycore.settings_base import BaseSettings

if TYPE_CHECKING:
    from cellpycore.cell_core import Data

DataFrame = TypeVar("DataFrame")


# -----------------------------------------------------------------------------
#   cellpy unit-spec class (promoted from ``cellpycore.legacy``; re-exported
#   there for backwards compatibility).
# -----------------------------------------------------------------------------
@dataclass
class CellpyUnits(BaseSettings):
    """These are the units used inside Cellpy.

    At least two sets of units needs to be defined; `cellpy_units` and `raw_units`.
    The `data.raw` dataframe is given in `raw_units` where the units are defined
    inside the instrument loader used. Since the `data.steps` dataframe is a summary of
    the step statistics from the `data.raw` dataframe, this also uses the `raw_units`.
    The `data.summary` dataframe contains columns with values directly from the `data.raw` dataframe
    given in `raw_units` as well as calculated columns given in `cellpy_units`.

    Remark that all input to cellpy through user interaction (or utils) should be in `cellpy_units`.
    This is also true for meta-data collected from the raw files. The instrument loader needs to
    take care of the translation from its raw units to `cellpy_units` during loading the raw data
    file for the meta-data (remark that this is not necessary and not recommended for the actual
    "raw" data that is going to be stored in the `data.raw` dataframe).

    As of 2022.09.29, cellpy does not automatically ensure unit conversion for input of meta-data,
    but has an internal method (`CellPyData.to_cellpy_units`) that can be used.

    These are the different attributes currently supported for data in the dataframes::

        current: str = "A"
        charge: str = "mAh"
        voltage: str = "V"
        time: str = "sec"
        resistance: str = "Ohms"
        power: str = "W"
        energy: str = "Wh"
        frequency: str = "hz"

    And here are the different attributes currently supported for meta-data::

        # output-units for specific capacity etc.
        specific_gravimetric: str = "g"
        specific_areal: str = "cm**2"  # used for calculating specific capacity etc.
        specific_volumetric: str = "cm**3"  # used for calculating specific capacity etc.

        # other meta-data
        nominal_capacity: str = "mAh/g"  # used for calculating rates etc.
        mass: str = "mg"
        length: str = "cm"
        area: str = "cm**2"
        volume: str = "cm**3"
        temperature: str = "C"

    """

    current: str = "A"
    charge: str = "mAh"
    voltage: str = "V"
    time: str = "sec"
    resistance: str = "ohm"
    power: str = "W"
    energy: str = "Wh"
    frequency: str = "hz"
    mass: str = "mg"  # for mass
    nominal_capacity: str = "mAh/g"
    specific_gravimetric: str = "g"  # g in specific capacity etc
    specific_areal: str = "cm**2"  # m2 in specific capacity etc
    specific_volumetric: str = "cm**3"  # m3 in specific capacity etc

    length: str = "cm"
    area: str = "cm**2"
    volume: str = "cm**3"
    temperature: str = "C"
    pressure: str = "bar"

    def update(self, new_units: dict):
        """Update the units."""

        logging.debug(f"{new_units=}")
        for k in new_units:
            if k in self.keys():
                self[k] = new_units[k]


@functools.lru_cache(maxsize=1)
def _get_unit_registry():
    """Create (once) and return the pint UnitRegistry.

    pint recommends a single shared registry per process (Quantities created by
    different registries cannot interoperate), so we memoize one instead of
    keeping a reassignable module-level global - this avoids shared mutable
    state. pint is an optional dependency (install the ``units`` extra); it is
    imported lazily so it stays off the core (summary/step) hot path, which now
    receives conversion factors by value.
    """
    try:
        import pint
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError(
            "pint is required for the cellpy-core unit-conversion helpers; "
            "install the 'units' extra (e.g. `uv pip install cellpycore[units]`)."
        ) from e

    ureg = pint.UnitRegistry()
    try:
        ureg.formatter.default_format = "~P"
    except AttributeError:
        ureg.default_format = "~P"
    return ureg


def Q(*args, **kwargs):
    return _get_unit_registry().Quantity(*args, **kwargs)


def get_cellpy_units(*args, **kwargs) -> CellpyUnits:
    """Returns an augmented global dictionary with units"""
    return CellpyUnits()


def get_default_output_units(*args, **kwargs) -> CellpyUnits:
    """Returns an augmented dictionary with units to use as default."""
    return CellpyUnits()


def get_converter_to_specific(
    data: Data,
    value: float = None,
    from_units: CellpyUnits = None,
    to_units: CellpyUnits = None,
    mode: str = "gravimetric",
) -> float:
    """Convert from absolute units to specific (areal or gravimetric).

    The method provides a conversion factor that you can multiply your
    values with to get them into specific values.

    Args:
        data: data instance
        value: value used to scale on.
        from_units: defaults to data.raw_units.
        to_units: defaults to cellpy_units.
        mode (str): gravimetric, areal or absolute

    Returns:
        conversion factor (float)

    """
    # TODO @jepe: implement handling of edge-cases
    # TODO @jepe: fix all the instrument readers (replace floats in raw_units with strings)

    new_units = to_units or get_cellpy_units()
    old_units = from_units or data.raw_units

    if mode == "gravimetric":
        value = value or data.mass
        value = Q(value, new_units["mass"])
        to_unit_specific = Q(1.0, new_units["specific_gravimetric"])

    elif mode == "areal":
        value = value or data.active_electrode_area
        value = Q(value, new_units["area"])
        to_unit_specific = Q(1.0, new_units["specific_areal"])

    elif mode == "volumetric":
        value = value or data.volume
        value = Q(value, new_units["volume"])
        to_unit_specific = Q(1.0, new_units["specific_volumetric"])

    elif mode == "absolute":
        value = Q(1.0, None)
        to_unit_specific = Q(1.0, None)

    else:
        logging.debug(f"mode={mode} not supported!")
        return 1.0

    from_unit_cap = Q(1.0, old_units["charge"])
    to_unit_cap = Q(1.0, new_units["charge"])

    # from unit is always in absolute values:
    from_unit = from_unit_cap

    to_unit = to_unit_cap / to_unit_specific

    conversion_factor = (from_unit / to_unit / value).to_reduced_units()
    logging.debug(f"conversion factor: {conversion_factor}")
    return conversion_factor.m


def nominal_capacity_as_absolute(
    data: Data,
    value: Optional[float] = None,
    specific: Optional[float] = None,
    nom_cap_specifics: Optional[str] = None,
    convert_charge_units: bool = False,
) -> float:
    """Get the nominal capacity as absolute value."""

    cellpy_units = get_cellpy_units()

    if nom_cap_specifics is None:
        nom_cap_specifics = data.nom_cap_specifics

    if specific is None:
        if nom_cap_specifics == "gravimetric":
            specific = data.mass
        elif nom_cap_specifics == "areal":
            specific = data.active_electrode_area

        # TODO: implement volumetric
        elif nom_cap_specifics == "volumetric":
            raise NotImplementedError("volumetric not implemented yet")

    if value is None:
        value = data.nom_cap

    value = Q(value, cellpy_units["nominal_capacity"])

    if nom_cap_specifics == "gravimetric":
        specific = Q(specific, cellpy_units["mass"])
    elif nom_cap_specifics == "areal":
        specific = Q(specific, cellpy_units["area"])
    elif nom_cap_specifics == "absolute":
        specific = 1

    # TODO: implement volumetric
    elif nom_cap_specifics == "volumetric":
        raise NotImplementedError("volumetric not implemented yet")

    if convert_charge_units:
        conversion_factor_charge = Q(1, cellpy_units["charge"]) / Q(
            1, data.raw_units["charge"]
        )
    else:
        conversion_factor_charge = 1.0

    try:
        absolute_value = (
            (value * conversion_factor_charge * specific).to_reduced_units().to("Ah")
        )
    except Exception as e:
        raise e

    return absolute_value.m
