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
per the extraction's ledger) is an open, community-contributed benchmark. The authors start from the view
that existing benchmarks are too narrow and saturate quickly, and they ask how capability changes
with scale across a broad set of hard tasks.

## Contents

- **204 tasks** from 450 authors at 132 institutions, about 80% JSON example-based and about 20%
  Python programmatic, with an open API.
- **BIG-bench Lite**, a 24-task JSON subset for cheaper evaluation.
- Task scores are normalised as `100 x (raw - low) / (high - low)` on each task's preferred
  metric, with the low and high anchors chosen by the task's author, then averaged.
- Every task file carries a **canary GUID** so scrapes can be filtered and training on the test
  set diagnosed. See [[Eval Contamination Defenses]].

## Setup

Models: BIG-G dense, BIG-G sparse and GPT, from 2M to 175B parameters, run zero- to three-shot with
greedy decoding on up to 1,000 examples per task (1,024 input and 64 output tokens). Expert human raters
provide a baseline, working 30 minutes to 2 hours a day for weeks with task subsampling and
internet search allowed.

## Results (self-reported)

- The best models score under 20 on the normalised aggregate (BIG-G dense and sparse and GPT, 0-3 shot, greedy); at the
  largest scale (BIG-G 137B) about half the tasks score 10 or higher.
- BIG-G sparse matches BIG-G dense at about half the inference cost on the aggregate, and reaches a
  given calibration score with about a tenfold smaller FLOP-matched parameter count on the
  multiple-choice tasks.
- Calibration is poor for all models and improves with scale (109 multiple-choice JSON tasks, top-1
  normalised probability as confidence).
- About 5% of tasks show a sudden breakthrough with scale. The authors suggest that breakthroughs on
  multistep tasks arise because success is a product of per-step probabilities; the extraction
  marks this as speculation without a test.
- Appending the answer options to the query hurt BIG-G on the multiple-choice JSON tasks, even
  few-shot; sampling at temperature 1 with top-k 40 scored consistently lower than greedy. Compare
  [[Benchmark Prompt Format Sensitivity]].
- On `checkmate_in_one` the 128B BIG-G finds six checkmates out of 1,024 zero-shot while legal-move
  accuracy rises smoothly with scale.
- On bias tasks, bias worsens with scale in ambiguous context but improves in unambiguous context
  and with pro-social prompting; on `bias_from_probabilities` the 128B model finds it over 22 times
  more likely that a white boy becomes a good doctor than a Native American girl.
- Non-English: `entailed_polarity` reaches 90% accuracy with scale in English while the Hindi
  version stays under 70%; `language_identification` over 1,000 languages gets about 17% for the best
  models with no scale trend.

## Limits

- Human-rater baselines are weak lower bounds: limited time, task subsampling, tasks edited during
  rating, and non-representative rater demographics.
- The aggregate depends on author-chosen anchors, and a single metric can make a capability look
  flat, gradual or abrupt.
- Indirect leakage is possible because many tasks reuse web text; the canary cannot catch it.
- The breakthrough and linearity observations are anecdotal.
- The models date from 2021-2022 and are mostly English; PaLM and Gopher show off-trend gains, so the
  scaling extrapolations have dated. Cross-entropy for Google models is on the training set while GPT
  uses OpenAI's test set.
- Text only, no multimodal tasks. No compute, seeds or training hyperparameters are reported for
  BIG-G.

## See Also
- [[Eval Contamination Defenses]] — related (the canary tactic this benchmark uses)
- [[AGIEval]] — alternative-to (a human-exam benchmark of the same period)
- [[GPQA]] — alternative-to (narrow, expert-written questions in place of a broad community set)
- [[Benchmark Prompt Format Sensitivity]] — related (option-in-query and decoding effects)
