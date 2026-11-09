---
title: BiDAF Bi-Directional Attention Flow
tags: [foundations, pattern]
summary: "BiDAF links a question and a paragraph with memory-less attention in both directions and passes per-word vectors on to a modeling layer instead of summarising the paragraph early."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-seo-2016-bidirectional-attention-flow-machine-comprehension.md
---

# BiDAF Bi-Directional Attention Flow

BiDAF is a reading-comprehension model. The hypothesis is that attention which is **memory-less** (each step depends only on the query and the context at that step, not on previous attention) and whose per-position vectors flow onward unsummarised divides labour cleanly between attention and modelling. The network stacks six layers: embeddings (character CNN plus GloVe) passed through a highway network of two layers, then a BiLSTM for context, the attention flow layer, a 2-layer BiLSTM modeling layer, and an output layer for span start and end. The attention layer uses one similarity matrix for **context-to-query** attention (which query words matter for each context word) and **query-to-context** attention (which context words are closest to some query word). The result is a **query-aware context representation**, one vector per context word. It trains from scratch on SQuAD with AdaDelta; the output layer is swapped for the CNN/DailyMail cloze task.

## Results

All numbers are self-reported.

- An ensemble of 12 runs gets 73.3 exact match on the hidden SQuAD test set, which led the leaderboard when submitted. A single model on test scores 68.0 EM and 77.3 F1; a single R-Net is ahead on EM at 68.4. On dev, one run scores 67.7 / 77.3 and the ensemble 72.6 / 80.7.
- Ablations (SQuAD dev, single run): without context-to-query attention EM falls to 57.2, the biggest attention loss; without query-to-context it falls to 63.6. Attention computed dynamically inside the modeling layer reaches 63.5, against 67.7 for static memory-less attention. Dropping word embedding hurts much more than dropping character embedding (55.5 versus 65.0).
- The trainable similarity w^T[h;u;h∘u] outperforms a dot product (65.5), a linear form (59.5), a bilinear form (61.6) and a linear form after an MLP (66.2).
- CNN test: 76.9 accuracy (single run, 19-word windows), above the best single baseline ReasoNet at 74.7; DailyMail test: 79.6, above the best ensemble.
- On dev, BiDAF gets right over 86% of the questions that the feature-based baseline gets right. Of 50 sampled exact-match errors, half are answers with imprecise boundaries.

## Limits

- The ablations are single runs without variance, and Tables 1b and 5 give two different dev scores (67.7/77.3 and 68.0/77.3) for one single model.
- The extraction notes two test rows are unpublished leaderboard entries dated 6 Dec 2016, and the claim of best results has long since aged.
- Multi-hop attention is left to future work; the error analysis covers only 50 examples.
- The extraction notes the model is built on LSTMs and slow to train (around 20 h on a single Titan X), and that Transformers and pretrained models have superseded it.
- Word-embedding ablation and visualisations are qualitative; the explanations are not tested directly.

## See Also
- [[DrQA Machine Reading at Scale]] — related
- [[Shared-Normalization Multi-Paragraph Reading]] — extends (reuses its attention layer as the paragraph model)
- [[Word Embeddings and Similarity Measures]] — related
