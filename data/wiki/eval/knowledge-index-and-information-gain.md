---
title: Knowledge Index and Information Gain
tags: [eval, pattern]
summary: "Two step-level scores for a chain of thought, Knowledge Index (are the facts right) and Information Gain (does the step move toward the answer), reported to separate what accuracy hides: on five medical benchmarks the Qwen R1-distilled model had similar Information Gain to its base but lower Knowledge Index and lower accuracy (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wu-2025-knowledge-or-reasoning.md
---

# Knowledge Index and Information Gain

Wu et al. (UC Santa Cruz and Stanford, arXiv 2506.02126, 2025 preprint, marked "under review") argue
that final-answer accuracy hides two separable things, and that training methods and domains affect them
differently. Their paper's stated position is that knowledge and reasoning should be two distinct
evaluation aspects.

## The two scores

GPT-4o splits each chain of thought into steps. Then:

- **Knowledge Index (KI)** is the fraction of steps that GPT-4o judges consistent with retrieved reference
  facts.
- **Information Gain (InfoGain)** is the mean per-step drop in the perplexity of the gold answer, scored
  by an untrained Qwen2.5-7B.

KI is computed for medical benchmarks only, since there is no knowledge base for math; math has
InfoGain only. The authors use a separate model for the perplexity so a model does not score its own
reasoning (they cite self-preference bias).

## Results (self-reported, Qwen2.5-7B family; no n, seeds or intervals reported)

- **Table 1, medical, five benchmarks averaged.** SFT only: Qwen-Base accuracy 52.79% against 38.07% for Qwen-R1
  (DeepSeek-R1-Distill-Qwen-7B); with SFT+RL: 60.02% against 31.48%. Average KI 63.40 against 56.49 (SFT only)
  and 64.23 against 54.29 (SFT+RL). Average InfoGain is near-equal (2.347 vs 2.249; 2.348 vs 2.309).
- **KI tracks accuracy.** Across the five medical benchmarks the average correlation of KI with accuracy is
  0.998, which the authors give as 0.3 higher than that of reasoning. On PubMedQA, KI correlates 0.897 and
  InfoGain 0.465; MedQA and MedXpert are above 0.9 for both.
- **SFT vs the untrained base (Fig. 6b).** Medical InfoGain 0.39 to 0.22 and math 0.13 to 0.09.
- **RL and knowledge (medical, Qwen-Base).** KI is 49.71 for the base, 60.24 RL-ed and 63.40 SFT-ed; RL
  on the base raises KI by 12.4 points on average and by 2.2 points when added after SFT.
- **Accuracy by domain (Fig. 6a).** Medical: SFT-ed 49.8%, RL-ed 49.8%, base 48.2%. Math: RL-ed 61.7%,
  SFT-ed 51.9%, base 40.5%.
- **Older step metrics.** In the appendix, the ROSCOE semantic-alignment metrics stay flat across base, SFT
  and RL models (Faithfulness-Step average 0.781 for all three), while KI and InfoGain move; the authors use
  this to argue older step metrics cannot discriminate.

## Limits

- **Internal inconsistencies in the paper.** The text says "54.06% vs. 31.48%" for the SFT+RL gap but
  Table 1 gives 60.02%; a "22.6% increase" cannot be reconciled with Table 1; the InfoGain drop on SFT is
  37.1% in the text but 38.9% in the abstract and intro; the intro's "6.2% average KI increase" for SFT
  appears as an accuracy gain in Sec. 4.2; the text's "4.6% and 6.2%" medical accuracy gains do not match
  the Fig. 6a values above; and Table 1 InfoGain looks like scaled raw units (MedMCQA about 9) while Fig. 6 uses
  0 to 1 values, with the scaling unexplained. Treat every number above as subject to these.
- Only Qwen 7B models and only math and medicine were tested.
- GPT-4o does the step splitting, knowledge extraction and consistency judging, with no human validation or
  judge-agreement figure; the InfoGain judge is an untrained Qwen2.5-7B, so the metric depends on that model.
- No seeds, variance or significance tests; gaps such as KI 64.2 against 63.4 are small and untested.
- The causal story is conjecture: the claim that RL prunes wrong knowledge rests on one case study, and the
  R1-conflict explanation is stated as "may stem from".
- The correlations are over five benchmark points. The KI reference source is described only vaguely, and the RL
  setup is PPO with a sparse +1/0 verifier reward.

## See Also
- [[LLM-as-Judge Evaluation]] — related (an LLM judges each step and no judge validation is reported)
- [[Eval Metric Interpretation Pitfalls]] — related (accuracy as a number that hides what moved)
- [[Prompting Reasoning Models]] — related (reasoning models trained by distillation and RL)
