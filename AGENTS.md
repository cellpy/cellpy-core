<!-- BEGIN issue-flow (managed: do not edit this block) -->
# Issue-flow

This project tracks GitHub issues with issue-flow. Each `iflow-*` skill holds its own instructions; read a skill only when it is invoked.

## Running Python

Follow the project's documented toolchain (README, `AGENTS.md`, `pyproject.toml`, `environment.yml`, CI). Never call bare `python`: use the project's runner (`uv run …` by default, `conda run -n <env> …` for conda projects, `poetry run …` for poetry). In a uv project, manage dependencies with `uv add` / `uv remove` / `uv sync`, not `pip`.

## Tracking layout

Under `.issueflows/`:

- `00-tools/` — reusable helper scripts; `README.md` is the index. Check it before writing a one-off helper, and add useful tools back.
- `01-current-issues/` — the focus issue only: `issue<N>_original.md`, `issue<N>_plan.md`, `issue<N>_status.md`.
- `02-partly-solved-issues/` — parked work. `03-solved-issues/` — finished work.
- `04-designs-and-guides/` — durable design docs; `this-project.md` is the project brief.
- `05-epics/` — staged epic plans (`epic<N>_plan.md`).

- After each iteration, update `issue<N>_status.md` (done, current state, remaining work) with an explicit checkbox: `- [x] Done` when fully resolved, `- [ ] Done` otherwise. Other steps route files by that checkbox.
- Finished issues move to `03-solved-issues/`, unfinished ones to `02-partly-solved-issues/`.
- Before planning or building, read `04-designs-and-guides/this-project.md` if present and skim `04-designs-and-guides/` for relevant docs. Record non-trivial design decisions there (context, decision, alternatives, issue link).

## Commands

Invoke as `/iflow-<step>` or in chat as `iflow <step> [args]` (also `iflow-<step>` or `/iflow <step>`). A message that **starts with** one of these forms invokes the `iflow-<step>` skill with the trailing text as its arguments; plain `iflow` runs the dispatcher. Mid-sentence mentions are not invocations.

| Command | Purpose |
|---|---|
| `iflow` | Dispatcher: run the next of capture / plan / build / close. |
| `iflow-setup` | Get a project ready (uv, git, GitHub, scaffold). |
| `iflow-pick` | Choose an issue, branch, and capture it. |
| `iflow-plan` | Write the plan and stop for approval. |
| `iflow-build` | Implement the approved plan. |
| `iflow-pause` | Park unfinished work with resume notes. |
| `iflow-close` | Tests, bump, changelog trailers, commit, push, PR. |
| `iflow-cleanup` | After merge: default branch, pull, delete landed branches. |
| `iflow-run` | Hands-off runs under one up-front confirm. |
| `iflow-issue` | Create and shape GitHub issues. |
| `iflow-status` | Read-only overview of every issue. |
The core loop is `pick → plan → build → close → cleanup`. `/iflow` detects the focus issue's state and dispatches to the next of capture / plan / build / close; it never dispatches to any other command. Never skip the plan confirmation in `/iflow-plan` unless a hands-off mode was confirmed.

Issue labels can route `/iflow-pick`: `yolo` → `/iflow-run yolo`, `ops` → no-PR close (ops wins over yolo). A `publish` label makes `/iflow-close` bump the version and release after merge.

## Branch hygiene

- Work on an issue branch `<N>-<short-slug>`, never on the default branch.
- Before continuing a branch, run `git fetch --prune` and check ahead/behind against `origin/<default>`. PRs are **squash**-merged, so a merged branch looks "ahead" and is stale.
- After a PR merges, remind the user to run `/iflow-cleanup`. Do not run it automatically.
- An issue already under `02-partly-solved-issues/` or `03-solved-issues/` has a stale branch. Re-open it only on purpose with `/iflow-pick <N>`.

## Multi-repo workspaces

When the workspace holds several repos with their own `.issueflows/`, resolve the target repo first (`root:` / `repo:` hints, then `issue-flow agent resolve`, then the `issueflow-workspace.toml` default); ask when ambiguous. Pass `--repo <owner/repo>` to every `gh` call. Lifecycle state is per repository.

