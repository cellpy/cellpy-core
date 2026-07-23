"""Pint-backed unit conversion helpers (optional ``units`` extra)."""

from __future__ import annotations

import functools
import logging
import numbers
import warnings
from typing import Any, Optional, TypeVar, Union

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


QuantityValue = Union[float, int, str]


def _default_unit(units: CellpyUnits, key: str) -> str:
    """Return the unit string for ``key`` on a ``CellpyUnits`` spec."""
    return units[key]


def _resolve_units_spec(
    cellpy_units: Optional[CellpyUnits] = None,
    to_units: Optional[CellpyUnits] = None,
) -> CellpyUnits:
    """Resolve output / cellpy default unit strings."""
    return cellpy_units or to_units or get_cellpy_units()


def _as_quantity(value: QuantityValue, default_unit: str, *, name: str = "value"):
    """Coerce a numeric value or pint quantity string to a ``Quantity``.

    Bare numbers use ``default_unit``; strings are parsed by pint and must
    include units (unitless numeric strings raise ``ValueError``).
    """
    if isinstance(value, str):
        try:
            quantity = Q(value)
        except Exception as exc:
            raise ValueError(
                f"Could not parse {name} as a quantity: {value!r}"
            ) from exc
        if quantity.dimensionless:
            raise ValueError(
                f"{name} {value!r} has no units; use a quantity string "
                f'(e.g. "3.579 mAh/g") or pass a number with an explicit unit'
            )
        return quantity
    if isinstance(value, numbers.Real):
        return Q(float(value), default_unit)
    raise TypeError(
        f"{name} must be a number or quantity string, got {type(value).__name__}"
    )


def _coerce_scale(
    scale: QuantityValue,
    *,
    default_unit: str,
    unit_override: Optional[str],
    explicit: bool,
    name: str,
):
    """Build a pint ``Quantity`` for a geometry scale (mass, area, volume)."""
    if not explicit:
        return Q(scale, default_unit)
    return _as_quantity(scale, unit_override or default_unit, name=name)


