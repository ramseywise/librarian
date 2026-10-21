---
title: Map Every State to Its Writer
tags: [meta, pattern]
summary: "A validator that accepts a state no component ever writes describes a machine larger than the one that runs — map each enum member to the code that writes it, and check the corpus: the galactus plan pipeline had three writerless states, and 6 of 6 executed docs sat at 'Review: pending' because the terminal transition had no writer, a defect no loop-back or orchestrator would have fixed."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-pipeline-orchestration.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-pipeline-orchestration.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-orchestrator-design.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-orchestrator-design.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-14-control-plane-design.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-14-control-plane-design.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-14-gua-111-review-field-discrimination.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-14-gua-111-review-field-discrimination.md
---

# Map Every State to Its Writer

The galactus orchestration research was opened to ask which pipeline edges should become
a graph. The finding that redirected it came from a two-column table: each `Status:` value
the hook accepts, and the skill line that writes it.

| State | Written by |
|---|---|
| `RESEARCHED` | **nothing** — only *read*, by the refine skill, which branches on it |
| `COMPLETE` | **nothing** |
| `SUPERSEDED` | **nothing** — yet the hook required a `Superseded-by:` companion: fully designed, never claimed |
| the other six | one or two skills each |

`RESEARCHED` was skipped structurally: the research skill wrote `PLANNED` at its own exit,
so the in-between state could never be occupied. "The hook validates a vocabulary three
words larger than the pipeline speaks."

## Check the corpus, not just the code

The 11-doc plan corpus confirmed the consequence: **0 docs had ever reached `COMPLETE`**,
and **6 of 6 `EXECUTED` docs sat at `Review: pending`** — the hook forced the field to
exist and never checked it flipped. A 6/6 skip rate at exactly the transition with no
writer. The motivating loop-back edge, by contrast, had zero observed traversals.

That reframed the build from "orchestrate the pipeline" to **"close the ledger"**: a
state-writer and hook-transition change. The skipped transition was *terminal*, where no
loop-back would have helped. An orchestrator cannot terminate a work item it cannot record
as done — it can only abandon it.

## Generalizes

- For every closed set a validator accepts, list the writer of each member; a member with
  only readers is a dead branch in every consumer.
- Prefer giving an orphan state a *job* over deleting it — the unclaimed `SUPERSEDED` became
  the legal destination for loop-bound exhaustion and NEEDS-SPLIT (see
  [[Loop Termination Design]]).
- Counts written into docs drift (a "three subcommands" docstring over four); derive counts
  rather than restating them.

## Second corpus: guacamayo plan docs (2026-08)

The same audit on a second repo found the same shape at larger scale:

- **7 of 51** docs reached `COMPLETE` with no writer anywhere; they were hand-edited.
- **21 of 24** `EXECUTED` docs sat at `Review: pending`. The enforcing hook checked that the
  field was *present*, not what its *value* was.
- The `ready` label and the `READY` status were false cognates. The label pipeline runs
  before the plan exists, and the doc status runs after it.
- The label hook advanced on skill *invocation*, not success. Nothing wrote `in-progress`, and
  review had no label effect, so drift was the designed behaviour.
- Plan docs were gitignored, so there was no transition history to audit.

## Fix the writer before validating the value (GUA-111)

The obvious fix was to validate `Review:` values in the hook. Measured, that would have
rejected only 2 docs and left the 21/24 trap untouched, because the one legal token
`pending` carried five meanings (not run, run but unparsed, approved but unrecorded, and so
on). `failed` was legal but had no writer. The working order:

1. **Give each outcome its own token and writer:** not-run → `pending`, approve → `passed`,
   request-changes → `failed`, comment → `passed`, insufficient-context → `blocked`.
2. **Share one parser** between the migration script and the hook. Quoted examples inside
   fenced blocks had been misread as live fields, so both now strip fences the same way.
3. **Backfill evidenced values separately from inferred ones** with a `Review-evidence:`
   line. Evidence that a change landed is not evidence that it was reviewed.
4. **Then validate,** sweeping the corpus by invoking the real hook. It rejected 36 of 161
   docs, against an estimate that was off by an order of magnitude. Prove each negative
   test by mutating the hook.

The same sequencing appears in [[Backfill Without the Forward Path]].

## See Also
- [[Plan-Doc Status Enum]] — extends (the enum audited here)
- [[Write-Only Fields and the Reader Map]] — alternative-to (the mirror defect: written, never read)
- [[Observed Transitions, Not Declared]] — extends (vocabulary vs transition validation)
- [[Decision-Seat Inventory for a Control Plane]] — prerequisite-for
- [[The Run Record Belongs to the Process]] — instance-of (writerless `pending`/`canceled` run statuses found while designing resume)
- [[Follow-Up Step Needs a Derived Worklist]] — related (a status flip that left the next step with no surface)
- [[Control Plane Owns the Join, Not the Truth]] — extends (the writer map is one subdomain of the join)
