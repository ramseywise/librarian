---
title: Delete an Unfinished RAG Retrofit, Don't Archive It
tags: [rag, decision]
summary: "A RAG stack forked from another domain's support bot, half-adapted, then suspended behind a web-search stopgap was finally deleted rather than archived — the domain (genre/artist lookup) never justified a vector store, the missing asset was a curated corpus not code, and suspended code kept leaking dead lineage into evals and masking the one live module inside it."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase8-rag-rightsize-agentic-search.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase8-rag-rightsize-agentic-search.md
  - data/raw/claude-docs/listen-wiseer/docs/reviews/phase8-rag-rightsize-agentic-search.md
  - data/raw/repos/listen-wiseer/.claude--docs--reviews--phase8-rag-rightsize-agentic-search.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase6_refactor.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase6_refactor.md
  - data/raw/claude-docs/listen-wiseer/docs/plans/phase5a_rag.md
  - data/raw/repos/listen-wiseer/.claude--docs--plans--phase5a_rag.md
---

# Delete an Unfinished RAG Retrofit, Don't Archive It

**Context (listen-wiseer, three phases).**

1. **Adopt (Phase 5a).** A full RAG core — chunker, embedder, reranker, generator,
   orchestration — was forked from a customer-support assistant built for a different
   language and search stack, and retrofitted: OpenSearch → DuckDB vss, a large multilingual
   embedder → MiniLM, support intents → music intents, lazy Wikipedia/Tavily ingestion.
2. **Suspend (Phase 6).** Judged overbuilt for its value: it needed a pre-populated vector
   store, ~500ms of model load at startup, and a Wikipedia corpus that goes stale, while a
   web-search API returned grounded, fresh answers in ~1s with zero local state. The tool
   was repointed at web search *behind the same tool name* (so the graph did not change),
   and the RAG code was left in place "to be re-evaluated as an enrichment layer."
3. **Delete (Phase 8).** A usage audit found exactly one live import out of the whole
   package — the keyword intent/query-understanding module — and a raw-SQL enrichment
   branch reading a vector table that no ingestion had ever filled (a permanent no-op).

## Decision

**Delete, don't archive.** Move the one domain-specific, load-bearing module (intent and
query understanding) to the agent package; delete the rest, plus its test tree, plus the
vector table. If a corpus-backed RAG is ever wanted, it is a new phase built clean against
the current architecture, not a resurrection of this code.

## Why

- **The domain did not justify a vector store.** Genre and artist lookup is answered better
  by live web search plus a confidence gate ([[Provenance-Tiered Confidence Gate]]) than by
  a small, stale, self-ingested corpus.
- **The gap was the corpus, not the code.** A justified doc-RAG elsewhere (curated ~50
  articles, cross-encoder rerank, citation guardrails, dedicated graders) shows what the
  investment actually is: a maintained corpus. Keeping retrieval code without one is
  carrying the cheap half.
- **Archiving relocates dead weight.** An `archive/` copy would keep the same unadapted
  generic scaffolding alive for grep, review, and onboarding to trip over.
- **Suspended code leaks.** The audit found the source project's lineage had spread past the
  suspended package into `evals/`: a runner importing the *original* never-adapted search
  client, metrics and golden-set generators, and model classes with a non-English
  `language` default and support-ticket ID fields — unambiguously not music. "Suspended"
  had meant "unowned".
- **Suspension hid the live part.** The only module anyone used sat inside a package
  everyone believed was dead, and its richer outputs (query decomposition, complexity
  score, retrieval-mode) were computed and discarded until this phase wired them into
  search fan-out ([[Write-Only Fields and the Reader Map]]).

## Tradeoffs accepted

- No local, offline retrieval path; artist context now depends on a paid search API.
- A second search provider was explicitly deferred — revisit only if faithfulness evals
  show gaps.

## Collateral findings from the same stabilize pass

The phase also found why testing had "stalled repeatedly": an unbounded
`requires-python = ">=3.11"` let the package manager pick the newest system interpreter,
on which a Cython extension (gensim) no longer compiled — fixed by committing a pinned
`.python-version`. An eval library's pytest plugin pinged telemetry at collection and hung
15+ minutes in a sandbox instead of failing fast — fixed by exporting its opt-out env var in
the Makefile. And a documented "32 failures = missing LFS database" baseline was stale; the
real baseline was 0 failures. Re-measure a recorded failure explanation before planning
around it.

## See Also
- [[RAG Architecture Selection]] — extends (the null option: no RAG for a lookup domain)
- [[Provenance-Tiered Confidence Gate]] — supersedes (what replaced the retrieval path)
- [[Write-Only Fields and the Reader Map]] — related (the computed-and-discarded query features)
- [[Listen-Wiseer Project]] — instance-of
