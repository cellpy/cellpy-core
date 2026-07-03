"""Pint-backed unit conversion helpers (optional ``units`` extra)."""

from __future__ import annotations

import functools
import logging
from typing import Any, Optional, TypeVar

from cellpycore.metadata.models import CellMeta
from cellpycore.units.spec import CellpyUnits

DataFrame = TypeVar("DataFrame")

logger = logging.getLogger(__name__)


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


def _resolve_optional_attr(
    *,
    explicit: Any,
    cell_meta: Optional[CellMeta],
    meta_attr: str,
    data: Any,
    data_attr: str,
) -> Any:
    """Resolve a scalar from explicit kwarg, ``CellMeta``, or duck-typed ``data``."""
    if explicit is not None:
        return explicit
    if cell_meta is not None:
        from_meta = getattr(cell_meta, meta_attr, None)
        if from_meta is not None:
            return from_meta
    if data is not None:
        from_data = getattr(data, data_attr, None)
        if from_data is not None:
            return from_data
    return None


def _require_attr(resolved: Any, name: str, *, context: str) -> Any:
    """Raise ``ValueError`` when a required conversion input is missing."""
    if resolved is None:
        raise ValueError(
            f"{name} is required for {context}; pass it explicitly, "
            f"supply cell_meta, or use a data object with .{name}"
        )
    return resolved


def _resolve_raw_units(
    from_units: Optional[CellpyUnits],
    data: Any,
) -> CellpyUnits:
    """Resolve raw/input charge units: explicit → duck ``data.raw_units`` → default."""
    if from_units is not None:
        return from_units
    if data is not None:
        raw_units = getattr(data, "raw_units", None)
        if raw_units is not None:
            return raw_units
    return CellpyUnits()


def get_converter_to_specific(
    data: Any = None,
    value: float = None,
    from_units: CellpyUnits = None,
    to_units: CellpyUnits = None,
    mode: str = "gravimetric",
    *,
    cell_meta: Optional[CellMeta] = None,
    mass: Optional[float] = None,
    active_electrode_area: Optional[float] = None,
    volume: Optional[float] = None,
) -> float:
    """Convert from absolute units to specific (areal or gravimetric).

    The method provides a conversion factor that you can multiply your
    values with to get them into specific values.

    Args:
        data: Optional data instance (cellpy's richer object may supply attrs).
        value: Explicit scale value for the mode (mass, area, or volume).
        from_units: Raw/input charge units; defaults to ``data.raw_units`` or
            ``CellpyUnits()`` when unset.
        to_units: Output units; defaults to cellpy units.
        mode: ``gravimetric``, ``areal``, ``volumetric``, or ``absolute``.
        cell_meta: Optional cell metadata (``mass``, ``active_electrode_area``).
        mass: Explicit active-material mass (gravimetric mode).
        active_electrode_area: Explicit electrode area (areal mode).
        volume: Explicit electrode volume (volumetric mode).

    Returns:
        Conversion factor (float).

    Raises:
        ValueError: When a required scale value is missing for the chosen mode.
    """
    # TODO @jepe: implement handling of edge-cases
    # TODO @jepe: fix all the instrument readers (replace floats in raw_units with strings)

    new_units = to_units or get_cellpy_units()
    old_units = _resolve_raw_units(from_units, data)

    if mode == "gravimetric":
        scale = (
            value
            if value is not None
            else _resolve_optional_attr(
                explicit=mass,
                cell_meta=cell_meta,
                meta_attr="mass",
                data=data,
                data_attr="mass",
            )
        )
        scale = _require_attr(scale, "mass", context="gravimetric mode")
        value = Q(scale, new_units["mass"])
        to_unit_specific = Q(1.0, new_units["specific_gravimetric"])

    elif mode == "areal":
        scale = (
            value
            if value is not None
            else _resolve_optional_attr(
                explicit=active_electrode_area,
                cell_meta=cell_meta,
                meta_attr="active_electrode_area",
                data=data,
                data_attr="active_electrode_area",
            )
        )
        scale = _require_attr(scale, "active_electrode_area", context="areal mode")
        value = Q(scale, new_units["area"])
        to_unit_specific = Q(1.0, new_units["specific_areal"])

    elif mode == "volumetric":
        scale = (
            value
            if value is not None
            else _resolve_optional_attr(
                explicit=volume,
                cell_meta=None,
                meta_attr="volume",
                data=data,
                data_attr="volume",
            )
        )
        scale = _require_attr(scale, "volume", context="volumetric mode")
        value = Q(scale, new_units["volume"])
        to_unit_specific = Q(1.0, new_units["specific_volumetric"])

    elif mode == "absolute":
        value = Q(1.0, None)
        to_unit_specific = Q(1.0, None)

    else:
        logger.debug(f"mode={mode} not supported!")
        return 1.0

    from_unit_cap = Q(1.0, old_units["charge"])
    to_unit_cap = Q(1.0, new_units["charge"])

    # from unit is always in absolute values:
    from_unit = from_unit_cap

    to_unit = to_unit_cap / to_unit_specific

    conversion_factor = (from_unit / to_unit / value).to_reduced_units()
    logger.debug(f"conversion factor: {conversion_factor}")
    return conversion_factor.m


