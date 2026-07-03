"""Step-type detection thresholds (mirrored from cellpy)."""

from dataclasses import dataclass

from cellpycore.settings_base import BaseSettings

# Step labels that modify the running capacity (reserved for future use).
CAPACITY_MODIFIERS = ["reset"]


@dataclass
class CellpyLimits(BaseSettings):
    """Thresholds used when classifying step types in ``make_step_table``.

    Since all instruments have an inherent inaccuracy, it is naive to assume
    that e.g. the voltage within a constant-voltage step does not change at all.
    These limits define what counts as "constant" and what is assumed to be
    zero.

    Verbatim mirror of ``cellpy.parameters.internal_settings.CellpyLimits``
    (field names and default values), kept here so cellpy-core can build a step
    table standalone and so the bridge copies stay contract-comparable (see
    jepegit/cellpy#378). The keys match :data:`summarizers.DEFAULT_RAW_LIMITS`.
    """

    current_hard: float = 1e-13
    current_soft: float = 1e-05
    stable_current_hard: float = 2.0
    stable_current_soft: float = 4.0
    stable_voltage_hard: float = 2.0
    stable_voltage_soft: float = 4.0
    stable_charge_hard: float = 0.9
    stable_charge_soft: float = 5.0
    ir_change: float = 1e-05
