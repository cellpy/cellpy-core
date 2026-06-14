#!/usr/bin/env python
"""Regenerate cellpy-core test-data fixtures (parquet) from legacy cellpy test files.

cellpy-core is the *core* engine and must not depend on instrument loaders (Arbin
ODBC, Maccor parsers, ...). So real cycling data is vendored as small parquet
snapshots of ``data.raw`` (already in the legacy ``HeadersNormal`` column naming)
plus a snapshot of the current engine's step table, which serves as the
regression oracle for the pandas->polars rewrite (issue #13).

The work splits into two independent stages, auto-detected by which libraries
import successfully:

  Stage A (raw export) - requires ``cellpy`` (+ an Arbin ODBC driver for the
      ``.res`` file). Run from the *cellpy* repo's environment::

          cd ../cellpy && uv run python ../cellpy-core/dev/regenerate_test_data.py

  Stage B (engine snapshot) - requires the *cellpy-core* working copy. Run from
      cellpy-core's environment::

          uv run python dev/regenerate_test_data.py

Outputs land in ``cellpy-core/tests/data/``. Set ``CELLPY_REPO`` to point at the
cellpy checkout if it is not the sibling ``../cellpy``.

Provenance: source files come from the cellpy repo (battery data from IFE,
Norway; the repo is MIT-licensed). See ``tests/data/README.md``.
"""

from __future__ import annotations

import os
from pathlib import Path

CORE_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = CORE_ROOT / "tests" / "data"
CELLPY_REPO = Path(os.environ.get("CELLPY_REPO", CORE_ROOT.parent / "cellpy"))

# Golden numbers for the canonical Arbin .res, mirrored from cellpy's own test
# suite (tests/test_cell_readers.py) so cellpy-core can assert cross-library
# parity without re-running the instrument loader.
ARBIN_GOLDEN = {"n_steps": 103, "n_cycles": 18, "summary_cyc1_data_point": 1457}

# (fixture name, path within the cellpy repo, cellpy.get kwargs). Empty kwargs
# means "use cellreader.from_raw" (avoids the auto-summary seam).
#
# arbin_cc      - the canonical 18-cycle Arbin .res (needs an ODBC driver); the
#                 cross-library golden oracle (103 steps / 18 cycles).
# arbin_small   - a tiny 47-row Arbin SQL-H5 export (1 cycle, 3 steps, real
#                 discharge current); no ODBC needed, ideal as a fast fixture.
RAW_SOURCES = [
    ("arbin_cc", "testdata/data/20160805_test001_45_cc_01.res", {}),
    (
        "arbin_small",
        "testdata/data/20200624_test001_cc_01.h5",
        {"instrument": "arbin_sql_h5"},
    ),
]


def stage_a_export_raw() -> bool:
    """Load each source with cellpy and write ``<name>_raw.parquet``."""
    try:
        import cellpy
        from cellpy import cellreader
    except Exception as exc:  # noqa: BLE001 - diagnostic only
        print(f"[stage A] cellpy not importable ({exc}); skipping raw export.")
        return False

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for name, rel, kwargs in RAW_SOURCES:
        src = CELLPY_REPO / rel
        if not src.is_file():
            print(f"[stage A] missing {src}; skip {name}")
            continue
        try:
            if kwargs:
                cell = cellpy.get(str(src), auto_summary=False, testing=True, **kwargs)
            else:
                cell = cellreader.CellpyCell()
                cell.from_raw(str(src))
            raw = cell.data.raw.reset_index(drop=True)
            out = DATA_DIR / f"{name}_raw.parquet"
            raw.to_parquet(out)
            print(f"[stage A] wrote {out.name}  ({len(raw)} rows, {raw.shape[1]} cols)")
        except Exception as exc:  # noqa: BLE001 - keep going for other sources
            print(f"[stage A] FAILED {name}: {type(exc).__name__}: {exc}")
    return True


def stage_b_engine_snapshot() -> bool:
    """Run the current cellpy-core engine on the raw parquet and snapshot steps."""
    try:
        import pandas as pd
        from cellpycore import summarizers
        from cellpycore.cell_core import Data, OldCellpyCellCore
        from cellpycore.config import Schema
        from cellpycore.legacy import HeadersNormal, HeadersStepTable, HeadersSummary
    except Exception as exc:  # noqa: BLE001 - diagnostic only
        print(f"[stage B] cellpycore not importable ({exc}); skipping snapshot.")
        return False

    if not hasattr(OldCellpyCellCore, "make_core_step_table"):
        print(
            "[stage B] the importable cellpycore predates make_core_step_table; "
            "run this from the cellpy-core working copy."
        )
        return False

    raw_path = DATA_DIR / "arbin_cc_raw.parquet"
    if not raw_path.is_file():
        print(f"[stage B] {raw_path.name} not found; run stage A first.")
        return False

    raw = pd.read_parquet(raw_path)
    schema = Schema(HeadersNormal(), HeadersSummary(), HeadersStepTable())
    data = Data()
    data.raw = raw
    result = summarizers.make_step_table(data, schema=schema, nom_cap=1.0)
    steps = result.steps.reset_index(drop=True)
    out = DATA_DIR / "arbin_cc_steps_expected.parquet"
    steps.to_parquet(out)

    n_steps = len(steps)
    max_cycle = int(steps[schema.step.cycle].max())
    print(f"[stage B] wrote {out.name}  ({n_steps} steps)")
    print(
        f"[stage B] golden check: n_steps={n_steps} (expect {ARBIN_GOLDEN['n_steps']}), "
        f"max_cycle={max_cycle} (expect {ARBIN_GOLDEN['n_cycles']})"
    )
    if n_steps != ARBIN_GOLDEN["n_steps"] or max_cycle != ARBIN_GOLDEN["n_cycles"]:
        print("[stage B] WARNING: engine output does not match the cellpy goldens!")
    return True


if __name__ == "__main__":
    ran_a = stage_a_export_raw()
    ran_b = stage_b_engine_snapshot()
    if not (ran_a or ran_b):
        raise SystemExit(
            "Nothing ran: need either cellpy (stage A) or the cellpy-core working "
            "copy (stage B) importable."
        )
