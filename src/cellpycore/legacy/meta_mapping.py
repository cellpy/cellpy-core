"""Authoritative legacy ⇄ core metadata field mapping (issue #117, Stage 1.16).

Declares once how legacy cellpy's two metadata dataclasses
(``cellpy.parameters.internal_settings.CellpyMetaCommon`` /
``CellpyMetaIndividualTest``) translate onto the core models
(``cellpycore.metadata.models.CellMeta`` / ``TestMeta``), following the same
pair-tables + exception-sets + totality-tests pattern as the header mapping
(``cellpycore.legacy.mapping``).

Key re-homing decision (metadata plan Step 1): legacy misfiles four
test-dependent fields under "common" (``cell_name``, ``start_datetime``,
``time_zone``, ``tester_ID``) — they map onto ``TestMeta``, not ``CellMeta``.

G9 decision (recorded 2026-07-14): the three tester software/calibration fields
are legitimate test-dependent provenance and map onto ``TestMeta`` fields of the
same name (added there in this change), rather than into an ``extra`` dict.

cellpy-core cannot import cellpy, so the legacy field inventories are pinned
here as frozensets; cellpy's own contract tests guard that the pinned lists
match the real legacy dataclasses (the same arrangement as
``cellpycore.legacy.headers``).
"""

from __future__ import annotations

import logging
from typing import Any, Mapping, Optional

from cellpycore.metadata.models import CellMeta, TestMeta

logger = logging.getLogger(__name__)

# --- pinned legacy field inventories -----------------------------------------
# ``cellpy.parameters.internal_settings.CellpyMetaCommon`` (29 fields).
LEGACY_COMMON_FIELDS = frozenset(
    {
        "cell_name",
        "start_datetime",
        "time_zone",
        "comment",
        "file_errors",
        "raw_id",
        "cellpy_file_version",
        "tester_ID",
        "tester_server_software_version",
        "tester_client_software_version",
        "tester_calibration_date",
        "material",
        "mass",
        "tot_mass",
        "nom_cap",
        "nom_cap_specifics",
        "active_electrode_area",
        "active_electrode_thickness",
        "active_electrode_loading",
        "electrolyte_volume",
        "electrolyte_type",
        "active_electrode_type",
        "counter_electrode_type",
        "reference_electrode_type",
        "experiment_type",
        "cell_type",
        "separator_type",
        "active_electrode_current_collector",
        "reference_electrode_current_collector",
    }
)

# ``cellpy.parameters.internal_settings.CellpyMetaIndividualTest``.
# Note: ``schedule_file_name`` is an **un-annotated class attribute** in the
# legacy dataclass (``schedule_file_name = None``), not a dataclass field —
# it still carries data when set, so it participates in the mapping; cellpy's
# contract test must compare against fields *plus* this documented attribute.
LEGACY_INDIVIDUAL_FIELDS = frozenset(
    {
        "channel_index",
        "creator",
        "schedule_file_name",
        "test_type",
        "voltage_lim_low",
        "voltage_lim_high",
        "cycle_mode",
        "test_ID",
    }
)

# --- pair tables ---------------------------------------------------------------
# ``(legacy_field, core_field)``; mostly identity for the cell-dependent block.
COMMON_TO_CELL_PAIRS = [
    ("material", "material"),
    ("mass", "mass"),
    ("tot_mass", "tot_mass"),
    ("nom_cap", "nom_cap"),
    ("nom_cap_specifics", "nom_cap_specifics"),
    ("active_electrode_area", "active_electrode_area"),
    ("active_electrode_thickness", "active_electrode_thickness"),
    ("active_electrode_loading", "active_electrode_loading"),
    ("electrolyte_volume", "electrolyte_volume"),
    ("electrolyte_type", "electrolyte_type"),
    ("active_electrode_type", "active_electrode_type"),
    ("counter_electrode_type", "counter_electrode_type"),
    ("reference_electrode_type", "reference_electrode_type"),
    ("separator_type", "separator_type"),
    ("cell_type", "cell_type"),
    ("experiment_type", "experiment_type"),
    ("active_electrode_current_collector", "active_electrode_current_collector"),
    ("reference_electrode_current_collector", "reference_electrode_current_collector"),
    ("comment", "comment"),
]

