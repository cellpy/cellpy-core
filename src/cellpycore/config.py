# Definitions of headers and other constants

"""
This module contains definitions of headers and other constants.

Planned features:
- It should also contain a custom dict-like object that can be used to store
the settings. It should allow for both "dot notation" and "bracket notation" to access the keys.
- It should work well with both Polars and Pandas.
- It should be extendable in case we want to add new features in the future.

"""

from dataclasses import dataclass
from enum import StrEnum


class TestMode(StrEnum):
    """Test mode of an electrochemical experiment (cycling configuration).

    Describes whether a cell test is run in the ordinary configuration
    (``NORMAL``) or in the inverted "anode mode" configuration (``INVERTED``).
    This determines the charge/discharge sign conventions the summary / step
    engine must apply when it processes the data.

    The enum is deliberately binary: for sign-convention purposes only "anode
    half-cell vs everything else" matters. cellpy's legacy ``cycle_mode`` string
    carries a wider vocabulary (``"anode"``, ``"cathode"``,
    ``"full_cell"``/``"fullcell"``, ``"standard"``); all non-anode values
    collapse to ``NORMAL`` here. If a finer distinction is ever needed, add new
    members rather than reintroducing free-form strings.

    This is the typed replacement for cellpy's loose ``cycle_mode`` string
    parameter (``cellpy.parameters.prms.Reader.cycle_mode``); it is defined for
    that future use and not yet wired up in this package. When cellpy is
    migrated onto cellpy-core it should pass a ``TestMode`` here instead of a
    bare string, so the mode is validated and the sign conventions are derived
    from it.

    Attributes:
        NORMAL (``"normal"``): The ordinary case (full cells, cathode
            half-cells). The first step uses the standard (non-inverted)
            charge/discharge convention. This is the baseline / default mode.
        INVERTED (``"inverted"``): Anode half-cell ("anode mode"). The electrode
            under test is the anode, cycled against lithium, so the convention
            is inverted relative to ``NORMAL`` (the first step is typically a
            lithiation). This is the case cellpy historically selected with
            ``cycle_mode="anode"``.

    Note:
        Name and members intentionally mirror batbase's metadata enum
        ``ElectroChemicalExperiment.TestMode`` (repo ``ife-bat/batbase``,
        ``src/runs/models.py``). batbase is the metadata/persistence layer; this
        enum is the processing-layer counterpart. They describe the same
        physical reality and must be kept in sync via this mapping::

            TestMode (here)   batbase (stored code)   cellpy cycle_mode
            INVERTED          INVERTED ("i")          "anode"
            NORMAL            NORMAL   ("n")          "full_cell" / "standard" / "cathode"

        Two traps to remember:

        - Storage values differ by layer on purpose: this StrEnum uses the
          self-describing values ``"normal"`` / ``"inverted"``, while batbase
          persists the short codes ``"n"`` / ``"i"`` (its ``TextChoices`` member
          names still read ``NORMAL`` / ``INVERTED``). Translate explicitly at
          the boundary; never compare raw stored values across the two layers.
        - Default-polarity trap: batbase defaults to ``NORMAL``, but cellpy
          historically defaulted ``cycle_mode="anode"`` (i.e. ``INVERTED``).
          When bridging metadata into the engine, map the mode explicitly and
          do not rely on either side's implicit default.
    """

    NORMAL = "normal"
    INVERTED = "inverted"


