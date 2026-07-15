import datetime
import logging
import time
from typing import Callable, Iterable, List, Optional, Sequence, TypeVar, Union

from cellpycore import config
from cellpycore.exceptions import NoDataFound
from cellpycore.legacy import Meta, MockMetaTestDependent, mapping
from cellpycore.metadata.models import CellMeta

DataFrame = TypeVar("DataFrame")

logger = logging.getLogger(__name__)


# cycle_mode spellings that select the inverted (anode half-cell) convention:
# cellpy's legacy ``"anode"``, this package's ``TestMode`` value ``"inverted"``,
# and batbase's short code ``"i"`` (see ``config.TestMode`` docstring).
_INVERTED_CYCLE_MODES = frozenset({"anode", "inverted", "i"})
# Recognized spellings that select the NORMAL convention. Anything outside either
# set (and not ``None``/empty) is unknown -> NORMAL *with a warning*.
_NORMAL_CYCLE_MODES = frozenset(
    {"normal", "n", "cathode", "full_cell", "fullcell", "full cell", "standard"}
)


def _cycle_mode_to_test_mode(cycle_mode: Optional[str]) -> config.TestMode:
    """Map a legacy ``cycle_mode`` string to a :class:`config.TestMode`.

    The inverted (anode half-cell) convention is selected by any of ``"anode"``
    (cellpy), ``"inverted"`` (this package's ``TestMode`` value) or ``"i"``
    (batbase short code), matched case-insensitively and whitespace-tolerantly.
    ``None`` and the recognized normal-convention spellings map to
    ``TestMode.NORMAL``.

    An *unrecognized* non-empty value also maps to ``NORMAL`` but logs a warning,
    so a mistyped or unmapped mode fails loudly instead of silently flipping the
    ``coulombic_efficiency`` / ``coulombic_difference`` sign conventions.

    Args:
        cycle_mode: Legacy mode string, or ``None``.

    Returns:
        The corresponding ``TestMode`` for summary sign conventions.
    """
    if cycle_mode is None:
        return config.TestMode.NORMAL
    key = cycle_mode.strip().lower()
    if key in _INVERTED_CYCLE_MODES:
        return config.TestMode.INVERTED
    if key == "" or key in _NORMAL_CYCLE_MODES:
        return config.TestMode.NORMAL
    logger.warning(
        "Unrecognized cycle_mode %r; defaulting to NORMAL convention. Use "
        "'anode'/'inverted' for anode half-cells, or one of "
        "'normal'/'cathode'/'full_cell'/'standard' for the ordinary case.",
        cycle_mode,
    )
    return config.TestMode.NORMAL


def validate_raw_frame(raw, raw_cols: Optional[config.Cols] = None) -> None:
    """Validate a native-schema raw frame against ``config.RawCols``.

    Checks that ``raw`` is a polars ``DataFrame`` carrying the load-bearing
    columns the step/summary engine needs, with sane dtypes. All problems are
    collected and reported in a single error so the caller sees the full
    picture at once instead of a deep polars stack trace later.

    Optional columns (``test_id``, ``internal_resistance``, ``ref_potential``,
    ``step_time``, the ``source_*`` and ``aux_*`` columns, …) are allowed
    absent and are not dtype-checked.

    Args:
        raw: The candidate raw frame (must be a ``polars.DataFrame``).
        raw_cols: The raw column-header schema to validate against. Defaults
            to the native ``config.RawCols`` when not provided.

    Raises:
        TypeError: If ``raw`` is not a ``polars.DataFrame``.
        ValueError: If required columns are missing or load-bearing columns
            have the wrong dtype. The message lists every problem found.
    """
    import polars as pl

    if not isinstance(raw, pl.DataFrame):
        raise TypeError(
            "raw must be a polars.DataFrame in the native cellpy-core schema "
            f"(got {type(raw).__name__}); pandas frames with legacy headers "
            "belong on the legacy bridge (OldCellpyCellCore)."
        )

    if raw_cols is None:
        raw_cols = config.RawCols()

    integer_cols = [raw_cols.datapoint_num, raw_cols.cycle_num, raw_cols.step_num]
    numeric_cols = [
        raw_cols.test_time,
        raw_cols.current,
        raw_cols.potential,
        raw_cols.cumulative_charge_capacity,
        raw_cols.cumulative_discharge_capacity,
    ]
    required = integer_cols + [raw_cols.epoch_time_utc] + numeric_cols

    problems = []

    missing = [col for col in required if col not in raw.columns]
    if missing:
        problems.append(f"missing required column(s): {', '.join(missing)}")

    schema = raw.schema
    epoch = raw_cols.epoch_time_utc
    if epoch not in missing and schema[epoch] != pl.Int64:
        problems.append(
            f"column '{epoch}' has dtype {schema[epoch]} but must be Int64 "
            "(int64 nanoseconds since the Unix epoch, UTC — the STEP-11 "
            "timestamp contract; see cellpycore.timestamps)"
        )
    for col in integer_cols:
        if col not in missing and not schema[col].is_integer():
            problems.append(
                f"column '{col}' has dtype {schema[col]} but must be an integer dtype"
            )
    for col in numeric_cols:
        if col not in missing and not schema[col].is_numeric():
            problems.append(
                f"column '{col}' has dtype {schema[col]} but must be numeric"
            )

    if problems:
        raise ValueError(
            "raw frame does not match the native cellpy-core raw schema "
            "(config.RawCols):\n- " + "\n- ".join(problems)
        )


