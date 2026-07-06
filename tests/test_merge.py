"""Tests for ``cellpycore.merge`` (merge + update)."""

import polars as pl
import pytest

from cellpycore import CellpyCellCore, Data, merge_data, summarizers, update_data
from cellpycore.config import CycleCols, RawCols, Schema, StepCols


def _schema() -> Schema:
    return Schema(raw=RawCols(), cycle=CycleCols(), step=StepCols())


def _single_test_raw(
    nhdr: RawCols,
    *,
    test_id: int = 0,
    cycle_start: int = 1,
    n_cycles: int = 2,
    dp_start: int = 0,
    scale: float = 1.0,
) -> pl.DataFrame:
    records = []
    dp = dp_start
    for cyc in range(cycle_start, cycle_start + n_cycles):
        for k in range(5):
            records.append(
                {
                    nhdr.test_id: test_id,
                    nhdr.datapoint_num: dp,
                    nhdr.test_time: float(dp),
                    nhdr.step_time: float(k),
                    nhdr.step_num: 1,
                    nhdr.cycle_num: cyc,
                    nhdr.current: 1.0,
                    nhdr.potential: 3.5 + 0.01 * k,
                    nhdr.cumulative_charge_capacity: scale * 0.1 * (k + 1),
                    nhdr.cumulative_discharge_capacity: 0.0,
                    nhdr.internal_resistance: 0.0,
                }
            )
            dp += 1
        for k in range(5):
            records.append(
                {
                    nhdr.test_id: test_id,
                    nhdr.datapoint_num: dp,
                    nhdr.test_time: float(dp),
                    nhdr.step_time: float(k),
                    nhdr.step_num: 2,
                    nhdr.cycle_num: cyc,
                    nhdr.current: -1.0,
                    nhdr.potential: 3.9 - 0.01 * k,
                    nhdr.cumulative_charge_capacity: scale * 0.5,
                    nhdr.cumulative_discharge_capacity: scale * 0.08 * (k + 1),
                    nhdr.internal_resistance: 0.0,
                }
            )
            dp += 1
    frame = pl.DataFrame(records)
    if nhdr.source_datapoint_num not in frame.columns:
        frame = frame.with_columns(
            pl.col(nhdr.datapoint_num).alias(nhdr.source_datapoint_num)
        )
    return frame


def _processed_data(
    nhdr: RawCols,
    schema: Schema,
    *,
    test_id: int = 0,
    cycle_start: int = 1,
    dp_start: int = 0,
    scale: float = 1.0,
) -> Data:
    data = Data()
    data.raw = _single_test_raw(
        nhdr,
        test_id=test_id,
        cycle_start=cycle_start,
        dp_start=dp_start,
        scale=scale,
    )
    summarizers.make_step_table(data, schema=schema)
    summarizers.add_step_c_rate(data, schema, nom_cap=1.0)
    summarizers.make_summary(data, schema=schema)
    return data


def test_merge_offsets_datapoint_num():
    nhdr = RawCols()
    schema = _schema()
    left = _processed_data(nhdr, schema, test_id=0, dp_start=0)
    right = _processed_data(nhdr, schema, test_id=1, dp_start=0)

    merged = merge_data(left, right, schema=schema)
    left_max = left.raw[nhdr.datapoint_num].max()
    assert left_max == 19
    assert merged.raw.height == 40
    # Issue spec: n2,i += n1,last — first right row shares the boundary index.
    right_dps = merged.raw.filter(pl.col(nhdr.test_id) == 1)[
        nhdr.datapoint_num
    ].to_list()
    assert right_dps[0] == left_max
    assert right_dps[-1] == left_max + 19


def test_merge_renumber_cycles_default():
    nhdr = RawCols()
    schema = _schema()
    left = _processed_data(nhdr, schema, test_id=0)
    right = _processed_data(nhdr, schema, test_id=1)

    merged = merge_data(left, right, schema=schema)
    right_cycles = (
        merged.raw.filter(pl.col(nhdr.test_id) == 1)[nhdr.cycle_num].unique().sort()
    )
    assert right_cycles.to_list() == [3, 4]


