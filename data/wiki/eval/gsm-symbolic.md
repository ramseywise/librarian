---
title: GSM-Symbolic
tags: [eval, reference]
summary: "A template-based rebuild of 100 GSM8K questions that can be re-instantiated with new names and numbers; across 25 models the score on one question set was a draw from a distribution, adding clauses lowered it, and one irrelevant clause (GSM-NoOp) cost o1-preview 17.5 points (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-05-mirzadeh-2024-gsm-symbolic.md
---

# GSM-Symbolic

GSM-Symbolic (Mirzadeh et al., Apple, ICLR 2025, arXiv 2410.05229) examines the
limitations of mathematical reasoning in LLMs. The authors turned 100
randomly chosen GSM8K test questions into templates: the names and numbers are variables
with allowed ranges, plus conditions on them in the template spec. Each template yields many
instances of the same problem, so a model can be scored on 50 different sets of 100
questions instead of one fixed set. It is a worked case of [[Parameterised Benchmark Instances]]
applied to a static question bank.

## Setup

All runs use 8-shot chain-of-thought with the original GSM8K demonstrations and greedy
decoding; the metric is accuracy. The paper does not say what `±` denotes, though its prose
discusses the figure as the spread across the 50 sets. The authors tested 25 models.

## Results (self-reported)

- **A score is a distribution.** Gemma2-9b-it scored 79.1 (±3.0) over the 50 sets against 87.0
  on the original GSM8K questions. The best-to-worst gap across sets was over 12 points for
  Gemma2-9b-it and about 15 for Phi-3.5-mini.
- **The original usually sits on the high side.** For 21 of 25 models the original-question score
  fell at the upper end of, or beyond, the re-instantiated distribution. The authors offer
  data contamination as one possible explanation and do not test it.
- **Drops differ by model.** Fig. 3 shows GPT-4o losing 0.3 points and Mistral-7b-it-v0.1
  losing 9.2, the two ends of the range, between the original and the symbolic sets.
- **Names matter less than numbers.** Gemma2-9b-it reached 88.6 when only names changed,
  fell to 83.1 when only numbers changed, and to 79.1 when both did, with the variance lower
  for the name-only change.
- **Difficulty.** Removing a clause, then adding one or two, gave Gemma2-9b-it 84.4, 68.1 and
  41.8 (the last two on one and two added clauses); GPT-4o went 94.4, 93.9, 88.0 with the
  spread widening as clauses were added.
- **GSM-NoOp.** Appending one plausible but irrelevant clause caused the largest falls,
  measured against the full GSM8K. Phi-3-mini dropped 65.7 points (from 83.7 to 18.0), GPT-4o
  32.0 and o1-preview 17.5 (from 94.9 to 77.4). Giving eight demonstrations of the same
  question barely helped: Phi-3-medium went from 29.4 to only 30.2, and Llama3-8b from 18.6
  to only 19.6.
- **Arithmetic is not the cause.** Gemma2-9b-it's arithmetic inside its answers stayed between
  97.1 and 98.9 across the variants.

From these results the authors hypothesise that the models are not performing genuine
logical reasoning; they state it as a hypothesis.

## Limits

- Contamination is raised as "one explanation" and never tested; there is no
  training-data or membership check.
- The reference is one score on 100 questions, and each set also holds 100, so a spread of
  about 3 is close to what sampling alone would give at around 80% accuracy (the extraction's
  own estimate, not computed in the paper). The v2 appendix concedes that whether the effect is
  significant depends on which test is used, and that a critic's assumptions would make the
  results non-significant: p was below 0.001 for most models but 0.13 for Llama3-8b and 0.6 for GPT-4o.
- The spread is over instantiations under greedy decoding, not over seeds; the o1 models are
  not greedy.
- Not uniform: on the 100-question baseline, o1-mini rose from 93.0 to 94.5 and
  Llama3-8b-instruct from 74.0 to 74.6, which sits oddly with the claim that every model drops.
- The templates widen the number ranges slightly, so the sets do not have strictly equal difficulty
  (a point the authors dismiss as immaterial). Some table cells look duplicated or inconsistent.
- The model list is from 2024; the largest open model is 27B.

## See Also
- [[Parameterised Benchmark Instances]] — related (the same generate-fresh-instances idea; this page is a static-benchmark case)
- [[Functional Benchmarks and the Reasoning Gap]] — related (an earlier template-based re-instantiation of MATH)
- [[Eval Contamination Defenses]] — related
- [[Eval Error Bars and Sample Size]] — related (a spread and a baseline of 100 questions)
- [[GHOSTS Benchmark]] — related (expert-graded maths prompts from 2023, before automated robustness sets)
