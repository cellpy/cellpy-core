"""Converter-parity tests for ``cellpycore.units`` (STEP-12, issue #40).

``cellpycore.units.get_converter_to_specific`` and ``nominal_capacity_as_absolute``
are verbatim ports of cellpy's converter functions
(``cellpy.readers.cellreader.CellpyCell``). cellpy-core must not import cellpy, so
parity is pinned here against hand-computed golden floats derived from the documented
unit math. These goldens let cellpy retire its duplicate converters without silent
drift: if either side's math changes, this test (or cellpy's) fails loudly.

Requires the optional ``units`` extra (pint); skipped otherwise.
"""

from types import SimpleNamespace

import pytest

pytest.importorskip("pint")

from cellpycore import units
from cellpycore.cell_core import Data
from cellpycore.metadata.models import CellMeta
from cellpycore.units import CellpyUnits


def _stub(raw_units=None, **attrs):
    """Minimal stand-in for ``Data`` exposing only what the converters read."""
    base = dict(
        raw_units=raw_units if raw_units is not None else CellpyUnits(),
        mass=2.0,  # mg
        active_electrode_area=2.0,  # cm**2
        volume=2.0,  # cm**3
        nom_cap=3000.0,  # mAh/g
        nom_cap_specifics="gravimetric",
    )
    base.update(attrs)
    return SimpleNamespace(**base)


# --- get_converter_to_specific -------------------------------------------------
# Default units: charge=mAh, mass=mg, area=cm**2, specific_gravimetric=g,
# specific_areal=cm**2, specific_volumetric=cm**3. With mass=area=volume=2.0:
#   gravimetric: (1 mAh)/(mAh/g)/(2 mg) = (1 g)/(2 mg) = 1000/2 = 500
#   areal:       (1 mAh)/(mAh/cm**2)/(2 cm**2) = 1/2 = 0.5
#   volumetric:  (1 mAh)/(mAh/cm**3)/(2 cm**3) = 1/2 = 0.5
#   absolute:    dimensionless 1.0
@pytest.mark.parametrize(
    "mode, expected",
    [
        ("gravimetric", 500.0),
        ("areal", 0.5),
        ("volumetric", 0.5),
        ("absolute", 1.0),
    ],
)
def test_get_converter_to_specific_modes(mode, expected):
    assert units.get_converter_to_specific(_stub(), mode=mode) == pytest.approx(
        expected
    )


def test_get_converter_to_specific_unknown_mode_is_identity():
    assert units.get_converter_to_specific(_stub(), mode="nonsense") == 1.0


def test_get_converter_to_specific_charge_unit_mismatch():
    # raw charge in A*h (=1000 mAh) vs output charge mAh scales the factor x1000.
    raw = CellpyUnits()
    raw["charge"] = "A*h"
    assert units.get_converter_to_specific(
        _stub(raw_units=raw), mode="gravimetric"
    ) == pytest.approx(500_000.0)


def test_get_converter_to_specific_via_cell_meta():
    meta = CellMeta(mass=2.0, active_electrode_area=2.0)
    assert units.get_converter_to_specific(
        data=None, cell_meta=meta, mode="gravimetric"
    ) == pytest.approx(500.0)
    assert units.get_converter_to_specific(
        data=None, cell_meta=meta, mode="areal"
    ) == pytest.approx(0.5)


def test_get_converter_to_specific_bare_data_raises_value_error():
    with pytest.raises(ValueError, match="mass"):
        units.get_converter_to_specific(Data(), mode="gravimetric")


# --- nominal_capacity_as_absolute ---------------------------------------------
# Gravimetric, default units: (nom_cap mAh/g * mass mg).to("Ah")
#   = nom_cap * mass * 1e-6 Ah. With nom_cap=3000, mass=2.0 -> 0.006 Ah.
def test_nominal_capacity_as_absolute_gravimetric():
    assert units.nominal_capacity_as_absolute(
        _stub(), nom_cap_specifics="gravimetric"
    ) == pytest.approx(0.006)


