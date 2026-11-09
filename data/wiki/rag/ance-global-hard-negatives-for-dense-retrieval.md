---
title: ANCE Global Hard Negatives for Dense Retrieval
tags: [rag, pattern]
summary: ANCE draws each training negative from the top results of an ANN index of the whole corpus, rebuilt asynchronously from a recent checkpoint, instead of using in-batch negatives.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-xiong-2021-approximate-nearest-neighbor-negative-contrastive.md
---

# ANCE Global Hard Negatives for Dense Retrieval

ANCE (Approximate nearest neighbor Negative Contrastive Estimation, Xiong et al.) targets why dense text retrieval trails sparse retrieval. The authors' hypothesis is that local in-batch negatives are uninformative, with near-zero loss and gradient, so negatives should be chosen globally with the model being trained.

## Mechanism

A RoBERTa-base BERT-Siamese dot-product retriever is trained with NLL loss. Training starts with a BM25-negative warm-up. Then an Inferencer process periodically (every 10k batches) re-encodes the corpus using a recent checkpoint and then rebuilds the index in Faiss, while the Trainer continues meanwhile. Per positive, one negative is drawn uniformly from the top 200 ANN results with known positives excluded.

## Results

All are self-reported.
- TREC DL 2019 passage: NDCG@10 0.648 against 0.506 for BM25. Document retrieval: 0.615 (FirstP) and 0.628 (MaxP) against BM25 0.519 and DeepCT 0.554.
- MARCO dev passage, same BM25 warm-up: random negatives reach just 0.280 MRR@10 and NCE in-batch negatives 0.279.
- Natural Questions: with the RAG-Token reader held fixed, replacing DPR retrieval by ANCE lifts the NQ test score from 41.5 to 46.0. TriviaQA gains are small.
- A commercial search engine's first-stage retrieval, offline: across three index configurations the relative gains are 18.4%, 14.2% and 15.5%.
- On TREC DL document with a single 32GB V100, online, dense retrieval runs roughly 100x faster than a BM25 plus BERT reranker pipeline; refreshing the index re-encodes the corpus in about 10 hours.
- Overlap with the 100 hardest negatives is 0% for local negatives and 15% for BM25, whereas for ANCE negatives it begins at 63% and converges toward 100%. Gradient norms on ANCE negatives are orders of magnitude larger than on local ones.
- Over 43 TREC DL document queries, ANCE outperforms BM25 on 29 of them, underperforms on 13, and ties on one. Its hole rate at 10 is 13.3% (FirstP) against 0.2% for BM25, meaning unlabelled results.

## Limits

- The gradient-norm bound comes from work on MLPs and is assumed to carry over to BERT; support is gradient-norm plots only. The in-batch probability estimate is given without a derivation.
- TREC DL 2019 labels were pooled from sparse systems only, so dense retrievers have high hole rates and recall is weakly informative.
- No false-negative handling: unlabelled relevant documents in the top 200 may be used as negatives.
- Little hyperparameter exploration; single runs; the commercial gains are relative numbers on proprietary data with an unnamed metric.
- Each refresh costs a full corpus re-encode. RAG-Sequence was not used because the release was unstable, and TriviaQA used the DPR reader.

## See Also
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[Contriever Unsupervised Contrastive Retrieval]] — alternative-to (unsupervised pre-training rather than hard negatives)
- [[RAG Sequence and RAG Token]] — related (its RAG-Token reader scores the NQ test)
- [[HNSW Hierarchical Navigable Small World Index]] — related (ANN indexes underpin negative mining)
