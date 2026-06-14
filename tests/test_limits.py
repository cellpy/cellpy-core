"""Tests for the CellpyLimits port (issue #12, Phase 1).

CellpyLimits holds the step-type detection thresholds and is mirrored from
``cellpy.parameters.internal_settings.CellpyLimits``. The standalone default
step-detection limits used by ``make_step_table`` are derived from it.
"""

from dataclasses import asdict

from cellpycore.legacy import CellpyLimits, STEP_TYPES, CAPACITY_MODIFIERS
from cellpycore.summarizers import DEFAULT_RAW_LIMITS


EXPECTED_LIMITS = {
    "current_hard": 1e-13,
    "current_soft": 1e-05,
    "stable_current_hard": 2.0,
    "stable_current_soft": 4.0,
    "stable_voltage_hard": 2.0,
    "stable_voltage_soft": 4.0,
    "stable_charge_hard": 0.9,
    "stable_charge_soft": 5.0,
    "ir_change": 1e-05,
}


def test_cellpy_limits_values_match_legacy():
    assert asdict(CellpyLimits()) == EXPECTED_LIMITS


def test_default_raw_limits_derived_from_cellpy_limits():
    assert DEFAULT_RAW_LIMITS == asdict(CellpyLimits())


def test_cellpy_limits_is_dict_like():
    """CellpyLimits behaves like a dict (BaseSettings), as the engine indexes it."""
    limits = CellpyLimits()
    assert limits["current_hard"] == limits.current_hard
    assert set(limits.keys()) == set(EXPECTED_LIMITS)


def test_step_types_are_canonical():
    """The canonical step-type labels include the ones make_step_table assigns."""
    for label in ("charge", "discharge", "rest", "cv_charge", "cv_discharge", "ir"):
        assert label in STEP_TYPES
    assert CAPACITY_MODIFIERS == ["reset"]