def test_nominal_capacity_as_absolute_via_cell_meta():
    meta = CellMeta(
        mass=2.0,
        nom_cap=3000.0,
        nom_cap_specifics="gravimetric",
    )
    assert units.nominal_capacity_as_absolute(
        data=None, cell_meta=meta, nom_cap_specifics="gravimetric"
    ) == pytest.approx(0.006)


def test_nominal_capacity_as_absolute_explicit_value_and_specific():
    # value=1000 mAh/g, specific=0.5 mg -> 1000 * 0.5 * 1e-6 = 5e-4 Ah.
    assert units.nominal_capacity_as_absolute(
        _stub(), value=1000.0, specific=0.5, nom_cap_specifics="gravimetric"
    ) == pytest.approx(0.0005)


def test_nominal_capacity_as_absolute_convert_charge_units():
    # raw charge A*h vs cellpy charge mAh -> extra 1e-3 factor: 0.006 * 1e-3.
    raw = CellpyUnits()
    raw["charge"] = "A*h"
    assert units.nominal_capacity_as_absolute(
        _stub(raw_units=raw),
        nom_cap_specifics="gravimetric",
        convert_charge_units=True,
    ) == pytest.approx(6e-6)


# --- standalone convenience helpers -------------------------------------------


def test_calculate_nom_cap_abs_from_specific_gravimetric():
    assert units.calculate_nom_cap_abs_from_specific(3000.0, 2.0) == pytest.approx(
        0.006
    )


def test_calculate_nom_cap_abs_from_specific_areal():
    # 100 mAh/cm**2 * 2 cm**2 -> 200 mAh = 0.2 Ah
    assert units.calculate_nom_cap_abs_from_specific(
        100.0, 2.0, specific_type="areal"
    ) == pytest.approx(0.2)


def test_calculate_current_conversion_factor_mA_to_A():
    assert units.calculate_current_conversion_factor("mA") == pytest.approx(0.001)


def test_calculate_current_conversion_factor_identity():
    assert units.calculate_current_conversion_factor("A") == pytest.approx(1.0)


def test_calculate_specific_conversion_factors_default_units():
    result = units.calculate_specific_conversion_factors(mass=2.0, area=2.0)
    assert result == {
        "gravimetric": pytest.approx(500.0),
        "areal": pytest.approx(0.5),
        "absolute": pytest.approx(1.0),
    }


def test_calculate_specific_conversion_factors_mass_only():
    result = units.calculate_specific_conversion_factors(mass=2.0)
    assert result == {
        "gravimetric": pytest.approx(500.0),
        "absolute": pytest.approx(1.0),
    }


def test_calculate_specific_converters_deprecated_alias():
    with pytest.deprecated_call():
        result = units.calculate_specific_converters(mass=2.0)
    assert result["gravimetric"] == pytest.approx(500.0)


# --- explicit units and quantity strings (issue #112) ------------------------


def test_calculate_nom_cap_abs_from_specific_ah_g_quantity_strings():
    expected = units.calculate_nom_cap_abs_from_specific(
        3.579, 1.334, nom_cap_unit="Ah/g", specific_unit="mg"
    )
    assert units.calculate_nom_cap_abs_from_specific(
        "3.579 Ah/g", "1.334 mg"
    ) == pytest.approx(expected)
    assert expected == pytest.approx(0.004774386)


def test_nominal_capacity_as_absolute_quantity_strings():
    assert units.nominal_capacity_as_absolute(
        value="1000 mAh/g", specific="0.5 mg", nom_cap_specifics="gravimetric"
    ) == pytest.approx(0.0005)


def test_get_converter_to_specific_mass_quantity_string():
    assert units.get_converter_to_specific(
        mass="2 mg", mode="gravimetric"
    ) == pytest.approx(500.0)


