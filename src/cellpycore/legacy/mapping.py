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
    ("test_id", "test_id"),  # identity; carried for campaign / multi-test (#136)
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
    ("temperature_cell_mean", "temperature_mean"),
    ("temperature_cell_last", "temperature_last"),
    # Identity pass-throughs (native name already equals the legacy name).
    ("test_id", "test_id"),  # campaign / multi-test key (#136)
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
LEGACY_ONLY_RAW = frozenset(
    {
        "aci_phase_angle",
        "ref_aci_phase_angle",
        "ac_impedance",
        "ref_ac_impedance",
        "charge_energy",
        "date_time",
        "discharge_energy",
        "power",
        "is_fc_data",
        "sub_step_index",
        "sub_step_time",
        "test_id",
        "reference_voltage",
        "dv_dt",
        "frequency",
        "amplitude",
        "channel_id",
        "data_flag",
        "test_name",
    }
)

# Native RawCols column values with no legacy HeadersNormal counterpart.
# (``ref_potential`` is deliberately not bridged to legacy ``reference_voltage``:
# legacy HeadersStepTable has no reference-voltage aggregates, so bridging the
# raw column would grow the legacy step frame and break byte parity. The signal
# is native-path only; see issue #43.)
NATIVE_ONLY_RAW = frozenset(
    {
        "source_datapoint_num",
        "mask",
        "epoch_time_utc",
        "source_type",
        "source_uuid",
        "test_id",
        "source_step_num",
        "step_type",
        "step_type_detail",
        "step_mode",
        "cycle_type",
        "cumulative_charge_energy",
        "cumulative_discharge_energy",
        "step_charge_power",
        "step_discharge_power",
        "ref_potential",
        "aux_temperature_cell",
        "aux_temperature_chamber",
        "aux_pressure_cell",
    }
)

# Legacy HeadersStepTable column values with no native StepCols counterpart.
# (``ustep`` is emitted by the engine as a literal "ustep" column only when
# ``usteps=True``; it has no declared StepCols field.)
LEGACY_ONLY_STEP = frozenset({"test", "ustep", "info", "ir_pct_change"})

# Native StepCols *signals* with no legacy counterpart (power / energy
# statistics, the boolean ``mask``). Compared at base-signal granularity, i.e.
# after stripping the ``STAT_SUFFIXES`` from statistic columns. ``test_id`` is
# bridged as an identity scalar (issue #136) so campaign merges keep per-test
# grouping through the legacy step table.
NATIVE_ONLY_STEP = frozenset(
    {"power", "charge_energy", "discharge_energy", "mask", "ref_potential"}
)

# Legacy HeadersSummary column values with no native CycleCols counterpart
# (legacy-only cruft: cumulated CE, shifted / RIC capacities, OCV mins/maxes,
# normalized capacities, temperatures, levels, passthrough identity columns).
LEGACY_ONLY_CYCLE = frozenset(
    {
        "date_time",
        "test_name",
        "data_flag",
        "channel_id",
        "cumulated_coulombic_efficiency",
        "normalized_charge_capacity",
        "normalized_discharge_capacity",
        "shifted_charge_capacity",
        "shifted_discharge_capacity",
        "ocv_first_min",
        "ocv_second_min",
        "ocv_first_max",
        "ocv_second_max",
        "cumulated_ric_disconnect",
        "cumulated_ric_sei",
        "cumulated_ric",
        "low_level",
        "high_level",
        "aux_",
    }
)

# Native CycleCols column values with no legacy HeadersSummary counterpart.
# (``test_id`` is bridged as an identity pass-through — issue #136.)
NATIVE_ONLY_CYCLE = frozenset(
    {
        "mask",
        "datapoint_num_first",
        "first_epoch_time_utc",
        "last_epoch_time_utc",
        "first_test_time",
        "cycle_duration",
        "charge_duration",
        "discharge_duration",
        "rest_duration",
        "test_net_capacity",
        "charge_energy",
        "discharge_energy",
        "cycle_net_energy",
        "energy_efficiency",
        "test_cumulated_charge_energy",
        "test_cumulated_discharge_energy",
        "test_net_energy",
        "current_charge_mean",
        "current_charge_mean_tw",
        "current_charge_mean_cw",
        "current_charge_max",
        "current_charge_min",
        "current_discharge_mean",
        "current_discharge_mean_tw",
        "current_discharge_mean_cw",
        "current_discharge_max",
        "current_discharge_min",
        "potential_charge_mean",
        "potential_charge_mean_tw",
        "potential_charge_mean_cw",
        "potential_charge_max",
        "potential_charge_min",
        "potential_discharge_mean",
        "potential_discharge_mean_tw",
        "potential_discharge_mean_cw",
        "potential_discharge_max",
        "potential_discharge_min",
        "potential_start_charge",
        "potential_start_discharge",
        "voltage_efficiency",
        "power_charge_mean",
        "power_charge_mean_tw",
        "power_charge_mean_cw",
        "power_charge_max",
        "power_charge_min",
        "power_discharge_mean",
        "power_discharge_mean_tw",
        "power_discharge_mean_cw",
        "power_discharge_max",
        "power_discharge_min",
        "ir_start_charge",
        "ir_end_charge",
        "ir_start_discharge",
        "ir_end_discharge",
        "relaxation_potential_charge",
        "relaxation_potential_discharge",
        "open_circuit_potential_charge",
        "open_circuit_potential_discharge",
        "cv_share",
        "cv_charge_capacity",
        "cv_charge_energy",
        "cv_charge_time",
        "cc_charge_capacity",
        "cc_charge_energy",
        "cc_charge_time",
        "temperature_cell_max",
        "temperature_cell_min",
        # Throughput-based ageing metrics (issue #138); no legacy counterpart.
        "test_cumulated_capacity_throughput",
        "equivalent_full_cycles",
    }
)


