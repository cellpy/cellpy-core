# Issue #359: handle full cells that starts with a discharge step

Source: https://github.com/jepegit/cellpy/issues/359

> **Provisional capture.** Upstream issue lives in `jepegit/cellpy` (Stage 5, S3,
> labelled `to core`). The cloud-agent token cannot create issues, so the
> `cellpy/cellpy-core` mirror issue has not been created yet. Once it exists,
> rename this group (`issue359_*` -> `issue<N>_*`) and update `Source:`.
> Draft mirror body: see `issue359_plan.md` -> "Mirror issue (to create)".

## Original issue text

We typically define the coulombic efficiency as charge/discharge. One exception is half-cells studying an anode material (where coulombic efficiency makes more sense if it is defined as discharge/charge). Therefore, `cellpy`'s `cycle_mode` parameter was implemented to control how coulombic efficiency is calculated. It is also used (at least for default settings) in defining how charge and discharge curves are extracted and visualized. 

A common pitfall is when testing commercial cells, where one might start with a discharge (cycle 1) and then continue with charge-discharge cycles (cycles 2, 3, 4, ...). It is likely that some files end up with an "erroneous" cycle counter (could be that the first cycle is discharge-charge-discharge, or that all cycles end up as discharge-charge).

Is there a method in `cellpy` to handle these cases? If not, could it be implemented (e.g. either as another alternative for the `cycle_mode` parameter, or some post-processing steps like `update_cycle_counter(...))?

## Comments (curated summary)

- **Clarifications / constraints**:
  - Owner (@jepegit) narrows to two candidate solutions: **(1)** more cycle modes, with the handling of each mode implemented in cellpycore; **(2)** more keyword arguments on the cellpycore cycle-summary creator for granular control of how cycle summaries are built.
  - The work "has to be done in cellpycore" (core-first; cellpy gets a thin surface).

_Note: this section is an interpretive summary of the comment thread, not a verbatim dump. Source comments: 1, last comment by @jepegit on 2026-07-23._
