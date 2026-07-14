"""Spec'd capacity / OCV curve extraction (issue #118, Stage 1.17).

Port of legacy cellpy's most-used data API — ``CellpyCell.get_cap`` /
``get_ccap`` / ``get_dcap`` / ``get_ocv`` — into the core, schema-injected and
with a spec'd output schema (``config.CurveCols`` / ``config.OcvCurveCols``;
authoritative spec in ``docs/specifications/curve-table.md``). The Stage-0
curve snapshots (jepegit/cellpy#433) are the parity oracle
(``tests/test_curves.py``).

Seam rules (unchanged from the rest of the engine):

- **Units by value.** The capacity columns are ``raw capacity × converter``;
  the caller computes the float ``converter`` (e.g. via
  ``cellpycore.units.get_converter_to_specific``). Core never resolves units.
- **Frames in, frames out.** Functions take a native ``Data`` (polars raw +
  steps) and return polars frames with ``CurveCols`` names.

Intentional differences from legacy (documented, not silent):

- Output column names are the spec'd native ones (``potential`` /
  ``capacity`` / ``cycle_num`` / ``direction``); the cellpy 2 wrapper renames
  for legacy consumers.
- Cycle iteration order is deterministic (sorted); legacy iterated a ``set``.
- The legacy ``usteps`` channel is not ported (native step tables carry no
  ``ustep`` column); ``dynamic`` (cellpy-file streaming) stays app-side.
- Interpolation uses numpy linear interpolation (mathematically identical to
  the legacy scipy ``interp1d(kind="linear", bounds_error=False)`` on the
  strictly monotonic segments this module feeds it; NaN outside the data
  range) so core gains no scipy dependency.
"""

from __future__ import annotations

import logging
from typing import Iterable, Optional, Union

import numpy as np
import polars as pl

from cellpycore.config import (
    CurveCols,
    OcvCurveCols,
    Schema,
    StepType,
    TestMode,
    default_schema,
)
from cellpycore.exceptions import NoDataFound

logger = logging.getLogger(__name__)

_VALID_METHODS = ("back-and-forth", "forth", "forth-and-forth")

# Legacy helper step types resolved to concrete step-type lists.
_HELPER_STEP_TYPES = {
    "ocv": [StepType.OCVRLX_UP.value, StepType.OCVRLX_DOWN.value],
    "charge_discharge": [StepType.CHARGE.value, StepType.DISCHARGE.value],
}


# ---------------------------------------------------------------------------
#   interpolation (numpy port of legacy ds.interpolate_y_on_x*)
# ---------------------------------------------------------------------------
def _interpolate_linear(
    xs: np.ndarray,
    ys: np.ndarray,
    *,
    dx: float = 10.0,
    number_of_points: Optional[int] = None,
    direction: int = 1,
) -> tuple[np.ndarray, np.ndarray]:
    """Linear interpolation of ``ys`` on ``xs`` (NaN outside the data range)."""
    if direction > 0:
        x_min, x_max, step = xs.min(), xs.max(), dx
    else:
        x_min, x_max, step = xs.max(), xs.min(), -dx
    if number_of_points:
        new_x = np.linspace(x_min, x_max, number_of_points)
    else:
        new_x = np.arange(x_min, x_max, step)
    order = np.argsort(xs, kind="mergesort")
    new_y = np.interp(new_x, xs[order], ys[order], left=np.nan, right=np.nan)
    return new_x, new_y


