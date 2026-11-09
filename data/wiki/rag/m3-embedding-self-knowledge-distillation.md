---
title: M3-Embedding Self-Knowledge Distillation
tags: [rag, concept]
summary: "M3-Embedding is one encoder that produces dense, sparse and multi-vector scores for 100+ languages and 8192-token inputs, trained with the combined score as a teacher for each head; hybrid scoring was best on MIRACL, MKQA and NarrativeQA in the authors' tests."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-chen-2024-m3-embedding.md
---

# M3-Embedding Self-Knowledge Distillation

M3-Embedding (Chen et al., Findings of ACL 2024) is a single embedding model meant to cover many languages, three retrieval functions and long inputs. XLM-RoBERTa-large has its position range stretched to 8192 and is adapted with RetroMAE. Contrastive pre-training uses 1.2B multilingual pairs (dense head only); fine-tuning then applies **self-knowledge distillation**, where a weighted sum of the dense, lexical and multi-vector scores serves as the teacher for each of the three. Hybrid retrieval reranks with that weighted sum of dense, sparse and multi-vector (ColBERT-style) scores. **MCLS** is a training-free trick that inserts one CLS token per 256 tokens of a long document at inference and averages their embeddings.

## Results (self-reported)

- MIRACL dev (18 languages, nDCG@10): dense alone beats mE5-large on average; sparse beats BM25 run on the XLM-R tokenizer yet sits well under dense; the all-three combination (weights 1, 0.3, 1; rerank top-200 dense) has the best average.
- Dense fine-tuning only gives 60.5 nDCG@10; with RetroMAE 66.1; with RetroMAE and unsupervised pre-training 69.2.
- Dropping the distillation step wrecks the sparse head on MIRACL.
- MKQA (25 query languages against English Wikipedia): the combination has the best Recall@100, while sparse does badly, since a query and its passage rarely share terms across languages.
- MLDR long documents (13 languages, 8192 tokens): sparse beats dense by about 10 points and the combination is best; BM25 with a Lucene analyzer beats M3 sparse (64.1 against 62.2). Per article, the Lucene analyzer produces 37% more distinct terms than the XLM-R tokenizer.
- NarrativeQA: the combination is best, above E5-mistral-7b as well as the text-embedding-3-large model.
- MCLS lifts dense retrieval on MLDR when the model had no long-document fine-tuning; split-batch grows the per-device batch by over 20x at length 8192.

## Limits

- The authors concede that results on other datasets and in real-world scenarios are untested; inputs beyond 8192 tokens and differences between individual languages among the claimed 100+ are also unexamined.
- Fusion weights are set by hand per benchmark (different for MLDR and MIRACL) with no tuning procedure; the combination reranks only the top-200 dense candidates, so recall is bounded by the dense first stage.
- No seeds or significance tests; parameter count, learning rate and optimizer are not stated.
- The hybrid merges three heads of a single model, so it is not the same as fusing separate BM25 and dense systems.

## See Also
- [[BM25 and the Lexical Gap]] — related
- [[RAG Reranking]] — related (multi-vector scores used as a reranking stage)
- [[LIMIT Embedding Dimension Retrieval Benchmark]] — related (sparse and multi-vector behave differently from single-vector dense)
- [[GritLM (Generative Representational Instruction Tuning)]] — alternative-to