class StepType(StrEnum):
    """Canonical step-type labels for the ``step_type`` column of the step table.

    This is the single source of truth for the step-type vocabulary (the
    ``STEP_TYPES`` list below is derived from it). It mirrors old cellpy's
    ``CellpyCell.list_of_step_types`` so cross-repo step-type parity is
    preserved.

    Like the other enums in this module it is a *reference* vocabulary: the step
    table stores plain strings and the engine does not validate against this
    enum, so unknown values are still allowed. Extend by adding members rather
    than introducing free-form strings elsewhere.

    Note:
        Not every member is emitted by the built-in classifier. ``_classify_steps``
        in ``summarizers.py`` currently emits only ``charge``, ``discharge``,
        ``cv_charge``, ``cv_discharge``, ``ocvrlx_up``, ``ocvrlx_down``, ``ir``
        and ``rest``. The remaining members (``taper_charge``,
        ``taper_discharge``, ``charge_cv``, ``discharge_cv``, ``not_known``)
        come from explicit step specifications, overrides, or legacy data.

        Known discrepancy (not reconciled here to preserve golden-test parity):
        the classifier labels uncategorized steps with the empty string ``""``,
        not ``not_known``. Unifying ``""`` and ``NOT_KNOWN`` is a follow-up.

    Attributes:
        CHARGE (``"charge"``): Constant-current (or general) charge step.
        DISCHARGE (``"discharge"``): Constant-current (or general) discharge step.
        CV_CHARGE (``"cv_charge"``): Constant-voltage portion of a charge step.
        CV_DISCHARGE (``"cv_discharge"``): Constant-voltage portion of a discharge step.
        TAPER_CHARGE (``"taper_charge"``): Tapering (CV tail) charge step.
        TAPER_DISCHARGE (``"taper_discharge"``): Tapering (CV tail) discharge step.
        CHARGE_CV (``"charge_cv"``): Charge step that includes a CV phase.
        DISCHARGE_CV (``"discharge_cv"``): Discharge step that includes a CV phase.
        OCVRLX_UP (``"ocvrlx_up"``): Open-circuit voltage relaxation, rising potential.
        OCVRLX_DOWN (``"ocvrlx_down"``): Open-circuit voltage relaxation, falling potential.
        IR (``"ir"``): Internal-resistance (instantaneous) step.
        REST (``"rest"``): Rest / pause step (no current, stable potential).
        NOT_KNOWN (``"not_known"``): Uncategorized step (see Note about ``""``).
    """

    CHARGE = "charge"
    DISCHARGE = "discharge"
    CV_CHARGE = "cv_charge"
    CV_DISCHARGE = "cv_discharge"
    TAPER_CHARGE = "taper_charge"
    TAPER_DISCHARGE = "taper_discharge"
    CHARGE_CV = "charge_cv"
    DISCHARGE_CV = "discharge_cv"
    OCVRLX_UP = "ocvrlx_up"
    OCVRLX_DOWN = "ocvrlx_down"
    IR = "ir"
    REST = "rest"
    NOT_KNOWN = "not_known"


# Canonical list of step-type labels, derived from ``StepType`` so there is a
# single source of truth. Kept as a plain list (and named ``STEP_TYPES``) for
# backwards compatibility with existing importers.
STEP_TYPES = [member.value for member in StepType]


class StepMode(StrEnum):
    """Control mode of a step for the ``step_mode`` column of the raw table.

    Describes how the cycler regulated the step (constant current, constant
    voltage, constant power). Like the other enums here it is a *reference*
    vocabulary: the raw table stores plain strings and unknown values are
    allowed; extend by adding members.

    Not produced by the engine yet (only the mock-data helper sets a value).

    Note:
        Absence / "no specific mode" is represented by a null value in the
        table, not by the literal string ``"None"``. The spec table in
        ``docs/data_format_specifications/harmonized_raw.md`` lists ``"None"``
        as a sample value; that is documentation shorthand for "missing" and is
        intentionally not a member here.

    Attributes:
        CC (``"CC"``): Constant current.
        CV (``"CV"``): Constant voltage.
        CP (``"CP"``): Constant power.
    """

    CC = "CC"
    CV = "CV"
    CP = "CP"


