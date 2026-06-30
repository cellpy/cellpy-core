# contains mocks and legacy code to help with the migration to cellpy core

from dataclasses import dataclass
import logging
import numbers
from typing import List

from cellpycore.config import STEP_TYPES  # noqa: F401  (re-exported; see note below)

# ``DictLikeClass``/``BaseSettings`` now live in ``cellpycore.settings_base`` and
# ``CellpyUnits`` in ``cellpycore.units`` (STEP-12 promotion, issue #40). They are
# re-imported here so existing ``cellpycore.legacy`` imports (and the cellpy<->core
# settings-parity contract test) keep resolving them from this module.
from cellpycore.settings_base import BaseSettings, DictLikeClass  # noqa: F401
from cellpycore.units import CellpyUnits  # noqa: F401


logger = logging.getLogger(__name__)


class CellpyError(Exception):
    """Base class for other exceptions"""

    pass


class NoDataFound(CellpyError):
    """Exception raised when no data is found"""

    pass


# Canonical list of step-type labels produced by step-type detection in
# ``summarizers.make_step_table`` (mirrors cellpy). The vocabulary is now
# defined once as ``config.StepType``; ``STEP_TYPES`` is imported from there
# (above) so this module keeps its historical name. ``CAPACITY_MODIFIERS`` lists
# step labels that modify the running capacity (reserved for future use).
CAPACITY_MODIFIERS = ["reset"]


# -----------------------------------------------------------------------------
#   Old cellpy limits class (step-type detection thresholds).
# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
#   Old cellpy meta class.
# -----------------------------------------------------------------------------
@dataclass
class Meta:
    pass


class MockMetaTestDependent(Meta):
    cycle_mode: str = "anode"


# -----------------------------------------------------------------------------
#   Old cellpy headers class.
# -----------------------------------------------------------------------------
@dataclass
class BaseHeaders(BaseSettings):
    """Subclass of BaseSetting including option to add postfixes.

    Example:
         >>> header["key_postfix"]  # returns "value_postfix"
    """

    postfixes = []

    def __getitem__(self, key):
        postfix = ""
        if key not in self._field_names:
            # check postfix:
            subs = key.split("_")
            _key = "_".join(subs[:-1])
            _postfix = subs[-1]
            if _postfix in self.postfixes:
                postfix = f"_{_postfix}"
                key = _key
        try:
            v = getattr(self, key)
            return f"{v}{postfix}"
        except AttributeError:
            raise KeyError(f"missing key: {key}")


@dataclass
class HeadersNormal(BaseHeaders):
    """Headers used for the normal (raw) data (used as column headers for the main data pandas DataFrames)"""

    aci_phase_angle_txt: str = "aci_phase_angle"
    ref_aci_phase_angle_txt: str = "ref_aci_phase_angle"
    ac_impedance_txt: str = "ac_impedance"
    ref_ac_impedance_txt: str = "ref_ac_impedance"
    charge_capacity_txt: str = "charge_capacity"
    charge_energy_txt: str = "charge_energy"
    current_txt: str = "current"
    cycle_index_txt: str = "cycle_index"
    data_point_txt: str = "data_point"
    datetime_txt: str = "date_time"
    discharge_capacity_txt: str = "discharge_capacity"
    discharge_energy_txt: str = "discharge_energy"
    internal_resistance_txt: str = "internal_resistance"
    power_txt: str = "power"
    is_fc_data_txt: str = "is_fc_data"
    step_index_txt: str = "step_index"
    sub_step_index_txt: str = "sub_step_index"
    step_time_txt: str = "step_time"
    sub_step_time_txt: str = "sub_step_time"
    test_id_txt: str = "test_id"
    test_time_txt: str = "test_time"
    voltage_txt: str = "voltage"
    ref_voltage_txt: str = "reference_voltage"
    dv_dt_txt: str = "dv_dt"
    frequency_txt: str = "frequency"
    amplitude_txt: str = "amplitude"
    channel_id_txt: str = "channel_id"
    data_flag_txt: str = "data_flag"
    test_name_txt: str = "test_name"


