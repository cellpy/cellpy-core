# Graph Report - cellpy-core  (2026-06-30)

## Corpus Check
- 44 files · ~45,501 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 670 nodes · 863 edges · 49 communities (38 shown, 11 thin omitted)
- Extraction: 86% EXTRACTED · 14% INFERRED · 0% AMBIGUOUS · INFERRED: 125 edges (avg confidence: 0.75)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d3a902df`
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

## God Nodes (most connected - your core abstractions)
1. `OldCellpyCellCore` - 28 edges
2. `Data` - 21 edges
3. `RawCols` - 19 edges
4. `default_schema()` - 19 edges
5. `CellpyCellCore` - 16 edges
6. `Cursor issue workflow (Agent Skills)` - 16 edges
7. `TestMetaCollection` - 12 edges
8. `DictLikeClass` - 11 edges
9. `_data_with_raw()` - 11 edges
10. `Development information` - 11 edges

## Surprising Connections (you probably didn't know these)
- `mock_data_empty()` --calls--> `Data`  [INFERRED]
  tests/conftest.py → src/cellpycore/cell_core.py
- `main()` --calls--> `create_raw_data()`  [INFERRED]
  dev/demo_mock_data.py → src/cellpycore/_helpers.py
- `main()` --calls--> `RawCols`  [INFERRED]
  dev/make_harmonized_raw.py → src/cellpycore/config.py
- `stage_b_engine_snapshot()` --calls--> `OldCellpyCellCore`  [INFERRED]
  dev/regenerate_test_data.py → src/cellpycore/cell_core.py
- `mock_data_with_raw()` --calls--> `Data`  [INFERRED]
  tests/conftest.py → src/cellpycore/cell_core.py

## Communities (49 total, 11 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (49): default_schema(), Bundle of the column-header objects for one cell.      Holds the raw, cycle (s, Return a Schema using the native cellpy-core column definitions.      Used as, Schema, LastIRExtractor, Pluggable per-cycle summary extractors.  A *summary extractor* is a callable o, Base class for callable per-cycle summary extractors.      Subclasses implemen, Return a per-cycle frame keyed by ``schema.cycle.cycle_num``.          Args: (+41 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (42): fetch_from_db(), from_dict(), from_json(), load_archive(), merge_test_meta(), push_to_db(), (De)serialization, merging, and persistence scaffolding for metadata.  This is, Load metadata from a cellpy archive file (HDF5). **Stub.**      Intended to re (+34 more)

### Community 2 - "Community 2"
Cohesion: 0.08
Nodes (41): Column-header definitions for the per-step summary table.      Each attribute, Column-header definitions for the harmonized raw data table.      Each attribu, RawCols, StepCols, _build_cumulative_raw(), _build_raw(), _data_with_raw(), _ir_raw_steps() (+33 more)

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
Cohesion: 0.1
Nodes (22): BaseCols, Cols, cols_check(), CycleCols, CycleType, FlexibleCols, Control mode of a step for the ``step_mode`` column of the raw table.      Des, Cycle classification for the ``cycle_type`` column of the raw table.      A *r (+14 more)

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
Cohesion: 0.16
Nodes (7): OldCellpyCellCore, Legacy CellpyCellCore class to make it easier to migrate to cellpy core., Build the step table via the polars engine, in/out in legacy form.          Se, Map the ``info`` column from step specifications onto the step table., Add the pandas-only legacy summary columns the native schema omits.          `, Build the per-cycle summary via the polars engine, in/out in legacy form., Legacy-bridge ``add_scaled_summary_columns`` (pandas<->polars seam).