class CycleType(StrEnum):
    """Cycle classification for the ``cycle_type`` column of the raw table.

    A *reference* vocabulary (plain strings stored in the table, unknown values
    allowed, extend by adding members). Values keep the capitalization used in
    the spec table in ``docs/data_format_specifications/harmonized_raw.md``.

    Not used by the engine yet.

    Note:
        This may migrate into per-test metadata as ``test_type`` rather than
        staying a per-row raw column (see
        ``.issueflows/04-designs-and-guides/test-metadata-and-merging.md``).
        ``GITT`` also appears as a ``test_type`` example, so ``cycle_type`` and
        ``test_type`` may later be unified into one vocabulary.

    Attributes:
        STANDARD (``"Standard"``): Ordinary cycling.
        GITT (``"GITT"``): Galvanostatic Intermittent Titration Technique.
        ICI (``"ICI"``): Intermittent Current Interruption.
        CHARACTERIZATION (``"Characterization"``): Characterization cycle.
    """

    STANDARD = "Standard"
    GITT = "GITT"
    ICI = "ICI"
    CHARACTERIZATION = "Characterization"


@dataclass
class BaseCols:
    """Shared base for all column-header objects.

    Provides the ``__version__`` field and bracket-notation access
    (``cols["name"]``) on top of attribute access (``cols.name``), so concrete
    header classes can be used interchangeably with both styles.
    """

    __version__: str = "0.1.0"

    def __getitem__(self, key: str) -> str:
        """Allow for bracket notation"""
        return getattr(self, key)


class FlexibleCols(BaseCols):
    """Opt-in base that allows per-attribute name modification.

    Behaves like ``BaseCols`` but routes every attribute access through
    ``__getattribute__``, so subclasses can transform header names on the fly
    (e.g. add a prefix/suffix). This flexibility costs some performance, so use
    it only when dynamic header names are actually needed.
    """

    def __getattribute__(self, key: str) -> str:
        """Modification of the attribute can be done here.

        When implemented in the actual column classes (e.g. CycleCols), you have to add
        a comment in this docstring to show the version of the implementation.

        version 0.1.0:
        - uses the default getattr method, implemented only for showing future us
          where to put code.

        Example: adding a suffix to the attribute name.

            >> original_item = super().__getattribute__(key)
            >> # Since __getattribute__ is used for all attributes (not only the ones we defined in the class)
            >> # we need to check the type of the attribute before we can modify it.
            >> if isinstance(original_item, str):
            >>     modified_item = original_item + "_modified"
            >> else:
            >>     modified_item = original_item
            >> return modified_item

        """

        return super().__getattribute__(key)


class Cols(BaseCols):
    """Standard base for the concrete column-header classes.

    ``CycleCols``, ``StepCols`` and ``RawCols`` inherit from this. Add common
    functionality shared across all header classes here (e.g. a ``to_json``
    method). To enable dynamic header names, swap the inheritance to
    ``FlexibleCols`` (which incurs some performance loss).
    """

    pass


@dataclass(frozen=True)
class Schema:
    """Bundle of the column-header objects for one cell.

    Holds the raw, cycle (summary) and step header definitions so the summary /
    step engine can read its column names from an injected object instead of
    module-level globals. This is what makes the engine schema-agnostic and
    thread-safe: each cell carries its own schema.

    Units are handled by value (the engine multiplies by precomputed conversion
    factors supplied by the caller), so units are deliberately not part of the
    schema.
    """

    raw: BaseCols
    cycle: BaseCols
    step: BaseCols


