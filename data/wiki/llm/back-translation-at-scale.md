---
title: "Back-Translation at Scale"
tags: [llm, pretraining-and-data, pattern]
summary: "Back-translation trains a reverse model to turn target-language monolingual text into synthetic sources; Edunov et al. (2018) compare greedy, beam, sampled, top-10 and noised-beam generation and find sampling or noise beats beam search once bitext is not tiny."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-edunov-2018-understanding-back-translation-scale.md
---

# Back-Translation at Scale

Back-translation trains an intermediate target-to-source system on the parallel data, uses it to translate monolingual target-language text into the source language, adds the synthetic pairs to the real bitext, and trains the final source-to-target system. Edunov et al. ask how the synthetic sources should be generated and how far this scales. Their hypothesis: greedy and beam (maximum a posteriori) outputs are too regular and miss much of the real data distribution, so sampled or noised beam output should teach more.

## Generation methods compared

- **greedy** and **beam**: the most likely output.
- **sampling**: draw from the model's distribution at each step.
- **top10**: sampling restricted at each step to the 10 most likely tokens, renormalised.
- **beam+noise**: beam output with each word deleted (p=0.1), swapped for a filler token (p=0.1), and words exchanged with others up to three positions away.

Setup: a reverse Big Transformer on WMT bitext translates newscrawl target text; the forward Transformer trains on bitext plus synthetic pairs (self-reported results below).

- Averaged over newstest2013-2017 En-De (5.2M bitext + 24M synthetic), sampling or noised beam is 1.7 BLEU ahead of plain beam search.
- In the largest setup sampling and beam+noise beat greedy and beam by 0.8 to 1.1 BLEU on newstest2012.
- Beam wins when the bitext is only 80K; at 640K and 5.2M, sampling wins.
- Sampling and beam+noise work without upsampling the bitext, whereas greedy and beam gain from larger upsample rates (read off a figure).
- Evidence for the "richer signal" account: on beam-generated data training perplexity drops under 2 within 5 epochs, so it is easier to fit than the bitext, and sampled data is harder. A 5-gram LM on real sources scores perplexity 75.34; beam-generated sources score 72.42, sampled 500.17 and beam+noise 2823.73.

## Scale and domain

- 226M sampled German sentences with 5.2M bitext (upsample rate 16, 250K updates) give 35 BLEU on the WMT'14 En-De test set newstest2014, which the paper reports as best to date for systems trained on WMT benchmark data alone; the detokenised sacreBLEU score is 33.8.
- On En-Fr, 31M sampled back-translations lift tokenised BLEU on newstest2014 from 42.90 (bitext alone) to 45.6 (35.7M bitext, 300K updates).
- Synthetic data from back-translating the bitext's own target side (sampled) recovers 83% of what real bitext adds when the domains match (640K bitext base, newstest2012 En-De), but only 67% on a mixed-domain validation set, 1.3 BLEU behind real bitext.

## Limits

- Sampling and noise are worse than beam in the 80K-bitext low-resource setup. Sampled sources are sometimes inadequate: Table 3 shows sampling adding target words absent from the source.
- Mostly En-De in one direction, using newswire monolingual text, with En-Fr only as a check. No seeds, variance or significance tests are reported.
- The richer-training-signal explanation is a conjecture backed by training loss and LM perplexity, with no causal test. The authors list end-to-end optimisation of the back-translation model as future work.
- The DeepL comparison is uneven, because DeepL trains on proprietary high-quality bitext.

## See Also
- [[Encoder-Decoder Translation Before the Transformer]] — prerequisite-for
- [[Transformer Architecture]] — prerequisite-for
- [[Sequence-Level Knowledge Distillation]] — related (both train on model-generated text for translation)