### Community 12 - "Community 12"
Cohesion: 0.12
Nodes (13): BaseSettings, CellpyError, CellpyUnits, MockCore, NoDataFound, Converts to pandas dataframe, These are the units used inside Cellpy.      At least two sets of units needs, Base class for other exceptions (+5 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (14): Cols, CycleCols, # TODO: dtype should be a python native "dtype object" if it exists, or a pl.Dat, simple_cols_check(), SimpleCols, super_duper_cols_check(), SuperDuperCols, SuperDuperColsBase (+6 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (17): 0. `/iflow` — smart dispatcher (quick start), 0a. `/iflow-pick` — choose the next issue (front door), 10. `/iflow-status` — status overview of all issues (read-only), 1. `/iflow-init` — capture the issue locally, 2. `/iflow-plan` — design the approach, 3. `/iflow-start` — implement the plan, 4. `/iflow-pause` — park work safely, 5. `/iflow-close` — land the work (+9 more)

### Community 15 - "Community 15"
Cohesion: 0.12
Nodes (16): Add on's, Cellpy Core Functionality, Cellpy Core Input (Harmonized_Raw), Cellpy Core Output, Core CycleTable, Current code structure:, Definition of Cellpy Core Functionality, Headers (+8 more)

### Community 16 - "Community 16"
Cohesion: 0.19
Nodes (16): _legacy_schema(), Golden / regression tests on real cycling data vendored as parquet.  The fixtu, The per-cycle summary has one row per cycle and the expected cyc-1 datapoint., Lock the current summary output as the regression oracle for the issue #13, Cross-repo parity (Phase 4): cellpy-core reproduces cellpy's own committed, Smoke test: a tiny (47-row, 3-step) real raw frame flows through the engine., cellpy-core reproduces cellpy's published step/cycle goldens on real data., Lock the current engine output so the polars rewrite (issue #13) stays faithful. (+8 more)

### Community 17 - "Community 17"
Cohesion: 0.14
Nodes (14): BaseHeaders, HeadersNormal, HeadersStepTable, HeadersSummary, Subclass of BaseSetting including option to add postfixes.      Example:, Headers used for the normal (raw) data (used as column headers for the main data, Headers used for the summary data (used as column headers for the main data pand, Headers used for the steps table (used as column headers for the steps pandas Da (+6 more)

### Community 18 - "Community 18"
Cohesion: 0.15
Nodes (12): cellpy-core, code:bash (pip install uv), code:bash (uv venv), code:bash (uv pip install -e ".[dev]"), code:bash (# Add a new package), code:bash (# Update all packages), code:bash (pytest), Common Commands (+4 more)

### Community 19 - "Community 19"
Cohesion: 0.21
Nodes (3): DictLikeClass, Get the value (postfixes not supported)., Add some dunder-methods so that it does not break old code that used     dictio

### Community 20 - "Community 20"
Cohesion: 0.18
Nodes (7): CellpyCellCore, Make the core summary.          Args:             data: The data to make the, Add specific summary columns to the summary.          Args:             data:, Resolve the specific-capacity conversion factor for a mode.          Prefers t, Make the core step table.          Delegates to ``summarizers.make_step_table`, Args:             initialize (bool): set to True if you want to initialize the, Initialize the CellpyCell object with empty Data instance.

### Community 21 - "Community 21"
Cohesion: 0.19
Nodes (11): _check_value_unit(), Parse for unit, update cellpy_units class, and return magnitude., get_converter_to_specific(), _get_unit_registry(), nominal_capacity_as_absolute(), Q(), Get the nominal capacity as absolute value., Create (once) and return the pint UnitRegistry.      pint recommends a single (+3 more)

### Community 22 - "Community 22"
Cohesion: 0.2
Nodes (11): legacy_to_native_raw(), legacy_to_native_step(), legacy_to_native_summary(), native_to_legacy_step(), native_to_legacy_summary(), Authoritative ``config.Cols`` <-> legacy ``Headers*`` column-name mapping.  Th, Return the legacy -> native rename dict for the raw frame.      Args:, Return the native -> legacy rename dict for the step table.      Expands :data (+3 more)

### Community 23 - "Community 23"
Cohesion: 0.24
Nodes (8): _declared_columns(), Conformance tests: config.py column classes match docs/data_format_specification, The renamed/removed legacy names are gone from RawCols., Map declared column attribute -> its string value for a Cols subclass., test_cycle_cols_match_spec(), test_no_legacy_raw_names(), test_raw_cols_match_spec(), test_step_cols_match_spec()

### Community 24 - "Community 24"
Cohesion: 0.24
Nodes (9): CellpyLimits, Thresholds used when classifying step types in ``make_step_table``.      Since, Tests for the CellpyLimits port (issue #12, Phase 1).  CellpyLimits holds the, CellpyLimits behaves like a dict (BaseSettings), as the engine indexes it., The canonical step-type labels include the ones make_step_table assigns., test_cellpy_limits_is_dict_like(), test_cellpy_limits_values_match_legacy(), test_default_raw_limits_derived_from_cellpy_limits() (+1 more)

### Community 25 - "Community 25"
Cohesion: 0.2
Nodes (9): Auxillary columns, Capacity convention, Cellpy Core Harmonized_Raw, Column Headers, Conventions, Follow-ups, Other discussion points, Purpose (+1 more)

### Community 26 - "Community 26"
Cohesion: 0.2
Nodes (9): Test that cellpycore can be imported successfully., Test that cellpycore has the expected package structure., Test that cellpycore has a version attribute (if defined)., Test that cellpycore is properly registered in sys.modules., Test that cellpycore can be imported., test_cellpycore_import(), test_cellpycore_in_sys_modules(), test_cellpycore_package_structure() (+1 more)

### Community 27 - "Community 27"
Cohesion: 0.22
Nodes (4): # TODO: v2.0 edit this from scalar to list, # TODO: v2.0 edit this from scalar to list, # TODO: move the data object to slim, # TODO: copy div settings to slim

### Community 28 - "Community 28"
Cohesion: 0.22
Nodes (6): create_raw_data(), Helper functions only intended for development purposes  (e.g. for creating mock, Create mock raw battery testing data with realistic values.      TODO: This fu, main(), mock_data_empty(), mock_data_with_raw()

### Community 29 - "Community 29"
Cohesion: 0.25
Nodes (7): code:bash (# Stage A — raw export (needs cellpy + Arbin ODBC for the .r), code:bash (uv run python dev/make_harmonized_raw.py), Files, Golden numbers, Provenance & license, Regenerating, Test data fixtures

### Community 30 - "Community 30"
Cohesion: 0.47
Nodes (5): Data, Meta, MockMetaTestDependent, Run the current cellpy-core engine on the raw parquet and snapshot the     step, stage_b_engine_snapshot()

### Community 31 - "Community 31"
Cohesion: 0.5
Nodes (3): Cellpy Core CycleTable (DRAFT), Column Headers, Purpose

### Community 32 - "Community 32"
Cohesion: 0.5
Nodes (3): Cellpy Core StepTable (DRAFT), Column Headers, Purpose

## Knowledge Gaps
- **315 isolated node(s):** `# TODO: dtype should be a python native "dtype object" if it exists, or a pl.Dat`, `Build the harmonized raw frame from a legacy-named frame.      Args:`, `Load each source with cellpy and write ``<name>_raw.parquet``.`, `Run the current cellpy-core engine on the raw parquet and snapshot the     step`, `True if a step table has been computed.` (+310 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `default_schema()` connect `Community 0` to `Community 2`, `Community 11`, `Community 7`?**
  _High betweenness centrality (0.134) - this node is a cross-community bridge._
- **Why does `OldCellpyCellCore` connect `Community 11` to `Community 10`, `Community 12`, `Community 16`, `Community 17`, `Community 20`, `Community 27`, `Community 30`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Why does `RawCols` connect `Community 2` to `Community 0`, `Community 28`, `Community 5`, `Community 7`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `OldCellpyCellCore` (e.g. with `NoDataFound` and `Meta`) actually correct?**
  _`OldCellpyCellCore` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `Data` (e.g. with `NoDataFound` and `Meta`) actually correct?**
  _`Data` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `RawCols` (e.g. with `main()` and `create_raw_data()`) actually correct?**
  _`RawCols` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `default_schema()` (e.g. with `.make_core_step_table()` and `.add_scaled_summary_columns()`) actually correct?**
  _`default_schema()` has 13 INFERRED edges - model-reasoned connections that need verification._