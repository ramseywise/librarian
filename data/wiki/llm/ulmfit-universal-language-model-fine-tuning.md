---
title: "ULMFiT: Universal Language Model Fine-Tuning"
tags: [llm, pretraining-and-data, concept]
summary: "ULMFiT pretrains an AWD-LSTM on Wikitext-103, fine-tunes it on target text with per-layer learning rates and a slanted triangular schedule, then trains a classifier with gradual unfreezing, reporting 18 to 24% error reductions on most of six classification sets."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-howard-2018-universal-language-model-fine-tuning.md
---

# ULMFiT: Universal Language Model Fine-Tuning

Howard and Ruder (ACL 2018) look for a way to adapt one pretrained language model to any text classification task while avoiding both overfitting and catastrophic forgetting. They argue that earlier attempts to fine-tune LMs in NLP failed because of the training recipe, and that the underlying idea was sound.

## Three stages

1. An AWD-LSTM language model is pretrained on Wikitext-103.
2. The entire LM is then tuned on text from the target task, using per-layer learning rates and a slanted triangular schedule.
3. A classifier is built by adding two linear blocks to the LM and trained with gradual unfreezing, concat pooling and BPT3C.

A forward model and a backward model are both trained, and their outputs are averaged.

- **Discriminative fine-tuning:** every layer has its own learning rate. The top layer's rate is picked first, and each layer beneath takes the rate of the layer above it and divides by 2.6.
- **Slanted triangular learning rates (STLR):** the rate climbs linearly during a brief opening phase, then falls linearly over a much longer one. With `cut = floor(T * cut_frac)`, `p` is `t/cut` before the cut and `1 - (t-cut)/(cut*(ratio-1))` afterwards, and the rate at step t is eta_max times (1 + p*(ratio-1)), all over ratio.
- **Gradual unfreezing:** begin with only the last layer unfrozen, then unfreeze the next layer down each epoch, always training everything already unfrozen, until the whole network trains.
- **Concat pooling:** the document vector `h_c` stacks the final hidden state, a max-pool and a mean-pool of the earlier states, all computed over as many recent time steps as memory permits.
- **BPT3C:** backpropagation through time adapted to classification; a document is cut into fixed-length batches, the hidden state passes from one to the next, and gradients reach every batch that fed the prediction.

## Results (self-reported)

- IMDb test, full ULMFiT with the bidirectional ensemble: relative error falls 43.9% versus CoVe and 22% versus the previous best. TREC-6 test error is 3.6%, against CoVe at 4.2 and LSTM-CNN at 3.9, a difference the authors say is not statistically significant. AG news test error is 5.01%, versus 6.57% for the CNN (a 23.7% relative drop). Other test errors: DBpedia 0.80 (previous 0.84), Yelp-bi 2.16 (previous 2.64), Yelp-full 29.98.
- Starting from 100 labeled examples, supervised ULMFiT does as well as a from-scratch model given 10x more data on IMDb and 20x more on AG. When unlabeled text (50k for IMDb, 100k for AG) is also used for LM tuning, the multiples become 100x and 50x (read off Fig 3).
- Ablations report validation error with 10% of the training data. Pretraining on Wikitext-103 takes TREC-6 from 10.67 down to 5.69, IMDb from 5.63 to 5.00 and AG from 5.52 to 5.38. For LM tuning, discriminative rates with STLR bring IMDb from 6.99 (no LM tuning) to 5.00; on TREC-6, plain full fine-tuning scores 6.54, worse than skipping LM tuning at 6.38.
- Tuning only the last layer in the classifier stage underfits badly on TREC-6 (16.09; from scratch 13.36; full recipe 5.69). The full recipe yields 5.00 on IMDb, 5.69 on TREC-6 and 5.38 on AG; a cosine-schedule variant reaches 5.29 on AG and Full + discr reaches 4.57 on IMDb.
- Averaging the forward and backward models cuts IMDb test error, from 5.30 for one direction to 4.58. Using a plain LM without dropout instead of AWD-LSTM gives IMDb 5.98 (versus 5.00) and overfits TREC-6 (7.41 versus 5.69).
- Dai and Le's LM fine-tuning appears here at 7.64 IMDb error versus 4.6 for ULMFiT; see [[Semi-Supervised Sequence Learning: LM-LSTM and SA-LSTM]].

## Limits

- Evaluation covers text classification on six English datasets; the authors call sequence labelling straightforward but did not test it, and say entailment and QA may require new methods.
- Pretraining uses a single corpus, Wikitext-103 (103M words).
- The paper gives no seeds, variance, confidence intervals or compute, and concedes the TREC-6 gain is not significant.
- Hyperparameters were set on the IMDb validation set and carried over to other tasks; the ablation numbers are validation error on 10% of the training data, not test scores.
- The unfreezing and STLR schedules and the 2.6 factor came from experiments, and the authors call for more study of what a pretrained LM captures.
- The base model is an AWD-LSTM, which is dated next to later transformer LMs.

## See Also
- [[Semi-Supervised Sequence Learning: LM-LSTM and SA-LSTM]] — prerequisite-for
- [[ELMo and TagLM: Contextual Embeddings from Bidirectional LMs]] — alternative-to
- [[CoVe: Contextualised Word Vectors from MT Encoders]] — alternative-to
- [[Transfer and Multi-Task Learning Conditions]] — related