def _interpolate_per_monotonic_segments(
    xs: np.ndarray,
    ys: np.ndarray,
    *,
    dx: float = 10.0,
    number_of_points: Optional[int] = None,
    direction: int = 1,
    max_segments: Optional[int] = 100,
) -> tuple[np.ndarray, np.ndarray]:
    """Interpolate per strictly monotonic segment, then concatenate.

    Split points, constant-x passthrough, short-segment skipping and the
    ``max_segments`` bailout mirror the legacy implementation exactly.
    """
    n = len(xs)
    if n < 2:
        return xs, ys
    if direction > 0:
        segment_start = np.r_[True, xs[1:] <= xs[:-1]]
    else:
        segment_start = np.r_[True, xs[1:] >= xs[:-1]]
    n_segments = int(segment_start.sum())
    if max_segments is not None and n_segments > max_segments:
        logger.warning(
            "interpolation: %d segments exceeds max_segments=%s; "
            "returning data unchanged (likely noisy x-data)",
            n_segments,
            max_segments,
        )
        return xs, ys
    segment_id = np.cumsum(segment_start) - 1
    xs_out: list[np.ndarray] = []
    ys_out: list[np.ndarray] = []
    for i in range(n_segments):
        mask = segment_id == i
        seg_x, seg_y = xs[mask], ys[mask]
        if len(seg_x) < 2:
            continue
        if seg_x.min() == seg_x.max():
            xs_out.append(seg_x)
            ys_out.append(seg_y)
            continue
        new_x, new_y = _interpolate_linear(
            seg_x, seg_y, dx=dx, number_of_points=number_of_points, direction=direction
        )
        xs_out.append(new_x)
        ys_out.append(new_y)
    if not xs_out:
        return xs, ys
    return np.concatenate(xs_out), np.concatenate(ys_out)


# ---------------------------------------------------------------------------
#   step-number selection (port of legacy get_step_numbers, dict flavour)
# ---------------------------------------------------------------------------
def select_step_numbers(
    steps: pl.DataFrame,
    schema: Optional[Schema] = None,
    *,
    step_type: Union[str, Iterable[str]] = "charge",
    cycles: Optional[Iterable[int]] = None,
    all_combined_types: bool = False,
    trim_taper_steps: Optional[int] = None,
    steps_to_skip: Optional[Iterable[int]] = None,
) -> dict[int, list[int]]:
    """Return ``{cycle: [step numbers]}`` for the selected step type(s).

    Args:
        steps: Native step table (polars).
        schema: Injected schema; defaults to :func:`default_schema`.
        step_type: A step-type label, one of the helper labels (``"ocv"``,
            ``"charge_discharge"``), or an iterable of labels.
        cycles: Cycle numbers to select (all cycles in ``steps`` if None).
        all_combined_types: When True and the type is charge/discharge, also
            include the combined ``<type>_cv`` / ``cv_<type>`` variants
            (legacy ``allctypes``).
        trim_taper_steps: Skip this many steps counted from the end of each
            cycle's selection (legacy taper trimming).
        steps_to_skip: Step numbers to exclude.

    Returns:
        dict: ``{cycle: [step, ...]}``; a cycle with no matching steps maps to
        ``[0]`` (the legacy placeholder convention).
    """
    schema = schema or default_schema()
    steps_to_skip = set(steps_to_skip or ())
    cycle_col = schema.step.cycle_num
    type_col = schema.step.step_type
    step_col = schema.step.step_num

    if isinstance(step_type, str):
        step_type = step_type.lower()
        steptypes = _HELPER_STEP_TYPES.get(step_type, [step_type])
    else:
        steptypes = [str(st).lower() for st in step_type]

    if all_combined_types:
        extra = []
        for st in steptypes:
            if st in ("charge", "discharge"):
                extra.extend([f"{st}_cv", f"cv_{st}"])
        steptypes = steptypes + extra

    if cycles is None:
        cycle_numbers = steps[cycle_col].unique().sort().to_list()
    else:
        cycle_numbers = list(cycles) if isinstance(cycles, Iterable) else [cycles]

    trim = -trim_taper_steps if trim_taper_steps is not None else None

    out: dict[int, list[int]] = {}
    for cycle in cycle_numbers:
        steplist: list[int] = []
        for st in steptypes:
            sel = steps.filter((pl.col(type_col) == st) & (pl.col(cycle_col) == cycle))
            if sel.height == 0:
                continue
            for step in sel[step_col].to_list()[:trim]:
                if step in steps_to_skip:
                    logger.debug("skipping step %s", step)
                else:
                    steplist.append(int(step))
        out[cycle] = steplist or [0]
    return out


