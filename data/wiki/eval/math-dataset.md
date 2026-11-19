---
title: MATH Dataset
tags: [eval, reasoning-and-math, reference]
summary: "Hendrycks et al.'s 12,500 competition problems with step-by-step solutions and boxed answers (7,500 train, 5,000 test), plus the AMPS pretraining corpus and 2021 GPT-2 and GPT-3 baselines of 3-7%."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-hendrycks-2021-measuring-mathematical-problem-solving-math.md
---

# MATH Dataset

Hendrycks et al. (NeurIPS 2021 Datasets and Benchmarks) study how well ML models handle competition mathematics, which calls for problem-solving heuristics instead of mechanical calculation, and hypothesise that scaling Transformers alone will not solve it. MATH has 12,500 problems from AMC/AIME-style contests (7,500 train, 5,000 test), difficulty levels 1-5 and 7 subjects, each with a step-by-step solution and a boxed final answer; scoring is exact match on the `\boxed{}` answer. AMPS (Auxiliary Mathematics Problems and Solutions) is a 23GB pretraining corpus from Khan Academy and Mathematica. Other math datasets are on [[Math Word Problem Benchmarks]].

## Baselines (self-reported)

The GPT-2 runs (0.1B to 1.5B) first pretrained on AMPS and then fine-tuned on MATH. GPT-3 was either fine-tuned or prompted few-shot with 8 examples, at temperature 0, generating at most 20 tokens, and without AMPS.

- Best average accuracy is 6.9% (GPT-2 1.5B with AMPS, beam search, final answer only). GPT-3 few-shot gets 3.0% at 13B and 5.2% at 175B; BART-Large 0.4B gets 4.9%.
- With AMPS pretraining, a 0.1B GPT-2 equals the 5.2% of a 13B GPT-3 fine-tuned without it.
- Scaling helps slowly: a 15-fold increase in parameters yields a 28% relative gain, and the authors extrapolate log-linearly to roughly 10^35 parameters to reach 40% accuracy.
- Prompting GPT-2 1.5B to write its own step-by-step solution lowers accuracy to 5.3% (the authors hypothesise snowballing errors); fine-tuning on final answers only gives 6.3%. Even when handed 99% of the reference solution, GPT-2 0.7B manages only about 40%.
- Confidence (mean token probability) detects errors weakly, AUROC 68.8%.
- Human reference: six students each took 20 random test problems in an hour without a calculator. A computer-science PhD who dislikes math scored about 40% and an IMO gold medallist 90%.
- Adding Math StackExchange to AMPS pretraining of GPT-2 0.3B gives 6.0%, under the 6.2% from AMPS alone.

## Limits

- The models are 2021-era GPT-2 and GPT-3; the 3-7% figures have been left far behind by later reasoning models (the course note cites 97.3% on MATH-500 for R1).
- Single runs, no seeds or significance tests; GPT-3 was not AMPS-pretrained, so comparisons confound pretraining. Learning rate, schedule and epochs are not stated.
- Only six people took part in the human study, on 20 problems, and four of them were authors. Exact match demands strict answer formatting.

## See Also
- [[Math Word Problem Benchmarks]] — related (earlier word-problem datasets)
- [[GSM-Symbolic]] — related
- [[OlympiadBench]] — related
- [[s1 Budget Forcing]] — related
- [[Minerva Quantitative Reasoning]] — extends
- [[Early GPT-4 Probing and Planning Limits (Sparks of AGI)]] — related
