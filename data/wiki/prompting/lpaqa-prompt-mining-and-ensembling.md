---
title: LPAQA Prompt Mining and Ensembling
tags: [prompting, pattern]
summary: "Jiang et al. treat any single hand-written prompt as a lower bound on what an LM knows and raise it by mining prompts from Wikipedia, paraphrasing them by back-translation and ensembling the best, released as LPAQA; the transferable finding is that masked LMs are brittle to small prompt edits (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-jiang-2020-how-can-we-know-what.md
---

# LPAQA Prompt Mining and Ensembling

Jiang et al. ask how to raise the lower bound on the factual knowledge an LM is shown to hold, using prompts better than hand-written ones. Their hypothesis is that one prompt yields only a lower bound, so mined, paraphrased and ensembled prompts should recover more facts. The released archive of learned prompts is **LPAQA** (LM Prompt And Query Archive).

## Method

- **Mining**: generate cloze prompts per relation from Wikipedia, either by a middle-word method or from dependency paths.
- **Paraphrasing**: rewrite a prompt by back-translation.
- **Ranking and ensembling**: rank candidates on a held-out train set, then either average log-probabilities of the top K prompts (rank ensemble) or learn softmax weights over prompts per relation (optimised ensemble), via s(y|x,r) = sum over prompts of P(t|r) log P_LM(y|x,t). BERT, ERNIE and KnowBert stay frozen; only the per-relation prompt weights are learned.

Setup for the results: T-REx subset of LAMA (41 relations), cloze-style single-token object prediction, T=40 prompts per relation, BERT-base unless stated.

## Findings (self-reported)

- On BERT-base micro accuracy, the best ensemble combining mined and manual prompts improves on the manual-prompt baseline, and the best single mined or paraphrased prompt beats the manual one too; the source states the direction without the values.
- A mined prompt such as "x who converted to y" gives the largest per-relation gain over the manual prompt (religion, P140). Single-word edits to a paraphrase change accuracy a lot (P413, "plays in y position" against "plays at y position").
- Prompt edit distance correlates only weakly with prediction divergence.
- With Mine+Man optimised ensembles, ERNIE beats BERT (BERT 39.6, gap 4.2 points), while with manual prompts KnowBert scores below BERT on LAMA (BERT 31.1).
- Ensemble weights learned on BERT-large and applied to BERT-base still outperform manual prompts.
- Gains on Google-RE are small, and one relation (birth date) has a single prompt with non-zero accuracy.
- LM-aware hill-climbing refinement raises the oracle upper bound but lowers ensembles by overfitting (BERT-base optimised ensemble 38.1 to 37.5). Adding backward probability gives negligible gain.

## Limits

- The method handles masked LMs and single-token objects only, since left-to-right LMs are not tractable in this setup, and each fact has one ground-truth object even where several are valid.
- Optimised weights are tuned for micro accuracy, so macro gains are smaller. A large distance remains between the optimised ensemble and the oracle, so ensembling is far from ideal. Gradient-based prompt search that is aware of the LM proved unstable, and hill-climbing overfit.
- The models are from the BERT era (2019); sensitivity to small prompt edits is the point that transfers.
- No seeds, variance or significance tests.

## See Also

- [[LAMA Knowledge Probe]] — prerequisite-for
- [[Prompt-Based Learning Survey Typology]] — related (the survey covers prompt mining, paraphrasing and ensembling)
- [[Prompt Optimization]] — related
- [[Continuous Prompts: P-Tuning, WARP and Soft-Prompt Mixtures]] — extends (replaces mined text prompts with learned continuous ones)
- [[True Few-Shot Prompt Selection]] — related (uses LPAQA prompts as candidates)