class CycleCols(Cols):
    """Column-header definitions for the per-cycle summary table.

    Each attribute maps a logical quantity to the column name used in the
    per-cycle summary produced by the summary engine (capacities, efficiencies,
    durations, per-direction current/potential/power statistics, etc.).
    """

    cycle_num: str = "cycle_num"
    mask: str = "mask"
    datapoint_num_first: str = "datapoint_num_first"
    datapoint_num_last: str = "datapoint_num_last"
    first_epoch_time_utc: str = "first_epoch_time_utc"
    last_epoch_time_utc: str = "last_epoch_time_utc"
    first_test_time: str = "first_test_time"
    last_test_time: str = "last_test_time"
    cycle_duration: str = "cycle_duration"
    charge_duration: str = "charge_duration"
    discharge_duration: str = "discharge_duration"
    rest_duration: str = "rest_duration"
    charge_capacity: str = "charge_capacity"
    discharge_capacity: str = "discharge_capacity"
    charge_capacity_loss: str = "charge_capacity_loss"
    discharge_capacity_loss: str = "discharge_capacity_loss"
    coulombic_difference: str = "coulombic_difference"
    coulombic_efficiency: str = "coulombic_efficiency"
    test_cumulated_charge_capacity: str = "test_cumulated_charge_capacity"
    test_cumulated_discharge_capacity: str = "test_cumulated_discharge_capacity"
    test_cumulated_coulombic_difference: str = "test_cumulated_coulombic_difference"
    test_cumulated_charge_capacity_loss: str = "test_cumulated_charge_capacity_loss"
    test_cumulated_discharge_capacity_loss: str = "test_cumulated_discharge_capacity_loss"
    test_net_capacity: str = "test_net_capacity"
    charge_energy: str = "charge_energy"
    discharge_energy: str = "discharge_energy"
    cycle_net_energy: str = "cycle_net_energy"
    energy_efficiency: str = "energy_efficiency"
    test_cumulated_charge_energy: str = "test_cumulated_charge_energy"
    test_cumulated_discharge_energy: str = "test_cumulated_discharge_energy"
    test_net_energy: str = "test_net_energy"
    current_charge_mean: str = "current_charge_mean"
    current_charge_mean_tw: str = "current_charge_mean_tw"
    current_charge_mean_cw: str = "current_charge_mean_cw"
    current_charge_max: str = "current_charge_max"
    current_charge_min: str = "current_charge_min"
    current_discharge_mean: str = "current_discharge_mean"
    current_discharge_mean_tw: str = "current_discharge_mean_tw"
    current_discharge_mean_cw: str = "current_discharge_mean_cw"
    current_discharge_max: str = "current_discharge_max"
    current_discharge_min: str = "current_discharge_min"
    potential_charge_mean: str = "potential_charge_mean"
    potential_charge_mean_tw: str = "potential_charge_mean_tw"
    potential_charge_mean_cw: str = "potential_charge_mean_cw"
    potential_charge_max: str = "potential_charge_max"
    potential_charge_min: str = "potential_charge_min"
    potential_discharge_mean: str = "potential_discharge_mean"
    potential_discharge_mean_tw: str = "potential_discharge_mean_tw"
    potential_discharge_mean_cw: str = "potential_discharge_mean_cw"
    potential_discharge_max: str = "potential_discharge_max"
    potential_discharge_min: str = "potential_discharge_min"
    potential_start_charge: str = "potential_start_charge"
    potential_end_charge: str = "potential_end_charge"
    potential_start_discharge: str = "potential_start_discharge"
    potential_end_discharge: str = "potential_end_discharge"
    voltage_efficiency: str = "voltage_efficiency"
    power_charge_mean: str = "power_charge_mean"
    power_charge_mean_tw: str = "power_charge_mean_tw"
    power_charge_mean_cw: str = "power_charge_mean_cw"
    power_charge_max: str = "power_charge_max"
    power_charge_min: str = "power_charge_min"
    power_discharge_mean: str = "power_discharge_mean"
    power_discharge_mean_tw: str = "power_discharge_mean_tw"
    power_discharge_mean_cw: str = "power_discharge_mean_cw"
    power_discharge_max: str = "power_discharge_max"
    power_discharge_min: str = "power_discharge_min"
    ir_start_charge: str = "ir_start_charge"
    ir_end_charge: str = "ir_end_charge"
    ir_start_discharge: str = "ir_start_discharge"
    ir_end_discharge: str = "ir_end_discharge"
    relaxation_potential_charge: str = "relaxation_potential_charge"
    relaxation_potential_discharge: str = "relaxation_potential_discharge"
    open_circuit_potential_charge: str = "open_circuit_potential_charge"
    open_circuit_potential_discharge: str = "open_circuit_potential_discharge"
    cv_share: str = "cv_share"
    cv_charge_capacity: str = "cv_charge_capacity"
    cv_charge_energy: str = "cv_charge_energy"
    cv_charge_time: str = "cv_charge_time"
    cc_charge_capacity: str = "cc_charge_capacity"
    cc_charge_energy: str = "cc_charge_energy"
    cc_charge_time: str = "cc_charge_time"
    # Per-cycle cell-temperature statistics, aggregated from the raw
    # ``aux_temperature_cell`` signal. Declared here (like the per-direction
    # current/potential/power stats above) ahead of engine support; the summary
    # engine does not populate them yet. ``_mean`` / ``_last`` map to the legacy
    # ``temperature_mean`` / ``temperature_last`` summary columns.
    temperature_cell_mean: str = "temperature_cell_mean"
    temperature_cell_max: str = "temperature_cell_max"
    temperature_cell_min: str = "temperature_cell_min"
    temperature_cell_last: str = "temperature_cell_last"
    # Derived/scaled columns produced by the standalone native summary path
    # (``add_scaled_summary_columns`` + the C-rate / IR helpers). These were
    # previously legacy-only "bridge extras" (see step-table-polars-migration.md,
    # Phase 3b); issue #21 brings them onto the native schema so the native path
    # is self-sufficient. ``ir_charge`` / ``ir_discharge`` are the behaviour-
    # preserving single-value IR targets (the four ``ir_start/end_*`` columns
    # above remain reserved for the richer future IR model).
    normalized_cycle_index: str = "normalized_cycle_index"
    charge_c_rate: str = "charge_c_rate"
    discharge_c_rate: str = "discharge_c_rate"
    ir_charge: str = "ir_charge"
    ir_discharge: str = "ir_discharge"

    @property
    def specific_columns(self) -> list:
        """Summary columns that get specific (per mass / area / volume) variants.

        Returns the capacity-like columns that ``generate_specific_summary_columns``
        scales into ``{col}_gravimetric`` / ``{col}_areal`` / ``{col}_absolute``
        variants. Mirrors the legacy ``HeadersSummary.specific_columns`` list using
        the native column names (the native schema has no ``shifted_*`` columns, so
        those legacy entries are dropped).
        """
        return [
            self.discharge_capacity,
            self.charge_capacity,
            self.test_cumulated_charge_capacity,
            self.test_cumulated_discharge_capacity,
            self.coulombic_difference,
            self.test_cumulated_coulombic_difference,
            self.discharge_capacity_loss,
            self.charge_capacity_loss,
            self.test_cumulated_discharge_capacity_loss,
            self.test_cumulated_charge_capacity_loss,
        ]


