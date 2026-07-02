# Graph Report - cellpy-core  (2026-07-02)

## Corpus Check
- 48 files · ~50,499 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 938 nodes · 1267 edges · 74 communities (51 shown, 23 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 205 edges (avg confidence: 0.72)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `db054a34`
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
- [[_COMMUNITY_Community 34|Community 34]]
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
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]

## God Nodes (most connected - your core abstractions)
1. `OldCellpyCellCore` - 34 edges
2. `RawCols` - 33 edges
3. `Data` - 32 edges
4. `default_schema()` - 29 edges
5. `CellpyUnits` - 25 edges
6. `DictLikeClass` - 21 edges
7. `CellpyCellCore` - 17 edges
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

## Communities (74 total, 23 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.06
Nodes (47): default_schema(), Return a Schema using the native cellpy-core column definitions.      Used as, Return a Schema using the native cellpy-core column definitions.      Used as, Return a Schema using the native cellpy-core column definitions.      Used as, create_selector(), get_cycle_numbers(), get_rates(), get_step_numbers() (+39 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (44): fetch_from_db(), from_dict(), from_json(), load_archive(), merge_test_meta(), push_to_db(), (De)serialization, merging, and persistence scaffolding for metadata.  This is, Load metadata from a cellpy archive file (HDF5). **Stub.**      Intended to re (+36 more)

### Community 2 - "Community 2"
Cohesion: 0.17
Nodes (12): Column-header definitions for the per-step summary table.      Each attribute, Column-header definitions for the per-step summary table.      Each attribute, Column-header definitions for the per-step summary table.      Each attribute, StepCols, The output column names follow the injected (native) schema, not any global., The output column names follow the injected (native) schema, not any global., The output column names follow the injected (native) schema, not any global., Two cells with different schemas each emit their own column names. (+4 more)

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (34): 1. Context and guiding principle, 1. Introduction: The Industrial Data Scalability Paradigm, 2. Core Challenges in High-Volume Data Management, 3.1 The M4 Algorithm, 3.2 LTTB and MinMaxLTTB, 3.3 Hierarchical Aggregation and the Visual Entity Budget, 3. Algorithmic Solutions for Scalable Visualization, 3. Implementation details (+26 more)

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
Nodes (30): BaseCols, Cols, cols_check(), CycleCols, CycleType, FlexibleCols, Canonical step-type labels for the ``step_type`` column of the step table., Control mode of a step for the ``step_mode`` column of the raw table.      Des (+22 more)

### Community 8 - "Community 8"
Cohesion: 0.08
Nodes (24): 1. **Function Organization**, 1. **Immutability by Design**, 2. **Error Handling**, 2. **Functional Programming Approach**, 3. **Constants and Configuration**, 3. **Type Safety**, 4. **Modular Design**, 5. **Configuration Management** (+16 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (24): 2. Stages, Before Stage 0 closes, Before Stage 2 starts, Before Stage 3 starts, Deliverables, Deliverables, Deliverables, Deliverables (+16 more)

### Community 10 - "Community 10"
Cohesion: 0.14
Nodes (16): _assert_pairs_bijective(), _legacy_values(), _native_values(), Round-trip / totality tests for the authoritative header mapping.  These lock, Distinct column-name strings declared on a native ``config.Cols`` class., Distinct column-name strings declared on a legacy ``Headers*`` dataclass., Reduce a step column ``<signal>_<stat>`` to its base ``<signal>``., _step_signal() (+8 more)

### Community 11 - "Community 11"
Cohesion: 0.17
Nodes (15): Golden / regression tests on real cycling data vendored as parquet.  The fixtu, The per-cycle summary has one row per cycle and the expected cyc-1 datapoint., Lock the current summary output as the regression oracle for the issue #13, Cross-repo parity (Phase 4): cellpy-core reproduces cellpy's own committed, Smoke test: a tiny real raw frame flows through the engine.      This fixture, cellpy-core reproduces cellpy's published step/cycle goldens on real data., Lock the current engine output so the polars rewrite (issue #13) stays faithful., _step_table() (+7 more)

### Community 12 - "Community 12"
Cohesion: 0.14
Nodes (10): CellpyError, NoDataFound, Base class for other exceptions, Exception raised when no data is found, Base class for other exceptions, Exception raised when no data is found, Set selected columns first in a pandas.DataFrame.      This function sets cols, Set selected columns first in a pandas.DataFrame.      This function sets cols (+2 more)

### Community 13 - "Community 13"
Cohesion: 0.07
Nodes (26): create_raw_data(), Helper functions only intended for development purposes  (e.g. for creating mock, Create mock raw battery testing data with realistic values.      TODO: This fu, Cols, CycleCols, # TODO: dtype should be a python native "dtype object" if it exists, or a pl.Dat, simple_cols_check(), SimpleCols (+18 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (17): 0. `/iflow` — smart dispatcher (quick start), 0a. `/iflow-pick` — choose the next issue (front door), 10. `/iflow-status` — status overview of all issues (read-only), 1. `/iflow-init` — capture the issue locally, 2. `/iflow-plan` — design the approach, 3. `/iflow-start` — implement the plan, 4. `/iflow-pause` — park work safely, 5. `/iflow-close` — land the work (+9 more)

### Community 15 - "Community 15"
Cohesion: 0.12
Nodes (16): Add on's, Cellpy Core Functionality, Cellpy Core Input (Harmonized_Raw), Cellpy Core Output, Core CycleTable, Current code structure:, Definition of Cellpy Core Functionality, Headers (+8 more)

### Community 16 - "Community 16"
Cohesion: 0.05
Nodes (41): OldCellpyCellCore, Legacy CellpyCellCore class to make it easier to migrate to cellpy core., Legacy CellpyCellCore class to make it easier to migrate to cellpy core., Build the step table via the polars engine, in/out in legacy form.          Se, Build the step table via the polars engine, in/out in legacy form.          Se, Legacy CellpyCellCore class to make it easier to migrate to cellpy core., Legacy CellpyCellCore class to make it easier to migrate to cellpy core., Map the ``info`` column from step specifications onto the step table. (+33 more)

### Community 17 - "Community 17"
Cohesion: 0.18
Nodes (9): BaseHeaders, BaseSettings, HeadersSummary, Converts to pandas dataframe, Headers used for the summary data (used as column headers for the main data pand, Subclass of BaseSetting including option to add postfixes.      Example:, Headers used for the summary data (used as column headers for the main data pand, Subclass of BaseSetting including option to add postfixes.      Example: (+1 more)

### Community 18 - "Community 18"
Cohesion: 0.15
Nodes (12): cellpy-core, code:bash (pip install uv), code:bash (uv venv), code:bash (uv pip install -e ".[dev]"), code:bash (# Add a new package), code:bash (# Update all packages), code:bash (pytest), Common Commands (+4 more)

### Community 19 - "Community 19"
Cohesion: 0.12
Nodes (17): _check_value_unit(), Parse for unit, update cellpy_units class, and return magnitude., Parse for unit, update cellpy_units class, and return magnitude., get_converter_to_specific(), _get_unit_registry(), nominal_capacity_as_absolute(), Q(), Get the nominal capacity as absolute value. (+9 more)

### Community 20 - "Community 20"
Cohesion: 0.21
Nodes (10): CellpyCellCore, Data, Args:             initialize (bool): set to True if you want to initialize the, Initialize the CellpyCell object with empty Data instance., Args:             initialize (bool): set to True if you want to initialize the, Initialize the CellpyCell object with empty Data instance., Meta, MockMetaTestDependent (+2 more)

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
Cohesion: 0.29
Nodes (7): HeadersNormal, HeadersStepTable, Headers used for the normal (raw) data (used as column headers for the main data, Headers used for the steps table (used as column headers for the steps pandas Da, Headers used for the normal (raw) data (used as column headers for the main data, Headers used for the steps table (used as column headers for the steps pandas Da, _legacy_schema()

### Community 29 - "Community 29"
Cohesion: 0.25
Nodes (7): code:bash (# Stage A — raw export (needs cellpy + Arbin ODBC for the .r), code:bash (uv run python dev/make_harmonized_raw.py), Files, Golden numbers, Provenance & license, Regenerating, Test data fixtures

### Community 30 - "Community 30"
Cohesion: 0.15
Nodes (14): _build_merged_raw(), _native_schema(), The native polars summary engine emits the clean CycleCols subset only., The native polars summary engine emits the clean CycleCols subset only., The native polars summary engine emits the clean CycleCols subset only., Two tests (test_id 0 and 1) with **overlapping** cycle_num/step_num.      Each, Two tests (test_id 0 and 1) with **overlapping** cycle_num/step_num.      Each, A merged object (2 tests, overlapping cycle/step) keeps every step row.      W (+6 more)

### Community 31 - "Community 31"
Cohesion: 0.5
Nodes (3): Cellpy Core CycleTable (DRAFT), Column Headers, Purpose

### Community 32 - "Community 32"
Cohesion: 0.5
Nodes (3): Cellpy Core StepTable (DRAFT), Column Headers, Purpose

### Community 34 - "Community 34"
Cohesion: 0.4
Nodes (4): Make the core step table.          Delegates to ``summarizers.make_step_table`, Make the core step table.          Delegates to ``summarizers.make_step_table`, Make the core step table.          Delegates to ``summarizers.make_step_table`, Make the core step table.          Delegates to ``summarizers.make_step_table`

### Community 49 - "Community 49"
Cohesion: 0.5
Nodes (4): c_rates_to_summary joins per-cycle first charge/discharge C-rates (native)., c_rates_to_summary joins per-cycle first charge/discharge C-rates (native)., c_rates_to_summary joins per-cycle first charge/discharge C-rates (native)., test_c_rates_to_summary_native()

### Community 50 - "Community 50"
Cohesion: 0.06
Nodes (43): _add_end_potentials(), c_rates_to_summary(), _calculate_nominal_capacity_from_cycles(), _classify_from_specifications(), _classify_steps(), _delta_expr(), _ensure_test_id(), equivalent_cycles_to_summary() (+35 more)

### Community 51 - "Community 51"
Cohesion: 0.14
Nodes (13): Bundle of the column-header objects for one cell.      Holds the raw, cycle (s, Bundle of the column-header objects for one cell.      Holds the raw, cycle (s, Schema, LastIRExtractor, Pluggable per-cycle summary extractors.  A *summary extractor* is a callable o, Base class for callable per-cycle summary extractors.      Subclasses implemen, Return a per-cycle frame keyed by ``schema.cycle.cycle_num``.          Args:, Default internal-resistance extractor (issue #23).      For each cycle it read (+5 more)

### Community 52 - "Community 52"
Cohesion: 0.33
Nodes (9): Converter-parity tests for ``cellpycore.units`` (STEP-12, issue #40).  ``cellp, Minimal stand-in for ``Data`` exposing only what the converters read., _stub(), test_get_converter_to_specific_charge_unit_mismatch(), test_get_converter_to_specific_modes(), test_get_converter_to_specific_unknown_mode_is_identity(), test_nominal_capacity_as_absolute_convert_charge_units(), test_nominal_capacity_as_absolute_explicit_value_and_specific() (+1 more)

### Community 53 - "Community 53"
Cohesion: 0.67
Nodes (3): A raw frame without test_id yields tables whose test_id column is all 0., A raw frame without test_id yields tables whose test_id column is all 0., test_single_test_defaults_test_id_to_zero()

### Community 54 - "Community 54"
Cohesion: 0.12
Nodes (16): _build_raw(), _data_with_raw(), c_rate = abs(current_mean / nom_cap): doubling nom_cap halves the rate., c_rate = abs(current_mean / nom_cap): doubling nom_cap halves the rate., c_rate = abs(current_mean / nom_cap): doubling nom_cap halves the rate., Build a minimal native-named raw DataFrame (2 cycles x charge/discharge/rest)., Build a minimal native-named raw DataFrame (2 cycles x charge/discharge/rest)., ir_to_summary adds ir_charge/ir_discharge (native, default extractor). (+8 more)

### Community 56 - "Community 56"
Cohesion: 0.12
Nodes (19): Column-header definitions for the harmonized raw data table.      Each attribu, Column-header definitions for the harmonized raw data table.      Each attribu, Column-header definitions for the harmonized raw data table.      Each attribu, RawCols, _build_cumulative_raw(), _cap_lists(), 2 cycles, each charge then discharge, with cycle-cumulative capacities held., Return the (charge, discharge) cumulative capacity lists, datapoint-ordered. (+11 more)

### Community 61 - "Community 61"
Cohesion: 0.19
Nodes (11): CellpyUnits, MockCore, These are the units used inside Cellpy.      At least two sets of units needs, CellpyUnits, get_cellpy_units(), get_default_output_units(), Returns an augmented global dictionary with units, Returns an augmented dictionary with units to use as default. (+3 more)

### Community 63 - "Community 63"
Cohesion: 0.5
Nodes (4): TestMode.INVERTED (anode) flips CE and coulombic_difference references., TestMode.INVERTED (anode) flips CE and coulombic_difference references., TestMode.INVERTED (anode) flips CE and coulombic_difference references., test_make_summary_anode_flips_coulombic_columns()

### Community 64 - "Community 64"
Cohesion: 0.21
Nodes (3): DictLikeClass, Get the value (postfixes not supported)., Add some dunder-methods so that it does not break old code that used     dictio

### Community 65 - "Community 65"
Cohesion: 0.17
Nodes (12): _ir_raw_steps(), Hand-built native raw + steps exercising the IR-extraction rules.      cycle 1, Hand-built native raw + steps exercising the IR-extraction rules.      cycle 1, Hand-built native raw + steps exercising the IR-extraction rules.      cycle 1, Default extractor picks the last datapoint of the last charge/discharge     ste, Default extractor picks the last datapoint of the last charge/discharge     ste, Default extractor picks the last datapoint of the last charge/discharge     ste, A custom SummaryExtractor passed via ir_extractor overrides the default. (+4 more)

### Community 67 - "Community 67"
Cohesion: 0.2
Nodes (10): Distinct step-type labels from a (polars) native step table., Step-type classification uses the supplied raw_limits, not a fixed default., Step-type classification uses the supplied raw_limits, not a fixed default., Step-type classification uses the supplied raw_limits, not a fixed default., Raw without ref_potential yields no ref_potential_* columns, engine unaffected., Raw without ref_potential yields no ref_potential_* columns, engine unaffected., Distinct step-type labels from a (polars) native step table., test_raw_limits_affect_classification() (+2 more)

### Community 68 - "Community 68"
Cohesion: 0.07
Nodes (21): from_raw_frame(), # TODO: v2.0 edit this from scalar to list, # TODO: v2.0 edit this from scalar to list, # TODO: move the data object to slim, # TODO: copy div settings to slim, Make the core summary.          Args:             data: The data to make the, Make the core summary.          Args:             data: The data to make the, # TODO: v2.0 edit this from scalar to list (+13 more)

### Community 69 - "Community 69"
Cohesion: 0.22
Nodes (5): BaseSettings, Generic dict-like settings base classes shared across cellpy-core.  These were, Base class for internal cellpy settings.      Usage::           @dataclass, Get the value (postfixes not supported)., Converts to pandas dataframe

### Community 73 - "Community 73"
Cohesion: 0.5
Nodes (4): generate_specific_summary_columns multiplies by the given factor (no pint)., generate_specific_summary_columns multiplies by the given factor (no pint)., generate_specific_summary_columns multiplies by the given factor (no pint)., test_generate_specific_columns_takes_factor_by_value()

## Knowledge Gaps
- **503 isolated node(s):** `# TODO: dtype should be a python native "dtype object" if it exists, or a pl.Dat`, `Build the harmonized raw frame from a legacy-named frame.      Args:`, `Load each source with cellpy and write ``<name>_raw.parquet``.`, `Run the current cellpy-core engine on the raw parquet and snapshot the     step`, `Validate a native-schema raw frame against ``config.RawCols``.      Checks tha` (+498 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `default_schema()` connect `Community 0` to `Community 2`, `Community 7`, `Community 16`, `Community 50`, `Community 51`, `Community 56`?**
  _High betweenness centrality (0.163) - this node is a cross-community bridge._
- **Why does `Data` connect `Community 20` to `Community 0`, `Community 65`, `Community 68`, `Community 73`, `Community 11`, `Community 12`, `Community 13`, `Community 16`, `Community 17`, `Community 21`, `Community 54`, `Community 56`, `Community 28`, `Community 61`, `Community 30`?**
  _High betweenness centrality (0.160) - this node is a cross-community bridge._
- **Why does `RawCols` connect `Community 56` to `Community 0`, `Community 65`, `Community 2`, `Community 67`, `Community 5`, `Community 7`, `Community 13`, `Community 49`, `Community 53`, `Community 54`, `Community 21`, `Community 30`, `Community 63`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `OldCellpyCellCore` (e.g. with `NoDataFound` and `Meta`) actually correct?**
  _`OldCellpyCellCore` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 27 inferred relationships involving `RawCols` (e.g. with `main()` and `create_raw_data()`) actually correct?**
  _`RawCols` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `Data` (e.g. with `NoDataFound` and `Meta`) actually correct?**
  _`Data` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `default_schema()` (e.g. with `.make_core_step_table()` and `.add_scaled_summary_columns()`) actually correct?**
  _`default_schema()` has 21 INFERRED edges - model-reasoned connections that need verification._