def test_merge_renumber_cycles_false_keeps_overlapping_cycles():
    nhdr = RawCols()
    schema = _schema()
    shdr = schema.step
    left = _processed_data(nhdr, schema, test_id=0)
    right = _processed_data(nhdr, schema, test_id=1)

    merged = merge_data(left, right, schema=schema, renumber_cycles=False)
    assert merged.steps.height == 8
    assert set(merged.steps[shdr.test_id].to_list()) == {0, 1}
    key = merged.steps.select(shdr.test_id, shdr.cycle_num, shdr.step_num)
    assert key.n_unique() == 8


def test_merge_duplicate_test_id_raises():
    nhdr = RawCols()
    schema = _schema()
    left = _processed_data(nhdr, schema, test_id=0)
    right = _processed_data(nhdr, schema, test_id=0)

    with pytest.raises(ValueError, match="duplicate test_id"):
        merge_data(left, right, schema=schema)


def test_merge_allow_duplicate_test_id_renumbers():
    nhdr = RawCols()
    schema = _schema()
    left = _processed_data(nhdr, schema, test_id=0)
    right = _processed_data(nhdr, schema, test_id=0)

    merged = merge_data(left, right, schema=schema, allow_duplicate_test_id=True)
    assert set(merged.raw[nhdr.test_id].unique().to_list()) == {0, 1}


def test_merge_empty_left_returns_copy_of_right():
    nhdr = RawCols()
    schema = _schema()
    left = Data()
    left.raw = pl.DataFrame(schema={c: pl.Int64 for c in (nhdr.datapoint_num,)})
    right = _processed_data(nhdr, schema, test_id=0)

    merged = merge_data(left, right, schema=schema)
    assert merged.raw.height == right.raw.height
    assert merged.steps is not None


def test_merge_empty_right_returns_copy_of_left():
    nhdr = RawCols()
    schema = _schema()
    left = _processed_data(nhdr, schema, test_id=0)
    right = Data()
    right.raw = pl.DataFrame(schema={c: pl.Int64 for c in (nhdr.datapoint_num,)})

    merged = merge_data(left, right, schema=schema)
    assert merged.raw.height == left.raw.height


def test_merge_does_not_mutate_inputs():
    nhdr = RawCols()
    schema = _schema()
    left = _processed_data(nhdr, schema, test_id=0)
    right = _processed_data(nhdr, schema, test_id=1)
    left_dp_max = left.raw[nhdr.datapoint_num].max()
    right_dp_max = right.raw[nhdr.datapoint_num].max()

    merge_data(left, right, schema=schema)

    assert left.raw[nhdr.datapoint_num].max() == left_dp_max
    assert right.raw[nhdr.datapoint_num].max() == right_dp_max


def test_merge_carries_cumulative_summary_forward():
    nhdr = RawCols()
    schema = _schema()
    chdr = schema.cycle
    left = _processed_data(nhdr, schema, test_id=0, scale=1.0)
    right = _processed_data(nhdr, schema, test_id=1, scale=2.0)

    merged = merge_data(left, right, schema=schema)
    s = merged.summary.sort([chdr.test_id, chdr.cycle_num])

    left_last_cum = left.summary.sort(chdr.cycle_num)[
        chdr.test_cumulated_charge_capacity
    ][-1]
    right_first_cum = s.filter(pl.col(chdr.test_id) == 1)[
        chdr.test_cumulated_charge_capacity
    ][0]
    right_first_cc = s.filter(pl.col(chdr.test_id) == 1)[chdr.charge_capacity][0]

    assert right_first_cum == pytest.approx(left_last_cum + right_first_cc)


def test_merge_core_data_on_cell():
    nhdr = RawCols()
    schema = _schema()
    cell = CellpyCellCore(initialize=False)
    left = _processed_data(nhdr, schema, test_id=0)
    right = _processed_data(nhdr, schema, test_id=1)

    merged = cell.merge_core_data(left, right)
    assert merged.raw.height == 40


def test_merge_requires_raw_on_both_sides():
    schema = _schema()
    with pytest.raises(ValueError, match="requires both"):
        merge_data(Data(), Data(), schema=schema)


def _process_raw(raw: pl.DataFrame, schema: Schema) -> Data:
    data = Data()
    data.raw = raw
    summarizers.make_step_table(data, schema=schema)
    summarizers.add_step_c_rate(data, schema, nom_cap=1.0)
    summarizers.make_summary(data, schema=schema)
    return data