def nominal_capacity_as_absolute(
    data: Any = None,
    value: Optional[float] = None,
    specific: Optional[float] = None,
    nom_cap_specifics: Optional[str] = None,
    convert_charge_units: bool = False,
    *,
    cell_meta: Optional[CellMeta] = None,
    raw_units: Optional[CellpyUnits] = None,
) -> float:
    """Get the nominal capacity as absolute value.

    Args:
        data: Optional data instance (cellpy's richer object may supply attrs).
        value: Nominal capacity in specific units (e.g. mAh/g).
        specific: Scale factor (mass, area, …) matching ``nom_cap_specifics``.
        nom_cap_specifics: How ``value`` is specified (gravimetric, areal, …).
        convert_charge_units: Whether to convert between raw and cellpy charge units.
        cell_meta: Optional cell metadata supplying ``nom_cap``, ``nom_cap_specifics``,
            ``mass``, and ``active_electrode_area``.
        raw_units: Raw charge units for ``convert_charge_units``; defaults to
            ``data.raw_units`` or ``CellpyUnits()`` when unset.

    Returns:
        Absolute nominal capacity in Ah.

    Raises:
        ValueError: When required inputs cannot be resolved.
        NotImplementedError: For volumetric mode.
    """

    cellpy_units = get_cellpy_units()

    if nom_cap_specifics is None:
        nom_cap_specifics = _resolve_optional_attr(
            explicit=None,
            cell_meta=cell_meta,
            meta_attr="nom_cap_specifics",
            data=data,
            data_attr="nom_cap_specifics",
        )

    if specific is None:
        if nom_cap_specifics == "gravimetric":
            specific = _resolve_optional_attr(
                explicit=None,
                cell_meta=cell_meta,
                meta_attr="mass",
                data=data,
                data_attr="mass",
            )
        elif nom_cap_specifics == "areal":
            specific = _resolve_optional_attr(
                explicit=None,
                cell_meta=cell_meta,
                meta_attr="active_electrode_area",
                data=data,
                data_attr="active_electrode_area",
            )

        # TODO: implement volumetric
        elif nom_cap_specifics == "volumetric":
            raise NotImplementedError("volumetric not implemented yet")

    if value is None:
        value = _resolve_optional_attr(
            explicit=None,
            cell_meta=cell_meta,
            meta_attr="nom_cap",
            data=data,
            data_attr="nom_cap",
        )

    if value is None:
        raise ValueError(
            "nom_cap is required; pass value=, supply cell_meta, "
            "or use a data object with .nom_cap"
        )

    value = Q(value, cellpy_units["nominal_capacity"])

    if nom_cap_specifics == "gravimetric":
        specific = _require_attr(specific, "mass", context="gravimetric nom_cap")
        specific = Q(specific, cellpy_units["mass"])
    elif nom_cap_specifics == "areal":
        specific = _require_attr(
            specific, "active_electrode_area", context="areal nom_cap"
        )
        specific = Q(specific, cellpy_units["area"])
    elif nom_cap_specifics == "absolute":
        specific = 1

    # TODO: implement volumetric
    elif nom_cap_specifics == "volumetric":
        raise NotImplementedError("volumetric not implemented yet")

    if convert_charge_units:
        resolved_raw_units = _resolve_raw_units(raw_units, data)
        conversion_factor_charge = Q(1, cellpy_units["charge"]) / Q(
            1, resolved_raw_units["charge"]
        )
    else:
        conversion_factor_charge = 1.0

    absolute_value = (
        (value * conversion_factor_charge * specific).to_reduced_units().to("Ah")
    )

    return absolute_value.m
