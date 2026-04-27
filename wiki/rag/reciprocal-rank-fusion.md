---
title: Reciprocal Rank Fusion (RRF)
tags: [rag, concept]
summary: Score-free fusion algorithm that combines multiple ranked lists by position — the standard method for merging BM25 and dense vector retrieval results.
updated: 2026-04-24
sources:
  - raw/playground-docs/librarian-stack-audit.md
  - raw/playground-docs/rag-agent-template-research.md
---

# Reciprocal Rank Fusion (RRF)

RRF combines multiple ranked lists into a single merged ranking without needing the underlying scores to be on the same scale. The score for a document `d` across `n` ranked lists is:

```
RRF(d) = Σ 1 / (k + rank_i(d))
```

Where `k=60` (paper default) and `rank_i(d)` is the position of `d` in list `i`. Documents not appearing in a list contribute 0.

## Why It Works

BM25 and dense vector scores live on incompatible scales — you can't directly add them. RRF bypasses this by using only *rank position*, which is scale-invariant. A document ranked 3rd by BM25 and 5th by vector gets a high fusion score regardless of what those raw scores were.

## In the Librarian Pipeline

Used in `EnsembleRetriever` to merge:
- BM25 term-match results
- Dense vector cosine-similarity results
- Multi-query expansion results (N reformulations of the same query, each producing its own ranked list)

```python
def rrf_score(ranks: list[int], k: int = 60) -> float:
    return sum(1.0 / (k + r) for r in ranks)
```

The result feeds into the [[RAG Reranking]] stage (cross-encoder or LLM listwise), which re-scores the fused candidate set.

## Key Properties

- **No score normalization needed** — works across heterogeneous retrievers
- **Robust to missing docs** — documents absent from a list simply don't contribute
- **k=60 is robust** — insensitive to k in the 40–80 range; don't tune it

## See Also
- [[RAG Retrieval Strategies]]
- [[RAG Reranking]]
- [[LangGraph CRAG Pipeline]]
