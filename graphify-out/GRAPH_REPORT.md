# Graph Report - cellpy-core  (2026-07-02)

## Corpus Check
- 47 files · ~48,514 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 871 nodes · 1166 edges · 78 communities (61 shown, 17 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 186 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `63066bf3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]

## God Nodes (most connected - your core abstractions)
1. `OldCellpyCellCore` - 32 edges
2. `Data` - 30 edges
3. `RawCols` - 30 edges
4. `CellpyUnits` - 25 edges
5. `default_schema()` - 22 edges
6. `DictLikeClass` - 21 edges
7. `CellpyCellCore` - 16 edges
8. `BaseSettings` - 16 edges
9. `_native_schema()` - 16 edges
10. `Cursor issue workflow (Agent Skills)` - 16 edges

## Surprising Connections (you probably didn't know these)
- `main()` --calls--> `create_raw_data()`  [INFERRED]
  dev/demo_mock_data.py → src/cellpycore/_helpers.py
- `main()` --calls--> `RawCols`  [INFERRED]
  dev/make_harmonized_raw.py → src/cellpycore/config.py
- `stage_b_engine_snapshot()` --calls--> `OldCellpyCellCore`  [INFERRED]
  dev/regenerate_test_data.py → src/cellpycore/cell_core.py
- `stage_b_engine_snapshot()` --calls--> `Data`  [INFERRED]
  dev/regenerate_test_data.py → src/cellpycore/cell_core.py
- `_BlockPint` --uses--> `Data`  [INFERRED]
  tests/test_units_optional.py → src/cellpycore/cell_core.py

## Communities (78 total, 17 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.14
Nodes (13): create_selector(), # TODO: implement also for energy and power (and probably others as well) - this, # TODO: @jepe - this method might be a bit slow for large datasets - consider us, # TODO: add support for selecting cycles based on other criteria (for example, b, # TODO: @jepe - include sub_steps here, # TODO: @jepe - include option for not selecting taper steps here, # TODO: @jepe - refactor this method!, # TODO: @jepe - include sub_steps here (+5 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (42): fetch_from_db(), from_dict(), from_json(), load_archive(), merge_test_meta(), push_to_db(), (De)serialization, merging, and persistence scaffolding for metadata.  This is, Load metadata from a cellpy archive file (HDF5). **Stub.**      Intended to re (+34 more)

### Community 2 - "Community 2"
Cohesion: 0.17
Nodes (12): Column-header definitions for the per-step summary table.      Each attribute, Column-header definitions for the per-step summary table.      Each attribute, Column-header definitions for the per-step summary table.      Each attribute, StepCols, The output column names follow the injected (native) schema, not any global., The output column names follow the injected (native) schema, not any global., The output column names follow the injected (native) schema, not any global., Two cells with different schemas each emit their own column names. (+4 more)

### Community 3 - "Community 3"
Cohesion: 0.08
Nodes (24): 1. Introduction: The Industrial Data Scalability Paradigm, 2. Core Challenges in High-Volume Data Management, 3.1 The M4 Algorithm, 3.2 LTTB and MinMaxLTTB, 3.3 Hierarchical Aggregation and the Visual Entity Budget, 3. Algorithmic Solutions for Scalable Visualization, 4.1 Microsoft Fabric-Native Patterns, 4.2 Tiger Data (formerly Timescale) (+16 more)

### Community 4 - "Community 4"
Cohesion: 0.06
Nodes (33): Additional tooling, Basic Structure, Branch Naming Convention, Branch Structure, Branching and Merging Strategy, Class Documentation, Code Documentation, Code Quality Standards (+25 more)

### Community 5 - "Community 5"
Cohesion: 0.09
Nodes (27): datetime_to_epoch_ns(), datetime_to_epoch_ns_expr(), epoch_ns_to_datetime(), epoch_ns_to_seconds(), epoch_ns_to_seconds_expr(), Build a ``polars`` expression converting a ``Datetime`` column to epoch ns., Build a ``polars`` expression converting epoch ns to float epoch seconds., Convert int64 epoch nanoseconds (UTC) to float epoch seconds (UTC).      Args: (+19 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (27): Auto-Clarity, Be token greedy - as a caveman, Boundaries, Branch hygiene, code:bash (# Either activate the environment first…), code:bash (# ❌ BAD: bare interpreter), code:bash (# Add or upgrade dependencies), code:bash (cellpycore/) (+19 more)

### Community 7 - "Community 7"
Cohesion: 0.07
Nodes (32): BaseCols, Cols, cols_check(), CycleCols, CycleType, FlexibleCols, Canonical step-type labels for the ``step_type`` column of the step table., Control mode of a step for the ``step_mode`` column of the raw table.      Des (+24 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (24): 1. **Function Organization**, 1. **Immutability by Design**, 2. **Error Handling**, 2. **Functional Programming Approach**, 3. **Constants and Configuration**, 3. **Type Safety**, 4. **Modular Design**, 5. **Configuration Management** (+16 more)

### Community 9 - "Community 9"
Cohesion: 0.06
Nodes (34): 1. Context and guiding principle, 2. Stages, 3. Implementation details, 4. Status, BatBase – The relational database layer, Before Stage 0 closes, Before Stage 2 starts, Before Stage 3 starts (+26 more)

### Community 10 - "Community 10"
Cohesion: 0.14
Nodes (16): _assert_pairs_bijective(), _legacy_values(), _native_values(), Round-trip / totality tests for the authoritative header mapping.  These lock, Distinct column-name strings declared on a native ``config.Cols`` class., Distinct column-name strings declared on a legacy ``Headers*`` dataclass., Reduce a step column ``<signal>_<stat>`` to its base ``<signal>``., _step_signal() (+8 more)

### Community 11 - "Community 11"
Cohesion: 0.15
Nodes (12): _BlockPint, _DummyData, pint_absent(), Optional-extra guard tests for the unit boundary (STEP-12, issue #40).  The st, meta_path finder that makes any ``import pint`` raise ModuleNotFoundError., Importing the package (and re-importing units) must not require pint., The step + summary engine runs end-to-end with pint blocked., Calling the pint-backed helpers raises a clear, extra-naming error. (+4 more)

### Community 12 - "Community 12"
Cohesion: 0.18
Nodes (6): HeadersStepTable, Headers used for the steps table (used as column headers for the steps pandas Da, Set selected columns first in a pandas.DataFrame.      This function sets cols, Headers used for the steps table (used as column headers for the steps pandas Da, Set selected columns first in a pandas.DataFrame.      This function sets cols, set_col_first()

### Community 13 - "Community 13"
Cohesion: 0.12
Nodes (16): Cols, CycleCols, # TODO: dtype should be a python native "dtype object" if it exists, or a pl.Dat, simple_cols_check(), SimpleCols, super_duper_cols_check(), SuperDuperCols, SuperDuperColsBase (+8 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (17): 0. `/iflow` — smart dispatcher (quick start), 0a. `/iflow-pick` — choose the next issue (front door), 10. `/iflow-status` — status overview of all issues (read-only), 1. `/iflow-init` — capture the issue locally, 2. `/iflow-plan` — design the approach, 3. `/iflow-start` — implement the plan, 4. `/iflow-pause` — park work safely, 5. `/iflow-close` — land the work (+9 more)

### Community 15 - "Community 15"
Cohesion: 0.12
Nodes (16): Add on's, Cellpy Core Functionality, Cellpy Core Input (Harmonized_Raw), Cellpy Core Output, Core CycleTable, Current code structure:, Definition of Cellpy Core Functionality, Headers (+8 more)

### Community 16 - "Community 16"
Cohesion: 0.19
Nodes (16): _legacy_schema(), Golden / regression tests on real cycling data vendored as parquet.  The fixtu, The per-cycle summary has one row per cycle and the expected cyc-1 datapoint., Lock the current summary output as the regression oracle for the issue #13, Cross-repo parity (Phase 4): cellpy-core reproduces cellpy's own committed, Smoke test: a tiny real raw frame flows through the engine.      This fixture, cellpy-core reproduces cellpy's published step/cycle goldens on real data., Lock the current engine output so the polars rewrite (issue #13) stays faithful. (+8 more)

### Community 17 - "Community 17"
Cohesion: 0.18
Nodes (9): BaseHeaders, BaseSettings, HeadersNormal, Converts to pandas dataframe, Headers used for the normal (raw) data (used as column headers for the main data, Subclass of BaseSetting including option to add postfixes.      Example:, Headers used for the normal (raw) data (used as column headers for the main data, Subclass of BaseSetting including option to add postfixes.      Example: (+1 more)

### Community 18 - "Community 18"
Cohesion: 0.15
Nodes (12): cellpy-core, code:bash (pip install uv), code:bash (uv venv), code:bash (uv pip install -e ".[dev]"), code:bash (# Add a new package), code:bash (# Update all packages), code:bash (pytest), Common Commands (+4 more)

### Community 19 - "Community 19"
Cohesion: 0.12
Nodes (17): _check_value_unit(), Parse for unit, update cellpy_units class, and return magnitude., Parse for unit, update cellpy_units class, and return magnitude., get_converter_to_specific(), _get_unit_registry(), nominal_capacity_as_absolute(), Q(), Get the nominal capacity as absolute value. (+9 more)

### Community 20 - "Community 20"
Cohesion: 0.15
Nodes (12): CellpyCellCore, Data, Make the core summary.          Args:             data: The data to make the, Make the core summary.          Args:             data: The data to make the, Make the core step table.          Delegates to ``summarizers.make_step_table`, Make the core step table.          Delegates to ``summarizers.make_step_table`, Args:             initialize (bool): set to True if you want to initialize the, Initialize the CellpyCell object with empty Data instance. (+4 more)

### Community 21 - "Community 21"
Cohesion: 0.14
Nodes (14): _build_step_cumulative_raw(), _build_test_cumulative_raw(), Tests for the injected Schema bundle and the step-table port.  These prove the, The globals bridge is gone: no module-level header/unit globals remain., The globals bridge is gone: no module-level header/unit globals remain., Same increments as ``_build_cumulative_raw`` but counters reset per step., Same increments as ``_build_cumulative_raw`` but counters reset per step., Same increments as ``_build_cumulative_raw`` but counters never reset.      Ca (+6 more)

### Community 22 - "Community 22"
Cohesion: 0.11
Nodes (20): legacy_to_native_raw(), legacy_to_native_step(), legacy_to_native_summary(), native_to_legacy_step(), native_to_legacy_summary(), Authoritative ``config.Cols`` <-> legacy ``Headers*`` column-name mapping.  Th, Return the legacy -> native rename dict for the raw frame.      Args:, Return the legacy -> native rename dict for the raw frame.      Args: (+12 more)

### Community 23 - "Community 23"
Cohesion: 0.19
Nodes (10): _declared_columns(), Conformance tests: config.py column classes match docs/data_format_specification, The renamed/removed legacy names are gone from RawCols., The renamed/removed legacy names are gone from RawCols., The renamed/removed legacy names are gone from RawCols., Map declared column attribute -> its string value for a Cols subclass., test_cycle_cols_match_spec(), test_no_legacy_raw_names() (+2 more)

### Community 24 - "Community 24"
Cohesion: 0.2
Nodes (11): BaseSettings, CellpyLimits, Thresholds used when classifying step types in ``make_step_table``.      Since, Thresholds used when classifying step types in ``make_step_table``.      Since, Tests for the CellpyLimits port (issue #12, Phase 1).  CellpyLimits holds the, CellpyLimits behaves like a dict (BaseSettings), as the engine indexes it., The canonical step-type labels include the ones make_step_table assigns., test_cellpy_limits_is_dict_like() (+3 more)

### Community 25 - "Community 25"
Cohesion: 0.2
Nodes (9): Auxillary columns, Capacity convention, Cellpy Core Harmonized_Raw, Column Headers, Conventions, Follow-ups, Other discussion points, Purpose (+1 more)

### Community 26 - "Community 26"
Cohesion: 0.2
Nodes (9): Test that cellpycore can be imported successfully., Test that cellpycore has the expected package structure., Test that cellpycore has a version attribute (if defined)., Test that cellpycore is properly registered in sys.modules., Test that cellpycore can be imported., test_cellpycore_import(), test_cellpycore_in_sys_modules(), test_cellpycore_package_structure() (+1 more)

### Community 28 - "Community 28"
Cohesion: 0.33
Nodes (4): create_raw_data(), Helper functions only intended for development purposes  (e.g. for creating mock, Create mock raw battery testing data with realistic values.      TODO: This fu, main()

### Community 29 - "Community 29"
Cohesion: 0.25
Nodes (7): code:bash (# Stage A — raw export (needs cellpy + Arbin ODBC for the .r), code:bash (uv run python dev/make_harmonized_raw.py), Files, Golden numbers, Provenance & license, Regenerating, Test data fixtures

### Community 30 - "Community 30"
Cohesion: 0.22
Nodes (9): _build_merged_raw(), Two tests (test_id 0 and 1) with **overlapping** cycle_num/step_num.      Each, Two tests (test_id 0 and 1) with **overlapping** cycle_num/step_num.      Each, A merged object (2 tests, overlapping cycle/step) keeps every step row.      W, A merged object (2 tests, overlapping cycle/step) keeps every step row.      W, Per-cycle cumulations restart at each test; no capacity leaks across tests., Per-cycle cumulations restart at each test; no capacity leaks across tests., test_merged_object_step_table_isolated_per_test() (+1 more)

### Community 31 - "Community 31"
Cohesion: 0.5
Nodes (3): Cellpy Core CycleTable (DRAFT), Column Headers, Purpose

### Community 32 - "Community 32"
Cohesion: 0.5
Nodes (3): Cellpy Core StepTable (DRAFT), Column Headers, Purpose

### Community 49 - "Community 49"
Cohesion: 0.15
Nodes (16): Column-header definitions for the harmonized raw data table.      Each attribu, Column-header definitions for the harmonized raw data table.      Each attribu, Column-header definitions for the harmonized raw data table.      Each attribu, RawCols, _native_schema(), TestMode.INVERTED (anode) flips CE and coulombic_difference references., TestMode.INVERTED (anode) flips CE and coulombic_difference references., TestMode.INVERTED (anode) flips CE and coulombic_difference references. (+8 more)

### Community 50 - "Community 50"
Cohesion: 0.16
Nodes (15): _add_end_potentials(), c_rates_to_summary(), _ensure_test_id(), _group_keys(), make_summary(), normalize_capacity_granularity(), Join per-cycle end-of-charge / end-of-discharge potentials onto ``summary``., Polars-native per-cycle summary (the clean native ``CycleCols`` subset). (+7 more)

### Community 51 - "Community 51"
Cohesion: 0.15
Nodes (12): Bundle of the column-header objects for one cell.      Holds the raw, cycle (s, Bundle of the column-header objects for one cell.      Holds the raw, cycle (s, Schema, LastIRExtractor, Pluggable per-cycle summary extractors.  A *summary extractor* is a callable o, Base class for callable per-cycle summary extractors.      Subclasses implemen, Return a per-cycle frame keyed by ``schema.cycle.cycle_num``.          Args:, Default internal-resistance extractor (issue #23).      For each cycle it read (+4 more)

### Community 52 - "Community 52"
Cohesion: 0.33
Nodes (9): Converter-parity tests for ``cellpycore.units`` (STEP-12, issue #40).  ``cellp, Minimal stand-in for ``Data`` exposing only what the converters read., _stub(), test_get_converter_to_specific_charge_unit_mismatch(), test_get_converter_to_specific_modes(), test_get_converter_to_specific_unknown_mode_is_identity(), test_nominal_capacity_as_absolute_convert_charge_units(), test_nominal_capacity_as_absolute_explicit_value_and_specific() (+1 more)

### Community 53 - "Community 53"
Cohesion: 0.17
Nodes (12): _classify_from_specifications(), _classify_steps(), _delta_expr(), make_step_table(), Per-step delta in percent (mirrors legacy cellpy's ``delta``).      ``100 * la, Create a table (v.5) that contains summary information for each step.      Thi, Build a step-type expression from explicit step specifications., Return a polars expression classifying each step into a step type.      Mirror (+4 more)

### Community 54 - "Community 54"
Cohesion: 0.17
Nodes (12): _build_raw(), _data_with_raw(), c_rate = abs(current_mean / nom_cap): doubling nom_cap halves the rate., c_rate = abs(current_mean / nom_cap): doubling nom_cap halves the rate., c_rate = abs(current_mean / nom_cap): doubling nom_cap halves the rate., Build a minimal native-named raw DataFrame (2 cycles x charge/discharge/rest)., Build a minimal native-named raw DataFrame (2 cycles x charge/discharge/rest)., The native CellpyCellCore add_scaled path runs on the polars summary. (+4 more)

### Community 55 - "Community 55"
Cohesion: 0.33
Nodes (6): _calculate_nominal_capacity_from_cycles(), equivalent_cycles_to_summary(), Calculate nominal capacity from specified normalization cycles.      Polars-na, Add the ``normalized_cycle_index`` (equivalent cycles) column to the summary., Calculate nominal capacity from specified normalization cycles.      Polars-na, Add the ``normalized_cycle_index`` (equivalent cycles) column to the summary.

### Community 56 - "Community 56"
Cohesion: 0.18
Nodes (12): _build_cumulative_raw(), _cap_lists(), 2 cycles, each charge then discharge, with cycle-cumulative capacities held., Return the (charge, discharge) cumulative capacity lists, datapoint-ordered., 2 cycles, each charge then discharge, with cycle-cumulative capacities held., Return the (charge, discharge) cumulative capacity lists, datapoint-ordered., STEP / TEST cumulative raw normalizes to the cycle-cumulative oracle., STEP / TEST cumulative raw normalizes to the cycle-cumulative oracle. (+4 more)

### Community 57 - "Community 57"
Cohesion: 0.4
Nodes (5): CellpyCellCore.schema bundles the (possibly overridden) header instances., The pandas selector pair was removed once cellpy migrated off it (#45)., CellpyCellCore.schema bundles the (possibly overridden) header instances., test_no_legacy_selector_functions(), test_schema_property_reflects_headers()

### Community 61 - "Community 61"
Cohesion: 0.15
Nodes (14): CellpyUnits, HeadersSummary, MockCore, These are the units used inside Cellpy.      At least two sets of units needs, Headers used for the summary data (used as column headers for the main data pand, Headers used for the summary data (used as column headers for the main data pand, CellpyUnits, get_cellpy_units() (+6 more)

### Community 62 - "Community 62"
Cohesion: 0.16
Nodes (14): default_schema(), Return a Schema using the native cellpy-core column definitions.      Used as, Return a Schema using the native cellpy-core column definitions.      Used as, Return a Schema using the native cellpy-core column definitions.      Used as, get_cycle_numbers(), get_rates(), get_step_numbers(), Get a array containing the cycle numbers in the test.      Parameters: (+6 more)

### Community 63 - "Community 63"
Cohesion: 0.22
Nodes (7): OldCellpyCellCore, Legacy CellpyCellCore class to make it easier to migrate to cellpy core., Legacy CellpyCellCore class to make it easier to migrate to cellpy core., Build the step table via the polars engine, in/out in legacy form.          Se, Build the step table via the polars engine, in/out in legacy form.          Se, Map the ``info`` column from step specifications onto the step table., Map the ``info`` column from step specifications onto the step table.

### Community 64 - "Community 64"
Cohesion: 0.21
Nodes (3): DictLikeClass, Get the value (postfixes not supported)., Add some dunder-methods so that it does not break old code that used     dictio

### Community 65 - "Community 65"
Cohesion: 0.17
Nodes (12): _ir_raw_steps(), Hand-built native raw + steps exercising the IR-extraction rules.      cycle 1, Hand-built native raw + steps exercising the IR-extraction rules.      cycle 1, Hand-built native raw + steps exercising the IR-extraction rules.      cycle 1, Default extractor picks the last datapoint of the last charge/discharge     ste, Default extractor picks the last datapoint of the last charge/discharge     ste, Default extractor picks the last datapoint of the last charge/discharge     ste, A custom SummaryExtractor passed via ir_extractor overrides the default. (+4 more)

### Community 66 - "Community 66"
Cohesion: 0.18
Nodes (6): Add specific summary columns to the summary.          Args:             data:, Add specific summary columns to the summary.          Args:             data:, Resolve the specific-capacity conversion factor for a mode.          Prefers t, Resolve the specific-capacity conversion factor for a mode.          Prefers t, Legacy-bridge ``add_scaled_summary_columns`` (pandas<->polars seam)., Legacy-bridge ``add_scaled_summary_columns`` (pandas<->polars seam).

### Community 67 - "Community 67"
Cohesion: 0.2
Nodes (10): Distinct step-type labels from a (polars) native step table., Step-type classification uses the supplied raw_limits, not a fixed default., Step-type classification uses the supplied raw_limits, not a fixed default., Step-type classification uses the supplied raw_limits, not a fixed default., Raw without ref_potential yields no ref_potential_* columns, engine unaffected., Raw without ref_potential yields no ref_potential_* columns, engine unaffected., Distinct step-type labels from a (polars) native step table., test_raw_limits_affect_classification() (+2 more)

### Community 68 - "Community 68"
Cohesion: 0.22
Nodes (4): # TODO: v2.0 edit this from scalar to list, # TODO: v2.0 edit this from scalar to list, # TODO: move the data object to slim, # TODO: copy div settings to slim

### Community 69 - "Community 69"
Cohesion: 0.22
Nodes (5): BaseSettings, Generic dict-like settings base classes shared across cellpy-core.  These were, Base class for internal cellpy settings.      Usage::           @dataclass, Get the value (postfixes not supported)., Converts to pandas dataframe

### Community 70 - "Community 70"
Cohesion: 0.25
Nodes (4): Add the pandas-only legacy summary columns the native schema omits.          `, Add the pandas-only legacy summary columns the native schema omits.          `, Build the per-cycle summary via the polars engine, in/out in legacy form., Build the per-cycle summary via the polars engine, in/out in legacy form.

### Community 71 - "Community 71"
Cohesion: 0.29
Nodes (7): CellpyError, NoDataFound, Base class for other exceptions, Exception raised when no data is found, Base class for other exceptions, Exception raised when no data is found, Exception

### Community 72 - "Community 72"
Cohesion: 0.5
Nodes (4): The native polars summary engine emits the clean CycleCols subset only., The native polars summary engine emits the clean CycleCols subset only., The native polars summary engine emits the clean CycleCols subset only., test_make_summary_native_schema()

### Community 73 - "Community 73"
Cohesion: 0.5
Nodes (4): generate_specific_summary_columns multiplies by the given factor (no pint)., generate_specific_summary_columns multiplies by the given factor (no pint)., generate_specific_summary_columns multiplies by the given factor (no pint)., test_generate_specific_columns_takes_factor_by_value()

### Community 74 - "Community 74"
Cohesion: 0.5
Nodes (4): ir_to_summary adds ir_charge/ir_discharge (native, default extractor)., ir_to_summary adds ir_charge/ir_discharge (native, default extractor)., ir_to_summary adds ir_charge/ir_discharge (native, default extractor)., test_ir_to_summary_native()

### Community 75 - "Community 75"
Cohesion: 0.67
Nodes (3): generate_specific_summary_columns(), Generate specific (per mass / area / volume) summary columns.      Polars-nati, Generate specific (per mass / area / volume) summary columns.      Polars-nati

### Community 76 - "Community 76"
Cohesion: 0.67
Nodes (3): The synthetic mock raw fixture exercises the ref_potential column., The synthetic mock raw fixture exercises the ref_potential column., test_mock_raw_data_carries_ref_potential()

## Knowledge Gaps
- **459 isolated node(s):** `# TODO: dtype should be a python native "dtype object" if it exists, or a pl.Dat`, `Build the harmonized raw frame from a legacy-named frame.      Args:`, `Load each source with cellpy and write ``<name>_raw.parquet``.`, `Run the current cellpy-core engine on the raw parquet and snapshot the     step`, `True if a step table has been computed.` (+454 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Data` connect `Community 20` to `Community 65`, `Community 66`, `Community 68`, `Community 70`, `Community 71`, `Community 73`, `Community 11`, `Community 12`, `Community 13`, `Community 16`, `Community 17`, `Community 21`, `Community 54`, `Community 56`, `Community 61`, `Community 30`, `Community 63`?**
  _High betweenness centrality (0.151) - this node is a cross-community bridge._
- **Why does `default_schema()` connect `Community 62` to `Community 0`, `Community 2`, `Community 66`, `Community 7`, `Community 49`, `Community 50`, `Community 51`, `Community 53`, `Community 55`, `Community 63`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Why does `RawCols` connect `Community 49` to `Community 65`, `Community 2`, `Community 67`, `Community 5`, `Community 7`, `Community 72`, `Community 74`, `Community 76`, `Community 21`, `Community 54`, `Community 30`, `Community 56`, `Community 28`, `Community 62`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `OldCellpyCellCore` (e.g. with `NoDataFound` and `Meta`) actually correct?**
  _`OldCellpyCellCore` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `Data` (e.g. with `NoDataFound` and `Meta`) actually correct?**
  _`Data` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `RawCols` (e.g. with `main()` and `create_raw_data()`) actually correct?**
  _`RawCols` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `CellpyUnits` (e.g. with `CellpyError` and `NoDataFound`) actually correct?**
  _`CellpyUnits` has 19 INFERRED edges - model-reasoned connections that need verification._