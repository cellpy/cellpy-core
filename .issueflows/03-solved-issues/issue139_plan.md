# Plan — issue #139 (legacy raw energy mapping)

## Goal

Bridge legacy raw energy columns through the authoritative header map so
`charge_energy` / `discharge_energy` rename to
`cumulative_charge_energy` / `cumulative_discharge_energy` (same pattern as
capacity), enabling `to_native()` / `harmonize()` consumers to find them under
the native schema names.

## Constraints

- Keep change to `mapping.py` + its existing totality / spot-check tests.
  No loader work, no engine changes, no cycle/step energy columns.
- Totality discipline (#116): every legacy attr / column value is either mapped
  or in an exception set — never both, never neither.
- Value-level pairs (`RAW_PAIRS`) drive DataFrame renames; attribute table
  (`LEGACY_ATTR_TO_SCHEMA`) must stay in sync (`test_legacy_attr_matches_value_mapping`).
- Out of scope (issue itself): `datetime_txt → epoch_time_utc` and the other
  unmapped native-only list — track separately if wanted.
- Cross-repo: core PR → core release → cellpy re-pin → cellpy consumes
  (cellpy #560). This issue is the core PR only.
- Spec already states the reset convention (see Approach); record that as the
  answer to the issue's ask — do not invent a new convention here.

### Prior art

- `RAW_PAIRS` / `LEGACY_ATTR_TO_SCHEMA["raw"]` / exception sets —
  [`src/cellpycore/legacy/mapping.py`](src/cellpycore/legacy/mapping.py).
  Mirror capacity entries (`charge_capacity_txt` →
  `cumulative_charge_capacity`).
- Totality + spot-check tests —
  [`tests/test_header_mapping.py`](tests/test_header_mapping.py)
  (`test_raw_*_totality`, `test_known_translations`,
  `test_legacy_attr_*`).
- Spec Capacity convention —
  [`docs/specifications/harmonized-raw.md`](docs/specifications/harmonized-raw.md)
  (§ Capacity convention): energy columns share cycle-cumulative / per-direction
  semantics with capacity.
- Issue #42 (solved): engine reset-granularity normalizer already covers
  `cumulative_*_energy` when source granularity differs.
- Fixture helper already assumes the rename —
  [`dev/make_harmonized_raw.py`](dev/make_harmonized_raw.py)
  (`charge_energy` → `cumulative_charge_energy`).
- Issue #116 (solved): attribute-table + `LEGACY_ATTR_UNMAPPED` discipline.
- Toolbox: none relevant.
- Graph: community 87 (`mapping.py`) / 82 (legacy headers) — no extra modules.

**Note vs architecture-plan D3:** `cellpy2-native-headers-migration-plan.md`
still lists raw energy as passthrough ("not synthesized — different reset
semantics"). That is **stale relative to the harmonized-raw Capacity
convention + #42**. Mapping is a rename of already-supplied columns, not
synthesis. After Accept, add a one-line correction in
`.issueflows/04-designs-and-guides/` (or a comment in the plan status) so
future agents do not re-block the bridge; updating the architecture-plan
doc can be a tiny follow-up outside this PR if desired.

## Approach

1. **Confirm convention (recorded decision):** energy matches capacity —
   cumulative per cycle, per direction, reset at cycle boundary
   (`harmonized-raw.md` Capacity convention). Cellpy loaders normalize the
   same way; if a source is step-cumulative, #42's normalizer is the path,
   not leaving the columns unmapped.

2. **Value map** — add to `RAW_PAIRS` (next to the capacity pairs):
   ```python
   ("cumulative_charge_energy", "charge_energy"),
   ("cumulative_discharge_energy", "discharge_energy"),
   ```

3. **Exception sets** — remove from the raw exceptions so totality stays
   exact:
   - `LEGACY_ONLY_RAW`: drop `"charge_energy"`, `"discharge_energy"`
   - `NATIVE_ONLY_RAW`: drop `"cumulative_charge_energy"`,
     `"cumulative_discharge_energy"`

4. **Attribute map** — add to `LEGACY_ATTR_TO_SCHEMA["raw"]`:
   ```python
   "charge_energy_txt": "cumulative_charge_energy",
   "discharge_energy_txt": "cumulative_discharge_energy",
   ```
   and remove those attrs from `LEGACY_ATTR_UNMAPPED["raw"]`.

5. **Do not touch** step/cycle maps (`NATIVE_ONLY_STEP` still has
   `charge_energy` / `discharge_energy` as *step-table* base signals — different
   columns).

6. **Behavior:** `legacy_to_native_raw()` / bridge renames will translate
   energy instead of leaving it as a passthrough extra. That is the intended
   fix for native-schema lookup and `harmonize()`.

## Files to touch

| Path | Change |
|------|--------|
| `src/cellpycore/legacy/mapping.py` | `RAW_PAIRS` + attr table + raw exception sets |
| `tests/test_header_mapping.py` | Extend `test_known_translations` expected dict with the two energy renames |
| `.issueflows/04-designs-and-guides/` (short note) | Optional: "raw energy bridged like capacity (#139)" so D3 staleness is local |

## Test strategy

```bash
uv run pytest tests/test_header_mapping.py
uv run ruff check && uv run ruff format --check
```

Existing totality / attr-sync tests should go green once exceptions and pairs
move together. No new fixture goldens expected (energy was not in
`RAW_PAIRS` before; bridge goldens that omit energy columns stay unaffected).

## Open questions

1. **Energy reset convention = capacity?** **Recommended: yes** (spec + #42
   already say so). Accepting this plan accepts that answer for the GitHub
   issue ask.
2. **Update architecture-plan D3 in this PR?** **Recommended: no** — keep
   core PR small; optional local design-guide note only. Say if you want the
   architecture-plan edit bundled.
