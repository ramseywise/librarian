---
title: Evaluating Prompts
tags: [prompting, eval, concept]
summary: Prompt-level evaluation — build the eval before the prompt; match test style to what changes (model, single prompt, composition); climb from a git-diffed example suite to an automated harness by solving sample sourcing and scoring independently; then A/B online with success and guardrail metrics fixed up front.
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--09-evaluating-prompts.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--01-prompt-engineering--notes--08-prompt-optimization.md
  - data/raw/papers/2026-11-06-yeadon-2024-comparison-human-gpt-3-5.md
  - data/raw/papers/2026-11-07-prompt-engineering-for-generative-ai-ch01-five-principles-of-prompting.md
  - data/raw/papers/2026-11-07-prompt-engineering-for-generative-ai-ch03-standard-practices-text-generation.md
  - data/raw/papers/2026-11-07-prompt-engineering-for-generative-ai-ch04-advanced-text-generation-langchain.md
  - data/raw/papers/2026-11-07-prompt-engineering-for-generative-ai-ch10-building-ai-powered-applications.md
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

## A course-marking study

Yeadon et al. (2024) compared students with GPT-4 on a university coding course, using a marker for scoring. Students averaged 91.9% (the body text says 91.1%, an internal inconsistency in the extraction) against 81.1% for GPT-4 with prompt engineering. Prompt engineering moved GPT-4 from 71.9 to 81.1 and GPT-3.5 from 30.9 to 48.8; a mixed condition scored 76.0. Marker accuracy was 85.3% with an ICC of 0.932 (all self-reported). Limits: one course, small samples, 2024-era models.

## Phoenix and Taylor's evaluation advice

Phoenix and Taylor (*Prompt Engineering for Generative AI*, chapters 1, 3, 4 and 10) replace blind trial and error with blind, shuffled thumbs ratings across several runs of each prompt variant. In their chapter 1 example, a zero-shot prompt and a two-example prompt for shoe product names were each run five times on gpt-3.5-turbo, and the few-shot variant won (one rater, no significance test). When ground truth exists they suggest scripted checks (cost, latency, classification, reasoning, hallucination, safety, refusals, similarity by BLEU/ROUGE or vector distance), recycling rated outputs as examples or fine-tuning data, and Elo to rank models. A shorter prompt that scores the same saves cost and latency, and many prompt parts turn out to be unnecessary.

- **Run counts.** Chapter 1 puts the number of runs needed to expose a prompt's flaw at under ten (author experience, no data). Chapter 10 recommends at least ten runs per case, since outputs vary, yet does not state its own count.
- **LLM as evaluator.** Chapter 3 claims model-based grading is about ten times cheaper than human grading and takes minutes, not days or weeks (no data), while conceding that evidence on LLM graders is mixed. Its example had gpt-4 label ten gpt-3.5-turbo replies to one question as concise or not; the labels agreed with the known alternating styles on all ten. Advice: grade a weak model with a stronger one, probe the grader with false-positive and false-negative cases, and try cheap code checks such as reply length first.
- **Cheaper model against GPT-4 labels.** Chapter 4's mistral-small (Mixtral 8x7b) matched GPT-4's labels exactly on 77.5% of bank transactions (type and category; transaction count unstated). It also says to read a pairwise judge's stated reasons yourself, because GPT-4 can misjudge tasks it handles badly.
- **Style-rewrite test.** Chapter 10 scored prompts on three test cases by embedding distance to a hand-written rewrite (smaller is closer), with scores shown only in a figure. It cites an OpenAI suggestion of 50 or more samples when fine-tuning for a writing style.

## Limits

- The Phoenix and Taylor material rests on 2023-24 models. Chapter 1's only quantitative test is five samples per variant with one rater, and the authors admit hand rating is laborious and may not reflect the target audience. Chapter 3's evaluator example is a single transcript whose printed script passes the reply as a second system message. Chapter 4's 77.5% is against GPT-4 labels, not human ones. Chapter 10's experiment is three test cases with no run count or spread, and the authors call their own evaluation advice haphazard and messy.

## See Also
- [[SOMA Judge Rubric]] — extends
- [[LLM-as-Judge Evaluation]] — extends
- [[Prompt Optimization]] — prerequisite-for
- [[Logprobs as Confidence Signal]] — extends
- [[FormatSpread]] — related (format spread as a reporting practice)
- [[Prompt Order Sensitivity and Entropy Probing]] — related
