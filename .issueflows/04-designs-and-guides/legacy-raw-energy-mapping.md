# Legacy raw energy mapping (#139)

**Context.** Raw `charge_energy` / `discharge_energy` used to sit in
`LEGACY_ONLY_RAW` (passthrough). Architecture-plan D3 still says that and
claims different reset semantics vs native cumulative energy.

**Decision.** Bridge them like capacity via `RAW_PAIRS` /
`LEGACY_ATTR_TO_SCHEMA["raw"]`:

| legacy value | native |
|---|---|
| `charge_energy` | `cumulative_charge_energy` |
| `discharge_energy` | `cumulative_discharge_energy` |

Reset convention matches capacity: cycle-cumulative, per direction
(`docs/specifications/harmonized-raw.md` Capacity convention). Wrong source
granularity → issue #42 normalizer, not leaving columns unmapped.

**Alternatives.** Keep passthrough (rejected — breaks `to_native()` /
`harmonize()` schema lookup). Synthesize energy from other signals (rejected —
rename only).

**Refs.** #139; cellpy #560; supersedes architecture-plan D3 for these two
columns only.
