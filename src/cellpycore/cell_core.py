import datetime
import logging
import time

from typing import Callable, Iterable, Union, Sequence, Optional, List, TypeVar


# The CellpyCell (currently named CellpyCellCore) is the main class that the full cellpy package
# should interact with.
# The Data class can be accessed through the data property (setter and getter).


from cellpycore import config

from cellpycore.legacy import NoDataFound
from cellpycore.legacy import Meta, MockMetaTestDependent

DataFrame = TypeVar("DataFrame")

logger = logging.getLogger(__name__)


class Data:
    def __init__(self):
        self.meta_test_dependent: Meta = MockMetaTestDependent()
        self.raw: Optional[DataFrame] = None
        # The step table and the per-cycle summary produced by the engine.
        # (``cycle``/``step`` are kept as legacy aliases for backwards
        # compatibility; the engine reads/writes ``steps``/``summary``.)
        self.steps: Optional[DataFrame] = None
        self.summary: Optional[DataFrame] = None
        self.cycle: Optional[DataFrame] = None
        self.step: Optional[DataFrame] = None

    @property
    def has_steps(self) -> bool:
        """True if a step table has been computed."""
        return self.steps is not None

    @property
    def has_summary(self) -> bool:
        """True if a summary has been computed."""
        return self.summary is not None


