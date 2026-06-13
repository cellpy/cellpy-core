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
    # TODO: implement make step table (utilize summarizers.py)
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

    def make_core_summary(
        self,
        data: Data,
        selector: Optional[Callable] = None,
        find_ir: bool = True,
        find_end_voltage: bool = False,
        select_columns: bool = True,
        final_data_points: Optional[Iterable[int]] = None,
    ) -> Data:
        """Make the core summary.

        Args:
            data: The data to make the summary from.
            selector: The selector to use.
            find_ir: Whether to find the IR.
            find_end_voltage: Whether to find the end voltage.
            select_columns: Whether to select only the minimum columns that are needed.
            final_data_points: The final data point for each cycle to use for the selector.

        Returns:
            Data object with the summary.
        """

        from cellpycore import selectors, summarizers

        time_00 = time.time()
        logger.debug("start making summary")

        if selector is None:
            selector = selectors.create_selector(
                data, final_data_points=final_data_points
            )
        summary = selector()
        column_names = summary.columns
        # TODO @jepe: use pandas.DataFrame properties instead (.len, .reset_index), but maybe first
        #  figure out if this is really needed and why it was implemented in the first place.
        summary_length = len(summary[column_names[0]])
        summary.index = list(range(summary_length))

        if select_columns:
            logger.debug("Sorry - select_columns is not implemented yet")

        data.summary = summary

        if self.cycle_mode == config.CyclingMode.ANODE:
            logger.info(
                "Assuming cycling in anode half-data (discharge before charge) mode"
            )
            _first_step_txt = self.cycle_cols.discharge_capacity
            _second_step_txt = self.cycle_cols.charge_capacity
        else:
            logger.info("Assuming cycling in full-data / cathode mode")
            _first_step_txt = self.cycle_cols.charge_capacity
            _second_step_txt = self.cycle_cols.discharge_capacity

        # ---------------- absolute -------------------------------

        data = summarizers.generate_absolute_summary_columns(
            data, _first_step_txt, _second_step_txt
        )

        # TODO @jepe: refactor this to method:
        if find_end_voltage:
            data = summarizers.end_voltage_to_summary(data)

        if find_ir and (self.raw_cols.internal_resistance_txt in data.raw.columns):
            data = summarizers.ir_to_summary(data)

        data = summarizers.c_rates_to_summary(data)

        logger.debug(f"(dt: {(time.time() - time_00):4.2f}s)")
        return data

    def add_scaled_summary_columns(
        self,
        data: Data,
        nom_cap_abs: float,
        normalization_cycles: Union[Sequence, int, None],
        step_txt: Optional[str] = None,
        specifics: Optional[List[str]] = None,
    ) -> Data:
        """Add specific summary columns to the summary.

        Args:
            data: The data to add the specific summary columns to.
            nom_cap_abs: The nominal capacity of the cell.
            normalization_cycles: The number of cycles to normalize the data by.
            step_txt: The step text to use (charge or discharge capacity, will pick 'first' based on cycle mode if not provided)
            specifics: The specifics to add.

        Returns:
            The data with the specific summary columns added.
        """
        from cellpycore import summarizers

        if specifics is None:
            specifics = ["gravimetric", "areal", "absolute"]

        if step_txt is None:
            if self.cycle_mode == "anode":
                step_txt = self.cycle_cols.discharge_capacity
            else:
                step_txt = self.cycle_cols.charge_capacity

        data = summarizers.equivalent_cycles_to_summary(
            data, nom_cap_abs, normalization_cycles, step_txt
        )

        data = summarizers.c_rates_to_summary(
            data, nom_cap_abs, normalization_cycles, step_txt
        )

        specific_columns = self.cycle_cols.specific_columns
        for mode in specifics:
            data = summarizers.generate_specific_summary_columns(
                data, mode, specific_columns
            )

        return data


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