def _steps_oracle_equal(got, expected, shdr: StepCols) -> None:
    sort_cols = [shdr.cycle_num, shdr.step_num, shdr.datapoint_num_first]
    g = got.sort(sort_cols)
    e = expected.sort(sort_cols)
    assert g.height == e.height
    assert g.select(sort_cols).equals(e.select(sort_cols))


def _summary_oracle_equal(got, expected, chdr: CycleCols) -> None:
    sort_cols = [chdr.cycle_num]
    g = got.sort(sort_cols)
    e = expected.sort(sort_cols)
    assert g.height == e.height
    for col in (
        chdr.charge_capacity,
        chdr.discharge_capacity,
        chdr.coulombic_efficiency,
    ):
        assert g[col].to_list() == pytest.approx(
            e[col].to_list(), rel=1e-9, nan_ok=True
        )


def test_update_overlap_matches_full_recompute_oracle():
    nhdr = RawCols()
    schema = _schema()
    shdr, chdr = schema.step, schema.cycle

    full_raw = _single_test_raw(nhdr, n_cycles=2)
    oracle = _process_raw(full_raw, schema)

    base_raw = full_raw.filter(pl.col(nhdr.source_datapoint_num) <= 9)
    base = _process_raw(base_raw, schema)
    extension = full_raw.filter(pl.col(nhdr.source_datapoint_num) >= 9)

    updated = update_data(base, extension, schema=schema)

    _steps_oracle_equal(updated.steps, oracle.steps, shdr)
    _summary_oracle_equal(updated.summary, oracle.summary, chdr)


def test_update_gap_append_matches_full_recompute_oracle():
    nhdr = RawCols()
    schema = _schema()
    shdr, chdr = schema.step, schema.cycle

    full_raw = _single_test_raw(nhdr, n_cycles=3)
    oracle = _process_raw(full_raw, schema)

    base_raw = full_raw.filter(pl.col(nhdr.source_datapoint_num) < 20)
    base = _process_raw(base_raw, schema)
    extension = full_raw.filter(pl.col(nhdr.source_datapoint_num) >= 20)

    updated = update_data(base, extension, schema=schema)

    _steps_oracle_equal(updated.steps, oracle.steps, shdr)
    _summary_oracle_equal(updated.summary, oracle.summary, chdr)


def test_update_full_replace_raises():
    nhdr = RawCols()
    schema = _schema()
    base = _processed_data(nhdr, schema)
    new_raw = _single_test_raw(nhdr, n_cycles=1)

    with pytest.raises(ValueError, match="full reload"):
        update_data(base, new_raw, schema=schema)


def test_update_does_not_mutate_input():
    nhdr = RawCols()
    schema = _schema()
    full_raw = _single_test_raw(nhdr, n_cycles=2)
    base_raw = full_raw.filter(pl.col(nhdr.source_datapoint_num) < 10)
    base = _process_raw(base_raw, schema)
    extension = full_raw.filter(pl.col(nhdr.source_datapoint_num) >= 9)
    raw_before = base.raw.clone()
    steps_before = base.steps.clone()

    update_data(base, extension, schema=schema)

    assert base.raw.equals(raw_before)
    assert base.steps.equals(steps_before)


def test_update_requires_processed_data():
    nhdr = RawCols()
    schema = _schema()
    data = Data()
    data.raw = _single_test_raw(nhdr, n_cycles=1)
    with pytest.raises(
        ValueError, match="requires data.raw, data.steps, and data.summary"
    ):
        update_data(data, _single_test_raw(nhdr, n_cycles=1), schema=schema)


def test_update_core_data_refresh_derived():
    nhdr = RawCols()
    schema = _schema()
    cell = CellpyCellCore(initialize=False)
    full_raw = _single_test_raw(nhdr, n_cycles=2)
    base = _process_raw(full_raw.filter(pl.col(nhdr.source_datapoint_num) < 10), schema)
    extension = full_raw.filter(pl.col(nhdr.source_datapoint_num) >= 9)

    updated = cell.update_core_data(base, extension)
    chdr = schema.cycle
    assert chdr.charge_c_rate in updated.summary.columns
    assert chdr.ir_charge in updated.summary.columns