class CellpyCellCore:  # Rename to CellpyCell when cellpy core is ready
    # TODO: move the data object to slim
    # TODO: copy div settings to slim

    def __init__(
        self,
        initialize: bool = False,
        debug: bool = False,
    ):
        """
        Args:
            initialize (bool): set to True if you want to initialize the cellpy object with an empty Data instance.
            debug (bool): set to True if you want to see debug messages.
        """

        self.debug = debug
        logger.debug("created CellpyCellCore instance")

        self._cell_name: Optional[str] = None
        self._cycle_mode: Optional[str] = None
        self._data: Optional[Data] = None

        self.cellpy_file_name: Optional[str] = None
        self.cellpy_object_created_at: datetime.datetime = datetime.datetime.now()
        self.forced_errors: int = 0

        # self.capacity_modifiers: List[str] = CAPACITY_MODIFIERS
        # self.list_of_step_types: List[str] = STEP_TYPES

        # - headers
        self.raw_cols: config.Cols = config.RawCols()
        self.cycle_cols: config.Cols = config.CycleCols()
        self.step_cols: config.Cols = config.StepCols()

        # Note! units is not used by cellpy core
        if initialize:
            self.initialize()

    def initialize(self):
        """Initialize the CellpyCell object with empty Data instance."""

        logger.debug("Initializing...")
        self._data = Data()

    @property
    def data(self) -> Data:
        """Returns the DataSet instance.

        Returns:
            DataSet instance.

        Raises:
            NoDataFound: If the CellpyCell does not have any data.
        """

        if not self._data:
            raise NoDataFound("The CellpyCell does not have any data.")
        else:
            return self._data

    @data.setter
    def data(self, new_data: Data):
        """Sets the Data instance"""

        self._data = new_data

    @property
    def cycle_mode(self) -> str:
        # TODO: v2.0 edit this from scalar to list
        try:
            data = self.data
            m = data.meta_test_dependent.cycle_mode
            # cellpy saves this as a list (ready for v2.0),
            # but we want to return a scalar for the moment
            # Temporary fix to make sure that cycle_mode is a scalar:
            if isinstance(m, (tuple, list)):
                return m[0]
            return m
        except NoDataFound:
            return self._cycle_mode

    @cycle_mode.setter
    def cycle_mode(self, cycle_mode: str):
        if isinstance(cycle_mode, (tuple, list)):
            cycle_mode = [cycle_mode.lower() for cycle_mode in cycle_mode]
        else:
            cycle_mode = cycle_mode.lower()
        # TODO: v2.0 edit this from scalar to list
        logger.debug(f"-> cycle_mode: {cycle_mode}")
        try:
            data = self.data
            data.meta_test_dependent.cycle_mode = cycle_mode
            self._cycle_mode = cycle_mode
        except NoDataFound:
            self._cycle_mode = cycle_mode

    @property
    def schema(self) -> config.Schema:
        """The column-header schema for this cell.

        Bundles the raw / cycle (summary) / step header objects so the summary
        and step engine can read their column names from an injected object
        instead of module-level globals. Built on access so subclass overrides of
        ``raw_cols`` / ``cycle_cols`` / ``step_cols`` (e.g. the legacy bridge) are
        always reflected.
        """
        return config.Schema(
            raw=self.raw_cols,
            cycle=self.cycle_cols,
            step=self.step_cols,
        )

    def make_core_summary(
        self,
        data: Data,
        selector: Optional[Callable] = None,
        find_ir: bool = True,
        find_end_voltage: bool = False,
        select_columns: bool = True,
        final_data_points: Optional[Iterable[int]] = None,
        current_conversion_factor: float = 1.0,
    ) -> Data:
        """Make the core summary.

        Args:
            data: The data to make the summary from.
            selector: The selector to use.
            find_ir: Whether to find the IR.
            find_end_voltage: Whether to find the end voltage.
            select_columns: Whether to select only the minimum columns that are needed.
            final_data_points: The final data point for each cycle to use for the selector.
            current_conversion_factor: Precomputed factor that converts the raw
                current unit to the desired output current unit for the C-rate
                columns (by value; default 1.0 = no conversion).

        Returns:
            Data object with the summary.
        """

        from cellpycore import summarizers

        # The native summary engine is polars-native on the native schema and
        # produces the clean ``CycleCols`` subset. The legacy-only summary
        # columns (IR, C-rates, RIC, shifted/normalized capacities, …) are added
        # only on the legacy bridge (``OldCellpyCellCore.make_core_summary``).
        time_00 = time.time()
        logger.debug("start making summary (native polars engine)")
        data = summarizers.make_summary(
            data, self.schema, final_data_points=final_data_points
        )
        logger.debug(f"(dt: {(time.time() - time_00):4.2f}s)")
        return data

    def add_scaled_summary_columns(
        self,
        data: Data,
        nom_cap_abs: float,
        normalization_cycles: Union[Sequence, int, None],
        step_txt: Optional[str] = None,
        specifics: Optional[List[str]] = None,
        specific_converters: Optional[dict] = None,
    ) -> Data:
        """Add specific summary columns to the summary.

        Args:
            data: The data to add the specific summary columns to.
            nom_cap_abs: The nominal capacity of the cell.
            normalization_cycles: The number of cycles to normalize the data by.
            step_txt: The step text to use (charge or discharge capacity, will pick 'first' based on cycle mode if not provided)
            specifics: The specifics to add.
            specific_converters: Mapping of ``mode -> conversion factor`` supplied
                by value by the caller (so this method needs no unit handling). If
                not provided, the factors are computed lazily via the units helper
                using ``self.cellpy_units`` as a fallback (legacy / standalone).

        Returns:
            The data with the specific summary columns added.
        """
        from cellpycore import summarizers

        schema = self.schema

        if specifics is None:
            specifics = ["gravimetric", "areal", "absolute"]

        if step_txt is None:
            if self.cycle_mode == "anode":
                step_txt = schema.cycle.discharge_capacity
            else:
                step_txt = schema.cycle.charge_capacity

        data = summarizers.equivalent_cycles_to_summary(
            data, schema, nom_cap_abs, normalization_cycles, step_txt
        )

        # Note: the C-rates are added by make_core_summary (using the step-table
        # rates, independent of nom_cap, matching legacy cellpy). Adding them again
        # here would duplicate the charge_c_rate/discharge_c_rate columns (pandas
        # merge would suffix them _x/_y), so it is intentionally not repeated.

        specific_columns = schema.cycle.specific_columns
        for mode in specifics:
            converter = self._resolve_specific_converter(
                data, mode, specific_converters
            )
            data = summarizers.generate_specific_summary_columns(
                data, mode, specific_columns, converter
            )

        return data

    def _resolve_specific_converter(
        self, data: Data, mode: str, specific_converters: Optional[dict]
    ) -> float:
        """Resolve the specific-capacity conversion factor for a mode.

        Prefers the caller-supplied factor (by value). Falls back to computing it
        via the units helper using ``self.cellpy_units`` (legacy / standalone use);
        this is the only place the summary path may touch pint, and only when the
        caller did not supply the factor.
        """
        if specific_converters is not None and mode in specific_converters:
            return specific_converters[mode]

        from cellpycore import units

        return units.get_converter_to_specific(
            data=data, mode=mode, to_units=getattr(self, "cellpy_units", None)
        )

    def make_core_step_table(
        self,
        data: Data,
        raw_limits: Optional[dict] = None,
        step_specifications=None,
        short: bool = False,
        override_step_types: Optional[dict] = None,
        override_raw_limits: Optional[dict] = None,
        usteps: bool = False,
        add_c_rate: bool = True,
        nom_cap: Optional[float] = None,
        skip_steps: Optional[Sequence] = None,
        sort_rows: bool = True,
        from_data_point: Optional[int] = None,
    ) -> Union[Data, "DataFrame"]:
        """Make the core step table.

        Delegates to ``summarizers.make_step_table`` using this cell's schema.
        The instrument resolution limits (``raw_limits``) and the absolute
        nominal capacity (``nom_cap``, for the C-rate) are supplied by the caller.

        Args:
            data: The data to make the step table from.
            raw_limits: The instrument resolution limits. If None, the summarizer
                default (DEFAULT_RAW_LIMITS) is used.
            step_specifications: Optional explicit step specifications.
            short: Whether step specifications are in short format.
            override_step_types: Override the detected step types.
            override_raw_limits: Override individual raw limits.
            usteps: Whether to investigate all (sub-)steps within a cycle.
            add_c_rate: Whether to include the per-step C-rate (rate_avr).
            nom_cap: Absolute nominal capacity used for the C-rate (default 1.0).
            skip_steps: Step numbers to skip.
            sort_rows: Whether to sort the rows after processing.
            from_data_point: First data point to use (returns a DataFrame when set).

        Returns:
            Data object with the step table, or a DataFrame when ``from_data_point``
            is given.
        """
        from cellpycore import summarizers

        kwargs = dict(
            schema=self.schema,
            step_specifications=step_specifications,
            short=short,
            override_step_types=override_step_types,
            override_raw_limits=override_raw_limits,
            usteps=usteps,
            add_c_rate=add_c_rate,
            nom_cap=nom_cap,
            skip_steps=skip_steps,
            sort_rows=sort_rows,
            from_data_point=from_data_point,
        )
        if raw_limits is not None:
            kwargs["raw_limits"] = raw_limits

        return summarizers.make_step_table(data, **kwargs)


