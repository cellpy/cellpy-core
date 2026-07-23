"""Legacy cellpy column-header dataclasses (``Headers*``)."""

from dataclasses import dataclass
from typing import List

from cellpycore.settings_base import BaseSettings


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
    test_id: str = "test_id"
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
    cumulated_capacity_throughput: str = "cumulated_capacity_throughput"
    equivalent_full_cycles: str = "equivalent_full_cycles"
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
    test_id: str = "test_id"
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
