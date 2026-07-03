import collections
import logging
from typing import Any, Optional, TypeVar, Union

from cellpycore.cell_core import Data
from cellpycore.config import STEP_TYPES, Schema, default_schema

DataFrame = TypeVar("DataFrame")

logger = logging.getLogger(__name__)


def get_step_numbers(
    data: Data,
    schema: Optional[Schema] = None,
    steptype: str = "charge",
    allctypes: bool = True,
    pdtype: bool = False,
    cycle_number: Optional[int] = None,
    trim_taper_steps: Optional[int] = None,
    steps_to_skip: Optional[list] = None,
    steptable: Optional[Any] = None,
    usteps: bool = False,
) -> Union[dict, DataFrame]:
    # TODO: @jepe - include sub_steps here
    # TODO: @jepe - include option for not selecting taper steps here
    # TODO: @jepe - refactor this method!
    """Get the step numbers of selected type.

    Returns the selected step_numbers for the selected type of step(s).
    Either in a dictionary containing a list of step numbers corresponding
    to the selected steptype for the cycle(s), or a ``pandas.DataFrame`` instead of
    a dict of lists if pdtype is set to True. The frame is a sub-set of the
    step-table frame (i.e. all the same columns, only filtered by rows).

    Args:
        steptype (string): string identifying type of step.
        allctypes (bool): get all types of charge (or discharge).
        pdtype (bool): return results as pandas.DataFrame
        cycle_number (int): selected cycle, selects all if not set.
        trim_taper_steps (int): number of taper steps to skip (counted
            from the end, i.e. 1 means skip last step in each cycle).
        steps_to_skip (list): step numbers that should not be included.
        steptable (pandas.DataFrame): optional steptable

    Returns:
        dict or ``pandas.DataFrame``

    Example:
        >>> my_charge_steps = CellpyCell.get_step_numbers(
        >>>    "charge",
        >>>    cycle_number = 3
        >>> )
        >>> print my_charge_steps
        {3: [5,8]}

    """
    if schema is None:
        schema = default_schema()

    if trim_taper_steps is not None and usteps:
        logger.warning(
            "Trimming taper steps is not possible when using usteps. Not doing any trimming."
        )
        trim_taper_steps = None

    if steps_to_skip is None:
        steps_to_skip = []

    if steptable is None:
        if not data.has_steps:
            logger.debug("step-table is not made")
            logger.info(
                "ERROR! Cannot use get_step_numbers: you must create your step-table first"
            )
            raise ValueError(
                "Cannot use get_step_numbers: you must create your step-table first"
            )

    # check if steptype is valid
    steptype = steptype.lower()
    steptypes = []
    helper_step_types = ["ocv", "charge_discharge"]
    valid_step_type = True
    if steptype in STEP_TYPES:
        steptypes.append(steptype)
    else:
        if steptype in helper_step_types:
            if steptype == "ocv":
                steptypes.append("ocvrlx_up")
                steptypes.append("ocvrlx_down")
            elif steptype == "charge_discharge":
                steptypes.append("charge")
                steptypes.append("discharge")
        else:
            valid_step_type = False
    if not valid_step_type:
        return None

    # in case of selection `allctypes`, then modify charge, discharge
    if allctypes:
        add_these = []
        for st in steptypes:
            if st in ["charge", "discharge"]:
                st1 = st + "_cv"
                add_these.append(st1)
                st1 = "cv_" + st
                add_these.append(st1)
        for st in add_these:
            steptypes.append(st)

    if steptable is None:
        st = data.steps
    else:
        st = steptable
    shdr = schema.step

    # Retrieving cycle numbers (if cycle_number is None, it selects all cycles)
    if cycle_number is None:
        cycle_numbers = get_cycle_numbers(data, schema, steptable=steptable)
    else:
        if isinstance(cycle_number, collections.abc.Iterable):
            cycle_numbers = cycle_number
        else:
            cycle_numbers = [cycle_number]

    if trim_taper_steps is not None:
        trim_taper_steps = -trim_taper_steps
        logger.debug("taper steps to trim given")

    if pdtype:
        if trim_taper_steps:
            logger.info(
                "Trimming taper steps is currently not"
                "possible when returning externals.pandas.DataFrame. "
                "Do it manually instead."
            )
        out = st[st[shdr.type].isin(steptypes) & st[shdr.cycle].isin(cycle_numbers)]
        return out

    out = dict()
    step_hdr = shdr.ustep if usteps else shdr.step
    for cycle in cycle_numbers:
        steplist = []
        for s in steptypes:
            mask_type_and_cycle = (st[shdr.type] == s) & (st[shdr.cycle] == cycle)
            if not any(mask_type_and_cycle):
                logger.debug(f"Cycle {cycle} | StepType {s}: Not present!")
            else:
                # Get the step numbers
                step = st[mask_type_and_cycle][step_hdr].tolist()
                for newstep in step[:trim_taper_steps]:
                    if newstep in steps_to_skip:
                        logger.debug(f"skipping step {newstep}")
                    else:
                        steplist.append(int(newstep))

        if not steplist:
            steplist = [0]
        out[cycle] = steplist
    return out


