---
title: BIG-bench
tags: [eval, reference]
summary: "A community-built benchmark of 204 tasks from 450 authors at 132 institutions, run on models from 2M to 175B parameters; the best models scored under 20 on the normalised aggregate where expert raters would score close to 100, and about 5% of tasks showed sudden gains with scale (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-srivastava-2022-beyond-imitation-game.md
---

# BIG-bench

BIG-bench (Srivastava et al., "Beyond the Imitation Game", arXiv 2206.04615, published in TMLR 2023
per the extraction's ledger) is an open benchmark built by community contributors. Its authors argue that
current benchmarks cover too little ground and top out fast, and they use it to study how performance
shifts with model scale over many difficult tasks.

## Contents

- **204 tasks**, written by 450 authors from 132 institutions: roughly 80% are JSON example-based and
  roughly 20% are Python programmatic, all behind an open API.
- **BIG-bench Lite** is a 24-task JSON subset meant to make evaluation cheaper.
- Each task score is normalised as `100 x (raw - low) / (high - low)` on the task's preferred
  metric, where the task's author picks the low and high anchors; the normalised scores are then averaged.
- Every task file contains a **canary GUID**, so that scrapes can be filtered out and training on the
  test set can be diagnosed. See [[Eval Contamination Defenses]].

## Setup

The model families are GPT and two BIG-G variants (dense and sparse), spanning 2M to 175B parameters, evaluated with zero to
three shots and greedy decoding on at most 1,000 examples per task (1,024 input tokens, 64 output tokens).
The human baseline comes from expert raters, who worked 30 minutes to 2 hours daily for several weeks,
saw only a subsample of each task, and could search the internet.

## Results (self-reported)

- Normalised aggregate scores for the best models stay below 20 (BIG-G dense and sparse and GPT, 0-3 shot, greedy).
  At the top scale (BIG-G 137B), roughly half of the tasks reach a score of 10 or more.
- On the aggregate, BIG-G sparse equals BIG-G dense at roughly half the inference cost. On the
  multiple-choice tasks it hits a given calibration score with a FLOP-matched parameter count about ten
  times smaller.
- Every model is poorly calibrated, and calibration gets better with scale (109 multiple-choice JSON
  tasks, with the top-1 normalised probability taken as confidence).
- Around 5% of tasks show an abrupt jump with scale. The authors propose that jumps on multistep tasks
  occur because overall success multiplies per-step probabilities; the extraction labels this
  speculation that was not tested.
- Adding the answer options to the query lowered BIG-G scores on the multiple-choice JSON tasks, even
  with few-shot examples. Stochastic sampling (temperature 1, top-k 40) also scored consistently below greedy.
  Compare [[Benchmark Prompt Format Sensitivity]].
- On `checkmate_in_one`, the 128B BIG-G produces six checkmates among 1,024 zero-shot attempts, while its
  accuracy at legal moves climbs smoothly with scale.
- On bias tasks, scaling makes bias worse when the context is ambiguous and better when it is
  unambiguous or when a pro-social prompt is used. On `bias_from_probabilities`, the 128B model rates a
  white boy becoming a good doctor as more than 22 times likelier than a Native American girl doing so.
- Non-English results: English `entailed_polarity` accuracy climbs to 90% with scale but the Hindi
  version stays below 70%; on `language_identification` across more than 1,000 languages the best models
  reach about 17%, with no trend over scale.

## Limits

- The human baselines are weak lower bounds, given the short rating time, the task subsampling, the
  tasks that were edited while rating was under way, and unrepresentative rater demographics.
- Aggregate scores hinge on anchors that task authors chose, and the choice of one metric can make a
  capability look flat, gradual or abrupt.
- Leakage can occur indirectly, since many tasks reuse text from the web, and the canary would miss it.
- The observations about breakthroughs and linearity are anecdotal.
- The models are from 2021-2022 and mostly evaluated in English. PaLM and Gopher gain off the trend, so
  the scaling extrapolations are now out of date. The Google models' cross-entropy is measured on
  their training set, whereas the GPT models are scored on OpenAI's test set.
- Text only, no multimodal tasks. No compute, seeds or training hyperparameters are reported for
  BIG-G.

## See Also
- [[HELM Holistic Evaluation]] — related (a standardized multi-metric evaluation that compares itself with BIG-bench)
- [[HELM Holistic Evaluation]] — related (a standardized multi-metric evaluation that compares itself with BIG-bench)
- [[Eval Contamination Defenses]] — related (the canary tactic this benchmark uses)
- [[AGIEval]] — alternative-to (a human-exam benchmark of the same period)
- [[GPQA]] — alternative-to (narrow, expert-written questions in place of a broad community set)
- [[Benchmark Prompt Format Sensitivity]] — related (option-in-query and decoding effects)
