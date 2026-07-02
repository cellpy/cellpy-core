# Graph Report - cellpy-core  (2026-07-02)

## Corpus Check
- 47 files · ~48,949 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 819 nodes · 1112 edges · 61 communities (46 shown, 15 thin omitted)
- Extraction: 83% EXTRACTED · 17% INFERRED · 0% AMBIGUOUS · INFERRED: 186 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8d65fb2f`
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

## God Nodes (most connected - your core abstractions)
1. `OldCellpyCellCore` - 31 edges
2. `Data` - 30 edges
3. `RawCols` - 29 edges
4. `CellpyUnits` - 25 edges
5. `default_schema()` - 21 edges
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

## Communities (61 total, 15 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.12
Nodes (20): default_schema(), Return a Schema using the native cellpy-core column definitions.      Used as, Return a Schema using the native cellpy-core column definitions.      Used as, create_selector(), get_cycle_numbers(), get_rates(), get_step_numbers(), # TODO: implement also for energy and power (and probably others as well) - this (+12 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (42): fetch_from_db(), from_dict(), from_json(), load_archive(), merge_test_meta(), push_to_db(), (De)serialization, merging, and persistence scaffolding for metadata.  This is, Load metadata from a cellpy archive file (HDF5). **Stub.**      Intended to re (+34 more)

### Community 2 - "Community 2"
Cohesion: 0.12
Nodes (18): Column-header definitions for the per-step summary table.      Each attribute, Column-header definitions for the per-step summary table.      Each attribute, StepCols, _ir_raw_steps(), The output column names follow the injected (native) schema, not any global., The output column names follow the injected (native) schema, not any global., Two cells with different schemas each emit their own column names., Two cells with different schemas each emit their own column names. (+10 more)

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
Nodes (32): BaseCols, Cols, cols_check(), CycleCols, CycleType, FlexibleCols, Canonical step-type labels for the ``step_type`` column of the step table., Control mode of a step for the ``step_mode`` column of the raw table.      Des (+24 more)

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
Cohesion: 0.06
Nodes (23): OldCellpyCellCore, # TODO: v2.0 edit this from scalar to list, # TODO: v2.0 edit this from scalar to list, Legacy CellpyCellCore class to make it easier to migrate to cellpy core., Build the step table via the polars engine, in/out in legacy form.          Se, # TODO: move the data object to slim, Map the ``info`` column from step specifications onto the step table., # TODO: copy div settings to slim (+15 more)

### Community 12 - "Community 12"
Cohesion: 0.14
Nodes (10): CellpyError, NoDataFound, Base class for other exceptions, Exception raised when no data is found, Base class for other exceptions, Exception raised when no data is found, Set selected columns first in a pandas.DataFrame.      This function sets cols, Set selected columns first in a pandas.DataFrame.      This function sets cols (+2 more)

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
Cohesion: 0.2
Nodes (9): BaseHeaders, HeadersStepTable, HeadersSummary, Headers used for the summary data (used as column headers for the main data pand, Subclass of BaseSetting including option to add postfixes.      Example:, Headers used for the steps table (used as column headers for the steps pandas Da, Headers used for the summary data (used as column headers for the main data pand, Headers used for the steps table (used as column headers for the steps pandas Da (+1 more)

### Community 18 - "Community 18"
Cohesion: 0.15
Nodes (12): cellpy-core, code:bash (pip install uv), code:bash (uv venv), code:bash (uv pip install -e ".[dev]"), code:bash (# Add a new package), code:bash (# Update all packages), code:bash (pytest), Common Commands (+4 more)

### Community 19 - "Community 19"
Cohesion: 0.06
Nodes (31): BaseSettings, CellpyUnits, _check_value_unit(), DictLikeClass, Get the value (postfixes not supported)., Converts to pandas dataframe, These are the units used inside Cellpy.      At least two sets of units needs, Parse for unit, update cellpy_units class, and return magnitude. (+23 more)

### Community 20 - "Community 20"
Cohesion: 0.15
Nodes (9): CellpyCellCore, Make the core summary.          Args:             data: The data to make the, Add specific summary columns to the summary.          Args:             data:, Resolve the specific-capacity conversion factor for a mode.          Prefers t, Make the core step table.          Delegates to ``summarizers.make_step_table`, Args:             initialize (bool): set to True if you want to initialize the, Initialize the CellpyCell object with empty Data instance., Meta (+1 more)

### Community 21 - "Community 21"
Cohesion: 0.12
Nodes (19): _build_raw(), _build_step_cumulative_raw(), _build_test_cumulative_raw(), Tests for the injected Schema bundle and the step-table port.  These prove the, The globals bridge is gone: no module-level header/unit globals remain., Distinct step-type labels from a (polars) native step table., The globals bridge is gone: no module-level header/unit globals remain., Build a minimal native-named raw DataFrame (2 cycles x charge/discharge/rest). (+11 more)

