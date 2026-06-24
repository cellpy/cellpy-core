"""Authoritative ``config.Cols`` <-> legacy ``Headers*`` column-name mapping.

This module is the single source of truth for how the native cellpy-core column
names (``config.RawCols`` / ``config.StepCols`` / ``config.CycleCols``) translate
to and from the legacy cellpy names (``legacy.HeadersNormal`` /
``legacy.HeadersStepTable`` / ``legacy.HeadersSummary``).

The legacy bridge (``cell_core.OldCellpyCellCore``) builds all of its native
<-> legacy rename dictionaries from the declarations here, so the translation
lives in exactly one place and is covered by ``tests/test_header_mapping.py``
(round-trip, totality, and bridge-parity tests).

Design notes:

- The mapping is defined over **column-name strings** (the values of the
  dataclass fields), not over attribute names. This is what DataFrame renames
  act on, and it side-steps the fact that legacy ``HeadersSummary`` has two
  attributes that share a value (``discharge_capacity`` /
  ``discharge_capacity_raw``).
- Pairs include **identity pass-throughs** (native string == legacy string,
  e.g. summary ``ir_charge`` / ``charge_c_rate`` / ``normalized_cycle_index``).
  These columns are intentionally not renamed by the bridge (they already share
  a name), but they are real, mapped columns and must be declared so the
  "total" claim holds.
- "Lossless and total" is defined **modulo the documented exception sets**
  below: every native column is either mapped or listed in a ``NATIVE_ONLY_*``
  set, and every legacy column is either mapped or listed in a ``LEGACY_ONLY_*``
  set. The exception sets are explicit (not derived) so that adding a new column
  on either side fails the totality test until it is deliberately categorised.

Step-table granularity: the step engine produces per-signal statistic columns
(``<signal>_<stat>``). The native/legacy *base-signal* correspondence is declared
in :data:`STEP_BASE_PAIRS` and expanded with :data:`STAT_SUFFIXES`; scalar
(non-statistic) step columns are in :data:`STEP_SCALAR_PAIRS`. Note that the
``datapoint_num`` and ``test_time`` step signals are declared in ``StepCols`` only
with ``_first`` / ``_last`` variants (the engine emits just those two stats for
them), even though they participate in the base-signal mapping.
"""

# --- statistic suffixes (native -> legacy) ----------------------------------
# The per-step engine names statistics ``<signal>_<native_stat>``; legacy cellpy
# uses ``<signal>_<legacy_stat>`` (only ``mean`` -> ``avr`` actually differs).
STAT_SUFFIXES = {
    "mean": "avr",
    "std": "std",
    "min": "min",
    "max": "max",
    "first": "first",
    "last": "last",
    "delta": "delta",
}

# --- raw frame (native RawCols <-> legacy HeadersNormal) ---------------------
# Each entry is ``(native, legacy)``. Only these raw columns cross the bridge;
# everything else is a documented exception below.
RAW_PAIRS = [
    ("datapoint_num", "data_point"),
    ("test_time", "test_time"),
    ("step_time", "step_time"),
    ("cycle_num", "cycle_index"),
    ("step_num", "step_index"),
    ("current", "current"),
    ("potential", "voltage"),
    ("cumulative_charge_capacity", "charge_capacity"),
    ("cumulative_discharge_capacity", "discharge_capacity"),
    ("internal_resistance", "internal_resistance"),
]

# --- step table (native StepCols <-> legacy HeadersStepTable) ----------------
# Base signals carry the seven ``STAT_SUFFIXES`` variants; ``(native, legacy)``.
STEP_BASE_PAIRS = [
    ("datapoint_num", "point"),
    ("test_time", "test_time"),
    ("step_time", "step_time"),
    ("current", "current"),
    ("potential", "voltage"),
    ("charge_capacity", "charge"),
    ("discharge_capacity", "discharge"),
    ("internal_resistance", "ir"),
]

# Scalar (non-statistic) step columns; ``(native, legacy)``.
STEP_SCALAR_PAIRS = [
    ("cycle_num", "cycle"),
    ("step_num", "step"),
    ("sub_step_num", "sub_step"),
    ("step_type", "type"),
    ("sub_step_type", "sub_type"),
    ("c_rate", "rate_avr"),
]