def get_converter_to_specific(
    data: Any = None,
    value: Optional[QuantityValue] = None,
    from_units: CellpyUnits = None,
    to_units: CellpyUnits = None,
    mode: str = "gravimetric",
    *,
    cell_meta: Optional[CellMeta] = None,
    mass: Optional[QuantityValue] = None,
    active_electrode_area: Optional[QuantityValue] = None,
    volume: Optional[QuantityValue] = None,
    mass_unit: Optional[str] = None,
    area_unit: Optional[str] = None,
    volume_unit: Optional[str] = None,
    cellpy_units: Optional[CellpyUnits] = None,
) -> float:
    """Convert from absolute units to specific (areal or gravimetric).

    The method provides a conversion factor that you can multiply your
    values with to get them into specific values.

    Args:
        data: Optional data instance (cellpy's richer object may supply attrs).
        value: Explicit scale value for the mode (mass, area, or volume). A bare
            number uses the matching cellpy unit (``mg``, ``cm**2``, or
            ``cm**3`` by default); a string is parsed as a pint quantity
            (e.g. ``"2 mg"``).
        from_units: Raw/input charge units; defaults to ``data.raw_units`` or
            ``CellpyUnits()`` when unset.
        to_units: Output units; defaults to cellpy units.
        mode: ``gravimetric``, ``areal``, ``volumetric``, or ``absolute``.
        cell_meta: Optional cell metadata (``mass``, ``active_electrode_area``).
        mass: Explicit active-material mass (gravimetric mode); same typing as
            ``value``.
        active_electrode_area: Explicit electrode area (areal mode).
        volume: Explicit electrode volume (volumetric mode).
        mass_unit: Unit string for bare numeric ``mass`` / gravimetric ``value``
            (default from ``cellpy_units`` or ``CellpyUnits().mass``).
        area_unit: Unit string for bare numeric areal scale inputs (default
            ``CellpyUnits().area``).
        volume_unit: Unit string for bare numeric volumetric scale inputs
            (default ``CellpyUnits().volume``).
        cellpy_units: Bulk override for default mass/area/volume unit strings
            when coercing explicit inputs; also used as ``to_units`` when that
            is unset.

    Returns:
        Conversion factor (float).

    Raises:
        ValueError: When a required scale value is missing for the chosen mode.
    """
    # TODO @jepe: implement handling of edge-cases
    # TODO @jepe: fix all the instrument readers (replace floats in raw_units with strings)

    units_spec = _resolve_units_spec(cellpy_units, to_units)
    new_units = units_spec
    old_units = _resolve_raw_units(from_units, data)

    if mode == "gravimetric":
        scale_explicit = value is not None or mass is not None
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
        value_q = _coerce_scale(
            scale,
            default_unit=new_units["mass"],
            unit_override=mass_unit,
            explicit=scale_explicit,
            name="mass",
        )
        to_unit_specific = Q(1.0, new_units["specific_gravimetric"])

    elif mode == "areal":
        scale_explicit = value is not None or active_electrode_area is not None
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
        value_q = _coerce_scale(
            scale,
            default_unit=new_units["area"],
            unit_override=area_unit,
            explicit=scale_explicit,
            name="active_electrode_area",
        )
        to_unit_specific = Q(1.0, new_units["specific_areal"])

    elif mode == "volumetric":
        scale_explicit = value is not None or volume is not None
        scale = (
            value
            if value is not None
            else _resolve_optional_attr(
                explicit=volume,
                cell_meta=cell_meta,
                meta_attr="volume",
                data=data,
                data_attr="volume",
            )
        )
        scale = _require_attr(scale, "volume", context="volumetric mode")
        value_q = _coerce_scale(
            scale,
            default_unit=new_units["volume"],
            unit_override=volume_unit,
            explicit=scale_explicit,
            name="volume",
        )
        to_unit_specific = Q(1.0, new_units["specific_volumetric"])

    elif mode == "absolute":
        value_q = Q(1.0, None)
        to_unit_specific = Q(1.0, None)

    else:
        logger.debug(f"mode={mode} not supported!")
        return 1.0

    from_unit_cap = Q(1.0, old_units["charge"])
    to_unit_cap = Q(1.0, new_units["charge"])

    # from unit is always in absolute values:
    from_unit = from_unit_cap

    to_unit = to_unit_cap / to_unit_specific

    conversion_factor = (from_unit / to_unit / value_q).to_reduced_units()
    logger.debug(f"conversion factor: {conversion_factor}")
    return conversion_factor.m


