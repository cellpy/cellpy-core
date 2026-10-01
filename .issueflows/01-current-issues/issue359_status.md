# Status — Issue #359: cycle counter for discharge-first full cells

Branch: `cursor/359-discharge-first-cycles-061c` (cloud-agent naming; local number
provisional, mirrors jepegit/cellpy#359 until the cellpy-core mirror issue exists).
PR: https://github.com/cellpy/cellpy-core/pull/153 (#153, draft)

- [ ] Done

## What's done

- 2026-10-01: issue captured, plan drafted and accepted (recommendations taken:
  `renumber_cycles`, single `opening: StepDirection` knob, keep source numbering base,
  no `CellpyCellCore` wrapper).
- `config.StepDirection` enum (CHARGE / DISCHARGE).
- `summarizers.renumber_cycles` + shared `_reaccumulate_cumulative` /
  `_present_cumulative_cols` helpers (extracted from `normalize_capacity_granularity`);
  exported from `cellpycore`.
- `tests/test_renumber_cycles.py` (14 tests: three patterns, rest/CV attachment, anode
  mirror, 0-based numbering, energy columns, multi `test_id`, pandas round-trip, summary
  drop, error paths, harmonized fixture no-op + recount). Full suite 303 passed; ruff clean.
- Docs: `standalone-use.md` section, `harmonized-raw.md` open question resolved, design
  note `04-designs-and-guides/cycle-renumbering.md`.

## Remaining work

- Create the `cellpy/cellpy-core` mirror issue (token here is read-only) and rename the
  `issue359_*` group to the real number.
- `/iflow-close`: changelog entry, `uv version --bump minor` (0.2.6 -> 0.3.0), final push.
- cellpy side (separate repo, later): `cycle_mode` variant wiring + release note.
