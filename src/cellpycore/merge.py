"""Merge and incremental-update helpers for ``Data`` objects."""

from __future__ import annotations

import logging
from copy import copy
from typing import TYPE_CHECKING, Any, Optional

import polars as pl

from cellpycore import config
from cellpycore.cell_core import Data
from cellpycore.summarizers import (
    _ensure_test_id,
    _resolve_nom_cap_abs,
    _step_c_rate_expr,
    make_step_table,
    make_summary,
)

if TYPE_CHECKING:
    from cellpycore.config import Schema

logger = logging.getLogger(__name__)

_CUMULATIVE_SUMMARY_ATTRS = (
    "test_cumulated_charge_capacity",
    "test_cumulated_discharge_capacity",
    "test_cumulated_coulombic_difference",
    "test_cumulated_charge_capacity_loss",
    "test_cumulated_discharge_capacity_loss",
    "test_cumulated_charge_energy",
    "test_cumulated_discharge_energy",
    "test_net_capacity",
    "test_net_energy",
)


def merge_data(
    left: Data,
    right: Data,
    *,
    schema: Optional["Schema"] = None,
    renumber_cycles: bool = True,
    allow_duplicate_test_id: bool = False,
) -> Data:
    """Merge two processed ``Data`` objects into a new one.

    Vertically concatenates ``raw`` and, when present on both sides, ``steps`` and
    ``summary``. Offsets ``datapoint_num`` on the right side by the last left
    datapoint (always). When ``renumber_cycles`` is True, also offsets cycle
    numbers on the right and carries cumulative summary columns forward from the
    last left summary row.

    Args:
        left: First dataset (D1).
        right: Second dataset (D2), appended after ``left``.
        schema: Column-header schema. Defaults to ``config.default_schema()``.
        renumber_cycles: If True (default), offset right ``cycle_num`` values by
            ``max(left.cycle_num)`` and shift cumulative summary columns. If False,
            cycle numbers are kept as-is (multi-test isolation via ``test_id``).
        allow_duplicate_test_id: If False (default), raise when both sides share
            a ``test_id``. If True, reassign colliding right-side ``test_id``
            values to the next free ids.

    Returns:
        A new ``Data`` with merged frames. Inputs are not modified.

    Raises:
        ValueError: If either side lacks ``raw``, or ``test_id`` values collide
            and ``allow_duplicate_test_id`` is False.
    """
    if schema is None:
        schema = config.default_schema()
    nhdr, shdr, chdr = schema.raw, schema.step, schema.cycle

    left_raw = left.raw
    right_raw = right.raw
    if left_raw is None or right_raw is None:
        raise ValueError("merge_data requires both Data objects to have raw frames")

    if _frame_is_empty(left_raw):
        return _copy_data(right)
    if _frame_is_empty(right_raw):
        return _copy_data(left)

    left_pl = _as_polars(left_raw)
    right_pl = _as_polars(right_raw)
    left_pl = _ensure_test_id(left_pl, nhdr.test_id)
    right_pl = _ensure_test_id(right_pl, nhdr.test_id)

    right_pl, test_id_map = _resolve_test_id_collisions(
        right_pl,
        left_pl,
        nhdr.test_id,
        allow_duplicate_test_id=allow_duplicate_test_id,
    )

    dp_offset = _max_column(left_pl, nhdr.datapoint_num)
    right_pl = _offset_int_column(right_pl, nhdr.datapoint_num, dp_offset)

    cycle_offset = 0
    if renumber_cycles:
        cycle_offset = _max_column(left_pl, nhdr.cycle_num)
        right_pl = _offset_int_column(right_pl, nhdr.cycle_num, cycle_offset)

    merged_raw = pl.concat([left_pl, right_pl], how="vertical")

    out = Data()
    out.raw = _restore_frame_type(merged_raw, left_raw)

    if left.steps is not None and right.steps is not None:
        left_steps = _as_polars(left.steps)
        right_steps = _as_polars(right.steps)
        right_steps = _remap_test_id(right_steps, shdr.test_id, test_id_map)
        right_steps = _offset_int_column(
            right_steps, shdr.datapoint_num_first, dp_offset
        )
        right_steps = _offset_int_column(
            right_steps, shdr.datapoint_num_last, dp_offset
        )
        if renumber_cycles:
            right_steps = _offset_int_column(right_steps, shdr.cycle_num, cycle_offset)
        merged_steps = pl.concat([left_steps, right_steps], how="vertical")
        out.steps = _restore_frame_type(merged_steps, left.steps)

    if left.summary is not None and right.summary is not None:
        left_summary = _as_polars(left.summary)
        right_summary = _as_polars(right.summary)
        right_summary = _remap_test_id(right_summary, chdr.test_id, test_id_map)
        right_summary = _offset_int_column(
            right_summary, chdr.datapoint_num_last, dp_offset
        )
        if renumber_cycles:
            right_summary = _offset_int_column(
                right_summary, chdr.cycle_num, cycle_offset
            )
            right_summary = _carry_forward_cumulative_summary(
                left_summary, right_summary, chdr
            )
        merged_summary = pl.concat([left_summary, right_summary], how="vertical")
        out.summary = _restore_frame_type(merged_summary, left.summary)

    return out


