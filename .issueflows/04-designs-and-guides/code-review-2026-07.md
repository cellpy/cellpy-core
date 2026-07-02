# Code review — weaknesses, improvements, and plan forward (2026-07)

Full-codebase review of `cellpy-core` at commit `076fac7` (post issue #48,
composite `test_id` group keys). Every claimed defect below was **verified by
executing code**, not just by reading it. The full test suite was green at the
time of review (88 passed, ~1.9 s).

Reviewed: all modules in `src/cellpycore/` (engine, config/schema, legacy
bridge, header mapping, units, selectors, timestamps, metadata scaffolding),
`tests/`, `pyproject.toml`, CI (`.github/workflows/simpletest.yml`), and repo
hygiene.

Related issue: local issue 50 (docs-only; this report is the deliverable).

## Overall verdict

The core is healthy. The polars engine (`summarizers.py`, `extractors.py`) is
clean, schema-injected, and well-documented. The header mapping
(`header_mapping.py`) is disciplined: totality-tested, with explicit exception
sets. The golden/parity test strategy is strong. The metadata scaffolding
matches the boundary decision in `cellpy-core-migration.md` §4. The weak spots
concentrate in the **edges**: legacy helpers, packaging, and the public API
surface.

## A. Bugs / latent breakage (verified)

### A1. `selectors.py` is broken with its own default schema

All four public functions (`summary_selector_exluder`, `get_step_numbers`,
`get_cycle_numbers`, `get_rates`) default to `default_schema()` but then
dereference **legacy-only** attribute names:

```python
# selectors.py — summary_selector_exluder
d_n_txt = custom_headers_normal.data_point_txt   # RawCols has `datapoint_num`
v_n_txt = custom_headers_normal.voltage_txt      # RawCols has `potential`
c_n_txt = custom_headers_normal.cycle_index_txt  # RawCols has `cycle_num`
```

Verified: the native `RawCols` has none of `data_point_txt` / `voltage_txt` /
`cycle_index_txt`, and the native `StepCols` has none of `cycle` / `type` /
`rate_avr` / `ustep` / `point`. So every function raises `AttributeError`
unless the caller injects the legacy `HeadersNormal` / `HeadersStepTable`.

Additional problems in the same module:

- Pandas-only (`.loc`, `.groupby`, `raw.copy()`) inside an otherwise
  polars-native package (`pl.DataFrame` has no `.copy()`).
- **Zero test coverage** — there is no `tests/test_selectors.py`.
- Open issue #45 covers removing `create_selector` /
  `summary_selector_exluder` only; `get_step_numbers`, `get_cycle_numbers`
  and `get_rates` share the same defect but are not in its scope.

### A2. `units.py` fallback path crashes on the core `Data` object

`get_converter_to_specific` reads `data.raw_units`, `data.mass`,
`data.active_electrode_area`, `data.volume`; `nominal_capacity_as_absolute`
reads `data.nom_cap_specifics`, `data.nom_cap`. The core `Data` class has
**none** of these attributes, so the fallback path (taken whenever a caller
omits `specific_converters` in `add_scaled_summary_columns`) raises
`AttributeError`. It only works when cellpy hands in its own richer data
object — a silent trap for standalone cellpy-core users.

Minor in the same file: `nominal_capacity_as_absolute` contains a pointless
`try: ... except Exception as e: raise e` block.

### A3. Falsy-override bug in step classification

`summarizers._classify_steps` resolves override limits with:

```python
current_hard = orl.get("current_hard") or raw_limits["current_hard"]
```

An explicit override of `0` / `0.0` is falsy and silently ignored, falling
back to the default. Use `if "current_hard" in orl:` (or
`orl.get(key, default)` with a sentinel) instead. Applies to all four
override keys.

### A4. Dead-parameter API lies in `make_core_summary`

The native `CellpyCellCore.make_core_summary` accepts `selector`,
`select_columns` and `find_end_voltage` but never uses them (end potentials
are always added by `make_summary`; `find_end_voltage` only affects the
**legacy** bridge's column ordering). A caller passing `selector=...` gets a
silent no-op.

### A5. Shared mutable default: `DEFAULT_RAW_LIMITS`

`DEFAULT_RAW_LIMITS = asdict(CellpyLimits())` is a module-level `dict` used
as a default argument of `make_step_table`. Any caller mutating it changes
behaviour process-wide — this conflicts with the project's stated
thread-safety goal. Freeze it (`types.MappingProxyType`) or build a fresh
dict per call.

### A6. Dead fields on `Data`

`Data.cycle` / `Data.step` are declared as "legacy aliases for backwards
compatibility", but nothing in the code base ever reads or writes them (the
engine uses `steps` / `summary`). Misleading; delete them or wire them as
properties over `steps` / `summary`.

## B. Design gaps

### B1. Schema-agnosticism is only partial in the step engine

