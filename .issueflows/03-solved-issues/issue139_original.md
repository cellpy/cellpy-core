# Issue #139: legacy mapping: no entries for the energy columns (charge_energy_txt -> cumulative_charge_energy)

Source: https://github.com/cellpy/cellpy-core/issues/139

## Original issue text

## Summary

`cellpycore.legacy.mapping.LEGACY_ATTR_TO_SCHEMA["raw"]` has no entries for the
energy columns, although both sides exist:

- native schema defines `cumulative_charge_energy` and
  `cumulative_discharge_energy`;
- cellpy's loader configurations declare `charge_energy_txt` and
  `discharge_energy_txt`, and vendor files carry the data (Maccor `Watt-hr`,
  Neware energy columns, …).

```python
>>> from cellpycore.legacy import mapping
>>> {k: v for k, v in mapping.LEGACY_ATTR_TO_SCHEMA["raw"].items() if "energy" in k}
{}
```

## Why it matters now

Found while porting loaders to the `harmonize()` framework
(jepegit/cellpy#559 → #560). Consequences today:

1. On the native runtime, `to_native()` passes the unmapped columns through
   under their **legacy** names, so a native frame carries `charge_energy`
   while the schema says the column should be `cumulative_charge_energy`.
   Asking `c.schema.raw` for energy finds nothing.
2. `harmonize()` drops undeclared columns by design, so a ported loader would
   silently lose energy data unless it declares a passthrough — which is the
   wrong long-term answer for a column the schema already has a name for.

## Ask

Add the mapping entries:

| legacy attribute | native column |
|---|---|
| `charge_energy_txt` | `cumulative_charge_energy` |
| `discharge_energy_txt` | `cumulative_discharge_energy` |

Please confirm the reset-granularity convention for the energy columns matches
the capacity one (cycle-cumulative per direction, per the harmonized-raw spec's
*Capacity convention*) — the cellpy side will normalise them the same way.

## Also unmapped (for a decision, not necessarily this issue)

These native raw columns have no legacy attribute mapped to them. Several are
correctly framework-owned or native-only, but `datetime_txt → epoch_time_utc`
looks like a genuine omission of the same kind:

`epoch_time_utc`, `step_type`, `step_mode`, `step_type_detail`, `cycle_type`,
`ref_potential`, `step_charge_power`, `step_discharge_power`, `aux_*`,
`source_*`, `mask`, `test_id`.

Cross-repo order per the cellpy 2 release plan §3: core PR → core release →
cellpy re-pin → cellpy consumes.
