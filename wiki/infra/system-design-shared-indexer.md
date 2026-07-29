---
title: System Design — Shared Code-Index Service
tags: [infra, rag, mcp, reference]
summary: Interview-format system design writeup of the DSSG shared indexer — centralized indexer + query API with MCP as a thin read-only client, DuckDB single-writer risk, and the pgvector escape hatch.
updated: 2026-07-17
sources:
  - raw/repos/librarian/CLAUDE.md
---

# System Design — Shared Code-Index Service

Interview-format writeup of a system actually designed (librarian → DSSG team knowledge base, decided 2026-07-15). Format: requirements → constraints → architecture → tradeoffs → scaling.

## Requirements

- A small nonprofit team needs grounded retrieval over both **compiled design knowledge** (wiki prose) and **live source repositories** (symbols, structure).
- Team members are not all technical: setup friction must be near zero.
- Repo read credentials must not be distributed to every member.

## Constraints

- 2025–2026 field consensus: LLM-paraphrased prose is right for design knowledge but wrong for live code — code wants AST/symbol-level indexing plus agentic grep-first retrieval. Two ingestion paths, not one.
- Single maintainer initially; infra budget near zero.

## Architecture

- **Centralized indexer, not per-user local.** One service (CI job, cron, or git-webhook-triggered) owns running the indexer against team repos and holds the repo credentials. Members never run ingest themselves.
- **Standalone indexer + query API** (small FastAPI service) writing to a shared DuckDB — indexing logic deliberately NOT embedded in the MCP server.
- **MCP server as a thin read-only client** of that API. This is the friction-removal move: what members configure is a dumb client, not a stateful service. The choice of MCP is secondary; the thin-client split is what matters.
- Wiki compile path stays as-is (raw/ → LLM compile → wiki/); the code index is a separate tree-sitter symbol index (the codemap pattern), exposed through the same MCP surface.

## Tradeoffs

- Centralized index = stale-by-minutes vs. per-user local = fresh but N credential holders and N machines running tree-sitter. Staleness is acceptable for design-time retrieval.
- DuckDB is free and zero-ops but **single-writer** — concurrent indexing of many repos contends. Escape hatch decided up front: Postgres + pgvector when write contention becomes real, without changing the API surface.
- LLM-compiling source code into prose was rejected: it burns tokens re-paraphrasing what an AST already states, and goes stale on every commit.

## Scaling path

1. Now: one indexer process, DuckDB file, MCP read clients.
2. Contention: move store to pgvector; API unchanged; MCP clients unchanged.
3. Where the shared index physically lives (shared volume / S3-synced / hosted API) is a deployment decision deliberately deferred — it does not block the architecture.

## See Also
- [[Librarian KB — Build Plan]] — extends
- [[Librarian Project]]
- [[Karpathy LLM Wiki Pattern]] — prerequisite-for