The per-step statistic columns are hardcoded as `f"{base}_{stat}"` (and the
classifier reads `pl.col("current_mean")` etc.). The injected `StepCols`
values are applied only to the group keys, `step_type` and `c_rate`. A custom
`StepCols.current_mean` is silently ignored. Either derive the stat column
names from the schema, or (cheaper, recommended) document that the
`<signal>_<stat>` names are a fixed engine contract.

### B2. Default-polarity inconsistency in `cycle_mode`

`MockMetaTestDependent.cycle_mode = "anode"` means an **initialized** `Data`
defaults to INVERTED mode, while an uninitialized cell
(`_cycle_mode = None`) resolves to NORMAL. This is exactly the
"default-polarity trap" the `config.TestMode` docstring warns about, live
inside the same package.

### B3. No input validation at the engine entry points

`make_step_table` / `make_summary` on `data.raw = None` produce a cryptic
`pl.from_pandas(None)` traceback. `NoDataFound` exists but the engine never
raises it. A cheap guard (raise `NoDataFound` for missing `raw`/`steps`, a
clear `ValueError` for missing required columns) is a big usability win.

### B4. Empty `__init__.py` — no public API surface

No exports, no `__version__` (one test even probes for it "if defined").
Consumers must deep-import `cellpycore.summarizers` etc.; there is no declared
stable surface for cellpy to build against.

## C. Packaging / hygiene

- **`pyproject.toml`:** description is still `"Add your description here"`;
  the classifier `Topic :: Software Development :: Build Tools` is wrong;
  and there are **unused heavy dependencies** — `duckdb`, `duckdb-engine`,
  `sqlalchemy`, `narwhals` have zero imports under `src/` (verified by
  search). `pyarrow` should stay (pandas↔polars conversion needs it).
- **Dead build dependency:** `uv-dynamic-versioning` is in
  `[build-system].requires` but never configured (no
  `[tool.uv-dynamic-versioning]` section, no hatch version source); the
  version stays static `0.1.0`.
- **Committed junk:** `scratch.db`, `tmp/simple.csv`, `tmp/simple.parquet`
  are tracked in git.
- **CI:** the single workflow runs tests only; `ruff` is in the dev group but
  there is no lint/format step, no ruff config, no coverage reporting.
- **Logging:** root-logger calls (`logging.debug(...)` instead of
  `logger.debug`) in `summarizers.py` (inside `make_step_table`),
  `settings_base.py` and `units.py` — violates the project's own
  logging rule.
- **Docs:** `README.md` is generic uv boilerplate with no project
  description; `.issueflows/04-designs-and-guides/this-project.md` is all
  TODO stubs — it is the first thing every agent is told to read and is
  currently empty.
- **Typing:** no `py.typed` marker; the `DataFrame = TypeVar("DataFrame")`
  idiom misuses a `TypeVar` as a type alias (use `TypeAlias` or real
  optional-import types).

## D. Plan forward (sequenced; one issue/PR each)

1. **Hygiene PR (small, zero risk):** drop the unused dependencies and
   `uv-dynamic-versioning`; fix the pyproject metadata; delete `scratch.db`
   and `tmp/`; add a ruff check to CI; replace the root-logger calls; remove
   `Data.cycle` / `Data.step`; fix the falsy-override bug (A3) with a
   regression test; freeze `DEFAULT_RAW_LIMITS` (A5).
2. **API truthing:** delete the unused `make_core_summary` parameters (or
   implement a native `find_end_voltage` gate); populate `__init__.py` with
   the public exports and a `__version__`; add `py.typed`. Fill in
   `this-project.md` and the README description while at it.
3. **Selectors decision (feeds #45):** either port `get_step_numbers` /
   `get_cycle_numbers` / `get_rates` to the native schema + polars with
   tests, or move the whole module next to `legacy.py` and document it as
   bridge-only until removal. The current state — broken by default and
   untested — is the worst of both.
4. **Units fallback (A2):** make `get_converter_to_specific` /
   `nominal_capacity_as_absolute` take explicit values or a
   `metadata.CellMeta` (which already has `mass`, `active_electrode_area`,
   `nom_cap`, `nom_cap_specifics` — a natural fit with the metadata-boundary
   decision). This removes the crashing `data.<attr>` fallback.
5. **Engine guards (B3):** raise `NoDataFound` / a clear `ValueError` for
   missing frames and missing required columns at the `make_step_table` /
   `make_summary` entry points.
6. **Then release (#44):** after items 1–2 land, tag `v0.1.0` and have cellpy
   pin it (per the migration doc: pin a tag before a cellpy release). Open
   issues #42 (reset-granularity normalization) and #43 (`ref_potential`
   support) slot in after the release — both are additive.
7. **Test gaps to backfill alongside:** selectors (none today); summarizer
   edge cases (empty raw frame, cycle without a charge step,
   `override_raw_limits` with `0.0`); and a thread-safety smoke test (two
   schemas, parallel `make_step_table`).
