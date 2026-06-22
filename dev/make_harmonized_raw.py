#!/usr/bin/env python
"""Convert a legacy-named raw parquet into a harmonized raw parquet fixture.

cellpy-core consumes the *harmonized raw* format whose authoritative spec is
``docs/data_format_specifications/harmonized_raw.md`` and whose column names are
defined by ``cellpycore.config.RawCols``. The vendored real-data fixture
``tests/data/arbin_cc_raw.parquet`` is still in the legacy cellpy ``HeadersNormal``
naming (``data_point``, ``voltage``, ``charge_capacity``, ...). This script
renames it into the harmonized schema so we have a real-data fixture in the
native naming.

The harmonized header names are read **from ``RawCols`` at runtime**, so if the
schema is ever changed (e.g. a column is renamed), re-running this script
regenerates an up-to-date fixture with no edits here::

    uv run python dev/make_harmonized_raw.py

The only maintenance point is ``LEGACY_TO_RAWCOLS`` below: the map from legacy
source columns to ``RawCols`` *attribute names*. It is pure ``polars`` and never
imports ``cellpy`` or any instrument loader (cellpy-core stays loader-free).

Capacity convention: legacy Arbin ``charge_capacity`` / ``discharge_capacity``
(and the energy columns) are already cumulative-per-cycle-per-direction (verified
on real Arbin data in issue #13), which is exactly what the harmonized
``cumulative_*`` columns require, so these are straight renames with no
recomputation. See the spec's *Capacity convention* section.

Provenance: the source fixture comes from the cellpy repo (IFE, Norway; MIT). See
``tests/data/README.md``.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from cellpycore.config import RawCols

CORE_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = CORE_ROOT / "tests" / "data"
SOURCE = DATA_DIR / "arbin_cc_raw.parquet"
OUTPUT = DATA_DIR / "arbin_cc_harmonized_raw.parquet"

# Constant value written into ``source_type`` for this Arbin fixture.
SOURCE_TYPE = "arbin"

# Map legacy ``HeadersNormal`` columns -> the ``RawCols`` *attribute name(s)* they
# feed. A legacy column may feed more than one harmonized column (e.g. the data
# point is both the corrected ``datapoint_num`` and the original
# ``source_datapoint_num``). The actual output header is looked up on ``RawCols``
# at runtime, so renaming a column in ``RawCols`` is enough to track it here.
LEGACY_TO_RAWCOLS: dict[str, tuple[str, ...]] = {
    "test_id": ("test_id",),
    "data_point": ("datapoint_num", "source_datapoint_num"),
    "test_time": ("test_time",),
    "step_time": ("step_time",),
    "step_index": ("step_num", "source_step_num"),
    "cycle_index": ("cycle_num",),
    "current": ("current",),
    "voltage": ("potential",),
    "charge_capacity": ("cumulative_charge_capacity",),
    "discharge_capacity": ("cumulative_discharge_capacity",),
    "charge_energy": ("cumulative_charge_energy",),
    "discharge_energy": ("cumulative_discharge_energy",),
    "internal_resistance": ("internal_resistance",),
}

# Legacy columns with no harmonized equivalent (cellpy-internal flags / EIS
# channels). Listed explicitly so the drop is intentional and visible.
DROPPED_LEGACY = ("is_fc_data", "dv_dt", "ac_impedance", "aci_phase_angle")


def build_harmonized(raw: pl.DataFrame, cols: RawCols) -> pl.DataFrame:
    """Build the harmonized raw frame from a legacy-named frame.

    Args:
        raw (pl.DataFrame): The legacy ``HeadersNormal``-named raw frame.
        cols (RawCols): The harmonized column-header definitions; output column
            names are taken from this object so the result tracks the schema.

    Returns:
        pl.DataFrame: A frame whose columns are the full ``RawCols`` set, in
        ``RawCols`` attribute order. Mapped columns carry the renamed source
        data; unmapped columns are emitted as nulls; ``mask`` and ``source_type``
        are generated.
    """
    exprs: dict[str, pl.Expr] = {}

    for legacy, attrs in LEGACY_TO_RAWCOLS.items():
        if legacy not in raw.columns:
            raise KeyError(
                f"expected legacy column {legacy!r} not found in source "
                f"(have: {raw.columns})"
            )
        for attr in attrs:
            exprs[getattr(cols, attr)] = pl.col(legacy)

    # date_time (naive Datetime) -> epoch_time_utc (float seconds). The naive
    # tester timestamp is treated as UTC; documented in the spec.
    exprs[cols.epoch_time_utc] = (pl.col("date_time").dt.epoch("ms") / 1000.0).cast(
        pl.Float64
    )

    # Generated / constant columns.
    exprs[cols.mask] = pl.lit(True)
    exprs[cols.source_type] = pl.lit(SOURCE_TYPE)

    out = raw.select(**exprs)

    # Emit every remaining RawCols column as null so the fixture is a complete
    # harmonized-schema example, ordered to match the spec table.
    ordered = [getattr(cols, name) for name in vars(RawCols) if not name.startswith("_")]
    missing = [name for name in ordered if name not in out.columns]
    out = out.with_columns([pl.lit(None).alias(name) for name in missing])
    return out.select(ordered)


def main() -> None:
    if not SOURCE.is_file():
        raise SystemExit(f"source fixture not found: {SOURCE}")

    cols = RawCols()
    raw = pl.read_parquet(SOURCE)

    present_drops = [c for c in DROPPED_LEGACY if c in raw.columns]
    print(f"read {SOURCE.name}: {raw.height} rows, {raw.width} cols")
    print(f"dropping legacy-only columns: {present_drops or '(none)'}")

    out = build_harmonized(raw, cols)
    out.write_parquet(OUTPUT)
    print(f"wrote {OUTPUT.name}: {out.height} rows, {out.width} cols")
    print(f"columns: {out.columns}")


if __name__ == "__main__":
    main()
