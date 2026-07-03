# Graph Report - cellpy-core  (2026-07-03)

## Corpus Check
- 52 files · ~53,480 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1162 nodes · 1596 edges · 109 communities (80 shown, 29 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 284 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f1116b43`
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
- [[_COMMUNITY_Community 45|Community 45]]
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
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 87|Community 87]]
- [[_COMMUNITY_Community 88|Community 88]]
- [[_COMMUNITY_Community 89|Community 89]]
- [[_COMMUNITY_Community 90|Community 90]]
- [[_COMMUNITY_Community 91|Community 91]]
- [[_COMMUNITY_Community 92|Community 92]]
- [[_COMMUNITY_Community 93|Community 93]]
- [[_COMMUNITY_Community 94|Community 94]]
- [[_COMMUNITY_Community 95|Community 95]]
- [[_COMMUNITY_Community 96|Community 96]]
- [[_COMMUNITY_Community 97|Community 97]]
- [[_COMMUNITY_Community 98|Community 98]]
- [[_COMMUNITY_Community 99|Community 99]]
- [[_COMMUNITY_Community 100|Community 100]]
- [[_COMMUNITY_Community 101|Community 101]]
- [[_COMMUNITY_Community 102|Community 102]]
- [[_COMMUNITY_Community 103|Community 103]]
- [[_COMMUNITY_Community 104|Community 104]]
- [[_COMMUNITY_Community 105|Community 105]]
- [[_COMMUNITY_Community 106|Community 106]]
- [[_COMMUNITY_Community 107|Community 107]]
- [[_COMMUNITY_Community 108|Community 108]]

## God Nodes (most connected - your core abstractions)
1. `RawCols` - 43 edges
2. `Data` - 38 edges
3. `OldCellpyCellCore` - 36 edges
4. `default_schema()` - 35 edges
5. `HeadersNormal` - 28 edges
6. `HeadersStepTable` - 27 edges
7. `HeadersSummary` - 26 edges
8. `CellpyUnits` - 26 edges
9. `DictLikeClass` - 22 edges
10. `_native_schema()` - 21 edges

## Surprising Connections (you probably didn't know these)
- `test_native_pipeline_matches_golden_counts()` --calls--> `default_schema()`  [INFERRED]
  tests/test_e2e.py → src/cellpycore/config.py
- `test_native_pipeline_step_types_and_capacities()` --calls--> `default_schema()`  [INFERRED]
  tests/test_e2e.py → src/cellpycore/config.py
- `test_default_schema_is_native()` --calls--> `default_schema()`  [INFERRED]
  tests/test_schema.py → src/cellpycore/config.py
- `main()` --calls--> `create_raw_data()`  [INFERRED]
  dev/demo_mock_data.py → src/cellpycore/_helpers.py
- `main()` --calls--> `RawCols`  [INFERRED]
  dev/make_harmonized_raw.py → src/cellpycore/config.py

## Communities (109 total, 29 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.16
Nodes (21): _build_cv_raw(), _data_with_steps(), _pandas_oracle(), Tests for native exclude-types summary support (issue #54).  ``summarizers.mak, exclude_step_types=["cv_"] reproduces the removed pandas implementation., CE / coulombic difference are computed from the corrected capacities., None (default) and [] are byte-identical to the plain summary., A prefix matching no step yields the uncorrected summary (fill_null path). (+13 more)

### Community 1 - "Community 1"
Cohesion: 0.05
Nodes (42): fetch_from_db(), from_dict(), from_json(), load_archive(), merge_test_meta(), push_to_db(), (De)serialization, merging, and persistence scaffolding for metadata.  This is, Load metadata from a cellpy archive file (HDF5). **Stub.**      Intended to re (+34 more)

### Community 2 - "Community 2"
Cohesion: 0.25
Nodes (8): The pandas selector pair was removed once cellpy migrated off it (#45)., The pandas selector pair was removed once cellpy migrated off it (#45)., The output column names follow the injected (native) schema, not any global., The output column names follow the injected (native) schema, not any global., The output column names follow the injected (native) schema, not any global., The output column names follow the injected (native) schema, not any global., test_make_step_table_uses_injected_schema(), test_no_legacy_selector_functions()

### Community 3 - "Community 3"
Cohesion: 0.06
Nodes (34): 1. Context and guiding principle, 1. Introduction: The Industrial Data Scalability Paradigm, 2. Core Challenges in High-Volume Data Management, 3.1 The M4 Algorithm, 3.2 LTTB and MinMaxLTTB, 3.3 Hierarchical Aggregation and the Visual Entity Budget, 3. Algorithmic Solutions for Scalable Visualization, 3. Implementation details (+26 more)

### Community 4 - "Community 4"
Cohesion: 0.22
Nodes (9): Basic Structure, Class Documentation, Code Documentation, code:python (def function_name(param1: str, param2: int = 10) -> bool:), code:python (class ExampleClass:), code:python ("""Module-level docstring.), Docstring Format, Documentation Standards (+1 more)

### Community 5 - "Community 5"
Cohesion: 0.08
Nodes (30): datetime_to_epoch_ns(), datetime_to_epoch_ns_expr(), epoch_ns_to_datetime(), epoch_ns_to_seconds(), epoch_ns_to_seconds_expr(), Build a ``polars`` expression converting a ``Datetime`` column to epoch ns., Build a ``polars`` expression converting a ``Datetime`` column to epoch ns., Build a ``polars`` expression converting epoch ns to float epoch seconds. (+22 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (27): Auto-Clarity, Be token greedy - as a caveman, Boundaries, Branch hygiene, code:bash (# Either activate the environment first…), code:bash (# ❌ BAD: bare interpreter), code:bash (# Add or upgrade dependencies), code:bash (cellpycore/) (+19 more)

### Community 7 - "Community 7"
Cohesion: 0.06
Nodes (56): BaseCols, Cols, cols_check(), CycleCols, CycleType, FlexibleCols, Canonical step-type labels for the ``step_type`` column of the step table., Control mode of a step for the ``step_mode`` column of the raw table.      Des (+48 more)

### Community 8 - "Community 8"
Cohesion: 0.22
Nodes (9): `cell_core.py`, Code Structure and Principles, code:block6 (src/cellpycore/), `config.py`, Module Responsibilities, Project Architecture, `selectors.py`, `summarizers.py` (+1 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (24): 2. Stages, Before Stage 0 closes, Before Stage 2 starts, Before Stage 3 starts, Deliverables, Deliverables, Deliverables, Deliverables (+16 more)

### Community 10 - "Community 10"
Cohesion: 0.14
Nodes (16): _assert_pairs_bijective(), _legacy_values(), _native_values(), Round-trip / totality tests for the authoritative header mapping.  These lock, Distinct column-name strings declared on a native ``config.Cols`` class., Distinct column-name strings declared on a legacy ``Headers*`` dataclass., Reduce a step column ``<signal>_<stat>`` to its base ``<signal>``., _step_signal() (+8 more)

### Community 11 - "Community 11"
Cohesion: 0.06
Nodes (51): legacy_schema(), Return a Schema using legacy cellpy column definitions.      For bridge-only h, get_cycle_numbers(), get_rates(), get_step_numbers(), Bridge-only pandas selectors for legacy-named step/raw tables.  These helpers, Get a array containing the cycle numbers in the test.      Parameters:, # TODO: add support for selecting cycles based on other criteria (for example, b (+43 more)

### Community 12 - "Community 12"
Cohesion: 0.17
Nodes (7): CellpyUnits, MockCore, These are the units used inside Cellpy.      At least two sets of units needs, Set selected columns first in a pandas.DataFrame.      This function sets cols, Set selected columns first in a pandas.DataFrame.      This function sets cols, Set selected columns first in a pandas.DataFrame.      This function sets cols, set_col_first()

### Community 13 - "Community 13"
Cohesion: 0.06
Nodes (31): create_raw_data(), Helper functions only intended for development purposes  (e.g. for creating mock, Create mock raw battery testing data with realistic values.      TODO: This fu, Cols, CycleCols, # TODO: dtype should be a python native "dtype object" if it exists, or a pl.Dat, simple_cols_check(), SimpleCols (+23 more)

### Community 14 - "Community 14"
Cohesion: 0.11
Nodes (17): 0. `/iflow` — smart dispatcher (quick start), 0a. `/iflow-pick` — choose the next issue (front door), 10. `/iflow-status` — status overview of all issues (read-only), 1. `/iflow-init` — capture the issue locally, 2. `/iflow-plan` — design the approach, 3. `/iflow-start` — implement the plan, 4. `/iflow-pause` — park work safely, 5. `/iflow-close` — land the work (+9 more)

### Community 15 - "Community 15"
Cohesion: 0.12
Nodes (16): Add on's, Cellpy Core Functionality, Cellpy Core Input (Harmonized_Raw), Cellpy Core Output, Core CycleTable, Current code structure:, Definition of Cellpy Core Functionality, Headers (+8 more)

### Community 16 - "Community 16"
Cohesion: 0.28
Nodes (6): OldCellpyCellCore, Legacy CellpyCellCore class to make it easier to migrate to cellpy core., Legacy CellpyCellCore class to make it easier to migrate to cellpy core., Legacy CellpyCellCore class to make it easier to migrate to cellpy core., Legacy CellpyCellCore class to make it easier to migrate to cellpy core., Legacy CellpyCellCore class to make it easier to migrate to cellpy core.

### Community 17 - "Community 17"
Cohesion: 0.2
Nodes (8): BaseSettings, BaseHeaders, BaseSettings, Converts to pandas dataframe, Subclass of BaseSetting including option to add postfixes.      Example:, Subclass of BaseSetting including option to add postfixes.      Example:, Subclass of BaseSetting including option to add postfixes.      Example:, Base class for internal cellpy settings.      Usage::           @dataclass

### Community 18 - "Community 18"
Cohesion: 0.18
Nodes (13): cellpy-core, code:python (import polars as pl), code:bash (pip install cellpycore), code:bash (pip install uv), code:bash (uv sync), code:bash (# Add a new package), code:bash (uv run pytest), Common Commands (+5 more)

### Community 19 - "Community 19"
Cohesion: 0.08
Nodes (27): _check_value_unit(), Parse for unit, update cellpy_units class, and return magnitude., Parse for unit, update cellpy_units class, and return magnitude., Parse for unit, update cellpy_units class, and return magnitude., get_cellpy_units(), get_converter_to_specific(), _get_unit_registry(), nominal_capacity_as_absolute() (+19 more)

### Community 20 - "Community 20"
Cohesion: 0.12
Nodes (17): CellpyCellCore, Data, Args:             initialize (bool): set to True if you want to initialize the, Args:             initialize (bool): set to True if you want to initialize the, Initialize the CellpyCell object with empty Data instance., Initialize the CellpyCell object with empty Data instance., Make the core step table.          Delegates to ``summarizers.make_step_table`, Make the core step table.          Delegates to ``summarizers.make_step_table` (+9 more)

### Community 21 - "Community 21"
Cohesion: 0.12
Nodes (17): _build_raw(), _build_step_cumulative_raw(), Tests for the injected Schema bundle and the step-table port.  These prove the, The globals bridge is gone: no module-level header/unit globals remain., The globals bridge is gone: no module-level header/unit globals remain., The globals bridge is gone: no module-level header/unit globals remain., Build a minimal native-named raw DataFrame (2 cycles x charge/discharge/rest)., Build a minimal native-named raw DataFrame (2 cycles x charge/discharge/rest). (+9 more)

### Community 22 - "Community 22"
Cohesion: 0.09
Nodes (25): legacy_to_native_raw(), legacy_to_native_step(), legacy_to_native_summary(), native_to_legacy_step(), native_to_legacy_summary(), Authoritative ``config.Cols`` <-> legacy ``Headers*`` column-name mapping.  Th, Return the legacy -> native rename dict for the raw frame.      Args:, Return the legacy -> native rename dict for the raw frame.      Args: (+17 more)

### Community 23 - "Community 23"
Cohesion: 0.18
Nodes (11): _declared_columns(), Conformance tests: config.py column classes match docs/data_format_specification, The renamed/removed legacy names are gone from RawCols., The renamed/removed legacy names are gone from RawCols., The renamed/removed legacy names are gone from RawCols., Map declared column attribute -> its string value for a Cols subclass., The renamed/removed legacy names are gone from RawCols., test_cycle_cols_match_spec() (+3 more)

### Community 24 - "Community 24"
Cohesion: 0.16
Nodes (14): CellpyLimits, Thresholds used when classifying step types in ``make_step_table``.      Since, Thresholds used when classifying step types in ``make_step_table``.      Since, Thresholds used when classifying step types in ``make_step_table``.      Since, Tests for the CellpyLimits port (issue #12, Phase 1).  CellpyLimits holds the, The module-level default is frozen so no caller can mutate it process-wide., CellpyLimits behaves like a dict (BaseSettings), as the engine indexes it., CellpyLimits behaves like a dict (BaseSettings), as the engine indexes it. (+6 more)

### Community 25 - "Community 25"
Cohesion: 0.2
Nodes (9): Auxillary columns, Capacity convention, Cellpy Core Harmonized_Raw, Column Headers, Conventions, Follow-ups, Other discussion points, Purpose (+1 more)

### Community 26 - "Community 26"
Cohesion: 0.14
Nodes (13): Test that cellpycore can be imported successfully., Test that cellpycore can be imported., Test that cellpycore has the expected package structure., Test that cellpycore has the expected package structure., Test that cellpycore has a version attribute (if defined)., Test that cellpycore has a version attribute (if defined)., Test that cellpycore is properly registered in sys.modules., Test that cellpycore is properly registered in sys.modules. (+5 more)

### Community 27 - "Community 27"
Cohesion: 0.25
Nodes (3): DictLikeClass, Add some dunder-methods so that it does not break old code that used     dictio, Add some dunder-methods so that it does not break old code that used     dictio

### Community 28 - "Community 28"
Cohesion: 0.18
Nodes (11): Raw with ref_potential yields all seven ref_potential_* step aggregates., Raw with ref_potential yields all seven ref_potential_* step aggregates., Raw without ref_potential yields no ref_potential_* columns, engine unaffected., Raw without ref_potential yields no ref_potential_* columns, engine unaffected., Raw with ref_potential yields all seven ref_potential_* step aggregates., Raw with ref_potential yields all seven ref_potential_* step aggregates., Raw without ref_potential yields no ref_potential_* columns, engine unaffected., Raw without ref_potential yields no ref_potential_* columns, engine unaffected. (+3 more)

### Community 29 - "Community 29"
Cohesion: 0.25
Nodes (7): code:bash, code:bash, Files, Golden numbers, Provenance & license, Regenerating, Test data fixtures

### Community 30 - "Community 30"
Cohesion: 0.13
Nodes (15): _build_merged_raw(), Hand-built native raw + steps exercising the IR-extraction rules.      cycle 1, Two tests (test_id 0 and 1) with **overlapping** cycle_num/step_num.      Each, A merged object (2 tests, overlapping cycle/step) keeps every step row.      W, A merged object (2 tests, overlapping cycle/step) keeps every step row.      W, Per-cycle cumulations restart at each test; no capacity leaks across tests., Per-cycle cumulations restart at each test; no capacity leaks across tests., Two tests (test_id 0 and 1) with **overlapping** cycle_num/step_num.      Each (+7 more)

### Community 31 - "Community 31"
Cohesion: 0.5
Nodes (3): Cellpy Core CycleTable (DRAFT), Column Headers, Purpose

### Community 32 - "Community 32"
Cohesion: 0.5
Nodes (3): Cellpy Core StepTable (DRAFT), Column Headers, Purpose

### Community 34 - "Community 34"
Cohesion: 0.25
Nodes (5): Legacy-bridge ``add_scaled_summary_columns`` (pandas<->polars seam)., Legacy-bridge ``add_scaled_summary_columns`` (pandas<->polars seam)., Legacy-bridge ``add_scaled_summary_columns`` (pandas<->polars seam)., Legacy-bridge ``add_scaled_summary_columns`` (pandas<->polars seam)., Legacy-bridge ``add_scaled_summary_columns`` (pandas<->polars seam).

### Community 48 - "Community 48"
Cohesion: 0.5
Nodes (3): [0.1.2] - 2026-07-02, Changelog, [Unreleased]

### Community 49 - "Community 49"
Cohesion: 0.14
Nodes (13): create_selector(), # TODO: implement also for energy and power (and probably others as well) - this, # TODO: @jepe - this method might be a bit slow for large datasets - consider us, # TODO: add support for selecting cycles based on other criteria (for example, b, # TODO: @jepe - include sub_steps here, # TODO: @jepe - include option for not selecting taper steps here, # TODO: @jepe - refactor this method!, # TODO: @jepe - include sub_steps here (+5 more)

### Community 50 - "Community 50"
Cohesion: 0.2
Nodes (10): _calculate_nominal_capacity_from_cycles(), equivalent_cycles_to_summary(), Calculate nominal capacity from specified normalization cycles.      Polars-na, Add the ``normalized_cycle_index`` (equivalent cycles) column to the summary., Calculate nominal capacity from specified normalization cycles.      Polars-na, Add the ``normalized_cycle_index`` (equivalent cycles) column to the summary., Calculate nominal capacity from specified normalization cycles.      Polars-na, Add the ``normalized_cycle_index`` (equivalent cycles) column to the summary. (+2 more)

### Community 51 - "Community 51"
Cohesion: 0.15
Nodes (11): LastIRExtractor, Pluggable per-cycle summary extractors.  A *summary extractor* is a callable o, Base class for callable per-cycle summary extractors.      Subclasses implemen, Return a per-cycle frame keyed by ``schema.cycle.cycle_num``.          Args:, Default internal-resistance extractor (issue #23).      For each cycle it read, SummaryExtractor, ir_to_summary(), Add per-cycle internal-resistance columns (``ir_charge`` / ``ir_discharge``). (+3 more)

### Community 52 - "Community 52"
Cohesion: 0.15
Nodes (12): _BlockPint, _DummyData, pint_absent(), Optional-extra guard tests for the unit boundary (STEP-12, issue #40).  The st, meta_path finder that makes any ``import pint`` raise ModuleNotFoundError., Importing the package (and re-importing units) must not require pint., The step + summary engine runs end-to-end with pint blocked., Calling the pint-backed helpers raises a clear, extra-naming error. (+4 more)

### Community 53 - "Community 53"
Cohesion: 0.19
Nodes (12): End-to-end tests for the native pipeline through the public API (issue #66)., n datapoints for one step; stype in {'charge', 'discharge'}., An empty (zero-row) raw frame yields empty steps, not a crash., A discharge-only cycle still yields a summary row (CE may be non-finite)., Thread-safety smoke: two schemas processed in parallel stay independent., _records(), test_cycle_without_charge_step(), test_empty_raw_frame_is_handled() (+4 more)

### Community 54 - "Community 54"
Cohesion: 0.14
Nodes (20): Column-header definitions for the harmonized raw data table.      Each attribu, Column-header definitions for the harmonized raw data table.      Each attribu, Column-header definitions for the harmonized raw data table.      Each attribu, Column-header definitions for the harmonized raw data table.      Each attribu, RawCols, _data_with_raw(), _native_schema(), The native polars summary engine emits the clean CycleCols subset only. (+12 more)

### Community 55 - "Community 55"
Cohesion: 0.18
Nodes (10): code:bash (pip install cellpycore            # or: uv add cellpycore), code:python (from cellpycore.cell_core import CellpyCellCore, Data), code:python (from cellpycore.cell_core import Data), Reference, The class-free alternative, The contract the caller must honor, The cycle-mode trap, The recommended entry point (+2 more)

### Community 56 - "Community 56"
Cohesion: 0.11
Nodes (19): _build_cumulative_raw(), _cap_lists(), 2 cycles, each charge then discharge, with cycle-cumulative capacities held., 2 cycles, each charge then discharge, with cycle-cumulative capacities held., Return the (charge, discharge) cumulative capacity lists, datapoint-ordered., 2 cycles, each charge then discharge, with cycle-cumulative capacities held., Return the (charge, discharge) cumulative capacity lists, datapoint-ordered., STEP / TEST cumulative raw normalizes to the cycle-cumulative oracle. (+11 more)

### Community 57 - "Community 57"
Cohesion: 0.22
Nodes (9): default_schema(), Return a Schema using the native cellpy-core column definitions.      Used as, Return a Schema using the native cellpy-core column definitions.      Used as, Return a Schema using the native cellpy-core column definitions.      Used as, Return a Schema using the native cellpy-core column definitions.      Used as, add_scaled_summary_columns with explicit by-value converters (no pint)., Exclusion keeps one row per cycle and subtracts the excluded deltas.      The, test_exclude_step_types_variant() (+1 more)

### Community 61 - "Community 61"
Cohesion: 0.23
Nodes (12): CellpyUnits, These are the units used inside Cellpy.      At least two sets of units needs, These are the units used inside Cellpy.      At least two sets of units needs, Converter-parity tests for ``cellpycore.units`` (STEP-12, issue #40).  ``cellp, Minimal stand-in for ``Data`` exposing only what the converters read., _stub(), test_get_converter_to_specific_charge_unit_mismatch(), test_get_converter_to_specific_modes() (+4 more)

### Community 62 - "Community 62"
Cohesion: 0.2
Nodes (10): get_cycle_numbers(), get_rates(), get_step_numbers(), Get a array containing the cycle numbers in the test.      Parameters:, Get the step numbers of selected type.      Returns the selected step_numbers, Get the rates in the test (only valid for constant current).      Args:, Get the rates in the test (only valid for constant current).      Args:, Get the step numbers of selected type.      Returns the selected step_numbers (+2 more)

### Community 63 - "Community 63"
Cohesion: 0.33
Nodes (6): TestMode.INVERTED (anode) flips CE and coulombic_difference references., TestMode.INVERTED (anode) flips CE and coulombic_difference references., TestMode.INVERTED (anode) flips CE and coulombic_difference references., TestMode.INVERTED (anode) flips CE and coulombic_difference references., TestMode.INVERTED (anode) flips CE and coulombic_difference references., test_make_summary_anode_flips_coulombic_columns()

### Community 64 - "Community 64"
Cohesion: 0.21
Nodes (3): DictLikeClass, Get the value (postfixes not supported)., Add some dunder-methods so that it does not break old code that used     dictio

### Community 65 - "Community 65"
Cohesion: 0.12
Nodes (17): _ir_raw_steps(), Hand-built native raw + steps exercising the IR-extraction rules.      cycle 1, Hand-built native raw + steps exercising the IR-extraction rules.      cycle 1, Hand-built native raw + steps exercising the IR-extraction rules.      cycle 1, Default extractor picks the last datapoint of the last charge/discharge     ste, Default extractor picks the last datapoint of the last charge/discharge     ste, Default extractor picks the last datapoint of the last charge/discharge     ste, A custom SummaryExtractor passed via ir_extractor overrides the default. (+9 more)

### Community 66 - "Community 66"
Cohesion: 0.2
Nodes (10): _add_end_potentials(), _group_keys(), Join per-cycle end-of-charge / end-of-discharge potentials onto ``summary``., Join per-cycle end-of-charge / end-of-discharge potentials onto ``summary``., Subtract excluded steps' per-cycle capacity deltas from the summary.      Port, Join per-cycle end-of-charge / end-of-discharge potentials onto ``summary``., Subtract excluded steps' per-cycle capacity deltas from the summary.      Port, Prepend ``test_id`` to ``base_keys`` when ``frame`` carries that column. (+2 more)

### Community 67 - "Community 67"
Cohesion: 0.29
Nodes (7): Distinct step-type labels from a (polars) native step table., Distinct step-type labels from a (polars) native step table., Regression for the falsy-override bug: an explicit 0.0 override must win., Regression for the falsy-override bug: an explicit 0.0 override must win., Distinct step-type labels from a (polars) native step table., test_override_raw_limits_zero_is_honoured(), _types()

### Community 68 - "Community 68"
Cohesion: 0.06
Nodes (29): from_raw_frame(), # TODO: v2.0 edit this from scalar to list, # TODO: v2.0 edit this from scalar to list, # TODO: move the data object to slim, # TODO: copy div settings to slim, # TODO: move the data object to slim, # TODO: copy div settings to slim, Make the core summary.          Args:             data: The data to make the (+21 more)

### Community 69 - "Community 69"
Cohesion: 0.17
Nodes (8): BaseSettings, Generic dict-like settings base classes shared across cellpy-core.  These were, Base class for internal cellpy settings.      Usage::           @dataclass, Base class for internal cellpy settings.      Usage::           @dataclass, Get the value (postfixes not supported)., Get the value (postfixes not supported)., Converts to pandas dataframe, Converts to pandas dataframe

### Community 71 - "Community 71"
Cohesion: 0.2
Nodes (10): _delta_expr(), make_step_table(), Per-step delta in percent (mirrors legacy cellpy's ``delta``).      ``100 * la, Create a table (v.5) that contains summary information for each step.      Thi, Per-step delta in percent (mirrors legacy cellpy's ``delta``).      ``100 * la, Create a table (v.5) that contains summary information for each step.      Thi, Create a table (v.5) that contains summary information for each step.      Thi, Per-step delta in percent (mirrors legacy cellpy's ``delta``).      ``100 * la (+2 more)

### Community 72 - "Community 72"
Cohesion: 0.22
Nodes (9): make_summary(), Polars-native per-cycle summary (the clean native ``CycleCols`` subset)., Polars-native per-cycle summary (the clean native ``CycleCols`` subset)., Polars-native per-cycle summary (the clean native ``CycleCols`` subset)., Raise ``NoDataFound`` when a required input frame is missing., Polars-native per-cycle summary (the clean native ``CycleCols`` subset)., Raise ``ValueError`` naming every required column missing from ``frame``., _require_columns() (+1 more)

### Community 73 - "Community 73"
Cohesion: 0.33
Nodes (6): generate_specific_summary_columns multiplies by the given factor (no pint)., generate_specific_summary_columns multiplies by the given factor (no pint)., generate_specific_summary_columns multiplies by the given factor (no pint)., generate_specific_summary_columns multiplies by the given factor (no pint)., generate_specific_summary_columns multiplies by the given factor (no pint)., test_generate_specific_columns_takes_factor_by_value()

### Community 74 - "Community 74"
Cohesion: 0.25
Nodes (5): large_raw(), Opt-in performance benchmarks for the core engine (issue #66).  Excluded from, ~40x the cycler fixture (~410k rows): shifts cycle numbers and datapoints     s, _steps(), test_benchmark_make_summary()

### Community 75 - "Community 75"
Cohesion: 0.18
Nodes (11): c_rate = abs(current_mean / nom_cap): doubling nom_cap halves the rate., c_rate = abs(current_mean / nom_cap): doubling nom_cap halves the rate., c_rate = abs(current_mean / nom_cap): doubling nom_cap halves the rate., Step-type classification uses the supplied raw_limits, not a fixed default., c_rate = abs(current_mean / nom_cap): doubling nom_cap halves the rate., Step-type classification uses the supplied raw_limits, not a fixed default., c_rate = abs(current_mean / nom_cap): doubling nom_cap halves the rate., Step-type classification uses the supplied raw_limits, not a fixed default. (+3 more)

### Community 81 - "Community 81"
Cohesion: 0.29
Nodes (8): CellpyError, NoDataFound, Base class for other exceptions, Base class for other exceptions, Base class for other exceptions, Exception raised when no data is found, Exception raised when no data is found, Exception

### Community 82 - "Community 82"
Cohesion: 0.4
Nodes (5): CellpyCellCore.schema bundles the (possibly overridden) header instances., CellpyCellCore.schema bundles the (possibly overridden) header instances., CellpyCellCore.schema bundles the (possibly overridden) header instances., CellpyCellCore.schema bundles the (possibly overridden) header instances., test_schema_property_reflects_headers()

### Community 83 - "Community 83"
Cohesion: 0.25
Nodes (8): _classify_from_specifications(), _classify_steps(), Build a step-type expression from explicit step specifications., Return a polars expression classifying each step into a step type.      Mirror, Build a step-type expression from explicit step specifications., Return a polars expression classifying each step into a step type.      Mirror, Build a step-type expression from explicit step specifications., Return a polars expression classifying each step into a step type.      Mirror

### Community 84 - "Community 84"
Cohesion: 0.29
Nodes (6): _ensure_test_id(), normalize_capacity_granularity(), Normalize cumulative raw capacity / energy columns to cycle-cumulative.      T, Return ``frame`` with a ``test_id`` column, defaulting to ``0`` when absent., Return ``frame`` with a ``test_id`` column, defaulting to ``0`` when absent., Normalize cumulative raw capacity / energy columns to cycle-cumulative.      T

### Community 85 - "Community 85"
Cohesion: 0.4
Nodes (5): c_rates_to_summary(), Add per-cycle charge / discharge C-rates to the summary.      Polars-native: t, Add per-cycle charge / discharge C-rates to the summary.      Polars-native: t, Add per-cycle charge / discharge C-rates to the summary.      Polars-native: t, Add per-cycle charge / discharge C-rates to the summary.      Polars-native: t

### Community 86 - "Community 86"
Cohesion: 0.4
Nodes (5): generate_specific_summary_columns(), Generate specific (per mass / area / volume) summary columns.      Polars-nati, Generate specific (per mass / area / volume) summary columns.      Polars-nati, Generate specific (per mass / area / volume) summary columns.      Polars-nati, Generate specific (per mass / area / volume) summary columns.      Polars-nati

### Community 87 - "Community 87"
Cohesion: 0.33
Nodes (6): Two cells with different schemas each emit their own column names., Two cells with different schemas each emit their own column names., Two cells with different schemas each emit their own column names., Two cells with different schemas each emit their own column names., Two cells with different schemas each emit their own column names., test_two_schemas_do_not_share_state()

### Community 88 - "Community 88"
Cohesion: 0.18
Nodes (11): ir_to_summary adds ir_charge/ir_discharge (native, default extractor)., ir_to_summary adds ir_charge/ir_discharge (native, default extractor)., ir_to_summary adds ir_charge/ir_discharge (native, default extractor)., The native CellpyCellCore add_scaled path runs on the polars summary., ir_to_summary adds ir_charge/ir_discharge (native, default extractor)., The native CellpyCellCore add_scaled path runs on the polars summary., ir_to_summary adds ir_charge/ir_discharge (native, default extractor)., The native CellpyCellCore add_scaled path runs on the polars summary. (+3 more)

### Community 89 - "Community 89"
Cohesion: 0.25
Nodes (5): Build the per-cycle summary via the polars engine, in/out in legacy form., Build the per-cycle summary via the polars engine, in/out in legacy form., Build the per-cycle summary via the polars engine, in/out in legacy form., Build the per-cycle summary via the polars engine, in/out in legacy form., Build the per-cycle summary via the polars engine, in/out in legacy form.

### Community 98 - "Community 98"
Cohesion: 0.25
Nodes (8): 1. **Immutability by Design**, 2. **Functional Programming Approach**, 3. **Type Safety**, 4. **Modular Design**, 5. **Configuration Management**, code:python (# ✅ Good: Non-modifying selector), code:python (from typing import TypeVar, Union, Optional), Design Principles

### Community 99 - "Community 99"
Cohesion: 0.25
Nodes (8): Branch Naming Convention, Branch Structure, Branching and Merging Strategy, code:block4 (type(scope): brief description), code:block5 (feat(selectors): add support for custom step type filtering), Commit Message Standards, Fancy Commmit Messages, Workflow Process

### Community 100 - "Community 100"
Cohesion: 0.29
Nodes (7): 1. **Function Organization**, 2. **Error Handling**, 3. **Constants and Configuration**, Code Organization Patterns, code:python (import logging), code:python (# Define constants at module level), code:python (# Group related functions together)

### Community 101 - "Community 101"
Cohesion: 0.29
Nodes (6): Code Review Process, Development Guide, Development Process, Development Workflow, Setting Up Development Environment, Table of Contents

### Community 102 - "Community 102"
Cohesion: 0.33
Nodes (5): Build the step table via the polars engine, in/out in legacy form.          Se, Add the pandas-only legacy summary columns the native schema omits.          `, Add the pandas-only legacy summary columns the native schema omits.          `, Add the pandas-only legacy summary columns the native schema omits.          `, Add the pandas-only legacy summary columns the native schema omits.          `

### Community 103 - "Community 103"
Cohesion: 0.33
Nodes (5): Map the ``info`` column from step specifications onto the step table., Map the ``info`` column from step specifications onto the step table., Map the ``info`` column from step specifications onto the step table., Map the ``info`` column from step specifications onto the step table., Map the ``info`` column from step specifications onto the step table.

### Community 104 - "Community 104"
Cohesion: 0.33
Nodes (4): Build the step table via the polars engine, in/out in legacy form.          Se, Build the step table via the polars engine, in/out in legacy form.          Se, Build the step table via the polars engine, in/out in legacy form.          Se, Build the step table via the polars engine, in/out in legacy form.          Se

### Community 105 - "Community 105"
Cohesion: 0.33
Nodes (6): c_rates_to_summary joins per-cycle first charge/discharge C-rates (native)., c_rates_to_summary joins per-cycle first charge/discharge C-rates (native)., c_rates_to_summary joins per-cycle first charge/discharge C-rates (native)., c_rates_to_summary joins per-cycle first charge/discharge C-rates (native)., c_rates_to_summary joins per-cycle first charge/discharge C-rates (native)., test_c_rates_to_summary_native()

### Community 106 - "Community 106"
Cohesion: 0.4
Nodes (5): Additional tooling, Code Quality Standards, Documentation Requirements, Linting and Formatting, Performance Considerations

### Community 107 - "Community 107"
Cohesion: 0.4
Nodes (5): code:python (def test_function_name_with_valid_input_returns_expected_res), Test Coverage, Test Naming, Test Structure, Testing Guidelines

### Community 108 - "Community 108"
Cohesion: 0.4
Nodes (5): _build_test_cumulative_raw(), Same increments as ``_build_cumulative_raw`` but counters never reset.      Ca, Same increments as ``_build_cumulative_raw`` but counters never reset.      Ca, Same increments as ``_build_cumulative_raw`` but counters never reset.      Ca, Same increments as ``_build_cumulative_raw`` but counters never reset.      Ca

## Knowledge Gaps
- **669 isolated node(s):** `# TODO: dtype should be a python native "dtype object" if it exists, or a pl.Dat`, `Build the harmonized raw frame from a legacy-named frame.      Args:`, `Load each source with cellpy and write ``<name>_raw.parquet``.`, `Run the current cellpy-core engine on the raw parquet and snapshot the     step`, `Validate a native-schema raw frame against ``config.RawCols``.      Checks tha` (+664 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RawCols` connect `Community 54` to `Community 65`, `Community 2`, `Community 67`, `Community 5`, `Community 7`, `Community 105`, `Community 75`, `Community 13`, `Community 53`, `Community 21`, `Community 87`, `Community 88`, `Community 57`, `Community 56`, `Community 28`, `Community 30`, `Community 63`?**
  _High betweenness centrality (0.110) - this node is a cross-community bridge._
- **Why does `default_schema()` connect `Community 57` to `Community 0`, `Community 34`, `Community 7`, `Community 104`, `Community 71`, `Community 72`, `Community 49`, `Community 50`, `Community 51`, `Community 84`, `Community 85`, `Community 54`, `Community 53`, `Community 21`, `Community 62`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._
- **Why does `Data` connect `Community 20` to `Community 0`, `Community 7`, `Community 11`, `Community 13`, `Community 21`, `Community 28`, `Community 30`, `Community 34`, `Community 52`, `Community 53`, `Community 54`, `Community 56`, `Community 61`, `Community 65`, `Community 68`, `Community 73`, `Community 81`, `Community 89`, `Community 104`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `RawCols` (e.g. with `HeadersNormal` and `HeadersStepTable`) actually correct?**
  _`RawCols` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 32 inferred relationships involving `Data` (e.g. with `Meta` and `MockMetaTestDependent`) actually correct?**
  _`Data` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `OldCellpyCellCore` (e.g. with `Meta` and `MockMetaTestDependent`) actually correct?**
  _`OldCellpyCellCore` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 26 inferred relationships involving `default_schema()` (e.g. with `.make_core_step_table()` and `.add_scaled_summary_columns()`) actually correct?**
  _`default_schema()` has 26 INFERRED edges - model-reasoned connections that need verification._