def nominal_capacity_as_absolute(
    data: Any = None,
    value: Optional[QuantityValue] = None,
    specific: Optional[QuantityValue] = None,
    nom_cap_specifics: Optional[str] = None,
    convert_charge_units: bool = False,
    *,
    cell_meta: Optional[CellMeta] = None,
    raw_units: Optional[CellpyUnits] = None,
    nom_cap_unit: Optional[str] = None,
    specific_unit: Optional[str] = None,
    cellpy_units: Optional[CellpyUnits] = None,
) -> float:
    """Get the nominal capacity as absolute value.

    Args:
        data: Optional data instance (cellpy's richer object may supply attrs).
        value: Nominal capacity in specific units (e.g. mAh/g when gravimetric).
            A bare number uses ``CellpyUnits().nominal_capacity`` (default
            ``mAh/g``); a string is parsed as a pint quantity.
        specific: Scale factor (mass, area, …) matching ``nom_cap_specifics``.
            Bare numbers use the matching cellpy unit (``mg`` or ``cm**2`` by
            default).
        nom_cap_specifics: How ``value`` is specified (gravimetric, areal, …).
        convert_charge_units: Whether to convert between raw and cellpy charge units.
        cell_meta: Optional cell metadata supplying ``nom_cap``, ``nom_cap_specifics``,
            ``mass``, and ``active_electrode_area``.
        raw_units: Raw charge units for ``convert_charge_units``; defaults to
            ``data.raw_units`` or ``CellpyUnits()`` when unset.
        nom_cap_unit: Unit string for a bare numeric ``value`` (overrides
            ``cellpy_units['nominal_capacity']``).
        specific_unit: Unit string for a bare numeric ``specific`` scale.
        cellpy_units: Bulk override for default unit strings when coercing
            explicit ``value`` / ``specific`` inputs.

    Returns:
        Absolute nominal capacity in Ah.

    Raises:
        ValueError: When required inputs cannot be resolved.
        NotImplementedError: For volumetric mode.
    """

    units_spec = _resolve_units_spec(cellpy_units)
    value_passed = value is not None
    specific_passed = specific is not None

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

    value_q = _coerce_scale(
        value,
        default_unit=units_spec["nominal_capacity"],
        unit_override=nom_cap_unit,
        explicit=value_passed,
        name="nom_cap",
    )

    if nom_cap_specifics == "gravimetric":
        specific = _require_attr(specific, "mass", context="gravimetric nom_cap")
        specific_q = _coerce_scale(
            specific,
            default_unit=units_spec["mass"],
            unit_override=specific_unit,
            explicit=specific_passed,
            name="mass",
        )
    elif nom_cap_specifics == "areal":
        specific = _require_attr(
            specific, "active_electrode_area", context="areal nom_cap"
        )
        specific_q = _coerce_scale(
            specific,
            default_unit=units_spec["area"],
            unit_override=specific_unit,
            explicit=specific_passed,
            name="active_electrode_area",
        )
    elif nom_cap_specifics == "absolute":
        specific_q = 1

    # TODO: implement volumetric
    elif nom_cap_specifics == "volumetric":
        raise NotImplementedError("volumetric not implemented yet")

    if convert_charge_units:
        resolved_raw_units = _resolve_raw_units(raw_units, data)
        conversion_factor_charge = Q(1, units_spec["charge"]) / Q(
            1, resolved_raw_units["charge"]
        )
    else:
        conversion_factor_charge = 1.0

    absolute_value = (
        (value_q * conversion_factor_charge * specific_q).to_reduced_units().to("Ah")
    )

    return absolute_value.m


def calculate_nom_cap_abs_from_specific(
    nom_cap: QuantityValue,
    specific: QuantityValue,
    *,
    specific_type: str = "gravimetric",
    nom_cap_unit: Optional[str] = None,
    specific_unit: Optional[str] = None,
    cellpy_units: Optional[CellpyUnits] = None,
    convert_charge_units: bool = False,
    raw_units: Optional[CellpyUnits] = None,
) -> float:
    """Convert a specific nominal capacity to an absolute value (e.g. Ah).

    Convenience wrapper for the common standalone case where ``nom_cap`` and
    geometry are known as plain floats or pint quantity strings. Gravimetric
    inputs delegate to ``nominal_capacity_as_absolute``; areal and absolute use
    the matching cellpy unit strings directly.

    Args:
        nom_cap: Nominal capacity in specific units. A bare number uses the
            default for ``specific_type`` (``mAh/g`` gravimetric,
            ``mAh/cm**2`` areal, ``mAh`` absolute); a string is parsed by pint
            (e.g. ``"3.579 Ah/g"``).
        specific: Matching scale factor — active-material mass for gravimetric,
            electrode area for areal (ignored when ``specific_type`` is
            ``"absolute"``). Defaults: ``mg`` (gravimetric), ``cm**2`` (areal).
        specific_type: How ``nom_cap`` is specified: ``"gravimetric"``,
            ``"areal"``, or ``"absolute"``.
        nom_cap_unit: Unit string for a bare numeric ``nom_cap``.
        specific_unit: Unit string for a bare numeric ``specific``.
        cellpy_units: Bulk override for default unit strings.
        convert_charge_units: When ``True``, convert from raw charge units to
            cellpy output charge units before returning (gravimetric only).
        raw_units: Raw charge units for ``convert_charge_units``; defaults to
            ``CellpyUnits()`` when unset.

    Returns:
        Absolute nominal capacity (float, in Ah).
    """
    units_spec = _resolve_units_spec(cellpy_units)

    if specific_type == "gravimetric":
        return nominal_capacity_as_absolute(
            value=nom_cap,
            specific=specific,
            nom_cap_specifics="gravimetric",
            convert_charge_units=convert_charge_units,
            raw_units=raw_units,
            nom_cap_unit=nom_cap_unit,
            specific_unit=specific_unit,
            cellpy_units=units_spec,
        )

    if specific_type == "areal":
        cap_unit = nom_cap_unit or (f"{units_spec['charge']}/{units_spec['area']}")
        cap = _as_quantity(nom_cap, cap_unit, name="nom_cap")
        area_q = _as_quantity(
            specific,
            specific_unit or units_spec["area"],
            name="active_electrode_area",
        )
        absolute = cap * area_q
    elif specific_type == "absolute":
        absolute = _as_quantity(
            nom_cap,
            nom_cap_unit or units_spec["charge"],
            name="nom_cap",
        )
    else:
        raise ValueError(
            f"unsupported specific_type {specific_type!r}; "
            "expected 'gravimetric', 'areal', or 'absolute'"
        )

    if convert_charge_units:
        resolved_raw = raw_units or CellpyUnits()
        absolute = absolute * (
            Q(1, units_spec["charge"]) / Q(1, resolved_raw["charge"])
        )

    return absolute.to_reduced_units().to("Ah").m