class OldCellpyCellCore(CellpyCellCore):
    """Legacy CellpyCellCore class to make it easier to migrate to cellpy core."""

    def __init__(self, *args, **kwargs):
        from cellpycore.units import get_cellpy_units, get_default_output_units
        from cellpycore.legacy import HeadersNormal, HeadersSummary, HeadersStepTable

        super().__init__(*args, **kwargs)
        self.cellpy_units = get_cellpy_units()
        self.output_units = get_default_output_units()
        self.raw_cols = HeadersNormal()
        self.cycle_cols = HeadersSummary()
        self.step_cols = HeadersStepTable()

    # ---- legacy <-> native bridge for the polars step engine ----------------
    # cellpy hands us pandas frames with legacy (``HeadersNormal``) column names.
    # The step engine is polars-native and operates on the native schema, so we
    # translate at this seam: legacy pandas raw -> native polars raw -> engine ->
    # native polars steps -> legacy pandas steps. The output frame reproduces the
    # legacy ``HeadersStepTable`` layout byte-for-byte (the golden oracle).

    _NATIVE_STAT_TO_LEGACY = {
        "mean": "avr",
        "std": "std",
        "min": "min",
        "max": "max",
        "first": "first",
        "last": "last",
        "delta": "delta",
    }

    def _legacy_to_native_raw_rename(self, columns) -> dict:
        leg, nat = self.raw_cols, config.RawCols()
        mapping = {
            leg.data_point_txt: nat.datapoint_num,
            leg.test_time_txt: nat.test_time,
            leg.step_time_txt: nat.step_time,
            leg.cycle_index_txt: nat.cycle_num,
            leg.step_index_txt: nat.step_num,
            leg.current_txt: nat.current,
            leg.voltage_txt: nat.potential,
            leg.charge_capacity_txt: nat.cumulative_charge_capacity,
            leg.discharge_capacity_txt: nat.cumulative_discharge_capacity,
            leg.internal_resistance_txt: nat.internal_resistance,
        }
        return {k: v for k, v in mapping.items() if k in columns}

    def _native_to_legacy_step_rename(self) -> dict:
        leg, nat = self.step_cols, config.StepCols()
        base_map = {
            "datapoint_num": leg.point,
            "test_time": leg.test_time,
            "step_time": leg.step_time,
            "current": leg.current,
            "potential": leg.voltage,
            "charge_capacity": leg.charge,
            "discharge_capacity": leg.discharge,
            "internal_resistance": leg.internal_resistance,
        }
        rename = {}
        for nbase, lbase in base_map.items():
            for nstat, lstat in self._NATIVE_STAT_TO_LEGACY.items():
                rename[f"{nbase}_{nstat}"] = f"{lbase}_{lstat}"
        rename[nat.cycle_num] = leg.cycle
        rename[nat.step_num] = leg.step
        rename[nat.sub_step_num] = leg.sub_step
        rename[nat.step_type] = leg.type
        rename[nat.sub_step_type] = leg.sub_type
        rename[nat.c_rate] = leg.rate_avr
        return rename

    def _legacy_step_column_order(self) -> list:
        leg = self.step_cols
        order = [leg.cycle, leg.step, leg.sub_step]
        bases = [
            leg.point, leg.test_time, leg.step_time, leg.current, leg.voltage,
            leg.charge, leg.discharge, leg.internal_resistance,
        ]
        for base in bases:
            order += [f"{base}_{stat}" for stat in self._NATIVE_STAT_TO_LEGACY.values()]
        order += [leg.rate_avr, leg.type, leg.sub_type, leg.info]
        return order

    def _native_steps_to_legacy(self, native_steps, sort_rows: bool):
        leg = self.step_cols
        pdf = native_steps.to_pandas()
        pdf = pdf.rename(columns=self._native_to_legacy_step_rename())

        order = self._legacy_step_column_order()
        if sort_rows:
            # sort + reset_index reproduces the legacy 'index' column (the
            # pre-sort, group-key-ordered position).
            pdf = pdf.sort_values(by=f"{leg.test_time}_first").reset_index()
            order = ["index"] + order

        order = [c for c in order if c in pdf.columns]
        return pdf[order]

    def make_core_step_table(
        self,
        data: Data,
        raw_limits: Optional[dict] = None,
        step_specifications=None,
        short: bool = False,
        override_step_types: Optional[dict] = None,
        override_raw_limits: Optional[dict] = None,
        usteps: bool = False,
        add_c_rate: bool = True,
        nom_cap: Optional[float] = None,
        skip_steps: Optional[Sequence] = None,
        sort_rows: bool = True,
        from_data_point: Optional[int] = None,
    ) -> Union[Data, "DataFrame"]:
        """Build the step table via the polars engine, in/out in legacy form.

        See the bridge note above. Returns a pandas frame with legacy
        ``HeadersStepTable`` columns (or that frame directly when
        ``from_data_point`` is given).
        """
        import polars as pl

        from cellpycore import summarizers
        from cellpycore.config import default_schema

        native_raw = pl.from_pandas(
            data.raw.rename(columns=self._legacy_to_native_raw_rename(data.raw.columns))
        )
        tmp = Data()
        tmp.raw = native_raw

        kwargs = dict(
            schema=default_schema(),
            step_specifications=step_specifications,
            short=short,
            override_step_types=override_step_types,
            override_raw_limits=override_raw_limits,
            usteps=usteps,
            add_c_rate=add_c_rate,
            nom_cap=nom_cap,
            skip_steps=skip_steps,
            sort_rows=False,  # the bridge handles legacy sorting + 'index' column
            from_data_point=from_data_point,
        )
        if raw_limits is not None:
            kwargs["raw_limits"] = raw_limits

        result = summarizers.make_step_table(tmp, **kwargs)
        native_steps = result if from_data_point is not None else result.steps

        legacy_steps = self._native_steps_to_legacy(native_steps, sort_rows=sort_rows)
        if from_data_point is not None:
            return legacy_steps
        data.steps = legacy_steps
        return data

    # ---- legacy <-> native bridge for the polars summary engine -------------
    # The native engine (summarizers.make_summary) produces the clean native
    # CycleCols subset. cellpy expects the full legacy HeadersSummary frame, so
    # this bridge renames native->legacy and computes the legacy-only "extras"
    # (cumulated CE, shifted capacities, RIC, IR, C-rates) that the curated
    # native cycle schema deliberately omits. Those extras reuse the (legacy)
    # pandas helpers, which is appropriate: they are legacy cruft.

    def _legacy_to_native_step_rename(self) -> dict:
        return {v: k for k, v in self._native_to_legacy_step_rename().items()}

    def _native_to_legacy_summary_rename(self) -> dict:
        leg, nat = self.cycle_cols, config.CycleCols()
        return {
            nat.cycle_num: leg.cycle_index,
            nat.datapoint_num_last: leg.data_point,
            nat.last_test_time: leg.test_time,
            nat.charge_capacity: leg.charge_capacity,
            nat.discharge_capacity: leg.discharge_capacity,
            nat.coulombic_efficiency: leg.coulombic_efficiency,
            nat.coulombic_difference: leg.coulombic_difference,
            nat.charge_capacity_loss: leg.charge_capacity_loss,
            nat.discharge_capacity_loss: leg.discharge_capacity_loss,
            nat.test_cumulated_charge_capacity: leg.cumulated_charge_capacity,
            nat.test_cumulated_discharge_capacity: leg.cumulated_discharge_capacity,
            nat.test_cumulated_coulombic_difference: leg.cumulated_coulombic_difference,
            nat.test_cumulated_charge_capacity_loss: leg.cumulated_charge_capacity_loss,
            nat.test_cumulated_discharge_capacity_loss: leg.cumulated_discharge_capacity_loss,
            nat.potential_end_charge: leg.end_voltage_charge,
            nat.potential_end_discharge: leg.end_voltage_discharge,
        }

    def _legacy_summary_column_order(self, find_end_voltage: bool) -> list:
        leg = self.cycle_cols
        order = [
            leg.ir_charge, leg.ir_discharge, leg.data_point, leg.test_time,
            leg.datetime, leg.cycle_index, leg.charge_capacity,
            leg.discharge_capacity, leg.coulombic_efficiency,
            leg.cumulated_coulombic_efficiency, leg.cumulated_charge_capacity,
            leg.cumulated_discharge_capacity, leg.discharge_capacity_loss,
            leg.charge_capacity_loss, leg.coulombic_difference,
            leg.cumulated_coulombic_difference, leg.cumulated_discharge_capacity_loss,
            leg.cumulated_charge_capacity_loss, leg.shifted_charge_capacity,
            leg.shifted_discharge_capacity, leg.cumulated_ric, leg.cumulated_ric_sei,
            leg.cumulated_ric_disconnect,
        ]
        if find_end_voltage:
            order += [leg.end_voltage_discharge, leg.end_voltage_charge]
        order += [leg.charge_c_rate, leg.discharge_c_rate]
        return order

    def _add_legacy_summary_extras(
        self, data: Data, find_ir: bool, current_conversion_factor: float
    ) -> None:
        from cellpycore import summarizers

        leg = self.cycle_cols
        s = data.summary
        cc = s[leg.charge_capacity]
        dc = s[leg.discharge_capacity]
        s[leg.cumulated_coulombic_efficiency] = s[leg.coulombic_efficiency].cumsum()
        s[leg.shifted_charge_capacity] = (cc - dc).cumsum()
        s[leg.shifted_discharge_capacity] = s[leg.shifted_charge_capacity] + cc
        s[leg.cumulated_ric] = ((cc.shift(1) - dc) / dc.shift(1)).cumsum()
        s[leg.cumulated_ric_sei] = ((cc - dc.shift(1)) / dc.shift(1)).cumsum()
        s[leg.cumulated_ric_disconnect] = ((dc.shift(1) - dc) / dc.shift(1)).cumsum()
        data.summary = s

        legacy_schema = config.Schema(self.raw_cols, self.cycle_cols, self.step_cols)
        if find_ir and (self.raw_cols.internal_resistance_txt in data.raw.columns):
            data = summarizers.ir_to_summary(data, legacy_schema)
        data = summarizers.c_rates_to_summary(
            data, legacy_schema, current_conversion_factor=current_conversion_factor
        )

    def make_core_summary(
        self,
        data: Data,
        selector: Optional[Callable] = None,
        find_ir: bool = True,
        find_end_voltage: bool = False,
        select_columns: bool = True,
        final_data_points: Optional[Iterable[int]] = None,
        current_conversion_factor: float = 1.0,
    ) -> Data:
        """Build the per-cycle summary via the polars engine, in/out in legacy form.

        Runs the native ``make_summary`` engine, renames native->legacy, then adds
        the legacy-only extras to reproduce the legacy ``HeadersSummary`` frame.
        """
        import polars as pl

        from cellpycore import summarizers

        native_raw = pl.from_pandas(
            data.raw.rename(columns=self._legacy_to_native_raw_rename(data.raw.columns))
        )
        native_steps = pl.from_pandas(
            data.steps.rename(columns=self._legacy_to_native_step_rename())
        )
        nd = Data()
        nd.raw = native_raw
        nd.steps = native_steps
        summarizers.make_summary(
            nd, config.default_schema(), final_data_points=final_data_points
        )

        leg = self.cycle_cols
        summary = nd.summary.to_pandas().rename(
            columns=self._native_to_legacy_summary_rename()
        )

        # date_time passthrough (native raw carries epoch time, not date_time)
        dp_txt = self.raw_cols.data_point_txt
        dt_txt = self.raw_cols.datetime_txt
        if dt_txt in data.raw.columns:
            dt_map = data.raw[[dp_txt, dt_txt]].drop_duplicates(subset=[dp_txt])
            dt_map = dt_map.rename(columns={dp_txt: leg.data_point})
            summary = summary.merge(dt_map, on=leg.data_point, how="left")

        summary.index = list(range(len(summary)))
        data.summary = summary

        self._add_legacy_summary_extras(
            data, find_ir=find_ir, current_conversion_factor=current_conversion_factor
        )

        order = self._legacy_summary_column_order(find_end_voltage)
        order = [c for c in order if c in data.summary.columns]
        data.summary = data.summary[order]
        return data