@dataclass
class HeadersSummary(BaseHeaders):
    """Headers used for the summary data (used as column headers for the main data pandas DataFrames)

    In addition to the headers defined here, the summary might also contain
    specific headers (ending in _gravimetric or _areal).
    """

    postfixes = ["gravimetric", "areal", "absolute"]

    cycle_index: str = "cycle_index"
    data_point: str = "data_point"
    test_time: str = "test_time"
    datetime: str = "date_time"
    discharge_capacity_raw: str = "discharge_capacity"
    charge_capacity_raw: str = "charge_capacity"
    test_name: str = "test_name"
    data_flag: str = "data_flag"
    channel_id: str = "channel_id"

    coulombic_efficiency: str = "coulombic_efficiency"
    cumulated_coulombic_efficiency: str = "cumulated_coulombic_efficiency"

    discharge_capacity: str = "discharge_capacity"
    charge_capacity: str = "charge_capacity"
    cumulated_charge_capacity: str = "cumulated_charge_capacity"
    cumulated_discharge_capacity: str = "cumulated_discharge_capacity"

    coulombic_difference: str = "coulombic_difference"
    cumulated_coulombic_difference: str = "cumulated_coulombic_difference"
    discharge_capacity_loss: str = "discharge_capacity_loss"
    charge_capacity_loss: str = "charge_capacity_loss"
    cumulated_discharge_capacity_loss: str = "cumulated_discharge_capacity_loss"
    cumulated_charge_capacity_loss: str = "cumulated_charge_capacity_loss"

    normalized_charge_capacity: str = "normalized_charge_capacity"
    normalized_discharge_capacity: str = "normalized_discharge_capacity"

    shifted_charge_capacity: str = "shifted_charge_capacity"
    shifted_discharge_capacity: str = "shifted_discharge_capacity"

    ir_discharge: str = "ir_discharge"
    ir_charge: str = "ir_charge"
    ocv_first_min: str = "ocv_first_min"
    ocv_second_min: str = "ocv_second_min"
    ocv_first_max: str = "ocv_first_max"
    ocv_second_max: str = "ocv_second_max"
    end_voltage_discharge: str = "end_voltage_discharge"
    end_voltage_charge: str = "end_voltage_charge"
    cumulated_ric_disconnect: str = "cumulated_ric_disconnect"
    cumulated_ric_sei: str = "cumulated_ric_sei"
    cumulated_ric: str = "cumulated_ric"
    normalized_cycle_index: str = "normalized_cycle_index"
    low_level: str = "low_level"
    high_level: str = "high_level"

    temperature_last: str = "temperature_last"
    temperature_mean: str = "temperature_mean"

    charge_c_rate: str = "charge_c_rate"
    discharge_c_rate: str = "discharge_c_rate"
    pre_aux: str = "aux_"

    @property
    def areal_charge_capacity(self) -> str:
        import warnings

        warnings.warn(
            "using old-type look-up (areal_charge_capacity) -> will be deprecated soon",
            DeprecationWarning,
            stacklevel=2,
        )
        return f"{self.charge_capacity}_areal"

    @property
    def areal_discharge_capacity(self) -> str:
        import warnings

        warnings.warn(
            "using old-type look-up (areal_discharge_capacity) -> will be deprecated soon",
            DeprecationWarning,
            stacklevel=2,
        )
        return f"{self.discharge_capacity}_areal"

    @property
    def specific_columns(self) -> List[str]:
        """Returns a list of the columns that can be "specific" (e.g. pr. mass or pr. area) for the summary table."""
        return [
            self.discharge_capacity,
            self.charge_capacity,
            self.cumulated_charge_capacity,
            self.cumulated_discharge_capacity,
            self.coulombic_difference,
            self.cumulated_coulombic_difference,
            self.discharge_capacity_loss,
            self.charge_capacity_loss,
            self.cumulated_discharge_capacity_loss,
            self.cumulated_charge_capacity_loss,
            self.shifted_charge_capacity,
            self.shifted_discharge_capacity,
            # self.cumulated_ric_disconnect,
            # self.cumulated_ric_sei,
            # self.cumulated_ric,
            # self.normalized_cycle_index,
        ]


@dataclass
class HeadersStepTable(BaseHeaders):
    """Headers used for the steps table (used as column headers for the steps pandas DataFrames)"""

    test: str = "test"
    ustep: str = "ustep"
    cycle: str = "cycle"
    step: str = "step"
    test_time: str = "test_time"
    step_time: str = "step_time"
    sub_step: str = "sub_step"
    type: str = "type"
    sub_type: str = "sub_type"
    info: str = "info"
    voltage: str = "voltage"
    current: str = "current"
    charge: str = "charge"
    discharge: str = "discharge"
    point: str = "point"
    internal_resistance: str = "ir"
    internal_resistance_change: str = "ir_pct_change"
    rate_avr: str = "rate_avr"


class MockCore:
    def __init__(self):
        self.cellpy_units = CellpyUnits()

    # Candidates for cellpy core extension.
    def _dump_cellpy_unit(self, value, parameter):
        """Parse for unit, update cellpy_units class, and return magnitude."""
        import numpy as np

        c_value, c_unit = self._check_value_unit(value, parameter)
        if not isinstance(c_value, numbers.Number) or np.isnan(c_value):
            logger.critical(f"Could not parse {parameter} ({value})")
            logger.critical("Setting it to 1.0")
            return 1.0
        if c_unit is not None:
            self.cellpy_units[parameter] = f"{c_unit}"
            logger.debug(f"Updated your cellpy_units['{parameter}'] to '{c_unit}'")

        return c_value

    @staticmethod
    def _check_value_unit(value, parameter) -> tuple:
        """Check if value is a valid number, or a quantity with units."""
        if isinstance(value, numbers.Number):
            return value, None
        logger.critical(f"Parsing {parameter} ({value})")

        try:
            from cellpycore.units import Q

            c = Q(value)
            c_unit = c.units
            c_value = c.magnitude
        except ValueError:
            logger.debug(f"Could not parse {value}")
            return None, None
        return c_value, c_unit


# NOT USED
def set_col_first(df, col_names):
    """Set selected columns first in a pandas.DataFrame.

    This function sets cols with names given in  col_names (a list) first in
    the DataFrame. The last col in col_name will come first (processed last)

    """

    column_headings = df.columns
    column_headings = column_headings.tolist()
    try:
        for col_name in col_names:
            column_headings.pop(column_headings.index(col_name))
            column_headings.insert(0, col_name)

    finally:
        df = df.reindex(columns=column_headings)
        return df