def cast_raw_frame(raw, raw_cols: Optional[config.RawCols] = None):
    """Cast a raw frame's columns to the native ``RawCols`` dtypes.

    Convenience for consumers converting foreign raw data (e.g. legacy pandas
    frames turned into polars) to the harmonized raw format: every column
    present in ``raw`` that appears in ``raw_cols.dtype_map()`` is cast to its
    authoritative dtype. Columns missing from the frame (optional columns) are
    skipped, and extra columns (e.g. custom ``aux_*`` columns) pass through
    untouched.

    Casts are strict — a lossy or impossible cast raises instead of silently
    coercing. Typical use is casting before the validating front door::

        data = Data.from_raw_frame(cast_raw_frame(df))

    Args:
        raw: The raw frame to cast (must be a ``polars.DataFrame``).
        raw_cols: The raw column-header schema providing ``dtype_map()``.
            Defaults to the native ``config.RawCols``.

    Returns:
        A new ``polars.DataFrame`` with the covered columns cast.

    Raises:
        TypeError: If ``raw`` is not a ``polars.DataFrame``.
        polars.exceptions.InvalidOperationError: If a cast fails (e.g. a
            non-numeric string in an integer column).
    """
    import polars as pl

    if not isinstance(raw, pl.DataFrame):
        raise TypeError(
            "raw must be a polars.DataFrame in the native cellpy-core schema "
            f"(got {type(raw).__name__}); pandas frames with legacy headers "
            "belong on the legacy bridge (OldCellpyCellCore)."
        )

    if raw_cols is None:
        raw_cols = config.RawCols()

    casts = [
        pl.col(name).cast(dtype)
        for name, dtype in raw_cols.dtype_map().items()
        if name in raw.columns
    ]
    return raw.with_columns(casts) if casts else raw


class Data:
    def __init__(self):
        self.meta_test_dependent: Meta = MockMetaTestDependent()
        self.raw: Optional[DataFrame] = None
        # The step table and the per-cycle summary produced by the engine.
        self.steps: Optional[DataFrame] = None
        self.summary: Optional[DataFrame] = None

    @classmethod
    def from_raw_frame(
        cls,
        raw,
        validate: bool = True,
        raw_cols: Optional[config.Cols] = None,
    ) -> "Data":
        """Create a ``Data`` object from a native-schema raw frame.

        The validating front door for slim consumers that build a polars
        frame in the native ``config.RawCols`` schema themselves and want
        step/cycle summaries straight from cellpy-core.

        Args:
            raw: A ``polars.DataFrame`` in the native raw schema.
            validate: Whether to check the frame against the schema via
                ``validate_raw_frame`` before wrapping it. Set to ``False``
                to skip all checks.
            raw_cols: The raw column-header schema to validate against.
                Defaults to the native ``config.RawCols``.

        Returns:
            A fresh ``Data`` with ``raw`` attached (and the usual
            ``MockMetaTestDependent`` metadata placeholder).

        Raises:
            TypeError: If ``raw`` is not a ``polars.DataFrame`` (when validating).
            ValueError: If the frame does not match the schema (when validating).
        """
        if validate:
            validate_raw_frame(raw, raw_cols)
        data = cls()
        data.raw = raw
        return data

    @property
    def has_steps(self) -> bool:
        """True if a step table has been computed."""
        return self.steps is not None

    @property
    def has_summary(self) -> bool:
        """True if a summary has been computed."""
        return self.summary is not None


