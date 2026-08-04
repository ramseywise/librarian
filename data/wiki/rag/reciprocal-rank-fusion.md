---
title: Reciprocal Rank Fusion (RRF)
tags: [rag, concept]
summary: Score-free fusion algorithm that combines multiple ranked lists by position — the standard method for merging BM25 and dense vector retrieval results, and for amplifying cross-query agreement in multi-query retrieval.
updated: 2026-08-04
sources:
  - raw/playground-docs/librarian-stack-audit.md
  - raw/playground-docs/rag-agent-template-research.md
  - raw/claude-docs/project-g/docs/rag/rrf.md
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

## Multi-Query Consensus Amplification

RRF's core value in multi-query retrieval is amplifying **cross-query agreement** as a signal. Current naive merge strategies treat agreement as noise by collapsing to max score:

```
query A results: [C1(0.78), C2(0.61), C3(0.55)]
query B results: [C1(0.81), C6(0.72), C2(0.59)]

Naive merge (max score): [C1(0.81), C6(0.72), C2(0.61)]  ← C6 ranks #2 despite single-query retrieval
RRF:                     [C1(0.033), C2(0.032), C6(0.016)] ← C2 promoted because two queries agreed
```

RRF correctly promotes C2 (ranked #2 in both lists) over C6 (ranked #2 in only one list, despite higher raw score). **Cross-query consensus is the signal; raw score is the noise.**

### TypeScript Implementation Pattern

```typescript
function rankByRrf(queryResultLists: KnowledgeBaseRetrievalResult[][]): KnowledgeBaseRetrievalResult[] {
  const RRF_K = 60;
  const seen = new Map<string, { result, rrfScore: number; maxRawScore: number }>();

  for (const results of queryResultLists) {
    results.forEach((result, rank) => {
      const fingerprint = `${url}|${contentFingerprint(content)}`;
      const contribution = 1 / (RRF_K + rank + 1);
      // accumulate RRF score; preserve maxRawScore for downstream threshold checks
      ...
    });
  }

  return [...seen.values()]
    .sort((a, b) => b.rrfScore - a.rrfScore)
    .map(({ result, maxRawScore }) => ({ ...result, score: maxRawScore }));
}
```

**Key invariant:** Return `score = maxRawScore` (not the RRF score) so downstream threshold checks (`scoreThreshold`, `kbTopScore`) continue operating on the raw cosine scale without recalibration.

### When Not to Apply RRF

- **Reranking path:** A cross-query reranker (e.g. `amazon.rerank-v1:0`) already reconciles multi-concept evidence. Applying RRF before the reranker, then sorting by reranker score, is the better sequence — don't double-count.
- **Single query:** RRF degrades to sort-by-rank, identical to sort-by-score. No harm but no benefit.
- **Below-threshold chunks:** RRF only re-orders chunks that survive the score threshold filter. It cannot surface new content if the top-5 cosine results are all irrelevant — that's a query generation or corpus problem.

## See Also
- [[RAG Retrieval Strategies]]
- [[RAG Reranking]]
- [[LangGraph CRAG Pipeline]]
- [[Semantic Cache for RAG Agents]]
- [[Vector Database Comparison]]
- [[RAG Architecture Selection]] — instance-of (Fusion RAG needs a scale-invariant merge across heterogeneous retrievers)
