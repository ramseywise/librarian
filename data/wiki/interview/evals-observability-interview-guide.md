---
title: Evals and Observability Interview Study Guide
tags: [eval, interview, reference]
summary: Exam-prep reference for eval and observability questions — vocabulary, grader types, three-tier taxonomy, pass@k vs pass^k, and the tracing-first discipline.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--guides--6-evals-observability--interview-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--evals-observability.md
  - data/raw/repos/sisyphus/interviewing--guides--6-evals-observability--interview-guide.md
  - data/raw/repos/sisyphus/interviewing--guides--6-evals-observability--00-overview.md
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

## Follow-ups (answer sketches)

*Provisional:* condensed from the reference answers to the chapter questions in *AI Agents in Depth* (Li), which the book itself flags as AI-drafted with light human review. Treat these as answer shapes to check, not settled claims.

- *Does LLM-as-judge have systematic blind spots?* Length and style bias, same-family favouritism.
  Detect with a 100–200 item human gold set (Cohen's κ), length-vs-score audits and red-team cases;
  correct with rubrics that penalise verbosity and judges from other model families
  ([[LLM-as-Judge Evaluation]], [[LLM Judge Biases]]).
- *Is there an endgame to benchmark leakage?* Not for static question banks — publish the generator,
  keep instances private, grade on final environment state. See [[Parameterised Benchmark Instances]].
- *Reliable rubrics for subjective dimensions.* Translate each into observable behaviours with examples
  and boundary cases per grade, grow the rubric into a casebook from rater disagreements, calibrate
  against a gold set.
- *Validating a simulated user.* Spot-check dialogues for progressive disclosure and no invented facts,
  and check that small real-user runs rank systems the same way. A distorted simulator makes absolute
  scores meaningless even when relative rankings hold ([[Simulated User Evaluation]]).
- *Preferences are not transitive — what happens to Bradley–Terry rankings?* They drift with the
  prompt mix. Rank per capability and publish the pairwise win-rate matrix
  ([[Bradley-Terry Preference Model]]).
- *Each hypothesis needs hundreds of runs.* Run cheap prompt-level hypotheses first and gate expensive
  ones on them; use paired tests (McNemar) on the same tasks ([[Paired Eval Comparison]]); do not decide inside the noise band; grow
  the set when it cannot resolve the expected gain.
- *When should thinking mode be on?* Route on task features, historical failure clusters and runtime
  uncertainty (backtracks, repeated errors). It hurts real-time voice and UI work and is waste on
  simple tasks.
- *Debugging an end-to-end voice model.* Make it emit readable intermediates (an inner-monologue text
  stream, event tags), compare against a cascaded run to separate perception from reasoning errors,
  keep per-dimension offline regressions.

## See Also
- [[Anthropic Three-Tier Eval Taxonomy]] — instance-of
- [[Observability & Evaluation Glossary]] — prerequisite-for
- [[VA Eval Harness]] — instance-of
- [[System Design — Unified Eval Harness]] — instance-of
- [[Agents Interview Study Guide]] — extends
- [[Parameterised Benchmark Instances]] — instance-of (the answer to benchmark leakage)
- [[AI Engineering Field Question Bank]] — related (cold-recall questions for this pillar)
- [[Agent Engineering Question Chains]] — extends (scenario main/follow-up chains on evals, tracing and prompt changes)
