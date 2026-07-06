"""Column mapping between the harmonized-raw schema and BDF notations.

The harmonized-raw side is resolved from an injected ``cellpycore.config``
column object (``RawCols`` by default), so custom schemas keep working. The
BDF side uses the notations from the Battery Data Alliance ontology:
https://battery-data-alliance.github.io/battery-data-format-ontology/battery-data-format.html

Conventions honored:

- cellpy-core capacities/energies are cumulative **per cycle, per direction**
  (reset each cycle), which matches the BDF ``cycle_*`` terms — not the
  never-resetting test-level ``charging_capacity_ah`` family.
- ``epoch_time_utc`` (int64 nanoseconds, UTC) maps to ``unix_time_second``
  (float seconds); the ns <-> s conversion is handled by export/read, not by
  this table.
- BDF says converters must not renumber cycles and should preserve
  ``step_type`` values as reported; the mapping only renames, never rewrites.
"""

from typing import Optional

from cellpycore import config

# BDF notation of the absolute-timestamp column; needs ns <-> s conversion.
BDF_UNIX_TIME = "unix_time_second"

# BDF obligation "required" — export fails fast when these are missing.
REQUIRED_BDF_COLUMNS = ("current_ampere", "voltage_volt")


def bdf_mapping(raw_cols: Optional[config.Cols] = None) -> dict[str, str]:
    """Build the harmonized-raw -> BDF column-name mapping.

    Args:
        raw_cols: The raw column-header schema to resolve harmonized-raw
            names from. Defaults to the native ``config.RawCols``.

    Returns:
        Mapping of harmonized-raw column name to BDF notation. Harmonized
        columns without a BDF counterpart (bookkeeping columns like
        ``source_uuid`` or ``test_id``) are deliberately absent.
    """
    r = raw_cols if raw_cols is not None else config.RawCols()
    return {
        r.datapoint_num: "record_index",
        r.epoch_time_utc: BDF_UNIX_TIME,
        r.test_time: "test_time_second",
        r.step_time: "step_time_second",
        r.step_num: "step_count",
        r.cycle_num: "cycle_count",
        r.step_type: "step_type",
        r.potential: "voltage_volt",
        r.current: "current_ampere",
        r.cumulative_charge_capacity: "cycle_charging_capacity_ah",
        r.cumulative_discharge_capacity: "cycle_discharging_capacity_ah",
        r.cumulative_charge_energy: "cycle_charging_energy_wh",
        r.cumulative_discharge_energy: "cycle_discharging_energy_wh",
        r.internal_resistance: "internal_resistance_ohm",
        r.aux_temperature_cell: "surface_temperature_celsius",
        r.aux_temperature_chamber: "ambient_temperature_celsius",
        r.aux_pressure_cell: "surface_pressure_pa",
    }
