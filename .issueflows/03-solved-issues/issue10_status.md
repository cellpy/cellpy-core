# Status — issue #10: Make sure column headers make sense

- [x] Done

Scope was **docs-only** (confirmed in the plan). All planned doc work is complete.

## What landed

- **Durable design doc** `.issueflows/04-designs-and-guides/column-headers-review.md` — full gap analysis (findings A–F), the decisions taken, the config-vs-doc drift recorded as the follow-up's starting point, and recommended follow-up issues.
- **Single source of truth for harmonized raw**: `docs/harmonized_raw_definition.md` promoted to authoritative (added Conventions: `potential`, seconds, `step_mode`, no `channel_status`; resolved the `channel_status` follow-up). Deleted the stale duplicate `docs/data_format_specifications/harmonized_raw.md`.
- **`docs/data_format_specifications/cycle_table.md`**: normalized all rows to the 5-column header (added missing sample-data cells for the epoch/test-time/duration rows, removed the extra cell in `test_net_energy`), fixed unit typos (`percetange (V)` → `Percentage (%)`, `Amphere-hour` → `Ampere-hour`, energy `Watt-hour (Ah)` → `(Wh)` in two rows), filled the empty `voltage_efficiency` description.
- **`docs/data_format_specifications/step_table.md`**: header was 4 columns while rows carried 5 → added the Description column; wrote a Purpose; renamed `power_capacity_*` → `power_*` with a note that `config.py` still lags.
- **`docs/data-object-definition.md`**: `voltage` → `potential`; `test_time`/`unix_time` units changed from millisecond → second.

## Decisions (confirmed with maintainer)
potential + seconds · drop `channel_status` / use `step_mode` · delete old harmonized_raw doc · defer all `config.py` changes · document SPEED-30 (versioning/units) and strategy gaps (UUID, BattINFO) only.

## Deferred to follow-up issues (captured in the design doc)
1. Align `config.py` `RawCols`/`StepCols`/`CycleCols` with the authoritative docs (+ update `_helpers.py`).
2. Adopt a unit+dtype-carrying, versioned header object (SPEED-30, `SuperDuperCols` prototype); migrate engine off legacy `*_txt`.
3. BattINFO/EMMO column mapping + UUID/identity fields (Stage-0 schema work).

## Next
Ready to ship — run `/issue-close`.
