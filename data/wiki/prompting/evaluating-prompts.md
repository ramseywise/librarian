---
title: Evaluating Prompts
tags: [prompting, eval, concept]
summary: Prompt-level evaluation — build the eval before the prompt; match test style to what changes (model, single prompt, composition); climb from a git-diffed example suite to an automated harness by solving sample sourcing and scoring independently; then A/B online with success and guardrail metrics fixed up front.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--09-evaluating-prompts.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--08-prompt-optimization.md
---

# Evaluating Prompts

Build the eval first — in one widely used code assistant, the eval framework was the oldest
part of the codebase, older than the prompts or the UI. Always log **latency and token
counts** too; they are cheap and catch regressions unrelated to quality.

| What changes | Test style |
|---|---|
| The model (swap/upgrade) | Broad regression suite; test each step on its own model |
| A single prompt | Small unit tests on one model call |
| The composition (chain, loop) | End-to-end regression — no unit-level substitute |

If you can build only one, build **end-to-end**, then unit-test the critical path.

## Offline tech tree

**Level 1 — example suite.** 5–20 realistic inputs, a script that renders each prompt,
calls the model, and writes prompt + completion to files; commit them and review with
`git diff`. Not pass/fail — you eyeball changes, and repeated exposure teaches the failure
modes. Works from the first draft; stops scaling at the number of diffs you'll read.

**Level 2 — harness.** Hundreds to thousands of examples with automatic scoring. Two
independent problems: where samples come from and how outputs are scored.

| Sample source | Strength | Watch out for |
|---|---|---|
| Existing records (people solving it without AI) | Realistic, plentiful | Ubiquity vs. similarity — e.g. delete function bodies from open-source repos to simulate "cursor here" |
| App telemetry | Real inputs | Absent before launch; invalidated by app changes; consent; outcomes biased by your own suggestions |
| Synthetic | Cheap controllable coverage | Tropes; **bias toward the generating model** if it is also under test ([[Diversity Seeding for Synthetic Data]]) |

Synthetic data works best when you can start from the solution and invent the problem
backward, or need situations without a gold answer.

**Scoring, most to least rigorous:**

1. **Gold-standard match** — exact for labels; *partial* on the one aspect that separates
   breaking from benign divergence (did it touch the heating system, not did it pick 77°F).
   For classification compare **logprobs**, not sampled labels ([[Logprobs as Confidence Signal]]).
   For tool calls check in order — called a tool → right tool → valid syntax → right values
   — since an early failure invalidates later checks.
2. **Functional test** — parses, compiles, passes the repo's own tests, calls only real tools
   with typed arguments.
3. **LLM-as-judge** — for helpfulness, tone; write it as a [[SOMA Judge Rubric]].

**Multi-turn:** canned conversations (isolate turns, miss compounding errors) or an
LLM-mocked user (end-to-end, inherits the mock's biases).

## Online

Live traffic is the only fully valid test but bandwidth is scarce — whittle candidates
offline first. Define **success metrics** (e.g. acceptance rate) and **guardrail metrics**
(error/complaint rate) *before* starting; compare randomly assigned users only (update
timing correlates with behaviour). Metrics from direct to incidental: explicit feedback
(captures frustration more than delight; delayed feedback often beats immediate) →
functional correctness → **user acceptance** (best productivity predictor for a code
assistant) → achieved impact → incidental (latency, conversation length).

## Case study: small changes, large effects

Clavié et al. (2023), job-posting classification, one modification at a time:

| Prompt | F1 | Template adherence |
|---|---|---|
| Baseline | 65.6 | 79% |
| Few-shot CoT | 78.4 | 87% |
| Zero-shot CoT | 81.4 | 65% |
| + role in system, task in user | 87.5 | 71% |
| + mocked acknowledgement + reiterated key points | 89.3 | 75% |
| + strict output template | 86.3 ↓ | 98% |
| + "reach the right conclusion" + common failures | 90.3 | 77% |
| + name + positive feedback | 91.7 | 81% |

- Wording moved F1 by **26 points** — more than the gap to a fine-tuned baseline the LLM beat.
- **Zero-shot CoT beat few-shot CoT**: the examples anchored the model ([[Few-Shot Prompting]]).
- **A strict template lowered accuracy** while raising adherence — parse loosely or
  constrain in a separate step ([[Structured Output]]).
- Instructions plus reiteration of key points was the largest single driver.
- The tiny gains are model-specific; **the methodology is the lesson — change one thing, re-score.**

## See Also
- [[SOMA Judge Rubric]] — extends
- [[LLM-as-Judge Evaluation]] — extends
- [[Prompt Optimization]] — prerequisite-for
- [[Logprobs as Confidence Signal]] — extends