# -----------------------------------------------------------------------------
#   Attribute-level mapping (issue #116, Stage 1.14).
#
#   The value-based tables above serve DataFrame renames; the deprecation shim
#   and ``translate.py`` also need to resolve **legacy attribute names**
#   (``headers_normal.voltage_txt``, ``hdr_steps.cycle``, ...) onto the native
#   schema. Keys below are the legacy dataclass *attribute* names; values are:
#
#   - "raw" / "cycle": the native ``RawCols`` / ``CycleCols`` field name.
#   - "step": the native **base-signal** name (statistic columns are formed by
#     appending ``STAT_SUFFIXES`` variants, exactly as in
#     :func:`native_to_legacy_step`); scalar step attributes resolve to their
#     ``StepCols`` field directly.
#
#   Totality discipline: every attribute of the legacy dataclass is either a
#   key here or listed in ``LEGACY_ATTR_UNMAPPED`` (its column value has no
#   native counterpart — same population as the ``LEGACY_ONLY_*`` value sets).
# -----------------------------------------------------------------------------
LEGACY_ATTR_TO_SCHEMA = {
    "raw": {
        # HeadersNormal attribute -> RawCols field
        "charge_capacity_txt": "cumulative_charge_capacity",
        "current_txt": "current",
        "cycle_index_txt": "cycle_num",
        "data_point_txt": "datapoint_num",
        "discharge_capacity_txt": "cumulative_discharge_capacity",
        "internal_resistance_txt": "internal_resistance",
        "step_index_txt": "step_num",
        "step_time_txt": "step_time",
        "test_time_txt": "test_time",
        "voltage_txt": "potential",
    },
    "step": {
        # HeadersStepTable attribute -> StepCols base signal or scalar field
        "charge": "charge_capacity",
        "current": "current",
        "cycle": "cycle_num",
        "discharge": "discharge_capacity",
        "internal_resistance": "internal_resistance",
        "point": "datapoint_num",
        "rate_avr": "c_rate",
        "step": "step_num",
        "step_time": "step_time",
        "sub_step": "sub_step_num",
        "sub_type": "sub_step_type",
        "test_id": "test_id",
        "test_time": "test_time",
        "type": "step_type",
        "voltage": "potential",
    },
    "cycle": {
        # HeadersSummary attribute -> CycleCols field
        "charge_c_rate": "charge_c_rate",
        "charge_capacity": "charge_capacity",
        "charge_capacity_loss": "charge_capacity_loss",
        "test_id": "test_id",
        # Duplicate-value pair: ``charge_capacity_raw`` shares its column value
        # with ``charge_capacity`` (both "charge_capacity"); the shim maps both
        # here and owns the disambiguation warning (native-headers plan D6).
        "charge_capacity_raw": "charge_capacity",
        "coulombic_difference": "coulombic_difference",
        "coulombic_efficiency": "coulombic_efficiency",
        "cumulated_charge_capacity": "test_cumulated_charge_capacity",
        "cumulated_charge_capacity_loss": "test_cumulated_charge_capacity_loss",
        "cumulated_coulombic_difference": "test_cumulated_coulombic_difference",
        "cumulated_discharge_capacity": "test_cumulated_discharge_capacity",
        "cumulated_discharge_capacity_loss": "test_cumulated_discharge_capacity_loss",
        "cycle_index": "cycle_num",
        "data_point": "datapoint_num_last",
        "discharge_c_rate": "discharge_c_rate",
        "discharge_capacity": "discharge_capacity",
        "discharge_capacity_loss": "discharge_capacity_loss",
        # Duplicate-value pair partner of ``discharge_capacity`` (see above).
        "discharge_capacity_raw": "discharge_capacity",
        "end_voltage_charge": "potential_end_charge",
        "end_voltage_discharge": "potential_end_discharge",
        "ir_charge": "ir_charge",
        "ir_discharge": "ir_discharge",
        "normalized_cycle_index": "normalized_cycle_index",
        "temperature_last": "temperature_cell_last",
        "temperature_mean": "temperature_cell_mean",
        "test_time": "last_test_time",
    },
}

