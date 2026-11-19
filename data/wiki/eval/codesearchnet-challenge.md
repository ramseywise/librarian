---
title: CodeSearchNet Challenge
tags: [eval, code, benchmark]
summary: "CodeSearchNet pairs a corpus of about 6 million functions in six languages with 99 natural-language queries carrying about 4k expert relevance labels; in the baselines, a bag-of-words encoder led on the human-labelled challenge while self-attention led on the docstring proxy task (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-husain-2019-codesearchnet-challenge.md
  - data/raw/papers/2026-11-06-zhang-2023-unifying-perspectives-nlp-software-engineering.md
  - data/raw/papers/2026-11-08-lu-2021-codexglue.md
---

# CodeSearchNet Challenge

Husain and colleagues ask how progress on semantic code search, meaning natural-language query in and code out, can be measured, and how far simple neural and keyword baselines get. They release a corpus, a labelled challenge and a leaderboard.

## Construction

- **Corpus:** open-source GitHub functions in six languages, about 6 million in all and about 2 million with documentation. A survey of code language models (Zhang et al.) quotes 6.5M functions with 2.3M paired with documentation and a size of 20 GB over 6 languages; the paper's own figures are the rounder ones.
- **Training pairs:** each function with documentation is paired with the first paragraph of that documentation, used as a proxy for a query.
- **Challenge:** 99 queries drawn from Bing and StaQC; experts graded relevance (scale 0-3) for each query's top-10 candidates in every language, about 4k annotations in total.
- **Baselines:** joint code and query embedding models (bag-of-words NBoW, 1D-CNN, biRNN, self-attention) trained with a softmax contrastive loss, plus ElasticSearch keyword search.

## Metrics

**NDCG Within** is computed over the functions that have human annotations; **NDCG All** is computed over the whole corpus.

## Results (self-reported)

- Docstring-to-code task: with 999 distractors on the test split and results averaged across the six languages, self-attention gets the highest MRR.
- Human-labelled challenge, scored on annotated functions and averaged across languages: NBoW tops NDCG Within, ahead of self-attention, and ElasticSearch holds its own.
- Over the whole corpus every model scores lower; NBoW leads with NDCG All 0.340 and ElasticSearch gets 0.205.
- Inter-annotator agreement is moderate (kappa 0.47, 891 pairs with more than one annotation).

## Use in later work

CodeXGLUE reuses CodeSearchNet for pretraining, search, cloze and summarisation tasks; see [[CodeXGLUE Code Understanding and Generation Benchmark]].

## Limits

- The training data comes from documentation, which the authors call a noisy proxy that does not match real queries well.
- There are few annotations (4,026), usually a single label per pair, unevenly spread (Python 2,089, Go 166) and collected from volunteers.
- The baselines themselves picked which candidates got annotated. That favours them under NDCG Within, while NDCG All counts relevant but unlabelled results against every model.
- No hyperparameters, seeds or variance are reported for the baselines; the pooling choice per model is not stated.
- An indexing bug found by an outside participant affected earlier results; the later corrected version holds the numbers above.
- English queries only, whole functions only.
- The survey's size figures (6.5M and 2.3M functions) differ from the paper's rounder ones, and the survey's own Table 2 and prose disagree on other corpora.

## See Also
- [[CodeXGLUE Code Understanding and Generation Benchmark]] — extends
- [[Spider Text-to-SQL Benchmark]] — related
- [[HumanEval and pass@k]] — related