class CellpyCellCore:
    """Native orchestration class for the cellpy-core summarization engine.

    Primary entry point for the full cellpy package and for slim standalone
    consumers. Attach a native-schema polars raw frame to a ``Data`` object,
    then run the step-table and summary pipeline without the legacy pandas /
    ``Headers*`` bridge (``OldCellpyCellCore``).

    The cell holds the column-header schema (``raw_cols``, ``cycle_cols``,
    ``step_cols``), exposes ``data`` and ``cycle_mode``, and delegates
    computation to ``summarizers`` through ``make_core_step_table``,
    ``make_core_summary``, and ``add_scaled_summary_columns``. Subclass to
    add application-specific helpers (cached views, loaders, etc.) while
    reusing the engine wiring.

    Attributes:
        raw_cols: Raw-frame column names (default ``config.RawCols``).
        cycle_cols: Per-cycle summary column names (default ``config.CycleCols``).
        step_cols: Step-table column names (default ``config.StepCols``).
        data: The attached ``Data`` instance (raises ``NoDataFound`` when unset).
        cycle_mode: Charge/discharge convention (e.g. ``"anode"`` for  anodehalf-cells).
            When ``data`` is attached, read/write goes through
            ``data.meta_test_dependent``; otherwise the value is kept on the cell.
        schema: Bundled ``config.Schema`` built from the three ``*_cols`` objects.

    Note:
        Processing order matters: run ``make_core_step_table`` before
        ``make_core_summary`` (the summary engine reads ``data.steps``).
        ``cycle_mode`` controls coulombic-efficiency direction and the default
        capacity column in ``add_scaled_summary_columns``. Unset ``cycle_mode``
        maps to normal convention; set ``"anode"`` explicitly for half-cells.

    Example:
        Basic pipeline::

            from cellpycore import CellpyCellCore, Data

            cell = CellpyCellCore()
            cell.data = Data.from_raw_frame(raw_polars_frame)
            cell.cycle_mode = "anode"  # anode half-cell; omit for normal convention

            data = cell.make_core_step_table(cell.data, nom_cap_abs=1.0)
            data = cell.make_core_summary(data)
            data = cell.add_scaled_summary_columns(
                data,
                nom_cap_abs=1.0,
                normalization_cycles=None,
                specific_conversion_factors={"gravimetric": f_g, "areal": f_a},
            )

        Subclassing for custom helpers::

            from functools import cached_property

            from cellpycore import CellpyCellCore

            class MyCell(CellpyCellCore):
                @cached_property
                def tests(self):
                    return build_tests_summary(self.data)

            # Note: build_tests_summary is a custom function that builds a summary frame for the tests.
            # It is currently not part of cellpy core, but is on the roadmap to be added.

    """

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
    def cycle_mode(self) -> Optional[str]:
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
        find_ir: bool = True,
        final_data_points: Optional[Iterable[int]] = None,
        current_conversion_factor: float = 1.0,
        ir_extractor: Optional[Callable] = None,
        exclude_step_types: Optional[Iterable[str]] = None,
    ) -> Data:
        """Make the core summary.

        Note:
            The native engine always emits the clean ``CycleCols`` subset
            including the end potentials; the legacy-only ``find_end_voltage``
            / ``select_columns`` knobs live on the bridge
            (``OldCellpyCellCore.make_core_summary``).

        Args:
            data: The data to make the summary from.
            find_ir: Whether to find the IR.
            final_data_points: The final data point for each cycle to use for the selector.
            current_conversion_factor: Precomputed factor that converts the raw
                current unit to the desired output current unit for the C-rate
                columns (by value; default 1.0 = no conversion).
            ir_extractor: Optional ``SummaryExtractor`` controlling how the per-cycle
                internal-resistance columns are derived. Defaults to
                ``extractors.LastIRExtractor`` when ``None``.
            exclude_step_types: Optional step-type prefixes to exclude from the
                summary (e.g. ``["cv_"]``); forwarded to
                ``summarizers.make_summary`` (issue #54).

        Returns:
            Data object with the summary.
        """

        from cellpycore import summarizers

        # The native summary engine is polars-native on the native schema and
        # produces the clean ``CycleCols`` subset plus C-rate / IR columns. The
        # remaining legacy-only cruft (cumulated CE, shifted / RIC capacities) is
        # added only on the legacy bridge (``OldCellpyCellCore.make_core_summary``).
        time_00 = time.time()
        logger.debug("start making summary (native polars engine)")
        test_mode = _cycle_mode_to_test_mode(self.cycle_mode)
        data = summarizers.make_summary(
            data,
            self.schema,
            final_data_points=final_data_points,
            test_mode=test_mode,
            exclude_step_types=exclude_step_types,
        )
        if find_ir and (self.schema.raw.internal_resistance in data.raw.columns):
            data = summarizers.ir_to_summary(
                data, self.schema, ir_extractor=ir_extractor
            )
        data = summarizers.c_rates_to_summary(
            data, self.schema, current_conversion_factor=current_conversion_factor
        )
        logger.debug(f"(dt: {(time.time() - time_00):4.2f}s)")
        return data

    def merge_core_data(
        self,
        left: Data,
        right: Data,
        *,
        renumber_cycles: bool = True,
        allow_duplicate_test_id: bool = False,
    ) -> Data:
        """Merge two ``Data`` objects via ``merge_data`` using this cell's schema.

        Args:
            left: First dataset.
            right: Second dataset, appended after ``left``.
            renumber_cycles: Offset right-side cycle numbers and carry cumulative
                summary values forward when True (default).
            allow_duplicate_test_id: Reassign colliding right-side ``test_id``
                values when True.

        Returns:
            A new merged ``Data`` object. Inputs are not modified.
        """
        from cellpycore.merge import merge_data

        return merge_data(
            left,
            right,
            schema=self.schema,
            renumber_cycles=renumber_cycles,
            allow_duplicate_test_id=allow_duplicate_test_id,
        )

    def update_core_data(
        self,
        data: Data,
        new_raw,
        *,
        nom_cap_abs: float = 1.0,
        refresh_derived: bool = True,
        find_ir: bool = True,
        current_conversion_factor: float = 1.0,
        nom_cap: Optional[float] = None,
        **kwargs,
    ) -> Data:
        """Incrementally update ``Data`` via ``update_data`` using this cell's schema.

        Args:
            data: Processed data to update.
            new_raw: New raw rows to append.
            nom_cap_abs: Absolute nominal capacity for per-step C-rate.
            refresh_derived: When True (default), run ``c_rates_to_summary`` and
                ``ir_to_summary`` after rebuilding the summary (mirrors
                ``make_core_summary`` extras).
            find_ir: Whether to add IR columns when ``refresh_derived`` is True.
            current_conversion_factor: Current-unit factor for C-rate columns.
            nom_cap: Deprecated alias for ``nom_cap_abs``.
            **kwargs: Forwarded to ``update_data`` / ``make_step_table``.

        Returns:
            A new updated ``Data`` object. The input is not modified.
        """
        import polars as pl

        from cellpycore.merge import update_data
        from cellpycore.summarizers import _resolve_nom_cap_abs

        nom_cap_abs = _resolve_nom_cap_abs(nom_cap_abs, nom_cap)

        if not isinstance(new_raw, pl.DataFrame):
            new_raw = pl.from_pandas(new_raw)

        test_mode = _cycle_mode_to_test_mode(self.cycle_mode)
        out = update_data(
            data,
            new_raw,
            schema=self.schema,
            nom_cap_abs=nom_cap_abs,
            test_mode=test_mode,
            **kwargs,
        )

        if refresh_derived:
            from cellpycore import summarizers

            out = summarizers.c_rates_to_summary(
                out, self.schema, current_conversion_factor=current_conversion_factor
            )
            if find_ir:
                raw_cols = out.raw.columns if hasattr(out.raw, "columns") else []
                if self.schema.raw.internal_resistance in raw_cols:
                    out = summarizers.ir_to_summary(out, self.schema)

        return out

    def add_scaled_summary_columns(
        self,
        data: Data,
        nom_cap_abs: float,
        normalization_cycles: Union[Sequence, int, None],
        step_txt: Optional[str] = None,
        specifics: Optional[List[str]] = None,
        specific_conversion_factors: Optional[dict] = None,
        cell_meta: Optional[CellMeta] = None,
        *,
        specific_converters: Optional[dict] = None,
    ) -> Data:
        """Add specific summary columns to the summary.

        Args:
            data: The data to add the specific summary columns to.
            nom_cap_abs: The nominal capacity of the cell.
            normalization_cycles: The number of cycles to normalize the data by.
            step_txt: The step text to use (charge or discharge capacity, will pick 'first' based on cycle mode if not provided)
            specifics: The specifics to add.
            specific_conversion_factors: Mapping of ``mode -> conversion factor``
                supplied by value by the caller (so this method needs no unit
                handling). If not provided, the factors are computed lazily via
                the units helper using ``self.cellpy_units`` as a fallback
                (legacy / standalone).
            cell_meta: Optional ``CellMeta`` supplying geometry for the units
                fallback when ``specific_conversion_factors`` is omitted. Bare
                ``Data`` without ``specific_conversion_factors`` and without
                geometry (via ``cell_meta`` or attrs on ``data``) raises
                ``ValueError``.
            specific_converters: Deprecated alias for
                ``specific_conversion_factors``.

        Returns:
            The data with the specific summary columns added.
        """
        from cellpycore import summarizers

        schema = self.schema
        factors = summarizers._resolve_specific_conversion_factors(
            specific_conversion_factors, specific_converters
        )

        if specifics is None:
            specifics = ["gravimetric", "areal", "absolute"]

        if step_txt is None:
            step_txt = (
                schema.cycle.discharge_capacity
                if _cycle_mode_to_test_mode(self.cycle_mode) == config.TestMode.INVERTED
                else schema.cycle.charge_capacity
            )

        data = summarizers.equivalent_cycles_to_summary(
            data, schema, nom_cap_abs, normalization_cycles, step_txt
        )

        # Note: the C-rates are added by make_core_summary (using the step-table
        # rates, independent of nom_cap, matching legacy cellpy). Adding them again
        # here would duplicate the charge_c_rate/discharge_c_rate columns (pandas
        # merge would suffix them _x/_y), so it is intentionally not repeated.

        specific_columns = schema.cycle.specific_columns
        for mode in specifics:
            factor = self._resolve_specific_conversion_factor(
                data, mode, factors, cell_meta=cell_meta
            )
            data = summarizers.generate_specific_summary_columns(
                data, mode, specific_columns, factor
            )

        return data

    def _resolve_specific_conversion_factor(
        self,
        data: Data,
        mode: str,
        specific_conversion_factors: Optional[dict],
        *,
        cell_meta: Optional[CellMeta] = None,
    ) -> float:
        """Resolve the specific-capacity conversion factor for a mode.

        Prefers the caller-supplied factor (by value). Falls back to computing it
        via the units helper using ``self.cellpy_units`` (legacy / standalone use);
        this is the only place the summary path may touch pint, and only when the
        caller did not supply the factor.
        """
        if (
            specific_conversion_factors is not None
            and mode in specific_conversion_factors
        ):
            return specific_conversion_factors[mode]

        logger.debug(
            "Specific conversion factor not provided, using units helper to compute it"
        )

        from cellpycore import units

        return units.get_converter_to_specific(
            data=data,
            mode=mode,
            to_units=getattr(self, "cellpy_units", None),
            cell_meta=cell_meta,
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
        nom_cap_abs: Optional[float] = None,
        skip_steps: Optional[Sequence] = None,
        sort_rows: bool = True,
        from_data_point: Optional[int] = None,
        *,
        nom_cap: Optional[float] = None,
    ) -> Union[Data, "DataFrame"]:
        """Make the core step table.

        Delegates to ``summarizers.make_step_table`` using this cell's schema,
        then appends the per-step C-rate via ``summarizers.add_step_c_rate``
        (the downstream summary extras, e.g. ``c_rates_to_summary``, need it).
        The instrument resolution limits (``raw_limits``) and the absolute
        nominal capacity (``nom_cap_abs``, for the C-rate) are supplied by the
        caller.

        Args:
            data: The data to make the step table from.
            raw_limits: The instrument resolution limits. If None, the summarizer
                default (DEFAULT_RAW_LIMITS) is used.
            step_specifications: Optional explicit step specifications.
            short: Whether step specifications are in short format.
            override_step_types: Override the detected step types.
            override_raw_limits: Override individual raw limits.
            usteps: Whether to investigate all (sub-)steps within a cycle.
            nom_cap_abs: Absolute nominal capacity used for the C-rate
                (default 1.0).
            skip_steps: Step numbers to skip.
            sort_rows: Whether to sort the rows after processing.
            from_data_point: First data point to use (returns a DataFrame when set).
            nom_cap: Deprecated alias for ``nom_cap_abs``.

        Returns:
            Data object with the step table, or a DataFrame when ``from_data_point``
            is given.
        """
        from cellpycore import summarizers

        nom_cap_abs = summarizers._resolve_nom_cap_abs(nom_cap_abs, nom_cap)

        kwargs = dict(
            schema=self.schema,
            step_specifications=step_specifications,
            short=short,
            override_step_types=override_step_types,
            override_raw_limits=override_raw_limits,
            usteps=usteps,
            skip_steps=skip_steps,
            sort_rows=sort_rows,
            from_data_point=from_data_point,
        )
        if raw_limits is not None:
            kwargs["raw_limits"] = raw_limits

        result = summarizers.make_step_table(data, **kwargs)
        _nom_cap_abs = nom_cap_abs if nom_cap_abs is not None else 1.0
        if from_data_point is not None:
            # The engine returned a bare steps frame; append the C-rate directly.
            return result.with_columns(
                summarizers._step_c_rate_expr(self.schema.step, _nom_cap_abs)
            )
        return summarizers.add_step_c_rate(
            result, self.schema, nom_cap_abs=_nom_cap_abs
        )


