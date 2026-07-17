# Legacy bridge carries `test_id` (#136)

**Context.** `OldCellpyCellCore` used to drop `test_id` from outbound steps /
summary via fixed column orders + `NATIVE_ONLY_*` exceptions. That forced cellpy
#507 to re-stamp steps so campaign summaries could window per test.

**Decision.** Bridge `test_id` as an identity column on steps and summary when
present. Window `_add_legacy_summary_cruft` by `test_id`. `merge_data` /
`update_data` require native `config.Schema` (hard `TypeError` on `Headers*`).

**Alternatives.** Opt-in flag for summary `test_id` — rejected (additive is
enough). Full legacy-schema merge aliases — rejected (step/cycle attrs incomplete;
cellpy uses pandas merge).

**Refs.** cellpy #507 / #510 / #511; release after this → re-pin cellpy.
