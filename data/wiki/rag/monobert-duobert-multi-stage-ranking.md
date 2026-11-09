---
title: monoBERT duoBERT Multi-Stage Ranking
tags: [rag, pattern]
summary: A three-stage ranking pipeline of BM25, pointwise monoBERT and pairwise duoBERT, where how many candidates each stage admits sets the trade-off between ranking quality and the number of BERT inferences.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-nogueira-2019-multi-stage-document-ranking-bert.md
---

# monoBERT duoBERT Multi-Stage Ranking

Nogueira et al. ask whether BERT can rank documents inside a multi-stage pipeline, first pointwise and then pairwise, so quality can be traded against latency. The hypothesis is that, with admission controlled at each stage, the pairwise stage lifts effectiveness at only a small latency cost.

## Mechanism

H0 is Anserini BM25 retrieving k0 candidates. H1 is monoBERT, a pointwise classifier scoring each (query, document) pair independently, keeping the top k1. H2 is duoBERT, which takes ordered pairs (q, di, dj) from those k1 documents and estimates the probability that di is more relevant than dj. Pairwise probabilities are aggregated into one score per document: SUM adds the probabilities, BINARY counts those above 0.5, MAX and a sampled variant were also tried. Target Corpus Pre-training (TCP) is an extra BERT pre-training phase on the task corpus.

## Results

Self-reported; MS MARCO passage ranking, with 6,980 dev and 6,837 eval queries, k0=1000 and k1=50; BERT was fine-tuned for 100k iterations at batch size 128 unless noted.
- On dev, monoBERT improves MRR@10 by 17.5 points over BM25. On eval, duoBERT SUM reaches an MRR@10 of 37.0, which is 0.5 above monoBERT; TCP adds 0.8 on eval (37.9), near the leaderboard best of 38.3 at the time.
- On dev, BINARY aggregation does best (38.3), 0.1 over SUM, while MAX falls well short of monoBERT alone (32.6 against 37.2).
- TREC CAR 2017 (2,254 queries, automatic annotations, MAP): monoBERT gains 19.5 over BM25; duoBERT adds 2.1 more, reaching 36.9.
- Cost: Each query costs duoBERT SUM an additional 50 x 49 BERT inferences. Varying k0 for monoBERT alone, over half the gain comes with about a fifth of the inferences. With k1=20 and BINARY (MS MARCO) or SUM (TREC CAR), scores are near maximum for about 40% more latency than monoBERT; k1=50 more than doubles inferences.
- For an equal inference budget, scoring all pairs from a smaller top-k1 beats sampling pairs uniformly from a larger candidate set.
- Fine-tuning used 12.8M pairs in about 24 hours on a TPU v3; three more days (50M pairs) gave no dev gain. Anserini BM25 recall@1000 is 85.7% against 81.5% for Microsoft's BM25.

## Limits

- The BERT size, parameter count and BM25 settings are not given, and latency is represented by counts of inferences instead of milliseconds.
- Runs are single; for most conditions there are no eval numbers, so as not to probe the leaderboard.
- Inputs are limited to 512 tokens; long documents untested. CAR scores use automatic annotations; the authors say CAR MAP gains exceed MS MARCO MRR@10 gains partly because of the metrics.
- Stages are tuned separately; leaderboard standings from October 2019 are dated.

## See Also
- [[RAG Reranking]] — prerequisite-for
- [[Lucene HNSW and Pyserini Dense Retrieval]] — related (BM25 first stage tooling)