class StepCols(Cols):
    """Column-header definitions for the per-step summary table.

    Each attribute maps a logical quantity to the column name used in the
    per-step summary (per-step statistics such as mean/std/min/max/first/last/
    delta for time, current, potential, capacity, energy, power and internal
    resistance, plus the per-step C-rate estimate).
    """

    cycle_num: str = "cycle_num"
    step_num: str = "step_num"
    sub_step_num: str = "sub_step_num"
    # ``step_type`` values draw from the ``StepType`` vocabulary.
    step_type: str = "step_type"
    # ``sub_step_type`` is currently reserved and left unpopulated (the step
    # engine writes null). When used it is expected to draw from the same
    # ``StepType`` vocabulary; its exact semantics are still TBD.
    sub_step_type: str = "sub_step_type"
    mask: str = "mask"
    datapoint_num_first: str = "datapoint_num_first"
    datapoint_num_last: str = "datapoint_num_last"
    test_time_first: str = "test_time_first"
    test_time_last: str = "test_time_last"
    step_time_mean: str = "step_time_mean"
    step_time_std: str = "step_time_std"
    step_time_min: str = "step_time_min"
    step_time_max: str = "step_time_max"
    step_time_first: str = "step_time_first"
    step_time_last: str = "step_time_last"
    step_time_delta: str = "step_time_delta"
    current_mean: str = "current_mean"
    current_std: str = "current_std"
    current_min: str = "current_min"
    current_max: str = "current_max"
    current_first: str = "current_first"
    current_last: str = "current_last"
    current_delta: str = "current_delta"
    potential_mean: str = "potential_mean"
    potential_std: str = "potential_std"
    potential_min: str = "potential_min"
    potential_max: str = "potential_max"
    potential_first: str = "potential_first"
    potential_last: str = "potential_last"
    potential_delta: str = "potential_delta"
    charge_capacity_mean: str = "charge_capacity_mean"
    charge_capacity_std: str = "charge_capacity_std"
    charge_capacity_min: str = "charge_capacity_min"
    charge_capacity_max: str = "charge_capacity_max"
    charge_capacity_first: str = "charge_capacity_first"
    charge_capacity_last: str = "charge_capacity_last"
    charge_capacity_delta: str = "charge_capacity_delta"
    discharge_capacity_mean: str = "discharge_capacity_mean"
    discharge_capacity_std: str = "discharge_capacity_std"
    discharge_capacity_min: str = "discharge_capacity_min"
    discharge_capacity_max: str = "discharge_capacity_max"
    discharge_capacity_first: str = "discharge_capacity_first"
    discharge_capacity_last: str = "discharge_capacity_last"
    discharge_capacity_delta: str = "discharge_capacity_delta"
    power_mean: str = "power_mean"
    power_std: str = "power_std"
    power_min: str = "power_min"
    power_max: str = "power_max"
    power_first: str = "power_first"
    power_last: str = "power_last"
    power_delta: str = "power_delta"
    charge_energy_mean: str = "charge_energy_mean"
    charge_energy_std: str = "charge_energy_std"
    charge_energy_min: str = "charge_energy_min"
    charge_energy_max: str = "charge_energy_max"
    charge_energy_first: str = "charge_energy_first"
    charge_energy_last: str = "charge_energy_last"
    charge_energy_delta: str = "charge_energy_delta"
    discharge_energy_mean: str = "discharge_energy_mean"
    discharge_energy_std: str = "discharge_energy_std"
    discharge_energy_min: str = "discharge_energy_min"
    discharge_energy_max: str = "discharge_energy_max"
    discharge_energy_first: str = "discharge_energy_first"
    discharge_energy_last: str = "discharge_energy_last"
    discharge_energy_delta: str = "discharge_energy_delta"
    internal_resistance_mean: str = "internal_resistance_mean"
    internal_resistance_std: str = "internal_resistance_std"
    internal_resistance_min: str = "internal_resistance_min"
    internal_resistance_max: str = "internal_resistance_max"
    internal_resistance_first: str = "internal_resistance_first"
    internal_resistance_last: str = "internal_resistance_last"
    internal_resistance_delta: str = "internal_resistance_delta"
    # Per-step C-rate estimate (legacy ``rate_avr``).
    c_rate: str = "c_rate"