def test_get_converter_to_specific_mass_in_grams():
    assert units.get_converter_to_specific(
        mass=2.0, mass_unit="g", mode="gravimetric"
    ) == pytest.approx(0.5)


def test_calculate_specific_conversion_factors_mass_quantity_string():
    result = units.calculate_specific_conversion_factors(mass="2 mg", area="2 cm**2")
    assert result == {
        "gravimetric": pytest.approx(500.0),
        "areal": pytest.approx(0.5),
        "absolute": pytest.approx(1.0),
    }


def test_as_quantity_rejects_unitless_string():
    from cellpycore.units.converters import _as_quantity

    with pytest.raises(ValueError, match="no units"):
        _as_quantity("3.579", "mAh/g", name="nom_cap")


# --- convert_value (issue #115, Stage 1.13) --------------------------------------


def test_convert_value_bare_number_default_specs_is_identity():
    assert units.convert_value(2.0, "mass") == pytest.approx(2.0)


def test_convert_value_between_specs():
    grams = CellpyUnits(mass="g")
    assert units.convert_value(2.0, "mass", from_units=grams) == pytest.approx(2000.0)
    assert units.convert_value(2000.0, "mass", to_units=grams) == pytest.approx(2.0)


def test_convert_value_quantity_string():
    assert units.convert_value("0.5 Ah", "charge") == pytest.approx(500.0)


def test_convert_value_tuple():
    assert units.convert_value((0.5, "Ah"), "charge") == pytest.approx(500.0)


def test_convert_value_temperature_c_means_celsius():
    kelvin = CellpyUnits(temperature="K")
    assert units.convert_value(25.0, "temperature", to_units=kelvin) == pytest.approx(
        298.15
    )


def test_convert_value_unknown_property_raises_keyerror():
    with pytest.raises(KeyError, match="physical_property"):
        units.convert_value(1.0, "swagger")


def test_convert_value_unitless_string_raises():
    with pytest.raises(ValueError, match="no units"):
        units.convert_value("5", "mass")


def test_convert_value_bad_type_raises():
    with pytest.raises(TypeError):
        units.convert_value(object(), "mass")


# --- calculate_scaler -------------------------------------------------------------


def test_calculate_scaler_ma_to_a():
    assert units.calculate_scaler("mA", "A") == pytest.approx(1e-3)


def test_calculate_scaler_identity():
    assert units.calculate_scaler("V", "V") == pytest.approx(1.0)


def test_calculate_scaler_from_raw_spec_matches_legacy_semantics():
    raw = CellpyUnits()
    assert units.calculate_scaler(raw["charge"], "Ah") == pytest.approx(1e-3)


# --- validate_units ---------------------------------------------------------------


def test_validate_units_default_spec_is_valid():
    spec = units.validate_units(CellpyUnits())
    assert isinstance(spec, CellpyUnits)
    assert spec["temperature"] == "C"
    assert spec["frequency"] == "hz"


def test_validate_units_mapping_layers_over_defaults():
    spec = units.validate_units({"charge": "Ah", "mass": "g"})
    assert spec["charge"] == "Ah"
    assert spec["mass"] == "g"
    assert spec["current"] == CellpyUnits().current


def test_validate_units_bad_label_raises():
    with pytest.raises(ValueError, match="does not parse"):
        units.validate_units({"charge": "not-a-unit"})


def test_validate_units_bad_label_warns_when_not_strict():
    with pytest.warns(UserWarning, match="does not parse"):
        spec = units.validate_units({"charge": "not-a-unit"}, strict=False)
    assert spec["charge"] == CellpyUnits().charge


def test_validate_units_float_label_raises_typeerror():
    with pytest.raises(TypeError, match="v7"):
        units.validate_units({"charge": 1000.0})


def test_validate_units_unknown_key_warns_and_is_dropped():
    with pytest.warns(UserWarning, match="unknown unit key"):
        spec = units.validate_units({"charge": "mAh", "swagger": "V"})
    assert "swagger" not in spec.keys()