# ---------------------------------------------------------------------------
#   single-branch extraction (port of legacy _get_cap)
# ---------------------------------------------------------------------------
def _extract_branch_arrays(
    data,
    schema: Schema,
    *,
    cycle: int,
    cap_type: str,
    converter: float,
    trim_taper_steps: Optional[int] = None,
    steps_to_skip: Optional[Iterable[int]] = None,
    steps: Optional[pl.DataFrame] = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(capacity, potential)`` arrays for one branch of one cycle."""
    if cap_type in ("charge_capacity", "discharge_capacity"):
        cap_type = cap_type.removesuffix("_capacity")
    steps_frame = steps if steps is not None else data.steps
    if steps_frame is None:
        raise NoDataFound("no step table available (run make_step_table first)")
    numbers = select_step_numbers(
        steps_frame,
        schema,
        step_type=cap_type,
        cycles=[cycle],
        all_combined_types=False,
        trim_taper_steps=trim_taper_steps,
        steps_to_skip=steps_to_skip,
    )
    step_list = numbers[cycle]
    if len(set(step_list)) < len(step_list):
        raise ValueError("duplicate step numbers in selection")

    cap_col = (
        schema.raw.cumulative_charge_capacity
        if cap_type == "charge"
        else schema.raw.cumulative_discharge_capacity
    )
    pot_col = schema.raw.potential
    cycle_col = schema.raw.cycle_num
    step_col = schema.raw.step_num

    caps: list[np.ndarray] = []
    pots: list[np.ndarray] = []
    for step in sorted(step_list):
        sel = data.raw.filter((pl.col(cycle_col) == cycle) & (pl.col(step_col) == step))
        if sel.height == 0:
            logger.debug("step %s is empty", step)
            continue
        caps.append(sel[cap_col].to_numpy().astype(np.float64) * converter)
        pots.append(sel[pot_col].to_numpy().astype(np.float64))
    if not caps:
        raise NoDataFound(f"no steps found (c:{cycle} s:{step_list} type:{cap_type})")
    return np.concatenate(caps), np.concatenate(pots)


def _branch_frame(
    capacity: np.ndarray, potential: np.ndarray, curve_cols: CurveCols
) -> pl.DataFrame:
    return pl.DataFrame(
        {curve_cols.potential: potential, curve_cols.capacity: capacity}
    )


def get_charge_curve(
    data,
    schema: Optional[Schema] = None,
    *,
    cycle: int,
    converter: float = 1.0,
    trim_taper_steps: Optional[int] = None,
    steps_to_skip: Optional[Iterable[int]] = None,
    steps: Optional[pl.DataFrame] = None,
    curve_cols: Optional[CurveCols] = None,
) -> pl.DataFrame:
    """Charge branch of one cycle as ``[potential, capacity]`` (spec'd names).

    ``capacity`` is the raw cumulative charge capacity × ``converter``
    (units by value; the caller owns the conversion factor).

    Raises:
        NoDataFound: When the cycle has no (non-empty) charge steps.
    """
    schema = schema or default_schema()
    cap, pot = _extract_branch_arrays(
        data,
        schema,
        cycle=cycle,
        cap_type="charge",
        converter=converter,
        trim_taper_steps=trim_taper_steps,
        steps_to_skip=steps_to_skip,
        steps=steps,
    )
    return _branch_frame(cap, pot, curve_cols or CurveCols())


def get_discharge_curve(
    data,
    schema: Optional[Schema] = None,
    *,
    cycle: int,
    converter: float = 1.0,
    trim_taper_steps: Optional[int] = None,
    steps_to_skip: Optional[Iterable[int]] = None,
    steps: Optional[pl.DataFrame] = None,
    curve_cols: Optional[CurveCols] = None,
) -> pl.DataFrame:
    """Discharge branch of one cycle as ``[potential, capacity]`` (spec'd names).

    Raises:
        NoDataFound: When the cycle has no (non-empty) discharge steps.
    """
    schema = schema or default_schema()
    cap, pot = _extract_branch_arrays(
        data,
        schema,
        cycle=cycle,
        cap_type="discharge",
        converter=converter,
        trim_taper_steps=trim_taper_steps,
        steps_to_skip=steps_to_skip,
        steps=steps,
    )
    return _branch_frame(cap, pot, curve_cols or CurveCols())


# ---------------------------------------------------------------------------
#   full capacity-curve assembly (port of legacy get_cap)
# ---------------------------------------------------------------------------
def _last_value(arr: np.ndarray) -> float:
    return float(arr[-1]) if arr.size else 0.0


def get_cap_curve(
    data,
    schema: Optional[Schema] = None,
    *,
    cycle: Union[int, Iterable[int], None] = None,
    cycles: Optional[Iterable[int]] = None,
    method: str = "back-and-forth",
    insert_nan: Optional[bool] = None,
    shift: float = 0.0,
    categorical_column: bool = False,
    label_cycle_number: bool = False,
    interpolated: bool = False,
    dx: float = 0.1,
    number_of_points: Optional[int] = None,
    ignore_errors: bool = True,
    inter_cycle_shift: bool = True,
    interpolate_along_cap: bool = False,
    capacity_then_voltage: bool = False,
    converter: float = 1.0,
    test_mode: Union[TestMode, str] = TestMode.NORMAL,
    trim_taper_steps: Optional[int] = None,
    steps_to_skip: Optional[Iterable[int]] = None,
    curve_cols: Optional[CurveCols] = None,
) -> pl.DataFrame:
    """Assemble the capacity-vs-potential curve(s) for the selected cycle(s).

    Faithful port of legacy ``CellpyCell.get_cap`` onto the native schema.
    Output columns follow ``CurveCols`` (``docs/specifications/curve-table.md``):
    ``potential`` and ``capacity`` always; ``cycle_num`` first when
    ``label_cycle_number``; ``direction`` (−1 first branch / +1 last branch,
    NaN on separator rows) when ``categorical_column``. With
    ``capacity_then_voltage`` the capacity/potential column order is swapped.

    Args:
        data: Native ``Data`` (polars ``raw`` + ``steps``).
        schema: Injected schema; defaults to :func:`default_schema`.
        cycle: Cycle number(s); all available cycles when None.
        cycles: Alias for ``cycle`` (takes precedence when given).
        method: ``"back-and-forth"`` (default), ``"forth"``, or
            ``"forth-and-forth"`` — same semantics as legacy.
        insert_nan: Insert a NaN separator row between branches; defaults to
            True only for ``"forth-and-forth"``.
        shift: Start value for the first branch's capacity axis.
        categorical_column: Add the ``direction`` column.
        label_cycle_number: Add the leading ``cycle_num`` column (tidy format).
        interpolated: Interpolate each branch per strictly monotonic segment.
        dx: Interpolation step (potential axis unless
            ``interpolate_along_cap``).
        number_of_points: Overrides ``dx`` (points per monotonic segment).
        ignore_errors: Continue past cycles whose extraction fails.
        inter_cycle_shift: Accumulate capacity shifts across cycles.
        interpolate_along_cap: Interpolate along the capacity axis instead.
        capacity_then_voltage: Put ``capacity`` before ``potential``.
        converter: Multiplicative capacity conversion factor (units by value).
        test_mode: ``TestMode.INVERTED`` (legacy ``cycle_mode="anode"``) makes
            the discharge branch the cycle's *first* branch.
        trim_taper_steps: Passed to step selection (legacy taper trimming).
        steps_to_skip: Passed to step selection.
        curve_cols: Output-column override (defaults to ``CurveCols()``).

    Returns:
        polars.DataFrame in the spec'd curve-table schema (possibly empty).
    """
    schema = schema or default_schema()
    ccols = curve_cols or CurveCols()

    inverted = TestMode(test_mode) == TestMode.INVERTED

    steps_frame = data.steps
    if steps_frame is None:
        raise NoDataFound("no step table available (run make_step_table first)")
    available = steps_frame[schema.step.cycle_num].unique().sort().to_list()

    if cycles is not None:
        cycle = cycles
    if cycle is None:
        cycle = available
    if not isinstance(cycle, Iterable):
        cycle = [cycle]
    # deterministic (sorted) — intentional difference from legacy's set order
    selected_cycles = sorted(set(cycle) & set(available))

    method = method.lower()
    if method not in _VALID_METHODS:
        logger.warning(
            "method %r is not a valid option - using 'back-and-forth'", method
        )
        method = "back-and-forth"
    if insert_nan is None:
        insert_nan = method == "forth-and-forth"

    x_is_potential = not interpolate_along_cap

    pot_parts: list[np.ndarray] = []
    cap_parts: list[np.ndarray] = []
    dir_parts: list[np.ndarray] = []
    cyc_parts: list[np.ndarray] = []

    def _append_block(
        pot: np.ndarray, cap: np.ndarray, direction_value: float, cycle_value: int
    ) -> None:
        pot_parts.append(pot)
        cap_parts.append(cap)
        if categorical_column:
            dir_parts.append(np.full(pot.shape, direction_value))
        if label_cycle_number:
            cyc_parts.append(np.full(pot.shape, cycle_value))
        if insert_nan:
            pot_parts.append(np.array([np.nan]))
            cap_parts.append(np.array([np.nan]))
            if categorical_column:
                dir_parts.append(np.array([np.nan]))
            if label_cycle_number:
                cyc_parts.append(np.array([float(cycle_value)]))

    initial = True
    prev_end = shift
    for current_cycle in selected_cycles:
        cc = cv = dc = dv = np.array([], dtype=np.float64)
        try:
            cc, cv = _extract_branch_arrays(
                data,
                schema,
                cycle=current_cycle,
                cap_type="charge",
                converter=converter,
                trim_taper_steps=trim_taper_steps,
                steps_to_skip=steps_to_skip,
            )
        except NoDataFound as e:
            logger.info(e)
            if not ignore_errors:
                break
        try:
            dc, dv = _extract_branch_arrays(
                data,
                schema,
                cycle=current_cycle,
                cap_type="discharge",
                converter=converter,
                trim_taper_steps=trim_taper_steps,
                steps_to_skip=steps_to_skip,
            )
        except NoDataFound as e:
            logger.info(e)
            if not ignore_errors:
                break

        if initial:
            prev_end = shift
            initial = False

        if inverted:  # legacy cycle_mode == "anode"
            first_c, first_v = dc, dv
            last_c, last_v = cc, cv
        else:
            first_c, first_v = cc, cv
            last_c, last_v = dc, dv

        if method == "back-and-forth":
            _last = _last_value(first_c)
            if not inter_cycle_shift:
                prev_end = 0.0
            last_c = _last - last_c + prev_end
            first_c = first_c + prev_end
            prev_end = _last_value(last_c)
        elif method == "forth":
            _last = _last_value(first_c)
            last_c = last_c + _last + prev_end
            first_c = first_c + prev_end
            prev_end = _last_value(last_c) if inter_cycle_shift else 0.0
        elif method == "forth-and-forth":
            last_c = last_c + shift
            first_c = first_c + shift

        # interpolation direction follows the legacy convention: the first
        # branch interpolates along decreasing x for anode-first branches etc.
        first_interp_dir = -1 if inverted else 1
        last_interp_dir = 1 if inverted else -1

        def _process(pot, cap, interp_dir):
            if interpolated:
                if x_is_potential:
                    x_arr, y_arr = _interpolate_per_monotonic_segments(
                        pot,
                        cap,
                        dx=dx,
                        number_of_points=number_of_points,
                        direction=interp_dir,
                    )
                    return x_arr, y_arr
                x_arr, y_arr = _interpolate_per_monotonic_segments(
                    cap,
                    pot,
                    dx=dx,
                    number_of_points=number_of_points,
                    direction=interp_dir,
                )
                return y_arr, x_arr
            return pot, cap

        first_pot, first_cap = _process(first_v, first_c, first_interp_dir)
        last_pot, last_cap = _process(last_v, last_c, last_interp_dir)

        if interpolate_along_cap:
            if method == "forth":
                first_pot, first_cap = first_pot[::-1], first_cap[::-1]
            elif method == "back-and-forth":
                first_pot, first_cap = first_pot[::-1], first_cap[::-1]
                last_pot, last_cap = last_pot[::-1], last_cap[::-1]

        if first_cap.size:
            _append_block(first_pot, first_cap, -1.0, current_cycle)
        if last_cap.size:
            _append_block(last_pot, last_cap, 1.0, current_cycle)

    if not pot_parts:
        columns = {}
        if label_cycle_number:
            columns[ccols.cycle_num] = pl.Series([], dtype=pl.Int64)
        columns[ccols.potential] = pl.Series([], dtype=pl.Float64)
        columns[ccols.capacity] = pl.Series([], dtype=pl.Float64)
        if categorical_column:
            columns[ccols.direction] = pl.Series([], dtype=pl.Float64)
        frame = pl.DataFrame(columns)
    else:
        columns = {}
        if label_cycle_number:
            cyc = np.concatenate(cyc_parts)
            columns[ccols.cycle_num] = cyc.astype(np.int64) if not insert_nan else cyc
        columns[ccols.potential] = np.concatenate(pot_parts)
        columns[ccols.capacity] = np.concatenate(cap_parts)
        if categorical_column:
            columns[ccols.direction] = np.concatenate(dir_parts)
        frame = pl.DataFrame(columns)

    if capacity_then_voltage:
        cols = frame.columns
        new_order = [ccols.capacity, ccols.potential] + [
            c for c in cols if c not in (ccols.capacity, ccols.potential)
        ]
        frame = frame.select(new_order)
    return frame


# ---------------------------------------------------------------------------
#   OCV relaxation curves (port of legacy get_ocv)
# ---------------------------------------------------------------------------
def get_ocv_curve(
    data,
    schema: Optional[Schema] = None,
    *,
    cycles: Union[int, Iterable[int], None] = None,
    direction: str = "up",
    remove_first: bool = False,
    interpolated: bool = False,
    dx: Optional[float] = None,
    number_of_points: Optional[int] = None,
    ocv_cols: Optional[OcvCurveCols] = None,
) -> pl.DataFrame:
    """Open-circuit-voltage relaxation curves (spec'd ``OcvCurveCols`` names).

    Args:
        data: Native ``Data`` (polars ``raw`` + ``steps``).
        schema: Injected schema; defaults to :func:`default_schema`.
        cycles: Cycle number(s); all when None. Passing an explicit list
            disables ``remove_first`` (legacy behavior).
        direction: ``"up"``, ``"down"``, or ``"both"``.
        remove_first: Drop the first relaxation (typically the initial rest).
        interpolated: Interpolate potential on step time per (cycle, step).
        dx: Interpolation step in step-time units (defaults to 10.0 when
            neither ``dx`` nor ``number_of_points`` is given).
        number_of_points: Overrides ``dx``.
        ocv_cols: Output-column override (defaults to ``OcvCurveCols()``).

    Returns:
        polars.DataFrame with ``cycle_num``, ``step_num``, ``step_time``,
        ``potential`` columns.
    """
    schema = schema or default_schema()
    ocols = ocv_cols or OcvCurveCols()

    steps_frame = data.steps
    if steps_frame is None:
        raise NoDataFound("no step table available (run make_step_table first)")
    cyc_col = schema.step.cycle_num
    type_col = schema.step.step_type
    step_col = schema.step.step_num

    if cycles is None:
        cycles = steps_frame[cyc_col].unique().sort().to_list()
    elif not isinstance(cycles, Iterable):
        cycles = [cycles]
    else:
        cycles = list(cycles)
        remove_first = False

    prefix = "ocvrlx"
    if direction == "up":
        prefix += "_up"
    elif direction == "down":
        prefix += "_down"

    ocv_steps = steps_frame.filter(
        pl.col(cyc_col).is_in(list(cycles)) & pl.col(type_col).str.starts_with(prefix)
    )
    if remove_first:
        ocv_steps = ocv_steps.slice(1)

    raw = data.raw
    r_cyc = schema.raw.cycle_num
    r_step = schema.raw.step_num
    r_time = schema.raw.step_time
    r_pot = schema.raw.potential

    selected = raw.filter(
        pl.col(r_cyc).is_in(ocv_steps[cyc_col].to_list())
        & pl.col(r_step).is_in(ocv_steps[step_col].to_list())
    ).select(
        pl.col(r_cyc).alias(ocols.cycle_num),
        pl.col(r_step).alias(ocols.step_num),
        pl.col(r_time).alias(ocols.step_time),
        pl.col(r_pot).alias(ocols.potential),
    )

    if interpolated:
        if dx is None and number_of_points is None:
            dx = 10.0
        pieces = []
        for (cyc, step), group in sorted(
            selected.group_by([ocols.cycle_num, ocols.step_num]),
            key=lambda item: item[0],
        ):
            new_x, new_y = _interpolate_linear(
                group[ocols.step_time].to_numpy().astype(np.float64),
                group[ocols.potential].to_numpy().astype(np.float64),
                dx=dx if dx is not None else 10.0,
                number_of_points=number_of_points,
            )
            pieces.append(
                pl.DataFrame(
                    {
                        ocols.cycle_num: np.full(new_x.shape, cyc, dtype=np.int64),
                        ocols.step_num: np.full(new_x.shape, step, dtype=np.int64),
                        ocols.step_time: new_x,
                        ocols.potential: new_y,
                    }
                )
            )
        selected = pl.concat(pieces) if pieces else selected.clear()

    return selected
