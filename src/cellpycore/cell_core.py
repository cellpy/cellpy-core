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
        self.cycle: Optional[DataFrame] = None
        self.step: Optional[DataFrame] = None


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

        from cellpycore import selectors, summarizers

        schema = self.schema

        time_00 = time.time()
        logger.debug("start making summary")

        if selector is None:
            selector = selectors.create_selector(
                data, schema, final_data_points=final_data_points
            )
        summary = selector()
        column_names = summary.columns
        # TODO @jepe: use pandas.DataFrame properties instead (.len, .reset_index), but maybe first
        #  figure out if this is really needed and why it was implemented in the first place.
        summary_length = len(summary[column_names[0]])
        summary.index = list(range(summary_length))

        if select_columns:
            logger.debug("keeping only selected set of columns")
            columns_to_keep = [
                schema.raw.charge_capacity_txt,
                schema.raw.cycle_index_txt,
                schema.raw.data_point_txt,
                schema.raw.datetime_txt,
                schema.raw.discharge_capacity_txt,
                schema.raw.test_time_txt,
            ]
            for cn in column_names:
                if not columns_to_keep.count(cn):
                    try:
                        summary.pop(cn)
                    except KeyError:
                        logger.debug(f"could not pop {cn}")

        data.summary = summary

        if self.cycle_mode == config.CyclingMode.ANODE:
            logger.info(
                "Assuming cycling in anode half-data (discharge before charge) mode"
            )
            _first_step_txt = schema.cycle.discharge_capacity
            _second_step_txt = schema.cycle.charge_capacity
        else:
            logger.info("Assuming cycling in full-data / cathode mode")
            _first_step_txt = schema.cycle.charge_capacity
            _second_step_txt = schema.cycle.discharge_capacity

        # ---------------- absolute -------------------------------

        data = summarizers.generate_absolute_summary_columns(
            data, schema, _first_step_txt, _second_step_txt
        )

        # TODO @jepe: refactor this to method:
        if find_end_voltage:
            data = summarizers.end_voltage_to_summary(data, schema)

        if find_ir and (schema.raw.internal_resistance_txt in data.raw.columns):
            data = summarizers.ir_to_summary(data, schema)

        data = summarizers.c_rates_to_summary(
            data, schema, current_conversion_factor=current_conversion_factor
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
