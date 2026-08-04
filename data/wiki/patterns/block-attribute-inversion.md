---
title: Block Attribute Inversion
tags: [llm, pattern]
summary: Turning a list of unanswerable design questions into per-component metadata — when each architectural block ships with its own failure mode, scaling limit, and cost driver, the design's weak points are generated from the assembly rather than interrogated from a user who cannot answer.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-30-system-design-rigor-gap.md
---

# Block Attribute Inversion

A gap analysis of a design-interview pipeline produced eight missing rubric elements —
non-functional budgets, bottleneck analysis, trade-off narration, observability planning.
The obvious remedy is six more interview questions. The non-obvious result of a second
research round was that **the gaps are not questions at all — they are attributes of the
components the design already names.**

> *"The six Round 1 gaps are not six independent questions to ask the user — they are
> per-block attributes."*

## The mechanism

Give every block in the design vocabulary a fixed metadata schema:

```
{failure_mode, detection, recovery, scaling_limit, cost_driver,
 latency_contribution, eval_metric, trade_off_axis}
```

Then bottleneck analysis and cost/latency budgeting are **generated from the assembly**
rather than asked. The user answers a question they can actually answer — *"does this
project need retrieval?"*, already asked as `/scope-poc` Q7b — and the "what breaks first"
content arrives attached to the retrieval block they just selected.

The schema is not invented. The source rubric already carries it distributed across tables:
a bottleneck table, a failure-mode table with Detection and Recovery columns, a trade-off
table naming each component's axis, and per-topic eval metrics and cost drivers. The
inversion is a relocation, not new content — *"the Round 1 gap list, relocated."*

## Why this defuses the "volunteer can't answer" objection

The strongest counter-argument against adding rigor to a nonprofit-volunteer design
interview is that the questions are unanswerable:

> *"A latency-budget question asked of a volunteer who has never deployed anything produces
> a made-up number."*

Worse, the pipeline's own *"'I don't know' is a first-class answer"* convention would then
park the non-answer as an Open Question — which **blocks the discovery-exit gate**. Adding
a rigorous question actively makes the pipeline worse for its actual audience. See
[[Scope-POC Design Interview]] for that convention.

Block attribute inversion sidesteps this entirely. The block supplies its failure mode
*"as a default to accept or override."* A made-up p95 is replaced by a defensible one the
volunteer can react to — which is a strictly easier cognitive task than generating it, and
the same asymmetry that makes [[Asked vs Derived Scaffold Variables]] derive-then-confirm
rather than ask.

## Blocks are chosen by recurrence, not by taxonomy

The vocabulary was derived empirically — count how often each component appears across the
rubric's eight worked examples:

| Block | Recurrence |
|---|---|
| Generation / LLM inference | 8 of 8 |
| Observability / tracing | 7 |
| Retrieval pipeline | 6 |
| Eval pipeline | 6 |
| Data pipeline / ingestion | 5 |
| Orchestration / agent loop | 4 |
| Output validation / guardrails, caching, model routing | 3 |
| State store, HITL queue, API gateway, knowledge graph | 2 |

Recurrence across independent worked examples is evidence a block is real rather than an
artifact of one architecture — the same reason [[Template Floor Raising]] counts repos
rather than trusting a single project's request.

## Topology-shaping vs. cross-cutting — the split that created the gap

Cross-referencing the recurrence table against what the scaffold's `design.yaml` actually
records revealed a clean and unstated rule:

> *"design.yaml names the blocks that are topology-shaping choices (which framework, which
> vector store) and omits the blocks that are cross-cutting concerns (tracing, caching,
> guardrails, state)."*

This is *"a defensible design philosophy, and it is the structural reason"* observability
and safety came out as **"code exists, decision never made."** A cross-cutting concern
classified as config gets shipped correctly and designed never — see
[[Derived-and-Hidden Design Decisions]].

## The limit: topology is not reasoning

The same research round tested whether the block graph could *be* the design artifact —
rendered as a mermaid node diagram. It can carry nodes; it cannot carry the graded content:

> *"A node graph carries topology, not reasoning… A diagram that omits the rationale
> reproduces [the trade-off gap] in prettier form."*

Per-block metadata is what rescues this. Each node can surface its own failure mode and
trade-off axis as an annotation, which is more than boxes — but the *"we chose X over Y,
giving up Z"* narration remains prose that no assembly generates.

## See Also
- [[Scope-POC Design Interview]] — extends (the interview whose unasked questions this replaces)
- [[Derived-and-Hidden Design Decisions]] — complements (what the topology/config split hid)
- [[Asked vs Derived Scaffold Variables]] — related (the same derive-then-confirm asymmetry)
- [[DESIGN.md Artifact]] — related (the artifact the blocks would render into)
- [[System Design Interview Study Guide]] — prerequisite-for (the rubric the blocks were derived from)
- [[Six-Pillar Agent Engineering Assessment]] — alternative-to (audit a codebase against a rubric rather than generate from blocks)
- [[Template Floor Raising]] — related (recurrence-counting as the evidence standard)
