---
title: Evals and Observability Interview Study Guide
tags: [eval, interview, reference]
summary: Exam-prep reference for eval and observability questions — vocabulary, grader types, three-tier taxonomy, pass@k vs pass^k, and the tracing-first discipline.
updated: 2026-07-19
sources:
  - raw/repos/learn-ai-engineering/interviewing--guides--6-evals-observability--interview-guide.md
---

# Evals and Observability Interview Study Guide

The topic that separates "built a demo" from "shipped a system." Nearly every 2026 loop asks some form of "how do you test non-deterministic outputs?" — this guide is that answer.

## Vocabulary (Get These Crisp)

- **Task / trial / grader**: a task is one test (inputs + success criteria); a trial is one attempt (outputs vary → run several); a grader scores one aspect. One task can have many graders.
- **Trajectory vs outcome**: outcome = did it achieve the goal; trajectory = did it get there acceptably (full record: tool calls, reasoning, intermediate steps). Grade both — right answer via unsafe path fails.
- **Agent harness vs eval harness**: the runtime being tested vs the infrastructure that runs tasks, records traces, applies graders, aggregates. The eval harness treats the agent harness as the system under test.
- **Offline vs online eval**: curated dataset runs vs scored live traffic.

## Grader Types — Choose the Simplest Reliable One

1. **Deterministic** — string/structure match, unit tests, state checks. Highest certainty; always prefer when a clear correct answer exists.
2. **LLM-as-judge** — rubric scoring, pairwise comparison, multi-model voting. For semantic quality. Judges have systematic biases → calibrate against a human-labeled set and re-check for drift.
3. **Human** — expert sampling, annotation. Slow, reliable; sets the ground truth that calibrates layer 2.

## Three-Tier Taxonomy (Cost-Ordered)

| Tier | What | Properties | Coverage |
|---|---|---|---|
| 1 Unit | tool selection, param extraction, routing, formatting | deterministic, CI-safe, no LLM calls | ~70% of regressions |
| 2 Trajectory | ordered node/tool sequence with mocked tools | semi-deterministic, traced, cost-gated | routing/path failures |
| 3 End-to-end | final answer quality (LLM judge, RAGAS/DeepEval) | most realistic, most expensive | release quality gates only |

Interview move: walk tiers bottom-up and say where each failure class gets caught — cheap tiers first is the judgment being tested.

## Non-Determinism: pass@k vs pass^k

- **pass@k** — at least one of k trials succeeds. Measures capability ceiling.
- **pass^k** — all k trials succeed. Measures deployment reliability: 75% per-trial success → pass^3 ≈ 42%. Customer-facing agents live and die by pass^k.

**Capability vs regression suites**: capability evals ask "what can it do?" (low pass rates fine); regression evals ask "does it still do everything it used to?" (~100% required). Saturated capability evals graduate into the regression suite.

## Tracing-First Discipline

You cannot evaluate what you cannot observe. Build the trace before the metric. Every tool call, every routing decision, every generation span should be a named span in the trace tree — that's what makes failure attribution possible.

## See Also
- [[Anthropic Three-Tier Eval Taxonomy]] — instance-of
- [[Observability & Evaluation Glossary]] — prerequisite-for
- [[VA Eval Harness]] — instance-of
- [[System Design — Unified Eval Harness]] — instance-of
- [[Agents Interview Study Guide]] — extends
