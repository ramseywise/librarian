---
title: Knowledge Index and Information Gain
tags: [eval, pattern]
summary: "Two step-level scores for a chain of thought, Knowledge Index (are the facts right) and Information Gain (does the step move toward the answer), reported to separate what accuracy hides: on five medical benchmarks the Qwen R1-distilled model had similar Information Gain to its base but lower Knowledge Index and lower accuracy (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-wu-2025-knowledge-or-reasoning.md
---

# Knowledge Index and Information Gain

Wu et al. (UC Santa Cruz and Stanford, arXiv 2506.02126, 2025 preprint, marked "under review") say
that accuracy on the final answer conflates two separable things, and that training methods and domains
act on them differently. The position the paper takes is that evaluation should treat knowledge and
reasoning as two separate aspects.

## The two scores

GPT-4o first cuts each chain of thought into steps. Two scores follow:

- **Knowledge Index (KI)** is the proportion of steps that GPT-4o rates as agreeing with reference
  facts it has retrieved.
- **Information Gain (InfoGain)** is the average, per step, of how much the perplexity of the gold answer
  falls; the perplexity comes from an untrained Qwen2.5-7B.

KI exists for the medical benchmarks only, because maths has no knowledge base; maths is scored with
InfoGain alone.

## Results (self-reported, Qwen2.5-7B family; no n, seeds or intervals reported)

- **Table 1, medical, mean of five benchmarks.** With SFT only, accuracy is 52.79% for Qwen-Base and
  38.07% for Qwen-R1 (DeepSeek-R1-Distill-Qwen-7B); with SFT+RL it is 60.02% and 31.48%. Mean KI: 63.40
  and 56.49 (SFT only), 64.23 and 54.29 (SFT+RL). Mean InfoGain is almost equal between the two
  (2.347 against 2.249, and 2.348 against 2.309).
- **KI tracks accuracy.** Over the five medical benchmarks, KI correlates with accuracy at 0.998 on
  average, a figure the authors put 0.3 above the reasoning counterpart. For PubMedQA the KI correlation is
  0.897 and the InfoGain one 0.465; for MedQA and MedXpert both exceed 0.9.
- **SFT compared with the untrained base (Fig. 6b).** InfoGain falls from 0.39 to 0.22 in medicine and from
  0.13 to 0.09 in maths.
- **RL and knowledge (medical, Qwen-Base).** KI values are 49.71 (base), 60.24 (RL-ed) and 63.40
  (SFT-ed). Applying RL to the base adds 12.4 KI points on average, but only 2.2 when applied after SFT.
- **Accuracy by domain (Fig. 6a).** In medicine: 49.8% SFT-ed, 49.8% RL-ed, 48.2% base. In maths: 61.7%
  RL-ed, 51.9% SFT-ed, 40.5% base.
- **Older step metrics.** The appendix reports that the ROSCOE semantic-alignment metrics do not move
  across the base, SFT and RL models (Faithfulness-Step mean 0.781 in all three), whereas KI and
  InfoGain do; the authors take this as evidence that older step metrics cannot tell the models apart.

## Limits

- **Internal inconsistencies in the paper.** For the SFT+RL gap the text says "54.06% vs. 31.48%", yet
  Table 1 shows 60.02%. A "22.6% increase" cannot be matched to Table 1. The InfoGain drop on SFT is
  37.1% in the body but 38.9% in the abstract and introduction. The introduction's "6.2% average KI
  increase" for SFT shows up as an accuracy gain in Sec. 4.2. The "4.6% and 6.2%" medical accuracy gains in
  the text disagree with the Fig. 6a values given above. InfoGain in Table 1 seems to be in scaled raw units
  (about 9 for MedMCQA) while Fig. 6 shows values from 0 to 1, with no explanation of the scaling. Every number
  above is subject to these.
- Only Qwen 7B models were tested, and only in maths and medicine.
- GPT-4o does all of the step splitting, extraction of knowledge and consistency judging; there is no
  human validation and no judge-agreement figure; the InfoGain scorer is an untrained Qwen2.5-7B, so the
  metric is tied to that model.
- There are no seeds, variance estimates or significance tests, so small gaps (such as KI of 64.2 against
  63.4) are untested.
- The causal account is conjecture: the claim that RL removes wrong knowledge relies on a single case
  study, and the explanation for the R1 conflict is worded "may stem from".
- Correlations are computed over only five benchmark points. The source of the KI references is
  described only loosely, and the RL stage is PPO whose reward is a sparse +1/0 signal from a verifier.

## See Also
- [[LLM-as-Judge Evaluation]] — related (an LLM judges each step and no judge validation is reported)
- [[Eval Metric Interpretation Pitfalls]] — related (accuracy as a number that hides what moved)
- [[Prompting Reasoning Models]] — related (reasoning models trained by distillation and RL)
