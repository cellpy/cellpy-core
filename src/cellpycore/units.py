import logging
from typing import Optional, TypeVar

from cellpycore.legacy import Data, CellpyUnits
DataFrame = TypeVar("DataFrame")

UNIT_REGISTER_LOADED = False
_ureg = None


def _create_unit_registry():
    import pint
    global UNIT_REGISTER_LOADED, _ureg
    if UNIT_REGISTER_LOADED:
        return _ureg

    _ureg = pint.UnitRegistry()
    try:
        _ureg.formatter.default_format = "~P"
    except AttributeError:
        _ureg.formatter.default_format = "~P"
    UNIT_REGISTER_LOADED = True


def Q(*args, **kwargs):
    global _ureg, UNIT_REGISTER_LOADED
    if not UNIT_REGISTER_LOADED:
        _create_unit_registry()
    return _ureg.Quantity(*args, **kwargs)


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