# --- cycle / summary (native CycleCols <-> legacy HeadersSummary) ------------
# ``(native, legacy)``. Includes identity pass-throughs (last block) so the
# totality claim holds; the bridge treats those as no-op renames.
CYCLE_PAIRS = [
    ("cycle_num", "cycle_index"),
    ("datapoint_num_last", "data_point"),
    ("last_test_time", "test_time"),
    ("charge_capacity", "charge_capacity"),
    ("discharge_capacity", "discharge_capacity"),
    ("coulombic_efficiency", "coulombic_efficiency"),
    ("coulombic_difference", "coulombic_difference"),
    ("charge_capacity_loss", "charge_capacity_loss"),
    ("discharge_capacity_loss", "discharge_capacity_loss"),
    ("test_cumulated_charge_capacity", "cumulated_charge_capacity"),
    ("test_cumulated_discharge_capacity", "cumulated_discharge_capacity"),
    ("test_cumulated_coulombic_difference", "cumulated_coulombic_difference"),
    ("test_cumulated_charge_capacity_loss", "cumulated_charge_capacity_loss"),
    ("test_cumulated_discharge_capacity_loss", "cumulated_discharge_capacity_loss"),
    ("potential_end_charge", "end_voltage_charge"),
    ("potential_end_discharge", "end_voltage_discharge"),
    # Identity pass-throughs (native name already equals the legacy name).
    ("ir_charge", "ir_charge"),
    ("ir_discharge", "ir_discharge"),
    ("charge_c_rate", "charge_c_rate"),
    ("discharge_c_rate", "discharge_c_rate"),
    ("normalized_cycle_index", "normalized_cycle_index"),
]

# -----------------------------------------------------------------------------
#   Documented exceptions (columns with no counterpart on the other side).
#   These make "lossless/total" well-defined; the totality test asserts that the
#   declared columns of each class equal (mapped columns) ∪ (its exception set).
# -----------------------------------------------------------------------------

# Legacy HeadersNormal column values with no native RawCols counterpart.
# (``test_id`` exists on both sides with the same name but is intentionally not
# translated by the raw bridge, so it is listed as an exception on both sides.)
LEGACY_ONLY_RAW = frozenset({
    "aci_phase_angle", "ref_aci_phase_angle", "ac_impedance", "ref_ac_impedance",
    "charge_energy", "date_time", "discharge_energy", "power", "is_fc_data",
    "sub_step_index", "sub_step_time", "test_id", "reference_voltage", "dv_dt",
    "frequency", "amplitude", "channel_id", "data_flag", "test_name",
})

# Native RawCols column values with no legacy HeadersNormal counterpart.
NATIVE_ONLY_RAW = frozenset({
    "source_datapoint_num", "mask", "epoch_time_utc", "source_type",
    "source_uuid", "test_id", "source_step_num", "step_type", "step_type_detail",
    "step_mode", "cycle_type", "cumulative_charge_energy",
    "cumulative_discharge_energy", "step_charge_power", "step_discharge_power",
    "aux_temperature_cell", "aux_temperature_chamber", "aux_pressure_cell",
})

# Legacy HeadersStepTable column values with no native StepCols counterpart.
# (``ustep`` is emitted by the engine as a literal "ustep" column only when
# ``usteps=True``; it has no declared StepCols field.)
LEGACY_ONLY_STEP = frozenset({"test", "ustep", "info", "ir_pct_change"})

# Native StepCols *signals* with no legacy counterpart (power / energy
# statistics, and the boolean ``mask``). Compared at base-signal granularity,
# i.e. after stripping the ``STAT_SUFFIXES`` from statistic columns.
NATIVE_ONLY_STEP = frozenset({"power", "charge_energy", "discharge_energy", "mask"})

# Legacy HeadersSummary column values with no native CycleCols counterpart
# (legacy-only cruft: cumulated CE, shifted / RIC capacities, OCV mins/maxes,
# normalized capacities, temperatures, levels, passthrough identity columns).
LEGACY_ONLY_CYCLE = frozenset({
    "date_time", "test_name", "data_flag", "channel_id",
    "cumulated_coulombic_efficiency", "normalized_charge_capacity",
    "normalized_discharge_capacity", "shifted_charge_capacity",
    "shifted_discharge_capacity", "ocv_first_min", "ocv_second_min",
    "ocv_first_max", "ocv_second_max", "cumulated_ric_disconnect",
    "cumulated_ric_sei", "cumulated_ric", "low_level", "high_level",
    "temperature_last", "temperature_mean", "aux_",
})