# Legacy attributes whose column values have no native counterpart (they mirror
# the ``LEGACY_ONLY_*`` value sets, keyed by attribute name instead of value).
LEGACY_ATTR_UNMAPPED = {
    "raw": frozenset(
        {
            "aci_phase_angle_txt",
            "ref_aci_phase_angle_txt",
            "ac_impedance_txt",
            "ref_ac_impedance_txt",
            "charge_energy_txt",
            "datetime_txt",
            "discharge_energy_txt",
            "power_txt",
            "is_fc_data_txt",
            "sub_step_index_txt",
            "sub_step_time_txt",
            "test_id_txt",
            "ref_voltage_txt",
            "dv_dt_txt",
            "frequency_txt",
            "amplitude_txt",
            "channel_id_txt",
            "data_flag_txt",
            "test_name_txt",
        }
    ),
    "step": frozenset({"test", "ustep", "info", "internal_resistance_change"}),
    "cycle": frozenset(
        {
            "datetime",
            "test_name",
            "data_flag",
            "channel_id",
            "cumulated_coulombic_efficiency",
            "normalized_charge_capacity",
            "normalized_discharge_capacity",
            "shifted_charge_capacity",
            "shifted_discharge_capacity",
            "ocv_first_min",
            "ocv_second_min",
            "ocv_first_max",
            "ocv_second_max",
            "cumulated_ric_disconnect",
            "cumulated_ric_sei",
            "cumulated_ric",
            "low_level",
            "high_level",
            "pre_aux",
        }
    ),
}

# The legacy attribute pairs that share one column value (native-headers plan
# D6): the accessor shim maps both sides and warns about the ambiguity.
DUPLICATE_VALUE_ATTRS = {
    "cycle": (
        ("charge_capacity", "charge_capacity_raw"),
        ("discharge_capacity", "discharge_capacity_raw"),
    ),
}


def legacy_attr_to_native(frame: str, attr: str) -> str:
    """Resolve a legacy header *attribute* name to its native name.

    Args:
        frame: ``"raw"``, ``"step"``, or ``"cycle"`` (the Schema frame).
        attr: The legacy dataclass attribute (e.g. ``"voltage_txt"``).

    Returns:
        The native field name (``"raw"``/``"cycle"``) or base-signal name
        (``"step"`` — combine with :data:`STAT_SUFFIXES` for statistic columns).

    Raises:
        KeyError: When the frame is unknown, or the attribute is unmapped
            (legacy-only) or entirely unknown.
    """
    try:
        table = LEGACY_ATTR_TO_SCHEMA[frame]
    except KeyError:
        raise KeyError(
            f"unknown frame {frame!r}; expected one of {sorted(LEGACY_ATTR_TO_SCHEMA)}"
        ) from None
    if attr in table:
        return table[attr]
    if attr in LEGACY_ATTR_UNMAPPED[frame]:
        raise KeyError(
            f"legacy attribute {attr!r} ({frame}) has no native counterpart "
            "(legacy-only column)"
        )
    raise KeyError(f"unknown legacy attribute {attr!r} for frame {frame!r}")


def expand_specific_columns(rename: dict, specific_columns, modes) -> dict:
    """Extend a native → legacy rename dict with ``{col}_{mode}`` variants.

    The ``{col}_{gravimetric|areal|absolute}`` postfix expansion previously
    inlined in ``OldCellpyCellCore.add_scaled_summary_columns`` — lifted here
    (issue #116) so the bridge and the cellpy-file importer share one
    implementation.

    Args:
        rename: Base native → legacy rename mapping (not mutated).
        specific_columns: Native column names that carry specific variants.
        modes: Postfix modes (e.g. ``["gravimetric", "areal", "absolute"]``).

    Returns:
        dict: A new mapping = ``rename`` plus ``{col}_{mode} ->
        {legacy_col}_{mode}`` for every combination (``legacy_col`` falls back
        to ``col`` when unmapped).
    """
    expanded = dict(rename)
    for col in specific_columns:
        legacy_col = rename.get(col, col)
        for mode in modes:
            expanded[f"{col}_{mode}"] = f"{legacy_col}_{mode}"
    return expanded


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
