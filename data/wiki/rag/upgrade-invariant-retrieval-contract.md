---
title: Upgrade-Invariant Retrieval Contract
tags: [rag, decision]
summary: Ship Postgres full-text search first and pgvector second, behind one search endpoint whose response shape never changes. Consumers code against the contract once. The vector upgrade is gated on a graded before/after eval, and re-embedding skips unchanged docs by content hash.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/dssg/docs/overview/design.md
  - data/raw/claude-docs/dssg/docs/milestones/kb-platform-api.md
  - data/raw/claude-docs/dssg/docs/scoping/kb-platform-api.md
  - data/raw/claude-docs/dssg/docs/overview/tooling.md
---

# Upgrade-Invariant Retrieval Contract

A retrieval decision from a 2026-07 platform design. A shared knowledge base needed lexical
search now and semantic retrieval soon. Three consumers were waiting to code against it.

## Decision

- **FTS first, pgvector second, same database.** No dedicated vector DB: it would be a second
  system to run for a corpus of hundreds of documents, not millions. Tenancy rides the same
  RLS as everything else.
- **One endpoint, frozen shape.** `GET /kb/search?q=` returns
  `{results: [{title, snippet, source_url, score}]}` in both phases. Consumers do not rewrite
  when retrieval upgrades. `source_url` is in the shape from day one, so citations never
  depend on the backend.
- **The upgrade has to win.** Semantic retrieval ships only when a ~20-question set,
  hand-graded before and after, shows vector beating full-text. Results are logged as
  structured fields.
- **Idempotent ingestion.** Running ingestion twice is a no-op the second time
  (content-hash match), and re-embedding skips unchanged docs. The pipeline also uses a
  similarity cutoff with a top-1 fallback. The pattern was adapted from a reference RAG
  copilot.
- **Hand-rolled over a framework.** Chunk, embed and cache are small and fully
  understood, so retrieval frameworks were rejected as churn without added capability. A
  document *parser* is added only when PDF or Office corpora enter scope, because parsing is
  the one genuinely hard sub-problem.
- **Graph storage stays out** unless a named use case defeats Postgres adjacency tables.

## Alternatives rejected

| Option | Why not |
|---|---|
| Dedicated vector DB | extra operational system at a corpus size that doesn't need it |
| Graph DB | no named use case beats adjacency tables yet |
| Retrieval framework | abstraction churn; nothing it adds was needed |

## See Also
- [[PGVector Migration Pattern]] — related (the same "preserve the public API" move, from in-memory to pgvector)
- [[RAG Retrieval Strategies]] — extends (lexical-then-semantic as a staged rollout)
- [[Named-Trigger Deferral]] — related (the vector phase is gated on an eval win, not on a date)
- [[Vector Database Comparison]] — extends
