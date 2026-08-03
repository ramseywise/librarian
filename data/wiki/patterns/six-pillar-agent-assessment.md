---
title: Six-Pillar Agent Engineering Assessment
tags: [llm, reference]
summary: A rubric scoring agent codebases across six engineering pillars — prompt, context, harness, loop, graph, evaluation — with each pillar's requirements tiered Must/Should/Nice so a coverage percentage separates "missing the foundation" from "not yet mature."
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/docs/research/template-pillar-gaps.md
---

# Six-Pillar Agent Engineering Assessment

A rubric for auditing an agent codebase — or a scaffold that generates them — against six
named engineering disciplines. Each pillar carries a table of requirements, each requirement
is tiered, and coverage is reported per pillar rather than as a single score.

| Pillar | What it audits |
|---|---|
| **Prompt** | System prompt with role + constraints, output format spec, template separation, versioning, few-shot structure, injection defense |
| **Context** | Retrieval integration point, static/dynamic context separation, progressive disclosure, compaction triggers, cache prefixes, token budgets |
| **Harness** | CLAUDE.md conventions, tool schemas, error handling, env-driven settings, hooks/middleware, guardrails, sandboxing, cost envelope |
| **Loop** | Iteration cap, termination condition, max-cycles test, verification loop, maker/checker separation, durable state, stall detection |
| **Graph** | Multi-agent decomposition, state schema, conditional routing, HITL interrupts, checkpointer wiring, fan-out/fan-in, subgraphs |
| **Evaluation** | Unit tests, CI, pre-commit hooks, task/trial/grader suite, golden datasets, metric gates, observability spans, drift monitoring |

The pillars are ordered roughly by scope: prompt is a string, context is a window, harness is
a process, loop is time, graph is topology, evaluation is the feedback that closes over all
five.

---

## The tiering is what makes coverage legible

Every requirement is **Must / Should / Nice**. Without tiers a coverage number is
uninterpretable — 65% could mean the foundation is missing or that the polish is. With
tiers it decomposes:

| Tier | Must | Should | Nice | Coverage |
|---|---|---|---|---|
| Overall (AIT, 2026-07-29) | **25/25** | 5/17 | 2/11 | 65% |

> *"AIT hits 100% of Must-tier requirements — the foundation is solid. The gaps are in
> Should (29%) and Nice (18%) tiers, which map exactly to the intermediate→advanced
> maturity jump."*

A 100%-Must / 29%-Should profile is a *different diagnosis* from a 60%-Must one, and the
prescription differs: the first needs capability additions, the second needs rework. The
flat percentage hides that distinction, which is why the pillar-by-tier matrix is reported
alongside it and not replaced by it.

## Per-pillar coverage localizes the weakness

Reporting one number per pillar identifies where to spend:

| Pillar | Coverage |
|---|---|
| Evaluation | 76% (strongest) |
| Prompt | 67% |
| Harness | 67% |
| Graph | 63% |
| Context | 60% |
| **Loop** | **50% (weakest)** |

Loop scoring lowest while Must-tier is complete is the characteristic intermediate profile:
the agent terminates (cap, condition, test — all three Must items present) but never
*verifies*. Every Should and Nice item in the pillar was absent — verification loop wrapper,
maker/checker separation, durable state by default, event triggers, stall detection,
hill-climbing trace analysis. The durable-state item is the one with an existing home —
see [[Runtime Topology and Checkpointer Alignment]].

## Evidence must cite file:line

Every `have` row in the scaffolded tables names a file and line — `agent.ts.jinja:24`,
`framework-lg.md:38-41`, `eval.md:176-223`. This is the same discipline as a
[[Capability Parity Audit]]: an assessment recorded from memory over-reports coverage,
because the author remembers the *intent* of the scaffold rather than its rendered state.
A requirement without a citation is a gap, regardless of what anyone recalls building.

The inverse also holds — several gap rows record that the *concept* exists somewhere in the
repo but is not wired in: compaction *"exists in `cap-compaction.md` reference but isn't
wired into the scaffold"*; `DriftGrader` is *"mentioned in eval.md but not scaffolded"*;
the checkpointer *"exists as optional skill, not default."* Documented-but-unwired counts
as absent, because a scaffold's job is to produce the wiring.

## See Also
- [[Capability Parity Audit]] — alternative-to (per-consumer request matrix rather than a fixed rubric)
- [[Template Floor Raising]] — extends (what to do with the gap list once produced)
- [[AI Project Template Scaffold]] — instance-of (the artifact under assessment)
- [[Runtime Topology and Checkpointer Alignment]] — part-of (the loop pillar's durable-state requirement)
- [[Send API Fan-out]] — part-of (the graph pillar's headline gap)
- [[Eval Ladder]] — alternative-to (maturity progression scoped to evaluation only)
- [[Anthropic Three-Tier Eval Taxonomy]] — related (tiering applied within the eval pillar)
- [[HistoryCondenser]] — part-of (the context pillar's compaction requirement)
- [[Prefix Caching]] — part-of (the context pillar's cache-prefix requirement)
