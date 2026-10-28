---
title: Reciprocal Rank Fusion (RRF)
tags: [rag, concept, conflict]
summary: Score-free fusion algorithm that combines multiple ranked lists by position — the standard method for merging BM25 and dense vector retrieval results, and for amplifying cross-query agreement in multi-query retrieval.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/docs/rag/rrf.md
  - data/raw/claude-docs/playground/docs/archived/librarian-stack-audit.md
  - data/raw/claude-docs/playground/docs/archived/rag-agent-template-research.md
  - data/raw/claude-docs/project-g/docs/rag/rrf.md
  - data/raw/claude-docs/akira/docs/research/2026-09-24-dis386-semantic-retrieval.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-24-dis386-semantic-retrieval.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-24-dis386-semantic-retrieval.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-dis386-lexical-rrf.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-dis386-lexical-rrf.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-dis386-lexical-rrf.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-dis386-lexical-rrf.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-dis386-lexical-rrf.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--research--2026-08-18_dssg-second-brain_team-rag.md
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

## RRF Decides the Pool, Not the Score

In a hybrid design where a structured filter feeds lexical and semantic arms (from
research on an events-discovery product, repo akira, 2026-09-24), RRF's output is the
**order and inclusion of candidates passed to the existing scoring pipeline, never a
scoring dimension itself**. The controlled-vocabulary dimensions keep deciding fit within
the pool. Two properties make this safe:

- A candidate absent from one list contributes 0 from that list, not a penalty, and a
  rank-1 exact-name lexical hit (`1/(k+1)`) outweighs a mediocre semantic rank. That
  protects name matching, where embeddings are weak.
- An arm being down is a **designed degraded mode**: RRF runs on the remaining arms, and
  the event is logged and non-fatal.

Storage for the semantic arm is in [[Embedding Side Table, Not Column]].

## As built: what k=60 actually guarantees

When the lexical arm was built (repo akira, 2026-09-25), a fusion test was first written
to assert the intuition above: a rank-1 single-list hit beats an id that appears lower in
both lists. It failed. At `k=60`, an id at rank `r` in **both** lists scores `2/(60+r)`,
which beats a single-list rank-1 hit (`1/61`) whenever `r < 62`. So with short lists the
double-appearance case numerically wins. The exact-name protection only holds against the
*same id's* weaker semantic rank, not against a different id that both arms return. The
test was rewritten to assert the real arithmetic, with an inline comment so a future
reader does not "fix" the assertion back to intuition. This contradicts the claim in
"RRF Decides the Pool" and is flagged in `_conflicts.md`.

The fusion module shipped dark: a grep-test asserts no serving path imports the hybrid
module, so the arm cannot reach users before its gated metric flips it on.

## Known weaknesses: what fusion does not fix

RRF solves BM25-vs-cosine score normalization. It does not fix the query classes where
*both* arms are wrong:
- **Negation** ("an API that does NOT require auth"). Embeddings are dominated by "auth",
  and BM25 treats "not" as one more token.
- **Entity disambiguation**. Two people or products with the same name fuse into one ranking.
- **Rare identifiers**. These are weak in the dense arm and can be drowned out by fusion.
- **Stale dual indexes**. If the lexical and dense indexes are refreshed on different
  schedules, fusion silently mixes two corpus versions.

Route these to an explicit reranking or override path. Do not try to tune `k` until they go
away (there is no evidence `k` fixes negation). In a shared index the candidate pools RRF
fuses must already be ACL-filtered: [[ACL-Aware Retrieval and Tenant Isolation]].

## See Also
- [[RAG Retrieval Strategies]]
- [[RAG Reranking]]
- [[LangGraph CRAG Pipeline]]
- [[Semantic Cache for RAG Agents]]
- [[Vector Database Comparison]]
- [[RAG Architecture Selection]] — instance-of (Fusion RAG needs a scale-invariant merge across heterogeneous retrievers)
- [[Embedding Side Table, Not Column]] — extends (storage and rollout for the semantic arm RRF fuses)
- [[Pure Derivation Is a Generated Column]] — extends (the lexical arm's storage)
- [[Embeddings That Only Rerank Cannot Recall]] — extends (RRF over a lexical-only pool does not lift recall)
- [[ACL-Aware Retrieval and Tenant Isolation]] — extends (filtered candidate pools and hard-query routing in a shared index)