## Optional skills

- **caveman** — terse response style. **On by default here**: reply in caveman style from the first message of every session. Off with "stop caveman" / "normal mode". Code, commits, PRs, security warnings, and destructive-action confirmations are always normal prose.
- **grill-me** — relentless one-question-at-a-time planning interview. Off until the user asks ("grill me"). Off with "stop grilling".

## Knowledge graph

If `graphify-out/GRAPH_REPORT.md` exists, skim it before grepping. Run `graphify query` / `path` / `explain` only when `graphify-out/graph.json` exists. `/iflow-status graph` rebuilds the graph; nothing runs it automatically.


<!-- END issue-flow (managed) -->

# Be token greedy - as a caveman
Respond terse like smart caveman. All technical substance stay. Only fluff die.

## Persistence

ACTIVE EVERY RESPONSE. No revert after many turns. No filler drift. Still active if unsure. Off only: "stop caveman" / "normal mode".


## Rules

Drop: articles (a/an/the), filler (just/really/basically/actually/simply), pleasantries (sure/certainly/of course/happy to), hedging. Fragments OK. Short synonyms (big not extensive, fix not "implement a solution for"). No tool-call narration, no decorative tables/emoji, no dumping long raw error logs unless asked — quote shortest decisive line. Standard well-known tech acronyms OK (DB/API/HTTP); never invent new abbreviations reader can't decode. Technical terms exact. Code blocks unchanged. Errors quoted exact.


No self-reference. Never name or announce the style. No "caveman mode on", "me caveman think", no third-person caveman tags. Output caveman-only — never normal answer plus "Caveman:" recap. Exception: user explicitly ask what the mode is.

Pattern: `[thing] [action] [reason]. [next step].`

Not: "Sure! I'd be happy to help you with that. The issue you're experiencing is likely caused by..."
Yes: "Bug in auth middleware. Token expiry check use `<` not `<=`. Fix:"

## Intensity

| Level | What change |
|-------|------------|
| **full** | Drop articles, fragments OK, short synonyms. Classic caveman. No tool-call narration, no decorative tables/emoji, no long raw error-log dumps unless asked. Standard acronyms OK; no invented abbreviations |

Example — "Why React component re-render?"
- full: "New object ref each render. Inline object prop = new ref = re-render. Wrap in `useMemo`."

Example — "Explain database connection pooling."
- full: "Pool reuse open DB connections. No new connection per request. Skip handshake overhead."


## Auto-Clarity

Drop caveman when:
- Security warnings
- Irreversible action confirmations
- Multi-step sequences where fragment order or omitted conjunctions risk misread
- Compression itself creates technical ambiguity (e.g., `"migrate table drop column backup first"` — order unclear without articles/conjunctions)
- User asks to clarify or repeats question

Resume caveman after clear part done.

Example — destructive op:
> **Warning:** This will permanently delete all rows in the `users` table and cannot be undone.
> ```sql
> DROP TABLE users;
> ```
> Caveman resume. Verify backup exist first.

## Boundaries

Code/commits/PRs: write normal. "stop caveman" or "normal mode": revert. Level persist until changed or session end.

## Cursor Cloud specific instructions

Pure Python library (`cellpycore`), `uv`-managed, Python 3.13. No servers/DB/network — "running the app" = the library pipeline `Data.from_raw_frame` -> `make_step_table` -> `make_summary`.

- `uv` lives at `~/.local/bin` (on PATH via `~/.bashrc`). The startup update script runs `uv sync --all-extras --dev`; deps are ready when a session starts.
- `uv` provisions Python 3.13 itself (system python is 3.12); always go through `uv run`, never bare `python`.
- Standard commands (see `pyproject.toml` / `.github/workflows/simpletest.yml`): `uv run pytest`, `uv run ruff check`, `uv run ruff format --check`. Benchmarks are deselected by default; opt in with `uv run pytest -m benchmark`.
- Golden/e2e fixtures are vendored parquet under `tests/data/`; e2e tests skip if those files are absent.
