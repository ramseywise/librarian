---
title: Prompted Reflection vs Graph-Gated CRAG
tags: [rag, langgraph, comparison]
summary: "Two ways to build corrective RAG — a single agent that runs grade/rewrite/re-search through tools under a system prompt, or explicit graph nodes with numeric confidence gates — trade adaptivity for inspectability; neither catches synthesis-step hallucination, and ablation shows the loop adds little when first-pass hybrid retrieval is already strong."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/project-g/docs/stakeholders/agent-comparison-findings.md
  - data/raw/claude-docs/project-g/docs/research/VIR-179-ablation.md
---

# Prompted Reflection vs Graph-Gated CRAG

From a side-by-side audit of three support agents on the same domain (project-g): a
template agent implementing CRAG as a prompted tool loop, a minimal one-tool ReAct baseline,
and a LangGraph pipeline implementing CRAG as explicit nodes — plus the ablation that measured
what the loop actually bought.

## The two shapes

**Prompted reflection loop (single ADK agent, ~6 tools).** The system prompt orchestrates:
`classify_and_search` first classifies query complexity — *simple* skips reflection,
*moderate* reflects, *complex* decomposes then multi-searches then reflects. Reflection is a
`grade_relevance` tool returning a structured per-document `relevant | ambiguous | irrelevant`
grade, an overall score, and a `needs_refinement` flag; refinement rewrites and re-searches,
with a hard ceiling of 3 attempts. The final answer embeds a HIGH/MEDIUM/LOW confidence tier.

**Graph-gated CRAG (LangGraph, ~9 nodes).** The same behaviour encoded structurally:
`planner → retriever → qa_policy_retrieval → [rerank | escalate | retry] → reranker →
qa_policy_rerank → [answer | escalate | retry] → answer → post_answer_evaluator`. Gates route
on numeric thresholds, not LLM reasoning (see [[CRAG Retry Logic]]).

| Dimension | Prompted loop | Graph gates |
|---|---|---|
| Routing decision | LLM reasons per step | Threshold comparison |
| Skips work on easy queries | Yes — complexity classified before retrieval | Only if a gate is built for it |
| Inspectability | Recover from trace tool sequences | Node path is the trace |
| Determinism | Prompt-sensitive | Same input → same path |
| Loop bound | Prompt + config ceiling | Graph edge + counter |
| Post-generation grounding | None in the audited template | `post_answer_evaluator` node |

## What neither shape gives you for free

**Synthesis-step hallucination.** In-flight reflection grades *retrieved documents*; an agent
can pass every grading loop and still hallucinate while writing the answer. Only a
post-generation grounding check (cited URL must be in the retrieved set; KB called but no
sources → escalate; claim-quote coverage) closes that — see
[[Safeguards Architecture — Five Protection Layers]].

**A measure of whether the loop helps.** Loop depth and success are measurable only if you
log them: count `grade → rewrite → search` cycles from trace tool sequences (prompted) or
increment a retrieval counter in state and emit it as run metadata at END (graph). Metrics:
iterations per query, fraction of loops that improved retrieval, iterations to success.

## What the ablation said

| Change | ΔMRR | Δlatency | Reading |
|---|---|---|---|
| CRAG off → on (graph agent) | +0.005 | +3.4s | Managed hybrid retrieval already returned good passages; the loop rarely triggered |
| CRAG + thinking budget | −0.063 | ~0 | Thinking changed citation formatting, breaking the CRAG grader's alignment — features interact |
| LLM planner replacing regex router | −0.031 | +0.6s | Domain-tuned regex beat the LLM classifier |
| Multi-query expansion | helped clean core subset, hurt full set | ~+5s always | Adds noise on edge/verify cases |

Decision recorded: **CRAG is better value than multi-query** — CRAG costs latency only on hard
queries; multi-query costs it on every query. But a correction loop on top of strong
first-pass retrieval is mostly latency; spend on retrieval quality first.

Related ablation lesson: the graph agent loaded conversation history into state but no
answering node ever read it — multi-turn context was silently dropped until a
`MEMORY_TURNS` injection was added. The ADK agent threads session history automatically, so
the bug existed on one side of the comparison only; parity audits should check that state is
*consumed*, not just populated.

## See Also
- [[CRAG Retry Logic]] — extends
- [[Agentic RAG — Advanced Patterns]] — extends
- [[ADK vs LangGraph Comparison]] — instance-of
- [[Multi-Step Graph Orchestration]] — extends
- [[project-g Eval Architecture]] — extends (the VIR-179 ablation numbers)
