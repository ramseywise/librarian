---
title: LLM-Blender PairRanker and GenFuser
tags: [infra, concept]
summary: "LLM-Blender runs 11 open-source LLMs on every input, ranks all candidate pairs with a cross-attention ranker, and fuses the top three with a generator; it beats any single model but costs more than one call, so it is an ensemble, not a cost-saving router."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-jiang-2023-llm-blender.md
---

# LLM-Blender PairRanker and GenFuser

Jiang, Ren and Lin start from the claim that the best open-source model varies per input: across the 5,000 MixInstruct examples even the strongest single model (Vicuna) is ranked first for just 21.22%. The method runs N = 11 models on every input; PairRanker (DeBERTa, 400M) jointly encodes the input and two candidates and its pairwise logit matrix is aggregated into a ranking; GenFuser (Flan-T5-XL, 3B) takes the input and the top K = 3 candidates and generates the final answer. A single bubble-sort pass cuts pairwise comparisons from O(N^2) to N-1, as the paper claims.

## Results (all self-reported)

Setup: MixInstruct test set (5,000 examples), 11 open-source LLMs, ChatGPT pairwise judge.

- Average GPT-Rank beats the best single model (Open Assistant, 3.90); for LLM-Blender the output is in the top 3 on 68.59% of examples, while Vicuna manages 52.88%.
- Used alone, PairRanker picks responses averaging GPT-Rank 3.20, an improvement of 0.70 on the best model. Pointwise rankers SimCLS and SummaReranker reach 3.50 and 3.66; MLM-Scoring fails to beat random selection (7.00 against 6.14).
- Gains over the best model on BERTScore, BARTScore and BLEURT are 4.41, 0.43 and 0.22.
- PairRanker's correlation with the oracle ranking exceeds all other rankers and metrics.

## Limits

- All N models must run per input and the full pairwise ranker needs O(N^2) calls; the main text gives no latency or cost numbers, and no comparison to cheaper routing is made.
- Judging uses ChatGPT, with no large-scale human evaluation. Only 11 open-source models from 2023; no closed models such as GPT-4.
- Training hyperparameters, decoding settings and the judge prompt sit in an appendix missing from the supplied text. Single run, no seeds.

## See Also

- [[Cheap-First Gating and Model Cascades]] — alternative-to (a cascade saves cost where this method adds it)
- [[RouteLLM Preference-Trained Routers]] — alternative-to
- [[LLM Inference Economics]] — related
- [[Open-Domain Dialogue Systems]] — alternative-to (per-turn random model mixing in the Blended paper)