def update_data(
    data: Data,
    new_raw: pl.DataFrame,
    *,
    schema: Optional["Schema"] = None,
    nom_cap_abs: float = 1.0,
    partition_col: str | None = None,
    test_mode: config.TestMode = config.TestMode.NORMAL,
    nom_cap: Optional[float] = None,
    **step_table_kwargs: Any,
) -> Data:
    """Incrementally update processed ``Data`` with new raw rows.

    Trims the overlap at ``source_datapoint_num`` (or ``datapoint_num`` when
    absent), refreshes affected step rows via ``make_step_table(from_data_point=…)``,
    and rebuilds the per-cycle summary on the combined frames.

    Args:
        data: Processed ``Data`` with ``raw``, ``steps``, and ``summary``.
        new_raw: New raw rows to append (may overlap the tail of ``data.raw``).
        schema: Column-header schema. Defaults to ``config.default_schema()``.
        nom_cap_abs: Absolute nominal capacity for the per-step C-rate appended
            to the rebuilt step rows (via ``add_step_c_rate``), so they match
            the kept steps.
        partition_col: Column used to detect overlap. Defaults to
            ``source_datapoint_num``, falling back to ``datapoint_num``.
        test_mode: Cell convention forwarded to ``make_summary``.
        nom_cap: Deprecated alias for ``nom_cap_abs``.
        **step_table_kwargs: Extra keyword arguments forwarded to
            ``make_step_table`` (except ``schema``, ``nom_cap_abs``,
            ``from_data_point``).

    Returns:
        A new ``Data`` object. The input is not modified.

    Raises:
        ValueError: If ``data`` is not fully processed, ``new_raw`` is invalid,
            more than one ``test_id`` is present, or ``new_raw`` starts at or
            before the beginning of the existing partition range (full reload).
    """
    nom_cap_abs = _resolve_nom_cap_abs(nom_cap_abs, nom_cap)
    if schema is None:
        schema = config.default_schema()
    nhdr, shdr = schema.raw, schema.step

    if data.raw is None or data.steps is None or data.summary is None:
        raise ValueError("update_data requires data.raw, data.steps, and data.summary")
    if new_raw is None or _frame_is_empty(new_raw):
        return _copy_data(data)

    raw_pl = _as_polars(data.raw)
    steps_pl = _as_polars(data.steps)
    new_pl = _as_polars(new_raw)
    raw_pl = _ensure_test_id(raw_pl, nhdr.test_id)
    new_pl = _ensure_test_id(new_pl, nhdr.test_id)

    _require_single_test_id(raw_pl, nhdr.test_id)
    _require_single_test_id(steps_pl, shdr.test_id)
    _require_single_test_id(new_pl, nhdr.test_id)

    partition = _resolve_partition_col(
        raw_pl, new_pl, nhdr, partition_col=partition_col
    )
    _require_columns(new_pl, {partition: partition}, "new_raw")

    r2_start = int(new_pl[partition].min())  # type: ignore[arg-type]
    r1_min = int(raw_pl[partition].min())  # type: ignore[arg-type]
    r1_max = int(raw_pl[partition].max())  # type: ignore[arg-type]

    if r2_start <= r1_min:
        raise ValueError(
            "new_raw starts at or before existing data; "
            "use Data.from_raw_frame for a full reload"
        )

    gap_append = r2_start > r1_max

    if gap_append:
        kept_raw = raw_pl
        kept_steps = steps_pl
    else:
        kept_raw = raw_pl.filter(pl.col(partition) < r2_start)
        kept_steps, from_data_point = _trim_steps_for_overlap(
            steps_pl,
            raw_pl.filter(pl.col(partition) >= r2_start),
            shdr,
            nhdr,
        )

    dp_max_kept = _max_column(kept_raw, nhdr.datapoint_num)
    new_dp_min = int(new_pl[nhdr.datapoint_num].min())  # type: ignore[arg-type]
    if new_dp_min <= dp_max_kept:
        new_pl = _offset_int_column(new_pl, nhdr.datapoint_num, dp_max_kept)

    combined_raw = pl.concat([kept_raw, new_pl], how="vertical")

    if gap_append:
        from_data_point = int(new_pl[nhdr.datapoint_num].min())  # type: ignore[arg-type]

    slice_data = Data()
    slice_data.raw = combined_raw
    new_steps = make_step_table(
        slice_data,
        schema=schema,
        from_data_point=from_data_point,
        **step_table_kwargs,
    )
    if not isinstance(new_steps, pl.DataFrame):
        new_steps = pl.from_pandas(new_steps)
    # When the kept steps carry ``c_rate`` (added post-step via add_step_c_rate),
    # append it to the rebuilt rows too so the vertical concat schemas match.
    if shdr.c_rate in kept_steps.columns:
        new_steps = new_steps.with_columns(_step_c_rate_expr(shdr, nom_cap_abs))

    combined_steps = pl.concat([kept_steps, new_steps], how="vertical")

    out = Data()
    out.raw = _restore_frame_type(combined_raw, data.raw)
    out.steps = _restore_frame_type(combined_steps, data.steps)

    summary_data = Data()
    summary_data.raw = out.raw
    summary_data.steps = out.steps
    make_summary(summary_data, schema=schema, test_mode=test_mode)
    out.summary = _restore_frame_type(_as_polars(summary_data.summary), data.summary)

    return out


