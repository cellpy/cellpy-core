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
    assert units.get_converter_to_specific(_stub(), mode=mode) == pytest.approx(expected)


def test_get_converter_to_specific_unknown_mode_is_identity():
    assert units.get_converter_to_specific(_stub(), mode="nonsense") == 1.0


def test_get_converter_to_specific_charge_unit_mismatch():
    # raw charge in A*h (=1000 mAh) vs output charge mAh scales the factor x1000.
    raw = CellpyUnits()
    raw["charge"] = "A*h"
    assert units.get_converter_to_specific(
        _stub(raw_units=raw), mode="gravimetric"
    ) == pytest.approx(500_000.0)


# --- nominal_capacity_as_absolute ---------------------------------------------
# Gravimetric, default units: (nom_cap mAh/g * mass mg).to("Ah")
#   = nom_cap * mass * 1e-6 Ah. With nom_cap=3000, mass=2.0 -> 0.006 Ah.
def test_nominal_capacity_as_absolute_gravimetric():
    assert units.nominal_capacity_as_absolute(
        _stub(), nom_cap_specifics="gravimetric"
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