def calculate_current_conversion_factor(
    raw_current_unit: str,
    *,
    to_units: Optional[CellpyUnits] = None,
) -> float:
    """Compute the factor that converts raw current units to cellpy output units.

    The returned float is suitable for ``current_conversion_factor`` in
    ``make_core_summary`` / ``c_rates_to_summary``: multiply raw-current C-rate
    contributions by this factor so they use the output current unit (default
    ``CellpyUnits().current``, typically ``"A"``).

    Args:
        raw_current_unit: Pint-compatible unit string for the raw current column
            (e.g. ``"mA"``).
        to_units: Output unit spec; defaults to ``CellpyUnits()``.

    Returns:
        Dimensionless conversion factor (raw → output current).
    """
    output_units = to_units or get_cellpy_units()
    factor = Q(1.0, raw_current_unit) / Q(1.0, output_units["current"])
    return factor.to_reduced_units().m


def calculate_throughput_conversion_factor(
    raw_current_unit: str,
    raw_time_unit: str,
    *,
    to_units: Optional[CellpyUnits] = None,
) -> float:
    """Compute the factor converting ``current * time`` to the charge unit.

    The returned float is suitable for ``conversion_factor`` in
    ``summarizers.throughput_to_raw``: the raw current integral is in
    ``current_unit * time_unit`` (e.g. A·s) and the nominal capacity it is
    divided by is a charge (e.g. mAh), so the integral needs scaling first
    (issue #138).

    Args:
        raw_current_unit: Pint-compatible unit string for the raw current
            column (e.g. ``"A"``).
        raw_time_unit: Pint-compatible unit string for the raw test-time
            column (e.g. ``"s"``).
        to_units: Output unit spec; defaults to ``CellpyUnits()``.

    Returns:
        Dimensionless conversion factor (raw current·time → output charge).
    """
    output_units = to_units or get_cellpy_units()
    return calculate_scaler(f"{raw_current_unit}*{raw_time_unit}", output_units["charge"])


# Per-property aliases for spec labels whose bare string means something else
# (or nothing) to pint. The spec keeps the legacy label; conversion/validation
# uses the pint-parsable form. Decision recorded on issue #115:
# temperature "C" is Celsius (never coulomb), frequency "hz" is hertz.
_PINT_LABEL_ALIASES: dict[str, dict[str, str]] = {
    "temperature": {"C": "degC"},
    "frequency": {"hz": "Hz"},
}


