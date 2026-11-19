---
title: XGLM Multilingual Few-Shot Language Models
tags: [llm, pretraining-and-data, concept]
summary: "Lin et al. train four GPT-3-style decoder-only models (564M to 7.5B) on 500B tokens in 30 languages; XGLM 7.5B beats GPT-3 6.7B on multilingual commonsense, XNLI and FLORES-101 few-shot, at a cost in English accuracy (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-artetxe-2022-efficient-large-scale-language-modeling.md
---

# XGLM Multilingual Few-Shot Language Models

Lin et al. (EMNLP 2022) study zero- and few-shot in-context learning in a multilingual decoder-only language model, and compare prompting approaches for tasks outside English. They train four GPT-3-style causal models (XGLM at 564M, 1.7B, 2.9B and 7.5B parameters) for up to 500B tokens on CC100-XL, a 30-language corpus with upsampling and a joint SentencePiece vocabulary of 250k. XGLM 7.5B took about 3 weeks on 256 A100 GPUs with a 4M-token batch. English makes up 32.6% of the data (163B tokens, about 54% of the English GPT-3 saw). The paper also adds XStoryCloze, English StoryCloze translated professionally into 10 languages. Evaluation covers 0, 1, 4, 32 and 128 shots, with GPT-3 Curie (6.7B), an English replication built in-house, and a translate-test baseline as comparisons. All figures are self-reported.

## Results

- Commonsense reasoning: XGLM 7.5B is ahead of GPT-3 6.7B by 7.4 points on average zero-shot and 9.4 at 4-shot (5 runs). Its XStoryCloze average is 65.4 zero-shot and 66.5 at 4-shot.
- XNLI, averaged over 15 languages: 46.3 zero-shot and 47.3 at 4-shot, where GPT-3 6.7B gets 40.9 and 41.9.
- FLORES-101 (devtest, 32-shot, greedy, spBLEU): better than GPT-3 6.7B in 171 of 182 directions, and better than the supervised M2M-124 615M model in 45. Averaged over a 14-language subset out of English, 12.2 against 5.0 for GPT-3 and 16.6 supervised. GPT-3 still wins high-resource pairs such as WMT-14 fr-en (35.3 against 33.2).
- English cost: XGLM 7.5B is 10.9% below GPT-3 6.7B on average over 8 English tasks zero-shot.
- Translate-test with the GPT-3 6.7B replication is a strong baseline: XNLI average 52.5 zero-shot, above XGLM's 46.3.

## Prompting findings

English templates gave the best XNLI average (45.2 zero-shot, 47.0 4-shot) against human-written multilingual templates (41.7 and 43.9); a Chinese template applied to all four test languages gave close to random accuracy (34.4 average zero-shot). When a good English template is used, the benefit of cross-lingual demonstrations is generally cancelled. On XNLI accuracy rises from 0 to 4 shots and falls from 32 shots on; PAWS-X stays near 50% at every shot count.

## Limits

- Seven languages (ko, fi, th, bg, ca, hi, et) were over-sampled by accident, and the cost of retraining kept the authors from ablating it.
- The non-English evaluation sets are professionally translated, a property that may flatter cross-lingual transfer, and the translate-test baseline may be flattered as well.
- The English gap is confounded, because XGLM saw 54% as much English as GPT-3 and the corpora differ (CommonCrawl only against BookCorpus and Wikipedia); there is no controlled experiment separating the curse of multilinguality.
- Decoder-only causal models only, from 564M to 7.5B; prompts were not tuned per model. The social-value tasks cover six languages, five of them Romance, with inconclusive results. The explanation that code-switching and shared sub-tokens drive cross-lingual prompting is not verified.
- Data is static CommonCrawl up to March 2020.
- Source filename and title disagree: the file name says "Efficient Large Scale Language Modeling" but its content is the multilingual few-shot paper.

## See Also

- [[XP3, BLOOMZ and mT0]] — related (multilingual multitask finetuning)
- [[Transformer Architecture]] — prerequisite-for
