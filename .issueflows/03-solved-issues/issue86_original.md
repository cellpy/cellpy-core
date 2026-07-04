# Issue #86: update data and merge tests

Source: https://github.com/cellpy/cellpy-core/issues/86

## Original issue text

We should add method for incremental updating as well as merging data as stated in the roadmap:

```markdown

## Merging cell tests

- **Merge many test files into one `Data` object** — Legacy cellpy exposes a method for
  merging cell tests (vertical concat of raw frames, aligned metadata, isolated per-test
  grouping via `test_id`). This can be compute-intensive at scale; cellpy-core should
  own the operation rather than leaving it to callers or the full cellpy package.
  Scaffolding exists (`raw.test_id`, composite group keys in the engine,
  `metadata.merge_test_meta`); a first-class **raw + metadata merge API** on `Data` /
  `CellpyCellCore` is still missing. See
  `.issueflows/04-designs-and-guides/test-metadata-and-merging.md`.

## Incremental summarization

- **Update step/summary tables from new raw rows only** — Summarizers today reprocess the
  entire `data.raw` frame on every call. For live or in-progress tests (e.g. polling
  cycler status), callers should be able to append new raw data and refresh steps /
  summary incrementally instead of recomputing from scratch. Likely needs defined
  merge/append semantics on `Data`, stable row keys (`test_id`, cycle/step boundaries),
  and incremental paths in `make_step_table` / `make_summary` (or companion helpers).

```


## Algorithms to use

### Merging

For merging two tests, we focus on merging the two data objects (the raw, steps summary, cycle summary frames)
for now. Lets label the two data objects D1 and D2. Then during merging we must do the following:

1. check that test-id for D1 is not the same as for D2. If it is - we raise an exception. We allow the user to override this by supplying a key-word argument.
2. the cycle numbers in D2 should be updtated (c2,i -> c2,i + c1,last). User can upt out.
3. the data point number in D2 should be updated (n2,i -> n2,i + n1,last). User can not opt out.

When merging the cycle summary, we need to make sure that the cummulative values in D2 continues from where the values stopped in D1.

### Updating a test with new data

Assume D1 is the data we already have processed. R2 contains new raw data (will probably overlap with one row, but could overlap with more). As default we use the source_datapoint_num (lets label them as r, i.e. for D1 they are r1(0), r1(1), etc.) as our key for partitioning. R1 denotes the raw data for D1. R1 contains the steps s1(0), s1(1), s1(2), ..., s1(last1). R2 the steps s2(0) .... s2(last2).

If r2(0) >= r1(last): find what step r2(0) is in. That step and all the ones after will then belong to R2. The steps before will belong to D1.

Then we have to calculate the step summary for D2. We already have for D1 (remember to not include the "overlapped" ones).
We pick the last cycle in D1 as reference cycle (used for calculating cummulative values) and calculates cycle summary. Then we append the new raw, steps summary, and cycle summary rows to D1 frames and return it.

## Structure

Open for suggestions. But should honour our principles.

<!-- Edit the body of your new issue then click the ✓ "Create Issue" button in the top right of the editor. The first line will be the issue title. Assignees and Labels follow after a blank line. Leave an empty line before beginning the body of the issue. -->