class RawCols(Cols):
    """Column-header definitions for the harmonized raw data table.

    Each attribute maps a logical quantity to the column name used in the
    harmonized raw format that cellpy-core consumes. The authoritative spec is
    ``docs/data_format_specifications/harmonized_raw.md``; the column order here
    mirrors that spec table.
    """

    # Follows docs/data_format_specifications/harmonized_raw.md (authoritative,
    # 2025-09-17). Column order mirrors the spec table.
    datapoint_num: str = "datapoint_num"
    source_datapoint_num: str = "source_datapoint_num"
    mask: str = "mask"
    epoch_time_utc: str = "epoch_time_utc"
    test_time: str = "test_time"
    step_time: str = "step_time"
    source_type: str = "source_type"
    source_uuid: str = "source_uuid"
    test_id: str = "test_id"
    step_num: str = "step_num"
    source_step_num: str = "source_step_num"
    step_type: str = "step_type"
    step_type_detail: str = "step_type_detail"
    step_mode: str = "step_mode"
    cycle_num: str = "cycle_num"
    cycle_type: str = "cycle_type"
    potential: str = "potential"
    current: str = "current"
    # Capacity / energy are cumulative per cycle, per direction (reset each cycle).
    # See docs/data_format_specifications/harmonized_raw.md ("Capacity convention").
    cumulative_charge_capacity: str = "cumulative_charge_capacity"
    cumulative_discharge_capacity: str = "cumulative_discharge_capacity"
    cumulative_charge_energy: str = "cumulative_charge_energy"
    cumulative_discharge_energy: str = "cumulative_discharge_energy"
    step_charge_power: str = "step_charge_power"
    step_discharge_power: str = "step_discharge_power"
    internal_resistance: str = "internal_resistance"
    # Auxiliary columns (aux_<quantity>_<name> scheme). Defaults below cover the
    # cell/chamber temperatures and cell pressure named in the spec.
    aux_temperature_cell: str = "aux_temperature_cell"
    aux_temperature_chamber: str = "aux_temperature_chamber"
    aux_pressure_cell: str = "aux_pressure_cell"