class OldCellpyCellCore(CellpyCellCore):
    """Legacy CellpyCellCore class to make it easier to migrate to cellpy core."""

    def __init__(self, *args, **kwargs):
        from cellpycore.legacy import HeadersNormal, HeadersStepTable, HeadersSummary
        from cellpycore.units import get_cellpy_units, get_default_output_units

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
    #
    # The native <-> legacy correspondence is declared once in
    # ``cellpycore.legacy.mapping``; the methods below just adapt it to the
    # DataFrame renames this bridge needs (see tests/test_header_mapping.py).

    def _legacy_to_native_raw_rename(self, columns) -> dict:
        return mapping.legacy_to_native_raw(columns)

    def _native_to_legacy_step_rename(self) -> dict:
        return mapping.native_to_legacy_step()

    def _legacy_step_column_order(self) -> list:
        leg = self.step_cols
        # ``ustep`` is only present when the engine ran with ``usteps=True`` (the
        # native frame names it literally "ustep" == ``leg.ustep``); it is filtered
        # out below when absent, so this is a no-op for the default step table.
        order = [leg.cycle, leg.step, leg.sub_step, leg.ustep]
        bases = [
            leg.point,
            leg.test_time,
            leg.step_time,
            leg.current,
            leg.voltage,
            leg.charge,
            leg.discharge,
            leg.internal_resistance,
        ]
        for base in bases:
            order += [f"{base}_{stat}" for stat in mapping.STAT_SUFFIXES.values()]
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
            skip_steps=skip_steps,
            sort_rows=False,  # the bridge handles legacy sorting + 'index' column
            from_data_point=from_data_point,
        )
        if raw_limits is not None:
            kwargs["raw_limits"] = raw_limits

        result = summarizers.make_step_table(tmp, **kwargs)
        native_steps = result if from_data_point is not None else result.steps
        if add_c_rate:
            # Appended before the legacy rename/reorder so ``rate_avr`` keeps its
            # byte-for-byte legacy position and values.
            native_steps = native_steps.with_columns(
                summarizers._step_c_rate_expr(
                    default_schema().step, nom_cap if nom_cap is not None else 1.0
                )
            )

        legacy_steps = self._native_steps_to_legacy(native_steps, sort_rows=sort_rows)
        # The native engine only classifies step ``type`` from the specifications;
        # the legacy ``info`` column is carried here in pandas so NaN entries keep
        # their legacy ``str(NaN) == "nan"`` behaviour.
        if step_specifications is not None:
            legacy_steps = self._apply_spec_info(
                legacy_steps, step_specifications, short
            )
        if from_data_point is not None:
            return legacy_steps
        data.steps = legacy_steps
        return data

    def _apply_spec_info(self, legacy_steps, step_specifications, short: bool):
        """Map the ``info`` column from step specifications onto the step table.

        Mirrors legacy cellpy: in short mode the spec is keyed by ``step`` only
        (applied across all cycles); otherwise by ``(cycle, step)``. Values are
        copied verbatim (a missing spec ``info`` stays NaN, i.e. ``"nan"``).
        """
        if "info" not in step_specifications.columns:
            return legacy_steps
        leg = self.step_cols
        spec = step_specifications
        if short:
            info_by_key = dict(zip(spec["step"], spec["info"]))
            legacy_steps[leg.info] = legacy_steps[leg.step].map(info_by_key)
        else:
            info_by_key = {
                (c, s): i for c, s, i in zip(spec["cycle"], spec["step"], spec["info"])
            }
            legacy_steps[leg.info] = [
                info_by_key.get((c, s))
                for c, s in zip(legacy_steps[leg.cycle], legacy_steps[leg.step])
            ]
        return legacy_steps

    # ---- legacy <-> native bridge for the polars summary engine -------------
    # The native engine (summarizers.make_summary) produces the clean native
    # CycleCols subset. cellpy expects the full legacy HeadersSummary frame, so
    # this bridge renames native->legacy and computes the legacy-only "extras"
    # (cumulated CE, shifted capacities, RIC, IR, C-rates) that the curated
    # native cycle schema deliberately omits. Those extras reuse the (legacy)
    # pandas helpers, which is appropriate: they are legacy cruft.

    def _legacy_to_native_step_rename(self) -> dict:
        return mapping.legacy_to_native_step()

    def _native_to_legacy_summary_rename(self) -> dict:
        return mapping.native_to_legacy_summary()

    def _legacy_to_native_summary_rename(self) -> dict:
        return mapping.legacy_to_native_summary()

    def _legacy_summary_column_order(self, find_end_voltage: bool) -> list:
        leg = self.cycle_cols
        order = [
            leg.ir_charge,
            leg.ir_discharge,
            leg.data_point,
            leg.test_time,
            leg.datetime,
            leg.cycle_index,
            leg.charge_capacity,
            leg.discharge_capacity,
            leg.coulombic_efficiency,
            leg.cumulated_coulombic_efficiency,
            leg.cumulated_charge_capacity,
            leg.cumulated_discharge_capacity,
            leg.discharge_capacity_loss,
            leg.charge_capacity_loss,
            leg.coulombic_difference,
            leg.cumulated_coulombic_difference,
            leg.cumulated_discharge_capacity_loss,
            leg.cumulated_charge_capacity_loss,
            leg.shifted_charge_capacity,
            leg.shifted_discharge_capacity,
            leg.cumulated_ric,
            leg.cumulated_ric_sei,
            leg.cumulated_ric_disconnect,
        ]
        if find_end_voltage:
            order += [leg.end_voltage_discharge, leg.end_voltage_charge]
        order += [leg.charge_c_rate, leg.discharge_c_rate]
        return order

    def _add_legacy_summary_cruft(self, data: Data) -> None:
        """Add the pandas-only legacy summary columns the native schema omits.

        ``cumulated_coulombic_efficiency``, ``shifted_*`` and ``cumulated_ric*`` are
        legacy cruft with no native ``CycleCols`` equivalent (unlike the C-rates /
        IR, which issue #21 moved onto the native schema). They are computed here in
        pandas, after the native->legacy rename.
        """
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

    def make_core_summary(
        self,
        data: Data,
        find_ir: bool = True,
        find_end_voltage: bool = False,
        select_columns: bool = True,
        final_data_points: Optional[Iterable[int]] = None,
        current_conversion_factor: float = 1.0,
        ir_extractor: Optional[Callable] = None,
        exclude_step_types: Optional[Iterable[str]] = None,
    ) -> Data:
        """Build the per-cycle summary via the polars engine, in/out in legacy form.

        Runs the native ``make_summary`` engine plus the now-native polars C-rate /
        IR helpers, renames native->legacy, then adds the remaining pandas-only
        legacy cruft to reproduce the legacy ``HeadersSummary`` frame.

        ``ir_extractor`` is forwarded to ``summarizers.ir_to_summary`` (defaults to
        ``extractors.LastIRExtractor`` when ``None``). ``exclude_step_types`` is
        forwarded to ``summarizers.make_summary`` (step-type prefixes whose
        capacity contributions are subtracted from the summary, issue #54).
        """
        import polars as pl

        from cellpycore import summarizers

        native_schema = config.default_schema()
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
            nd,
            native_schema,
            final_data_points=final_data_points,
            exclude_step_types=exclude_step_types,
        )

        # C-rate / IR are now native-schema columns (issue #21): compute them on the
        # native polars frame before the single native->legacy rename. Their native
        # names match the legacy names, so they survive the rename untouched.
        if find_ir and (native_schema.raw.internal_resistance in nd.raw.columns):
            summarizers.ir_to_summary(nd, native_schema, ir_extractor=ir_extractor)
        summarizers.c_rates_to_summary(
            nd, native_schema, current_conversion_factor=current_conversion_factor
        )

        leg = self.cycle_cols
        summary = nd.summary.to_pandas().rename(
            columns=self._native_to_legacy_summary_rename()
        )

        # date_time passthrough (native raw carries epoch time, not date_time)
        dp_txt = self.raw_cols.data_point_txt
        dt_txt = self.raw_cols.datetime_txt
        if dt_txt in data.raw.columns:
            # cellpy keeps data_point as both the raw index and a column; drop the
            # index here so the merge key is unambiguous (otherwise pandas raises
            # "'data_point' is both an index level and a column label").
            dt_map = (
                data.raw[[dp_txt, dt_txt]]
                .reset_index(drop=True)
                .drop_duplicates(subset=[dp_txt])
            )
            dt_map = dt_map.rename(columns={dp_txt: leg.data_point})
            summary = summary.merge(dt_map, on=leg.data_point, how="left")

        summary.index = list(range(len(summary)))
        data.summary = summary

        self._add_legacy_summary_cruft(data)

        order = self._legacy_summary_column_order(find_end_voltage)
        order = [c for c in order if c in data.summary.columns]
        data.summary = data.summary[order]
        return data

    def add_scaled_summary_columns(
        self,
        data: Data,
        nom_cap_abs: float,
        normalization_cycles: Union[Sequence, int, None],
        step_txt: Optional[str] = None,
        specifics: Optional[List[str]] = None,
        specific_conversion_factors: Optional[dict] = None,
        cell_meta: Optional[CellMeta] = None,
        *,
        specific_converters: Optional[dict] = None,
    ) -> Data:
        """Legacy-bridge ``add_scaled_summary_columns`` (pandas<->polars seam).

        The native helpers are polars-native on the native schema, but cellpy calls
        this on the legacy pandas summary. So this bridges: legacy pandas summary ->
        native polars -> native ``equivalent_cycles`` / ``generate_specific`` ->
        legacy pandas, mapping the produced specific columns back to legacy names.
        """
        import polars as pl

        from cellpycore import summarizers
        from cellpycore.config import default_schema

        native_schema = default_schema()
        factors = summarizers._resolve_specific_conversion_factors(
            specific_conversion_factors, specific_converters
        )
        if specifics is None:
            specifics = ["gravimetric", "areal", "absolute"]

        nd = Data()
        nd.summary = pl.from_pandas(
            data.summary.rename(columns=self._legacy_to_native_summary_rename())
        )

        if step_txt is None:
            step_txt = (
                native_schema.cycle.discharge_capacity
                if _cycle_mode_to_test_mode(self.cycle_mode) == config.TestMode.INVERTED
                else native_schema.cycle.charge_capacity
            )

        summarizers.equivalent_cycles_to_summary(
            nd, native_schema, nom_cap_abs, normalization_cycles, step_txt
        )
        specific_columns = native_schema.cycle.specific_columns
        for mode in specifics:
            factor = self._resolve_specific_conversion_factor(
                data, mode, factors, cell_meta=cell_meta
            )
            summarizers.generate_specific_summary_columns(
                nd, mode, specific_columns, factor
            )

        # native -> legacy, incl. the generated ``{col}_{mode}`` specific columns.
        rename = mapping.expand_specific_columns(
            self._native_to_legacy_summary_rename(), specific_columns, specifics
        )
        result = nd.summary.to_pandas().rename(columns=rename)
        result.index = list(range(len(result)))
        data.summary = result
        return data
