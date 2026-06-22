"""Pluggable per-cycle summary extractors.

A *summary extractor* is a callable object that derives one or more per-cycle
columns from the engine frames (``raw`` / ``steps`` / ``summary``) and returns
them as a small polars frame keyed by the cycle-number column. The summary
helpers in :mod:`cellpycore.summarizers` accept an extractor so the *what to
extract* policy can be swapped without touching the engine plumbing (the join
onto the summary and null handling stay in the helper).

The first user is :func:`cellpycore.summarizers.ir_to_summary`, whose default
:class:`LastIRExtractor` implements the corrected internal-resistance semantics
(issue #23): per cycle, the internal resistance of the last datapoint of the
cycle's last charge / discharge step. Developers building on cellpy-core can
subclass :class:`SummaryExtractor` to plug in their own logic (for example an
extractor keyed off the dedicated ``"ir"`` step type) and pass it via the
``ir_extractor`` keyword argument.

This abstraction is intentionally minimal: only the IR extractor is provided
today. Other per-cycle helpers (C-rate, end-voltage) could adopt it later.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import polars as pl

if TYPE_CHECKING:
    from cellpycore.config import Schema


class SummaryExtractor:
    """Base class for callable per-cycle summary extractors.

    Subclasses implement :meth:`__call__`, deriving per-cycle values from the
    (polars) engine frames and returning a polars frame keyed by the summary
    cycle-number column (``schema.cycle.cycle_num``) carrying one or more summary
    columns. The caller left-joins the result onto the summary, so cycles the
    extractor omits become missing (the helper decides how to fill them).
    """

    def __call__(
        self,
        *,
        raw: "pl.DataFrame",
        steps: "pl.DataFrame",
        summary: "pl.DataFrame",
        schema: "Schema",
    ) -> "pl.DataFrame":
        """Return a per-cycle frame keyed by ``schema.cycle.cycle_num``.

        Args:
            raw: The raw datapoint frame (polars, native schema).
            steps: The per-step table (polars, native schema).
            summary: The per-cycle summary built so far (polars, native schema).
            schema: The column-header schema in use.

        Returns:
            A polars frame with a ``schema.cycle.cycle_num`` column plus one or
            more derived per-cycle columns.

        Raises:
            NotImplementedError: Always, unless overridden by a subclass.
        """
        raise NotImplementedError


class LastIRExtractor(SummaryExtractor):
    """Default internal-resistance extractor (issue #23).

    For each cycle it reads the ``internal_resistance`` of the **last raw
    datapoint** of the cycle's **last charge step** (``ir_charge``) and of the
    cycle's **last discharge step** (``ir_discharge``). The value is taken
    literally (no skipping of zero/null readings). Cycles without a charge
    (resp. discharge) step are simply absent from the returned frame, so the
    caller fills them with ``NaN``.

    This fixes the legacy off-by-one cycle attribution (the old helper read the
    first datapoint of the *first* charge/discharge step) and makes the
    multiple-step case explicit (the *last* step wins instead of a silent
    ``[0]``).
    """

    def __call__(
        self,
        *,
        raw: "pl.DataFrame",
        steps: "pl.DataFrame",
        summary: "pl.DataFrame",
        schema: "Schema",
    ) -> "pl.DataFrame":
        headers_raw = schema.raw
        headers_steps = schema.step
        headers_cycle = schema.cycle

        # internal resistance of the last raw datapoint of each (cycle, step).
        # maintain_order (no sort) mirrors the raw frame's natural acquisition
        # order, so ``last`` is the chronologically last reading of the step.
        ir_per_step = raw.group_by(
            [headers_raw.cycle_num, headers_raw.step_num], maintain_order=True
        ).agg(pl.col(headers_raw.internal_resistance).last().alias("__ir"))

        def _side(step_type: str, out_name: str) -> "pl.DataFrame":
            last_step = (
                steps.filter(pl.col(headers_steps.step_type) == step_type)
                .group_by(headers_steps.cycle_num, maintain_order=True)
                .agg(pl.col(headers_steps.step_num).last().alias("__step"))
            )
            return last_step.join(
                ir_per_step,
                left_on=[headers_steps.cycle_num, "__step"],
                right_on=[headers_raw.cycle_num, headers_raw.step_num],
                how="left",
            ).select(
                pl.col(headers_steps.cycle_num).alias(headers_cycle.cycle_num),
                pl.col("__ir").alias(out_name),
            )

        ir_charge = _side("charge", headers_cycle.ir_charge)
        ir_discharge = _side("discharge", headers_cycle.ir_discharge)
        return ir_charge.join(
            ir_discharge, on=headers_cycle.cycle_num, how="full", coalesce=True
        )