def _pint_unit_label(physical_property: str, unit: str) -> str:
    """Return the pint-parsable label for a unit string on the spec."""
    return _PINT_LABEL_ALIASES.get(physical_property, {}).get(unit, unit)


def convert_value(
    value: Union[QuantityValue, tuple],
    physical_property: str,
    from_units: Optional[CellpyUnits] = None,
    to_units: Optional[CellpyUnits] = None,
) -> float:
    """Convert ``value`` between unit specs for one physical property.

    Generalized port of legacy ``CellpyCell.to_cellpy_unit`` (unit plan §3):
    the default direction is raw units → cellpy units, both falling back to
    ``CellpyUnits()`` when unset.

    Args:
        value: A bare number (interpreted in ``from_units[physical_property]``),
            a pint quantity string (e.g. ``"25 mV"``), or a ``(value, unit)``
            tuple (e.g. ``(25, "mV")``).
        physical_property: Key on the ``CellpyUnits`` spec (e.g. ``"voltage"``).
        from_units: Input unit spec; defaults to ``CellpyUnits()``.
        to_units: Output unit spec; defaults to ``CellpyUnits()``.

    Returns:
        The value expressed in ``to_units[physical_property]`` (float).

    Raises:
        KeyError: When ``physical_property`` is not a ``CellpyUnits`` field.
        ValueError: When a quantity string carries no units.
        TypeError: When ``value`` is neither number, string, nor tuple.
    """
    source = from_units or CellpyUnits()
    target = to_units or CellpyUnits()
    if physical_property not in source.keys():
        raise KeyError(
            f"unknown physical_property {physical_property!r}; expected one of "
            f"{sorted(CellpyUnits().keys())}"
        )
    default_unit = _pint_unit_label(physical_property, source[physical_property])
    target_unit = _pint_unit_label(physical_property, target[physical_property])
    if isinstance(value, tuple):
        quantity = Q(*value)
    else:
        quantity = _as_quantity(value, default_unit, name=physical_property)
    return quantity.to(target_unit).m


def calculate_scaler(from_unit: str, to_unit: str) -> float:
    """Return the multiplicative factor that converts ``from_unit`` → ``to_unit``.

    Port of legacy ``CellpyCell.unit_scaler_from_raw`` reduced to its essence
    (``Q(1, a).to(b).m``); cellpy wraps it as
    ``calculate_scaler(raw_units[prop], unit)``.

    Note: only valid for multiplicative units — offset units (``degC``) raise
    ``pint.errors.OffsetUnitCalculusError`` by design; use ``convert_value``
    for temperatures.
    """
    return Q(1.0, from_unit).to(to_unit).m


def validate_units(units: Any, *, strict: bool = True) -> CellpyUnits:
    """Validate a unit spec: every label must be a pint-parsable unit string.

    The loader-boundary validator (unit plan Phase 3, loader plan §2.2):
    instrument configurations declare ``raw_units`` and this turns them into a
    validated ``CellpyUnits`` built on top of the defaults.

    Args:
        units: A ``CellpyUnits`` instance or a plain mapping of
            ``physical_property -> unit label``.
        strict: When ``True`` (default) an unparsable label raises
            ``ValueError``; when ``False`` it downgrades to a warning
            (the ``local_instrument`` escape hatch).

    Returns:
        A ``CellpyUnits`` with the validated labels applied over the defaults.
        Keys unknown to ``CellpyUnits`` are warned about, label-checked, and
        left out of the returned spec.

    Raises:
        TypeError: When a label is not a string (e.g. a legacy v7 float scale
            factor).
        ValueError: When a label does not parse as a pint unit (strict mode).

    Notes:
        ``temperature="C"`` is accepted and means Celsius (validated as
        ``degC``, never coulomb); ``frequency="hz"`` is accepted as hertz.
        The original labels are preserved on the returned spec.
    """
    registry = _get_unit_registry()
    known = set(CellpyUnits().keys())
    spec = CellpyUnits()
    items = units.items() if hasattr(units, "items") else dict(units).items()
    for key, label in items:
        if not isinstance(label, str):
            raise TypeError(
                f"unit label for {key!r} must be a string, got "
                f"{type(label).__name__} ({label!r}); float scale factors are a "
                "legacy v7 artifact - declare real unit strings instead"
            )
        try:
            registry.Unit(_pint_unit_label(key, label))
        except Exception as exc:
            message = f"unit label for {key!r} does not parse: {label!r} ({exc})"
            if strict:
                raise ValueError(message) from exc
            warnings.warn(message, stacklevel=2)
            continue
        if key in known:
            spec[key] = label
        else:
            warnings.warn(
                f"unknown unit key {key!r} (validated but kept out of the "
                "CellpyUnits spec)",
                stacklevel=2,
            )
    return spec