def _resolve_partition_col(
    raw: pl.DataFrame,
    new_raw: pl.DataFrame,
    nhdr: config.RawCols,
    *,
    partition_col: str | None,
) -> str:
    if partition_col is not None:
        return partition_col
    if (
        nhdr.source_datapoint_num in raw.columns
        and nhdr.source_datapoint_num in new_raw.columns
    ):
        return nhdr.source_datapoint_num
    logger.warning(
        "source_datapoint_num missing; falling back to datapoint_num for update partition"
    )
    return nhdr.datapoint_num


def _require_columns(frame: pl.DataFrame, mapping: dict[str, str], label: str) -> None:
    missing = [name for name in mapping if name not in frame.columns]
    if missing:
        raise ValueError(f"{label} missing required column(s): {', '.join(missing)}")


def _require_single_test_id(frame: pl.DataFrame, test_id_col: str) -> None:
    if test_id_col not in frame.columns:
        return
    if frame[test_id_col].n_unique() > 1:
        raise ValueError(
            "update_data v1 supports a single test_id only (multi-test update is not implemented)"
        )


def _trim_steps_for_overlap(
    steps: pl.DataFrame,
    overlap_raw: pl.DataFrame,
    shdr: config.StepCols,
    nhdr: config.RawCols,
) -> tuple[pl.DataFrame, int]:
    """Drop the overlap step and all later steps; return kept steps and ``from_data_point``."""
    if overlap_raw.is_empty():
        return steps, int(steps[shdr.datapoint_num_first].min())  # type: ignore[arg-type]

    first_dp = int(
        overlap_raw.sort(nhdr.datapoint_num)[nhdr.datapoint_num][0]  # type: ignore[index]
    )
    steps_sorted = steps.sort(shdr.datapoint_num_first)
    overlap_idx = None
    for idx, row in enumerate(steps_sorted.iter_rows(named=True)):
        first = row[shdr.datapoint_num_first]
        last = row[shdr.datapoint_num_last]
        if first <= first_dp <= last:
            overlap_idx = idx
            from_data_point = int(first)
            break

    if overlap_idx is None:
        from_data_point = first_dp
        kept = steps_sorted.filter(pl.col(shdr.datapoint_num_last) < first_dp)
        return kept, from_data_point

    kept = steps_sorted.head(overlap_idx)
    return kept, from_data_point


