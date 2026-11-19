---
title: Pretrained Transformer OOD Robustness Benchmark
tags: [eval, datasets-and-contamination, benchmark]
summary: "Hendrycks et al. build seven NLP train/test pairs with natural distribution shifts and report that pretrained Transformers have smaller in-distribution to OOD gaps than bag-of-words, ConvNet and LSTM models, while larger or distilled models do not follow the vision pattern (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-hendrycks-2020-pretrained-transformers-improve-out-distribution.md
---

# Pretrained Transformer OOD Robustness Benchmark

Hendrycks and colleagues (2020) test whether pretrained Transformers keep their accuracy off the training distribution, since that did not follow from in-distribution (IID) accuracy in vision. Results are the authors' own (self-reported).

## Method

Thirteen models, from bag-of-words through word-embedding encoders to pretrained Transformers, train on one distribution and test on another. The shifts (style, topic, vocabulary) come from splitting a dataset by metadata or pairing related datasets, over seven datasets (MNLI, ReCoRD, STS-B, Amazon, Yelp, IMDb, SST-2). Generalisation is the gap between IID and OOD accuracy. Detection scores examples by negative maximum softmax probability from an SST-2 classifier and reports FAR95, the false alarm rate on in-distribution data at the point where 95% of OOD examples are caught.

## Results

- STS-B, trained on Images and tested on MSRvid: an LSTM word2vec model loses over 35% while RoBERTa Large rises slightly (read off a figure). BERT Base on MNLI, trained on Telephone, holds similar accuracy on other genres.
- Bigger BERT and ALBERT models do not narrow the gap for IMDb-to-SST-2 (figure only). DistilBERT generalises worse than BERT on ReCoRD and IMDb. RoBERTa outdoes BERT Large; the authors credit more varied, larger pretraining data but say volume alone does not explain it.
- Detection: models without pretraining (BoW, averaged word2vec, LSTM, ConvNet) do about as badly as chance or worse, with false alarm rates near 100% on 20 Newsgroups. Pretrained Transformers consistently beat a random detector on FAR95 over 20 Newsgroups, Multi30K, RTE, SNLI and WMT16, yet still fail to separate IID from OOD cleanly.

## Limits

- Scope is classification, entailment, QA and similarity with 2020-scale models (BERT, RoBERTa, ALBERT); generative and autoregressive models are absent.
- The authors treat the reason pretrained models are more robust as open, offering data diversity and self-supervision as partial answers.
- Maximum-softmax detection stays far from perfect for pretrained Transformers.
- Seeds, hyperparameters, dataset sizes and per-dataset numbers are missing from the main text, and the PDF has no appendix.
- The shifts are natural rather than adversarial, and domain adaptation is excluded.

## See Also
- [[NLI Annotation Artifacts and Hard/Easy Splits]] — related (spurious cues offered as an explanation of brittleness)
- [[Knowledge Distillation with Soft Targets]] — related (distillation as a factor in robustness)
- [[Dynabench]] — related
