---
title: REFINER Critic Feedback on Reasoning Steps
tags: [prompting, concept]
summary: A generator-critic framework in which a trained critic gives structured, typed feedback on a model's intermediate reasoning, reported to beat scalar PPO reward and LLM-written self-feedback on small math, logic and norm tasks (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-paul-2024-refiner.md
---

# REFINER Critic Feedback on Reasoning Steps

REFINER (EACL 2024) asks whether a trained critic that gives fine-grained, structured feedback on intermediate reasoning improves final answers, and whether it beats a scalar reward. The critic (UnifiedQA-T5-base) is supervised on hypotheses that were automatically perturbed into implausible ones, each paired with a templated error-type message. The generator first gets a warm-up on 10% of the data. It is then trained for T=3 iterations, conditioning on the context, its own previous hypothesis and the critic's feedback; the critic is an oracle during training and exploration uses nucleus sampling. When running, the trained critic keeps giving feedback until it answers "No hint".

## Results (self-reported)

- Math word problems, trained on MAWPs and tested on SVAMP equation generation, 3 runs: the 220M UQA-base generator goes from 34.1 to 47.2 EM with the critic in the loop (+13.1); the 770M large variant reaches 53.8 against 48.2 for UQA-large with PPO on a BLEU reward and 46.7 for UQA-large alone.
- Few-shot GPT-3.5 with CoT on SVAMP, with 2 demos per class, a critic trained on MAWPs and 3 runs: accuracy goes from 67.1 to 70.6 once the trained critic is added. On sNLR the critic adds +6.8 EM for inference rules but just +1.5 for the consequent.
- Against LLM-written feedback: SVAMP with GPT-3.5, 70.6 for REFINER against 67.6 for Self-Refine; GSM8K with ChatGPT, 75.9 against 74.7 (over 3 runs, with a binomial sign test giving p<0.05). On these math problems Self-Refine and Self-reflection add almost nothing; for GPT-3.5 on SVAMP, CoT scores 67.1 and Self-Refine 67.6.
- Combined with other methods on GPT-3.5: self-consistency (5 samples) plus REFINER gives 72.1 on SVAMP against 69.5 for self-consistency alone; ReAct plus REFINER gives 67.8 on GSM8K against 64.7 for ReAct alone.
- With GPT-Neo 1.3B on GSM8K and the Self-Correct protocol: 23.4 for REFINER, 21.2 for Self-Correct, 8.5 base.
- Moral Stories human evaluation, over 100 test examples judged by 3 AMT workers with a majority vote and UQA-large as the baseline: relevant norms rise from 49 to 69 and relevant actions from 58 to 73 (out of 100).
- Ablations on the math task with UQA-base: no critic at inference, 39.8 EM; an oracle critic at inference, 66.0; a critic trained on 30K GPT-3.5-generated implausible hypotheses, 44.1 against 47.2 for rule-based perturbations; dropping the exploration phase, 37.4.
- Noise: a critic with less than 50% noise during training is statistically indistinguishable from the oracle, and past 75% the generator learns to disregard the critic. At inference, 25% critic noise already makes the generator worse than with the trained critic, and over 50% significantly harms it.
- On 500 instances per task, the trained UQA critic produces structured feedback better than few-shot GPT-3.5 (math 69.5 for the 220M critic against 63.5 for GPT-3 175B; sNLR 95.5 against 34.5).

## Limits

- Only three tasks (math word problems, sNLR, Moral Stories); the critic is specific to its task, and the error types are hand-designed for each.
- Feedback helps only when the critic is accurate; the critic fails on outputs with several mistakes, and the generator sometimes ignores or misapplies correct feedback.
- Training relies on an oracle critic with gold hypotheses, whereas the trained critic is used at inference, so a gap to the oracle remains (66.0 against 47.2).
- The human evaluation covers 100 examples and annotator agreement is low to moderate (alpha between 0.33 and 0.64); Moral Stories skews Western.

## See Also
- [[Self-Refine]] — alternative-to (LLM-written feedback with no trained critic)
- [[Reflexion]] — alternative-to
- [[Chain of Thought]] — prerequisite-for
- [[Verification Loops]] — related