# The re-homed fields: legacy filed them under "common", but they are
# test-dependent — they land on ``TestMeta``. Includes the G9 tester triplet.
COMMON_TO_TEST_PAIRS = [
    ("cell_name", "cell_name"),
    ("start_datetime", "start_datetime"),
    ("time_zone", "time_zone"),
    ("tester_ID", "tester_id"),
    ("tester_server_software_version", "tester_server_software_version"),
    ("tester_client_software_version", "tester_client_software_version"),
    ("tester_calibration_date", "tester_calibration_date"),
]

# ``CellpyMetaIndividualTest`` fields — all map onto ``TestMeta``.
INDIVIDUAL_TO_TEST_PAIRS = [
    ("channel_index", "channel"),
    ("creator", "creator"),
    ("schedule_file_name", "schedule_file_name"),
    ("test_type", "test_type"),
    ("voltage_lim_low", "voltage_lim_low"),
    ("voltage_lim_high", "voltage_lim_high"),
    ("cycle_mode", "cycle_mode"),
    ("test_ID", "test_id"),  # int coercion; see ``coerce_test_id``
]

# --- documented exceptions -------------------------------------------------------
# Legacy fields that die or move to other layers; value = destination note.
LEGACY_ONLY = {
    "file_errors": "dropped (marked 'not in use' in legacy)",
    "raw_id": "superseded by TestMeta.uuid",
    "cellpy_file_version": "file-format layer (cellpy readers/cellpy_file/format.py)",
}

# Core fields legacy never had. Migration fills them from context (provenance
# stamped by the loading framework; ``volume`` is the new volumetric-mode field).
CORE_ONLY_CELL = frozenset({"volume"})
CORE_ONLY_TEST = frozenset(
    {
        "uuid",
        "test_family",
        "source_kind",
        "source_type",
        "source_uri",
        "source_uuid",
        "raw_file_names",
        "loaded_datetime",
        "comment",
        "cell",
    }
)


# --- helpers ----------------------------------------------------------------------
def coerce_test_id(value: Any, *, default: int = 0) -> int:
    """Coerce a legacy ``test_ID`` value to a compact int ``test_id``.

    Legacy sometimes holds lists (multi-test files): take the first entry and
    log the rest, per the metadata plan Step 1.

    Args:
        value: Legacy ``test_ID`` (int, numeric string, list/tuple, or None).
        default: Returned when ``value`` is None or empty.

    Returns:
        The coerced integer test id.

    Raises:
        ValueError: When the value (or its first list entry) is not
            interpretable as an integer.
    """
    if value is None:
        return default
    if isinstance(value, (list, tuple)):
        if not value:
            return default
        if len(value) > 1:
            logger.info(
                "legacy test_ID holds %d values %r; taking the first",
                len(value),
                value,
            )
        value = value[0]
    if isinstance(value, bool):
        raise ValueError(f"cannot interpret legacy test_ID {value!r} as an int")
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"cannot interpret legacy test_ID {value!r} as an int"
        ) from exc


def _pick(source: Mapping[str, Any], key: str) -> Any:
    """Read ``key`` from a mapping or attribute-style legacy object."""
    if hasattr(source, "get"):
        return source.get(key)
    return getattr(source, key, None)


def legacy_meta_to_core(
    common: Optional[Mapping[str, Any]] = None,
    individual: Optional[Mapping[str, Any]] = None,
) -> tuple[CellMeta, TestMeta]:
    """Build ``(CellMeta, TestMeta)`` from legacy metadata objects/mappings.

    Pure translation via the pair tables — no provenance is invented here
    (that is the loading framework's job). ``LEGACY_ONLY`` fields are ignored
    with their documented destinations; absent fields stay ``None``.

    Args:
        common: Legacy ``CellpyMetaCommon`` instance or field mapping.
        individual: Legacy ``CellpyMetaIndividualTest`` instance or mapping.

    Returns:
        The translated ``(CellMeta, TestMeta)`` pair (``TestMeta.cell`` is left
        unset; linking is the caller's decision).
    """
    cell = CellMeta()
    test = TestMeta()
    if common is not None:
        for legacy_field, core_field in COMMON_TO_CELL_PAIRS:
            value = _pick(common, legacy_field)
            if value is not None:
                setattr(cell, core_field, value)
        for legacy_field, core_field in COMMON_TO_TEST_PAIRS:
            value = _pick(common, legacy_field)
            if value is not None:
                setattr(test, core_field, value)
    if individual is not None:
        for legacy_field, core_field in INDIVIDUAL_TO_TEST_PAIRS:
            value = _pick(individual, legacy_field)
            if core_field == "test_id":
                test.test_id = coerce_test_id(value)
            elif value is not None:
                setattr(test, core_field, value)
    return cell, test