def _copy_data(data: Data) -> Data:
    """Return a shallow copy of ``data`` with frame references duplicated."""
    out = Data()
    out.raw = _clone_frame(data.raw)
    out.steps = _clone_frame(data.steps)
    out.summary = _clone_frame(data.summary)
    if hasattr(data, "meta_test_dependent"):
        out.meta_test_dependent = copy(data.meta_test_dependent)
    return out


def _clone_frame(frame):
    if frame is None:
        return None
    if isinstance(frame, pl.DataFrame):
        return frame.clone()
    return frame.copy()


def _frame_is_empty(frame) -> bool:
    if isinstance(frame, pl.DataFrame):
        return frame.is_empty()
    return len(frame) == 0


def _as_polars(frame) -> pl.DataFrame:
    if isinstance(frame, pl.DataFrame):
        return frame.clone()
    return pl.from_pandas(frame)


def _restore_frame_type(frame: pl.DataFrame, prototype):
    import pandas as pd

    if isinstance(prototype, pd.DataFrame):
        return frame.to_pandas()
    return frame


def _max_column(frame: pl.DataFrame, col: str) -> int:
    if col not in frame.columns or frame.is_empty():
        return 0
    value = frame[col].max()
    if value is None:
        return 0
    return int(value)


def _offset_int_column(frame: pl.DataFrame, col: str, offset: int) -> pl.DataFrame:
    if offset == 0 or col not in frame.columns:
        return frame
    return frame.with_columns((pl.col(col) + pl.lit(offset)).alias(col))


def _distinct_test_ids(frame: pl.DataFrame, col: str) -> set[int]:
    if col not in frame.columns:
        return {0}
    return set(frame[col].unique().to_list())


def _resolve_test_id_collisions(
    right: pl.DataFrame,
    left: pl.DataFrame,
    test_id_col: str,
    *,
    allow_duplicate_test_id: bool,
) -> tuple[pl.DataFrame, dict[int, int]]:
    left_ids = _distinct_test_ids(left, test_id_col)
    right_ids = _distinct_test_ids(right, test_id_col)
    overlap = left_ids & right_ids
    if not overlap:
        return right, {}
    if not allow_duplicate_test_id:
        raise ValueError(
            f"duplicate test_id {sorted(overlap)} while merging "
            f"(pass allow_duplicate_test_id=True to reassign)"
        )

    used = set(left_ids)
    id_map: dict[int, int] = {}
    for tid in sorted(right_ids):
        if tid not in used:
            used.add(tid)
            continue
        next_id = 0
        while next_id in used:
            next_id += 1
        id_map[tid] = next_id
        used.add(next_id)

    return _remap_test_id(right, test_id_col, id_map), id_map


def _remap_test_id(
    frame: pl.DataFrame, test_id_col: str, id_map: dict[int, int]
) -> pl.DataFrame:
    if not id_map or test_id_col not in frame.columns:
        return frame
    expr = pl.col(test_id_col)
    for old_id, new_id in id_map.items():
        expr = (
            pl.when(pl.col(test_id_col) == old_id).then(pl.lit(new_id)).otherwise(expr)
        )
    return frame.with_columns(expr.alias(test_id_col))


def _carry_forward_cumulative_summary(
    left: pl.DataFrame,
    right: pl.DataFrame,
    chdr: config.CycleCols,
) -> pl.DataFrame:
    """Add last left cumulative summary values onto every right summary row."""
    if left.is_empty() or right.is_empty():
        return right

    sort_cols = [c for c in (chdr.test_id, chdr.cycle_num) if c in left.columns]
    last = left.sort(sort_cols).tail(1)

    exprs = []
    for attr in _CUMULATIVE_SUMMARY_ATTRS:
        col = getattr(chdr, attr)
        if col not in left.columns or col not in right.columns:
            continue
        base = last[col][0]
        if base is None:
            continue
        exprs.append((pl.col(col) + pl.lit(base)).alias(col))

    if not exprs:
        return right
    return right.with_columns(exprs)