def get_cycle_numbers(
    data: Data,
    schema: Optional[Schema] = None,
    steptable=None,
    rate=None,
    rate_on=None,
    rate_std=None,
    rate_agg="first",
    inverse=False,
):
    """Get a array containing the cycle numbers in the test.

    Parameters:
        steptable (pandas.DataFrame): the step-table to use (if None, the step-table
            from the cellpydata object will be used).
        rate (float): the rate to filter on. Remark that it should be given
            as a float, i.e. you will have to convert from C-rate to
            the actual numeric value. For example, use rate=0.05 if you want
            to filter on cycles that has a C/20 rate.
        rate_on (str): only select cycles if based on the rate of this step-type (e.g. on="discharge").
        rate_std (float): allow for this inaccuracy in C-rate when selecting cycles
        rate_agg (str): perform an aggregation on rate if more than one step of charge or discharge is found
            (e.g. "mean", "first", "max"). For example, if agg='mean', the average rate for each cycle
            will be returned. Set to None if you want to keep all the rates.
        inverse (bool): select steps that does not have the given C-rate.

    Returns:
        numpy.ndarray of cycle numbers.
    """

    # TODO: add support for selecting cycles based on other criteria (for example, based on the
    #   existence of particular step-types, or max, min values of current, voltage, etc)

    logger.debug("getting cycle numbers")

    if schema is None:
        schema = default_schema()

    if steptable is None:
        d = data.raw
        cycles = d[schema.raw.cycle_index_txt].dropna().unique()
        steptable = data.steps
    else:
        logger.debug("steptable is given as input parameter")
        cycles = steptable[schema.step.cycle].dropna().unique()

    if rate is None:
        return cycles

    logger.debug("filtering on rate")

    if rate is None:
        rate = 0.05

    if rate_std is None:
        rate_std = 0.1 * rate

    if rate_on is None:
        rate_on = ["charge", "discharge"]
    rates = get_rates(
        data, schema, steptable=steptable, agg=rate_agg, direction=rate_on
    )
    rate_column = schema.step.rate_avr
    cycles_mask = (rates[rate_column] < (rate + rate_std)) & (
        rates[rate_column] > (rate - rate_std)
    )

    if inverse:
        cycles_mask = ~cycles_mask

    filtered_rates = rates[cycles_mask]
    filtered_cycles = filtered_rates[schema.step.cycle].unique()

    return filtered_cycles


def get_rates(
    data: Data,
    schema: Optional[Schema] = None,
    steptable: Optional[Any] = None,
    agg: str = "first",
    direction: Optional[str] = None,
) -> DataFrame:
    """
    Get the rates in the test (only valid for constant current).

    Args:
        steptable: provide custom steptable (if None, the steptable from the cellpydata object will be used).
        agg (str): perform an aggregation if more than one step of charge or
            discharge is found (e.g. "mean", "first", "max"). For example, if agg='mean', the average rate
            for each cycle will be returned. Set to None if you want to keep all the rates.
        direction (str or list of str): only select rates for this direction (e.g. "charge" or "discharge").

    Returns:
        ``pandas.DataFrame`` with cycle, type, and rate_avr (i.e. C-rate) columns.
    """

    if schema is None:
        schema = default_schema()

    if steptable is None:
        steptable = data.steps
    rates = steptable[
        [
            schema.step.cycle,
            schema.step.type,
            schema.step.rate_avr,
        ]
    ].dropna()

    if agg:
        rates = (
            rates.groupby([schema.step.cycle, schema.step.type]).agg(agg).reset_index()
        )

    if direction is not None:
        if not isinstance(direction, (list, tuple)):
            direction = [direction]
        rates = rates.loc[rates[schema.step.type].isin(direction), :]

    return rates


def _main():
    print("selectors.py - no main function yet")


if __name__ == "__main__":
    _main()