# Native CycleCols column values with no legacy HeadersSummary counterpart.
NATIVE_ONLY_CYCLE = frozenset({
    "mask", "datapoint_num_first", "first_epoch_time_utc", "last_epoch_time_utc",
    "first_test_time", "cycle_duration", "charge_duration", "discharge_duration",
    "rest_duration", "test_net_capacity", "charge_energy", "discharge_energy",
    "cycle_net_energy", "energy_efficiency", "test_cumulated_charge_energy",
    "test_cumulated_discharge_energy", "test_net_energy",
    "current_charge_mean", "current_charge_mean_tw", "current_charge_mean_cw",
    "current_charge_max", "current_charge_min", "current_discharge_mean",
    "current_discharge_mean_tw", "current_discharge_mean_cw",
    "current_discharge_max", "current_discharge_min",
    "potential_charge_mean", "potential_charge_mean_tw", "potential_charge_mean_cw",
    "potential_charge_max", "potential_charge_min", "potential_discharge_mean",
    "potential_discharge_mean_tw", "potential_discharge_mean_cw",
    "potential_discharge_max", "potential_discharge_min",
    "potential_start_charge", "potential_start_discharge", "voltage_efficiency",
    "power_charge_mean", "power_charge_mean_tw", "power_charge_mean_cw",
    "power_charge_max", "power_charge_min", "power_discharge_mean",
    "power_discharge_mean_tw", "power_discharge_mean_cw", "power_discharge_max",
    "power_discharge_min", "ir_start_charge", "ir_end_charge", "ir_start_discharge",
    "ir_end_discharge", "relaxation_potential_charge",
    "relaxation_potential_discharge", "open_circuit_potential_charge",
    "open_circuit_potential_discharge", "cv_share", "cv_charge_capacity",
    "cv_charge_energy", "cv_charge_time", "cc_charge_capacity", "cc_charge_energy",
    "cc_charge_time",
})


# -----------------------------------------------------------------------------
#   Derivation helpers (the bridge builds its rename dicts from these).
# -----------------------------------------------------------------------------
def legacy_to_native_raw(columns=None) -> dict:
    """Return the legacy -> native rename dict for the raw frame.

    Args:
        columns: Optional iterable of column names actually present. When given,
            the result is filtered to keys in ``columns`` (so the dict is safe to
            pass straight to ``DataFrame.rename``).

    Returns:
        dict: Mapping ``legacy_name -> native_name``.
    """
    mapping = {legacy: native for native, legacy in RAW_PAIRS}
    if columns is not None:
        cols = set(columns)
        mapping = {k: v for k, v in mapping.items() if k in cols}
    return mapping


def native_to_legacy_step() -> dict:
    """Return the native -> legacy rename dict for the step table.

    Expands :data:`STEP_BASE_PAIRS` with every :data:`STAT_SUFFIXES` variant and
    appends the scalar :data:`STEP_SCALAR_PAIRS`.

    Returns:
        dict: Mapping ``native_name -> legacy_name``.
    """
    rename = {}
    for native_base, legacy_base in STEP_BASE_PAIRS:
        for native_stat, legacy_stat in STAT_SUFFIXES.items():
            rename[f"{native_base}_{native_stat}"] = f"{legacy_base}_{legacy_stat}"
    for native, legacy in STEP_SCALAR_PAIRS:
        rename[native] = legacy
    return rename


def legacy_to_native_step() -> dict:
    """Return the inverse of :func:`native_to_legacy_step` (legacy -> native)."""
    return {v: k for k, v in native_to_legacy_step().items()}


def native_to_legacy_summary() -> dict:
    """Return the native -> legacy rename dict for the per-cycle summary.

    Returns:
        dict: Mapping ``native_name -> legacy_name`` (identity pass-throughs
        included; harmless no-op renames for the bridge).
    """
    return {native: legacy for native, legacy in CYCLE_PAIRS}


def legacy_to_native_summary() -> dict:
    """Return the inverse of :func:`native_to_legacy_summary` (legacy -> native)."""
    return {v: k for k, v in native_to_legacy_summary().items()}
