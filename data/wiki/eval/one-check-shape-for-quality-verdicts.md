---
title: One Check Shape for Quality Verdicts
tags: [eval, infra, pattern]
summary: Nine quality flag vocabularies across a pipeline, none of which joined, were replaced by one Check shape — component, kind, rule, rubric, runner, grader — writing to one `quality_verdicts` store keyed by `trace_id`; evals never score production rows (fixtures are exported from human overturns), each component's judged dimensions stay UNGATED until a human-agreement ceiling exists, and the trace tool is where you debug a call while the verdict store is where you read the rate.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-quality-verdicts-refactor.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-quality-verdicts-refactor.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-quality-verdicts-refactor.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-qc-eval-loop.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-qc-eval-loop.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-qc-eval-loop.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-qc-eval-loop.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-qc-eval-loop.md
---

# One Check Shape for Quality Verdicts

A content pipeline (repo akira) had grown quality signals stage by stage: extraction
confidence flags, enrichment status, a QC agent's verdict, a review gate's four statuses,
human review verdicts, sampling outcomes, eval scores — **nine flag vocabularies, none of
which joined** to each other or to the trace of the call that produced the row. The
refactor plan replaced them with one shape.

## The Check

| Field | Meaning |
|---|---|
| `component` | which pipeline stage is being judged (extraction, enrichment, ranking, …) |
| `kind` | deterministic rule vs judged rubric |
| `rule` / `rubric` | the check's definition, versioned |
| `runner` | where it executes — in the pipeline, in the eval harness, in the sampler |
| `grader` | code, LLM judge, or human |
| store | one `quality_verdicts` table, every row carrying `trace_id` |

A human overturning a judge verdict is a Check too (grader = human), written to the same
store, which is what makes overturn rates a query rather than a reconciliation project.

## Three rules that fell out

1. **Evals never score production rows.** The harness runs on fixtures. New fixtures are
   **exported from human overturns** — every time a reviewer disagrees with the system,
   that row becomes a regression case. Production rows are judged by the sampler at
   runtime and recorded; the two populations are never mixed.
2. **UNGATED is per component.** Deterministic checks gate at 1.0 from day one. Judged
   dimensions are recorded but ungated until a [[Human Agreement Ceiling Protocol]]
   result exists for that component. The registry carries the gate state explicitly, so
   "not gated yet" is a visible row, not an absence.
3. **Trace vs record.** The tracing platform (Langfuse here) is where you debug *a*
   call — prompt, tokens, latency. The verdict store is where you read *the rate*.
   `trace_id` on the verdict row is the only join needed; the platform's prompt registry
   and dataset features were deliberately left unused rather than becoming a second
   source of truth for what the pipeline ran.

## Why one shape

The dashboard question "what fraction of enrichment rows this week had a defect, by
stage?" was unanswerable across nine vocabularies and is one `GROUP BY component` with
one. It also makes the [[Taste vs Defect Verdict Split]] general: the defect list on a
human verdict is a Check result like any other.

## Precursor: two judges built twice, split by kind (akira QC eval-loop plan, 2026-09)

The umbrella plan before this refactor found the same thing at smaller scale. An online
QC stage (one LLM verdict per event, gating publish) and offline eval judges (per-attribute
rubrics, graded on 10 hand-written fixtures each) were the same kind of thing, an LLM
judging enrichment output, built twice and never joined. Neither was scored against
humans, while human labels sat unused in five tables. The plan's layout decision was to
**split by kind, not move wholesale**:

- **Production rubrics move to a shared `checks/` module** (heuristic rules + judge
  rubrics), importable by both the pipeline and the eval tree. A lint rule forbade
  anything outside `evals/` from importing it, so a rubric QC needed at runtime *could
  not* live there. Today's judges were unusable online by construction.
- **Exact-match heuristic graders stay in `evals/`** as the CI gate, which runs with no
  key and no network.
- **Rejected:** everything into the tracing vendor (the gate would need a network, and
  30-day retention loses the evidence behind every threshold). Also rejected: everything
  into QC (inverts the evals→app import arrow and drags fixtures onto the production
  graph). Also rejected: a tracing folder in `observability/` (a provider client outside
  the model seam).

The same plan put the three phases in strict order: before-number, then change, then
after-number. It also added a **disagreement stratum** to random human sampling: rows
where QC accepted but a judge said implausible, or where precheck and model disagreed.
Human time goes where the models disagree.

## See Also
- [[Taste vs Defect Verdict Split]] — extends (the human-verdict row this generalises)
- [[Human Agreement Ceiling Protocol]] — prerequisite-for (what un-UNGATEs a judged component)
- [[Eval Suite Maintenance]] — extends (add-from-overturn as the regression-fixture path)
- [[Langfuse Platform]] — related (trace is evidence; the verdict row is the record)
- [[Eval Maturity Ladder]] — related (one store with sampling is the level-4 property)
- [[Online Eval Sampling]] — related
- [[Single-Call LLM Gate Weakness Audit]] — related (the QC stage this generalises)
- [[Human Verdicts as Judge Fixtures]] — related (the labels-to-fixtures half of the same umbrella plan)
