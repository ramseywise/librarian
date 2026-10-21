---
title: Embeddings That Only Rerank Cannot Recall
tags: [rag, patterns, pattern]
summary: "When BM25 alone fills the candidate pool and embeddings only rescore it, a page with no lexical overlap with the query is unfindable whatever the embedding quality. Swapping the score blend for RRF over that same pool changes nothing. Only a vector recall arm lifts the ceiling."
updated: 2026-10-17
sources:
  - data/raw/repos/librarian/.claude--docs--research--2026-08-20_retrieval-parity_tencentdb.md
  - data/raw/repos/librarian/.claude--docs--research--2026-08-22_semantica-parity.md
---

# Embeddings That Only Rerank Cannot Recall

A retrieval stack can have embeddings and still be lexical-only in practice. librarian's
search core found this during two reference-architecture parity reviews (2026-08). The
candidate set came from BM25 alone (`LIMIT limit*3`). The vector only appeared afterwards,
as one term of a fixed linear blend:

```python
final = 0.5 * text_score + 0.3 * sem_score + 0.2 * (backlinks / max_backlinks)
```

**Consequence:** if BM25 misses a page, semantic scoring can never bring it back. A query
that shares no words with the target page cannot find it, however good the embedding model
is. Most memory and RAG systems do it the other way round: vectors recall, lexical reranks.
A reference system with no embeddings at all (FTS5 seeds plus graph BFS) turned out to be
recall-equivalent. The embeddings looked like a difference between the two systems, but
they did not change what each one could recall.

## Two compounding limits

- **Truncated embed window.** Only the title, the summary and the first 600 characters of
  each page were embedded. Content below that window had no semantic representation.
- **Uncalibrated blend.** The blend mixes three scales that cannot be compared directly:
  BM25 normalised against the *batch* max (not a stable scale), cosine in [-1, 1], and a
  backlink ratio in [0, 1]. None of the three weights was tuned. Rank-based
  [[Reciprocal Rank Fusion (RRF)]] (k=60) avoids the miscalibration.

## The sequencing trap

The second review nearly recommended "replace the blend with RRF" as the fix. It then
corrected itself: **RRF over a BM25-only candidate pool still cannot surface a page that
BM25 missed.** RRF is a real cleanup, but it does not lift the recall ceiling. Add the
vector recall arm first, or do both in one change. Shipping RRF alone and calling
retrieval fixed is the mistake. Evaluate the change against both the normal and the
FTS-ablated baselines.

## When it is acceptable

This is not automatically a bug. In this corpus the page is the chunk. Backlinks are
mandatory, and the authoring rule is one page per named mechanism. Together these make
lexical recall work far better than it would over arbitrary prose. The repo's own ablation
supports this: turning FTS off dropped hit-rate from 1.00 to 0.58. So the ceiling was
acceptable at 284 pages. The failure was that nothing documented it. Write the ceiling
down, and re-test it when the corpus or the query mix changes.

## How to detect it

Look at where candidates are generated, not at whether an embedding model is loaded. A
quick test: pick a page, write a query that paraphrases it with zero shared terms, and
check whether it ever appears in the results.

## See Also
- [[Reciprocal Rank Fusion (RRF)]] — extends (RRF fixes calibration, not recall)
- [[RAG Reranking]] — extends (a reranker can only reorder what recall produced)
- [[Typed-Graph Retrieval Ablation]] — extends (the same corpus where lexical + rerank sat at ceiling)
- [[Compiled-Prose KB vs Graph-Native Store]] — instance-of (finding from the parity reviews)
- [[Fallback Mistaken for the Design]] — extends (an unadvertised degraded path read as the design)