def calculate_specific_conversion_factors(
    *,
    mass: Optional[QuantityValue] = None,
    area: Optional[QuantityValue] = None,
    from_units: Optional[CellpyUnits] = None,
    to_units: Optional[CellpyUnits] = None,
    mass_unit: Optional[str] = None,
    area_unit: Optional[str] = None,
    cellpy_units: Optional[CellpyUnits] = None,
) -> dict[str, float]:
    """Build a ``specific_conversion_factors`` mapping for ``add_scaled_summary_columns``.

    Computes gravimetric and/or areal factors via ``get_converter_to_specific``
    and always includes ``"absolute"`` (charge-unit conversion only, typically
    ``1.0`` when raw and output charge units match).

    Args:
        mass: Active-material mass for the gravimetric factor. A bare number
            uses the cellpy mass unit (default ``mg``); a string is parsed by
            pint (e.g. ``"2 mg"``).
        area: Electrode area for the areal factor (default unit ``cm**2``).
        from_units: Raw/input charge units; defaults to ``CellpyUnits()``.
        to_units: Output units; defaults to ``CellpyUnits()``.
        mass_unit: Unit string for a bare numeric ``mass``.
        area_unit: Unit string for a bare numeric ``area``.
        cellpy_units: Bulk override for default mass/area unit strings.

    Returns:
        Mapping ``mode -> factor`` with keys among ``gravimetric``, ``areal``,
        and ``absolute``.
    """
    units_spec = _resolve_units_spec(cellpy_units, to_units)
    factors: dict[str, float] = {}
    if mass is not None:
        factors["gravimetric"] = get_converter_to_specific(
            mass=mass,
            from_units=from_units,
            to_units=to_units,
            mode="gravimetric",
            mass_unit=mass_unit,
            cellpy_units=units_spec,
        )
    if area is not None:
        factors["areal"] = get_converter_to_specific(
            active_electrode_area=area,
            from_units=from_units,
            to_units=to_units,
            mode="areal",
            area_unit=area_unit,
            cellpy_units=units_spec,
        )
    factors["absolute"] = get_converter_to_specific(
        from_units=from_units,
        to_units=to_units,
        mode="absolute",
        cellpy_units=units_spec,
    )
    return factors


def calculate_specific_converters(
    *,
    mass: Optional[QuantityValue] = None,
    area: Optional[QuantityValue] = None,
    from_units: Optional[CellpyUnits] = None,
    to_units: Optional[CellpyUnits] = None,
    mass_unit: Optional[str] = None,
    area_unit: Optional[str] = None,
    cellpy_units: Optional[CellpyUnits] = None,
) -> dict[str, float]:
    """Deprecated alias for ``calculate_specific_conversion_factors``."""
    warnings.warn(
        "`calculate_specific_converters` is deprecated; "
        "use `calculate_specific_conversion_factors` instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return calculate_specific_conversion_factors(
        mass=mass,
        area=area,
        from_units=from_units,
        to_units=to_units,
        mass_unit=mass_unit,
        area_unit=area_unit,
        cellpy_units=cellpy_units,
    )
