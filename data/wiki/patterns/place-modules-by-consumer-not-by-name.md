---
title: Place Modules by Consumer, Not by Name
tags: [foundations, pattern]
summary: "A module belongs in a shared layer only if it passes two tests — no I/O, and substrate for several consumer trees; a pure parser with exactly one consumer is a stage of that consumer and lives inside it — and inside a pipeline folder, name each node folder for the data cluster it writes, delete the utils file by giving each export its consumer's home, and treat 'docs match the tree' as the half of a refactor no green gate checks."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-09-core-layout-refactor.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-09-core-layout-refactor.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-09-core-layout-refactor.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-09-core-layout-refactor.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-09-core-layout-refactor.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-09-core-layout-refactor.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-09-core-layout-refactor.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-09-core-layout-refactor.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-09-core-layout-refactor.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-09-core-layout-refactor.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-09-core-layout-refactor.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-09-core-layout-refactor.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-09-core-layout-refactor.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-09-core-layout-refactor.md
---

# Place Modules by Consumer, Not by Name

From an akira layout refactor of `src/core/` (eight top-level folders meaning four
different things) and its 10-dimension review.

## The two-part placement test

An earlier reading proposed moving the HTML-extraction module into the agents layer,
because the project's CLAUDE.md listed it there. That was the wrong direction:

- The listed directory **did not exist** — the CLAUDE.md line was stale, and the change
  contract recorded the opposite move deliberately.
- The operative test (from a prior move that brought scoring and moment modules *back* into
  the agents layer) has two halves: **no I/O** *and* **substrate for several trees**. Scoring
  and moment each had six consumer trees. Extraction had **one** — the ingestion pipeline.
  It passes the purity half and fails the substrate half.

So extraction is not a shared stage; it is the first stage of ingestion and belongs
*inside* it. Purity alone says a module *could* be shared; consumer count says whether it
*is*. Verify by grep (`grep -rn "core/extraction" <every other tree>` → no hits).

## Inside a pipeline: name nodes for what they write

The ingestion folder was 18 flat files spanning three write clusters. The fix borrowed the
graph analogy without a graph framework (the pipeline is linear, and a CLI plus scheduled
workflow depend on its 0/1/2 exit-code contract): **root files are the edges, folders are
the nodes, each node named for the data cluster it writes** — `source/`, `content/`,
`enrich/`, plus `extract/` which writes nothing. That answers "which of these files
writes what" for free (see [[Data Clusters by Writer and Trust]]).

Top level went from 8 folders meaning four things to 5 folders meaning five things:
pipeline, entrypoints, repo-check helpers, scheduled jobs, local tooling.

## Delete `utils`, don't move it

A 92-line `utils.ts` held three unrelated exports with three different consumers. Each went
to the home its consumer already implied: link extraction into `extract/`, slug building
into `content/`, a `sleep` with one caller inlined into the fetcher. A file named
`utils` is the file with no home; moving it intact just relocates the problem.

## Deliberate asymmetries must be argued in place

One cross-cutting file (pipeline-wide dry-run write suppression) stayed at the root because
the lint config names its exact path twice. The plan required the README to say why — or
the next reader moves it, lint still passes, and the `no-console` carve-out silently stops
applying ([[Config Reference Rot]]).

## What the review found: the docs half

The acceptance criterion was "no behaviour change + docs match the tree". All 15 gate
targets passed; half the important findings were against the second half, which a green
gate cannot check:

- **A new README comment claimed a 1:1 pairing** (entrypoint ↔ pure helper) that only 5
  of 10 entrypoints had — and silently contradicted the README's own "cli holds no logic"
  rule for the other five. State the real ratio and name the exception.
- **Path mentions listed in the plan's own definition-of-done were missed** in two live
  specs, still citing the never-existed directory the refactor corrected everywhere else.
- **Two copies of one contract, fixed in one** — see
  [[A Partial Fix of a Duplicated Doc Is Worse Than None]].
- **The path sweep matched the qualified form, not the bare relative one** — two comments
  still said `./runLog.ts` after the file moved into `source/`.
- **Unrelated working-tree changes swept in by `git add`** into a "pure move" diff, so a
  revert of the layout work would silently revert them too. Commit them separately.
- **A function promoted to its own module, documented as the natural key, with zero
  tests** — a slug change would silently re-create every event. Characterisation-test it.

The user reviewing the result also could not explain the new `cli/` vs. `gates/` vs.
`ops/` split — evidence the "one folder, several meanings" problem had moved down a level
rather than being solved.

## See Also
- [[ML Stage Layering with Typed Contracts]] — related (organise by process stage; technique folders are libraries)
- [[Data Clusters by Writer and Trust]] — extends (folder names follow the write cluster)
- [[A Partial Fix of a Duplicated Doc Is Worse Than None]] — related (the review's contract finding)
- [[Config Reference Rot]] — related (path-named config that silently stops applying)
