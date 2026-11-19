---
title: "CoVe: Contextualised Word Vectors from MT Encoders"
tags: [llm, pretraining-and-data, concept]
summary: "CoVe freezes the two-layer BiLSTM encoder of an English-German attentional MT model and concatenates its per-token outputs with GloVe as input to task models; larger MT training sets gave larger downstream gains."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-mccann-2017-learned-translation.md
---

# CoVe: Contextualised Word Vectors from MT Encoders

McCann et al. (NIPS 2017) test whether the encoder from an attentional translation model can be reused as a contextual word representation that beats plain pretrained word vectors on other tasks. They hypothesise that translation data could play a role like ImageNet's, so more of it should yield more useful encoders.

## Method

A two-layer BiLSTM encoder is trained as part of an English-German attentional seq2seq translator (built on OpenNMT) on one of three MT datasets, with GloVe inputs held fixed; afterwards the encoder is frozen. CoVe is the sequence of context vectors the encoder produces: `CoVe(w) = MT-LSTM(GloVe(w))`, and the task input is `[GloVe(w); CoVe(w)]`, optionally with character n-gram vectors. Task models are a biattentive classification network (BCN), which handles one-sentence and two-sentence classification, and a Dynamic Coattention Network for SQuAD.

## Results (self-reported)

- CoVe pushes the SNLI baseline (BCN with character vectors and CoVe, single model) and SST-5 fine-grained sentiment to new test state of the art.
- SQuAD dev, DCN with character vectors and CoVe-L, single model, not submitted for test: beats the published R-NET on validation EM and F1.
- SQuAD F1 rises across CoVe-S, CoVe-M and CoVe-L, which the paper uses to argue larger MT training sets give larger gains.
- Added to GloVe, CoVe does better than character n-grams on SST-2 and SQuAD, and using both together is best; on SST-2 validation CoVe-L also edges out skip-thought vectors.
- IMDb (first 200 words) and TREC-6 test accuracy fall below several published models (for example oh-LSTM 94.1 on IMDb), and TREC-50 below rule-based systems.
- Elsewhere, [[ELMo and TagLM: Contextual Embeddings from Bidirectional LMs]] reports a larger SQuAD gain than CoVe's 1.8 on the same baseline.

## Limits

- The only source task is English-German translation; no other task or language pair was tried.
- Runs are single, with no seeds, variance or significance; the paper omits compute, batch size, epoch counts and the MT models' parameter counts.
- Some gains are small (SNLI validation moves 87.7 to 88.1, TREC-6 moves 94.9 to 95.8), and IMDb and TREC results are not state of the art.
- The SQuAD result is validation only.
- The link between MT data size and gain rests on three points and confounds size with domain and language complexity.
- CoVe is frozen features, not fine-tuned.

## See Also
- [[ELMo and TagLM: Contextual Embeddings from Bidirectional LMs]] — alternative-to
- [[ULMFiT: Universal Language Model Fine-Tuning]] — alternative-to
- [[Word Embeddings and Similarity Measures]] — prerequisite-for