### Community 22 - "Community 22"
Cohesion: 0.13
Nodes (16): legacy_to_native_raw(), legacy_to_native_step(), legacy_to_native_summary(), native_to_legacy_step(), native_to_legacy_summary(), Authoritative ``config.Cols`` <-> legacy ``Headers*`` column-name mapping.  Th, Return the legacy -> native rename dict for the raw frame.      Args:, Return the legacy -> native rename dict for the raw frame.      Args: (+8 more)

### Community 23 - "Community 23"
Cohesion: 0.21
Nodes (9): _declared_columns(), Conformance tests: config.py column classes match docs/data_format_specification, The renamed/removed legacy names are gone from RawCols., The renamed/removed legacy names are gone from RawCols., Map declared column attribute -> its string value for a Cols subclass., test_cycle_cols_match_spec(), test_no_legacy_raw_names(), test_raw_cols_match_spec() (+1 more)

### Community 24 - "Community 24"
Cohesion: 0.2
Nodes (11): BaseSettings, CellpyLimits, Thresholds used when classifying step types in ``make_step_table``.      Since, Thresholds used when classifying step types in ``make_step_table``.      Since, Tests for the CellpyLimits port (issue #12, Phase 1).  CellpyLimits holds the, CellpyLimits behaves like a dict (BaseSettings), as the engine indexes it., The canonical step-type labels include the ones make_step_table assigns., test_cellpy_limits_is_dict_like() (+3 more)

### Community 25 - "Community 25"
Cohesion: 0.2
Nodes (9): Auxillary columns, Capacity convention, Cellpy Core Harmonized_Raw, Column Headers, Conventions, Follow-ups, Other discussion points, Purpose (+1 more)

### Community 26 - "Community 26"
Cohesion: 0.2
Nodes (9): Test that cellpycore can be imported successfully., Test that cellpycore has the expected package structure., Test that cellpycore has a version attribute (if defined)., Test that cellpycore is properly registered in sys.modules., Test that cellpycore can be imported., test_cellpycore_import(), test_cellpycore_in_sys_modules(), test_cellpycore_package_structure() (+1 more)

### Community 27 - "Community 27"
Cohesion: 0.14
Nodes (7): BaseSettings, DictLikeClass, Generic dict-like settings base classes shared across cellpy-core.  These were, Add some dunder-methods so that it does not break old code that used     dictio, Base class for internal cellpy settings.      Usage::           @dataclass, Get the value (postfixes not supported)., Converts to pandas dataframe

### Community 28 - "Community 28"
Cohesion: 0.25
Nodes (6): create_raw_data(), Helper functions only intended for development purposes  (e.g. for creating mock, Create mock raw battery testing data with realistic values.      TODO: This fu, main(), The synthetic mock raw fixture exercises the ref_potential column., test_mock_raw_data_carries_ref_potential()

### Community 29 - "Community 29"
Cohesion: 0.25
Nodes (7): code:bash (# Stage A — raw export (needs cellpy + Arbin ODBC for the .r), code:bash (uv run python dev/make_harmonized_raw.py), Files, Golden numbers, Provenance & license, Regenerating, Test data fixtures

### Community 30 - "Community 30"
Cohesion: 0.18
Nodes (12): Data, mock_data_empty(), mock_data_with_raw(), _build_merged_raw(), generate_specific_summary_columns multiplies by the given factor (no pint)., generate_specific_summary_columns multiplies by the given factor (no pint)., Two tests (test_id 0 and 1) with **overlapping** cycle_num/step_num.      Each, A merged object (2 tests, overlapping cycle/step) keeps every step row.      W (+4 more)

### Community 31 - "Community 31"
Cohesion: 0.5
Nodes (3): Cellpy Core CycleTable (DRAFT), Column Headers, Purpose

### Community 32 - "Community 32"
Cohesion: 0.5
Nodes (3): Cellpy Core StepTable (DRAFT), Column Headers, Purpose

### Community 49 - "Community 49"
Cohesion: 0.14
Nodes (18): Column-header definitions for the harmonized raw data table.      Each attribu, Column-header definitions for the harmonized raw data table.      Each attribu, RawCols, _native_schema(), c_rate = abs(current_mean / nom_cap): doubling nom_cap halves the rate., c_rate = abs(current_mean / nom_cap): doubling nom_cap halves the rate., Step-type classification uses the supplied raw_limits, not a fixed default., Step-type classification uses the supplied raw_limits, not a fixed default. (+10 more)

### Community 50 - "Community 50"
Cohesion: 0.15
Nodes (15): _add_end_potentials(), _ensure_test_id(), generate_specific_summary_columns(), _group_keys(), make_summary(), normalize_capacity_granularity(), Join per-cycle end-of-charge / end-of-discharge potentials onto ``summary``., Polars-native per-cycle summary (the clean native ``CycleCols`` subset). (+7 more)

### Community 51 - "Community 51"
Cohesion: 0.15
Nodes (12): Bundle of the column-header objects for one cell.      Holds the raw, cycle (s, Bundle of the column-header objects for one cell.      Holds the raw, cycle (s, Schema, LastIRExtractor, Pluggable per-cycle summary extractors.  A *summary extractor* is a callable o, Base class for callable per-cycle summary extractors.      Subclasses implemen, Return a per-cycle frame keyed by ``schema.cycle.cycle_num``.          Args:, Default internal-resistance extractor (issue #23).      For each cycle it read (+4 more)

### Community 52 - "Community 52"
Cohesion: 0.22
Nodes (12): MockCore, CellpyUnits, These are the units used inside Cellpy.      At least two sets of units needs, Converter-parity tests for ``cellpycore.units`` (STEP-12, issue #40).  ``cellp, Minimal stand-in for ``Data`` exposing only what the converters read., _stub(), test_get_converter_to_specific_charge_unit_mismatch(), test_get_converter_to_specific_modes() (+4 more)

### Community 53 - "Community 53"
Cohesion: 0.17
Nodes (12): _classify_from_specifications(), _classify_steps(), _delta_expr(), make_step_table(), Per-step delta in percent (mirrors legacy cellpy's ``delta``).      ``100 * la, Create a table (v.5) that contains summary information for each step.      Thi, Build a step-type expression from explicit step specifications., Return a polars expression classifying each step into a step type.      Mirror (+4 more)

### Community 54 - "Community 54"
Cohesion: 0.2
Nodes (10): _data_with_raw(), c_rates_to_summary joins per-cycle first charge/discharge C-rates (native)., c_rates_to_summary joins per-cycle first charge/discharge C-rates (native)., ir_to_summary adds ir_charge/ir_discharge (native, default extractor)., ir_to_summary adds ir_charge/ir_discharge (native, default extractor)., The native CellpyCellCore add_scaled path runs on the polars summary., The native CellpyCellCore add_scaled path runs on the polars summary., test_c_rates_to_summary_native() (+2 more)

### Community 55 - "Community 55"
Cohesion: 0.22
Nodes (9): c_rates_to_summary(), _calculate_nominal_capacity_from_cycles(), equivalent_cycles_to_summary(), Calculate nominal capacity from specified normalization cycles.      Polars-na, Add the ``normalized_cycle_index`` (equivalent cycles) column to the summary., Add per-cycle charge / discharge C-rates to the summary.      Polars-native: t, Calculate nominal capacity from specified normalization cycles.      Polars-na, Add the ``normalized_cycle_index`` (equivalent cycles) column to the summary. (+1 more)

### Community 56 - "Community 56"
Cohesion: 0.25
Nodes (9): _build_cumulative_raw(), _cap_lists(), 2 cycles, each charge then discharge, with cycle-cumulative capacities held., Return the (charge, discharge) cumulative capacity lists, datapoint-ordered., 2 cycles, each charge then discharge, with cycle-cumulative capacities held., STEP / TEST cumulative raw normalizes to the cycle-cumulative oracle., A CYCLE input is returned untouched (goldens stay byte-stable)., test_normalize_capacity_granularity_cycle_is_noop() (+1 more)

### Community 57 - "Community 57"
Cohesion: 0.33
Nodes (6): HeadersNormal, Headers used for the normal (raw) data (used as column headers for the main data, Headers used for the normal (raw) data (used as column headers for the main data, CellpyCellCore.schema bundles the (possibly overridden) header instances., CellpyCellCore.schema bundles the (possibly overridden) header instances., test_schema_property_reflects_headers()

## Knowledge Gaps
- **411 isolated node(s):** `# TODO: dtype should be a python native "dtype object" if it exists, or a pl.Dat`, `Build the harmonized raw frame from a legacy-named frame.      Args:`, `Load each source with cellpy and write ``<name>_raw.parquet``.`, `Run the current cellpy-core engine on the raw parquet and snapshot the     step`, `True if a step table has been computed.` (+406 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Data` connect `Community 30` to `Community 2`, `Community 11`, `Community 12`, `Community 13`, `Community 16`, `Community 17`, `Community 20`, `Community 52`, `Community 54`, `Community 21`, `Community 56`, `Community 57`?**
  _High betweenness centrality (0.150) - this node is a cross-community bridge._
- **Why does `default_schema()` connect `Community 0` to `Community 2`, `Community 7`, `Community 11`, `Community 49`, `Community 50`, `Community 51`, `Community 53`, `Community 55`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Why does `RawCols` connect `Community 49` to `Community 0`, `Community 2`, `Community 5`, `Community 7`, `Community 21`, `Community 54`, `Community 56`, `Community 28`, `Community 30`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `OldCellpyCellCore` (e.g. with `NoDataFound` and `Meta`) actually correct?**
  _`OldCellpyCellCore` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `Data` (e.g. with `NoDataFound` and `Meta`) actually correct?**
  _`Data` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 24 inferred relationships involving `RawCols` (e.g. with `main()` and `create_raw_data()`) actually correct?**
  _`RawCols` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `CellpyUnits` (e.g. with `CellpyError` and `NoDataFound`) actually correct?**
  _`CellpyUnits` has 19 INFERRED edges - model-reasoned connections that need verification._