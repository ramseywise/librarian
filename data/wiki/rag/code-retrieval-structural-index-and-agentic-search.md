---
title: "Code Retrieval: Structural Index and Agentic Search"
tags: [rag, infra, concept]
summary: Live code wants a different retrieval stack than prose knowledge — AST/symbol-level chunking (tree-sitter, cAST), a lightweight symbol reference graph (Aider-style PageRank) instead of a graph database, grep-first agentic search with embeddings as fuzzy fallback, and Merkle/content-hash incremental re-indexing.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/state/research_agentic_kb_for_code.md
  - data/raw/claude-docs/guacamayo/docs/research/2026-08-20_tencentdb-memory_parity.md
  - data/raw/repos/librarian/.claude--docs--plans--codemap-code-index.md
  - data/raw/repos/librarian/.claude--docs--research--2026-08-20_retrieval-parity_tencentdb.md
---

# Code Retrieval: Structural Index and Agentic Search

Field survey (2025–2026) captured in guacamayo while scoping a team knowledge base. Core
conclusion: an LLM-paraphrased prose compile (the librarian wiki model) is right for design
knowledge and **wrong for live code**. Code needs its own ingestion path.

## 1. Chunk by structure, not by size

Fixed-size or line chunking cuts functions mid-body. Consensus is AST-based chunking:
**cAST** (EMNLP Findings 2025, `astchunk`) recursively splits large AST nodes and merges
siblings within a token budget. **Tree-sitter** is the near-universal parser backbone
(multi-language, incremental). The retrieval unit is the **symbol** — function/class with
signature, docstring, byte/line range and scope chain. Call/import-graph extraction is a
separate pass on top of the AST.

## 2. Graph vs vector vs hybrid

Pure vector search underperforms on code: caller and callee can be textually dissimilar, so
semantic similarity misses structural relevance. Research systems build repo-level code
graphs and retrieve k-hop ego-graphs around key symbols combined with BM25. The
small-team pattern worth copying is **Aider's repo-map**: tree-sitter tag extraction →
directed multigraph of file-to-file symbol references → personalized PageRank weighted by
identifiers mentioned in the conversation → top-ranked definitions rendered as an elided
map within a token budget. Full property-graph databases pay off only at multi-repo /
monorepo scale or when precise "what calls this" blast-radius queries dominate.

## 3. Agentic search over pre-built indexes

The dominant shift: away from vector indexes toward tool-based search. Claude Code dropped
vector search in 2025 for grep/glob-driven iterative exploration — better precision (exact
match), freshness (no index drift during edits) and simplicity. A 2026 paper reported
agentic keyword search reaching ~94.5% of RAG faithfulness with no vector store. The agent
greps/globs/reads, follows import and call edges for multi-hop questions, and self-corrects
by re-querying — CRAG-style correction via tool loops rather than a trained evaluator.
Multi-hop over call graphs matters most for cross-file refactors and "what breaks if I
change X"; single-file Q&A rarely needs it.

## 4. Freshness: re-index only what changed

Unlike append-only, human-cadenced doc ingestion, code tracks fast git history. Cursor
computes a **Merkle tree** over the workspace and walks only branches whose hashes differ,
re-embedding changed files; other tools use content-hashed incremental indexing with a
debounced watcher. Pattern: hook/watcher → targeted AST re-chunk → re-embed changed chunks
→ upsert/delete (not rebuild) → update import edges. "Staleness envelopes" (metadata
flagging drift from HEAD) are emerging; full reindex is reserved for parser/schema changes.
A parity review of librarian (2026-08) flagged exactly this gap on the prose side: any edit
triggered a full drop-and-re-embed, and the embedding only reranked BM25 candidates via a
fixed blend over the first ~600 characters of a page — there was no independent vector
recall path.

## 5. Small-team stack

tree-sitter → cAST chunking → SQLite/DuckDB for symbol metadata + FTS5/BM25 → local
embedding model into a lightweight vector store for semantic fallback → file/symbol
reference graph stored as SQLite edges (Aider-style PageRank) → git hook/watcher for
incremental updates. Wrap it in an agent loop that **prefers grep and symbol-graph lookups
first** and falls back to embeddings for fuzzy, conceptual queries.

## 6. Implementation notes: librarian's codemap

librarian built a small-team version of section 5 as `tools/codemap/` (2026-07). It uses
tree-sitter to extract symbols plus import and call edges into `.code_index.duckdb`, with
content-hash manifest skips for incremental reindexing. Decisions worth reusing:

- **Query through an API, never through the DB file.** MCP tools call a FastAPI layer over
  HTTP, and that layer owns the DuckDB connection. Indexing can later move to one central
  process that holds the repo credentials, while any number of read-only clients keep
  querying. Moving to a shared host is then an env-var change (`CODEMAP_API_URL`), not a
  rearchitecture.
- **Ambiguous call names fan out; they are not dropped.** A callee name that matches
  several symbols gets one edge per match. `main` alone produced 256 edges across the repo.
  Dropping ambiguous matches was rejected because it silently loses real edges, and
  precision can be recovered at query time.
- **Label speculative scaffolding honestly.** The multi-language registry, call edges and
  symbol embeddings were built ahead of need. They were proven only synthetically: a fake
  `.fakepy` language over the Python grammar, and the repo's own call graph. Each was
  recorded as "still not triggered" so that building them was never read as evidence of
  demand. No query had yet shown symbol-name search missing something that semantic
  search found.

## See Also
- [[System Design — Shared Code-Index Service]] — instance-of (the service this survey informed)
- [[RAG Retrieval Strategies]] — extends
- [[CRAG Retry Logic]] — alternative-to (trained evaluator vs tool-loop self-correction)
- [[Librarian RAG Architecture]] — alternative-to (prose compile path)
- [[Embeddings That Only Rerank Cannot Recall]] — extends (librarian's rerank-only gap, in depth)
- [[Agentic RAG — Advanced Patterns]] — extends