def default_schema() -> Schema:
    """Return a Schema using the native cellpy-core column definitions.

    Used as a standalone fallback when no schema is injected; the legacy bridge
    (OldCellpyCellCore) always injects its own legacy-named schema.
    """
    return Schema(raw=RawCols(), cycle=CycleCols(), step=StepCols())


def cols_check():
    import pandas as pd
    import polars as pl

    print(80 * "-")
    print("CHECKING CycleCols")
    print(f"CycleCols.__version__: {CycleCols.__version__}")
    print(80 * "-")

    test_data = {
        "cycle_num": [1, 2, 3],
        "step_num": [4, 5, 6],
        "charge_capacity": [7, 8, 9],
    }

    cycle_cols = CycleCols()
    df = pl.DataFrame(test_data)
    df_pandas = pd.DataFrame(test_data)

    print("pandas:")
    print(df_pandas)
    print(df_pandas.columns)
    print(df_pandas.dtypes)

    print("polars:")
    print(df)
    print(df.schema)

    print(80 * "-")
    print(cycle_cols)
    print(cycle_cols.cycle_num)
    print(cycle_cols.step_num)
    print(cycle_cols.charge_capacity)
    print(80 * "-")
    print(f"{cycle_cols.cycle_num=}")
    print(f"{cycle_cols.step_num=}")
    print(f"{cycle_cols.charge_capacity=}")
    print(80 * "-")
    print(f"{cycle_cols['cycle_num']=}")
    print(f"{cycle_cols['step_num']=}")
    print(f"{cycle_cols['charge_capacity']=}")
    print(80 * "-")

    print(80 * "=")
    print("using Cols for polars")
    print(80 * "=")
    print(df.select(pl.col(cycle_cols.cycle_num)))
    print(df.select(pl.col(cycle_cols.step_num)))
    print(df.select(pl.col(cycle_cols.charge_capacity)))
    print(80 * "-")
    print(df.select(pl.col(cycle_cols["cycle_num"])))
    print(df.select(pl.col(cycle_cols["step_num"])))
    print(df.select(pl.col(cycle_cols["charge_capacity"])))

    print(80 * "=")
    print("using Cols for pandas")
    print(80 * "=")
    print(df_pandas.loc[:, cycle_cols.cycle_num])
    print(df_pandas.loc[:, cycle_cols.step_num])
    print(df_pandas.loc[:, cycle_cols.charge_capacity])
    print(80 * "-")
    print(df_pandas.loc[:, cycle_cols["cycle_num"]])
    print(df_pandas.loc[:, cycle_cols["step_num"]])
    print(df_pandas.loc[:, cycle_cols["charge_capacity"]])


if __name__ == "__main__":
    cols_check()
