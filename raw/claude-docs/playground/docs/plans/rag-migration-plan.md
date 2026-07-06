# RAG Migration Plan

**Date:** 2026-04-25
**Status:** P0–P4 complete (Track 2) | P5 optional | Track 1 deferred pending corpus
**Research:** [rag-integration-strategy.md](../research/rag-integration-strategy.md)

---

## Overview

Two parallel tracks to integrate the custom RAG pipeline into the playground, replacing the unused AWS Bedrock Knowledge Base call in `mcp_servers/billy/`.

| Track | What | Status |
|---|---|---|
| **Track 2** | Migrate `help-support-rag-agent` → `playground/va-support-rag/` as a standalone agentic RAG peer service | **P0–P4 complete** — 176 tests pass; service live on :8002; Docker + eval harness working |
| **Track 1** | Replace `fetch_support_knowledge` (Bedrock) in billy MCP with thin RAG tool | **Deferred** — Billy corpus (`billy_raw`) does not exist yet |

---

## Data Architecture

### Corpus inventory

| Name | Source | Status | Docs | Format |
|---|---|---|---|---|
| `clara_raw` | sevdesk help center, FAQ, blog, Atlassian/Confluence | **Indexed** (April 18) | 598 total (268 help + 54 FAQ + 169 blog + 107 Atlassian) | JSONL (scraped by `raptor_scraper`) |
| `billy_raw` | Billy accounting help docs | **Not yet available** — to be scraped/exported | TBD | TBD |

> Note: "Clara" is the internal name for the sevdesk support assistant corpus. The raw JSONL files are already in `help-support-rag-agent/data/raptor_scraper/output/v2/`.

### Three-store layout

Both tracks feed into the same three-store pattern per corpus:

```
data/
  raw/
    clara_raw/          ← scraped_help.jsonl, scraped_faq.jsonl, scraped_blog.jsonl, scraped_atlassian.jsonl
    billy_raw/          ← (not yet available)

  stores/
    vectordb/           ← dense embeddings (DuckDB; rag_chunks table with FLOAT[] embedding column)
      clara.duckdb      ← already exists: data/vectorstore/rag_index.duckdb (6.8MB, April 18)
      billy.duckdb      ← built when billy_raw is ready
    metadb/             ← document-level bookkeeping + sentence snippets
      clara_meta.db     ← maps to existing ingest_documents + ingest_snippets tables in DuckDB
      billy_meta.db
    graphdb/            ← entity/relation graph for multi-hop queries (future)
      clara/            ← Neo4j or Kuzu (see below)
      billy/
```

> The existing `rag_index.duckdb` already contains three tables that map directly to this layout:
> - `rag_chunks` → **vectordb** (chunk text + FLOAT[] embedding)
> - `ingest_documents` → **metadb** (SHA-256 checksum, chunk_count, word_count, ingested_at, source_file)
> - `ingest_snippets` → **metadb** (sentence-level full-text search)
>
> Migration step: extract `ingest_documents` + `ingest_snippets` into a separate `clara_meta.db`; keep `rag_chunks` in `clara.duckdb`. Or keep all three in one file for local dev — decision at migration time.

### What metadata IS stored (recoverable from disk)

- ✅ Ingestion timestamp (`ingested_at`)
- ✅ SHA-256 checksum per document (dedup-safe)
- ✅ `chunk_count`, `snippet_count`, `word_count` per document
- ✅ `source_file`, `source`, `content_type`, `topic`, `url`, `title`
- ✅ Stable chunk IDs (`{doc_id}_{index}`) — aligned with eval dataset `relevant_chunks` field

### What is NOT stored (inferred from code — gap to fix at migration)

- ❌ Embedding model name/revision (defaults: `all-MiniLM-L6-v2` 384-dim; or `multilingual-e5-large` 1024-dim)
- ❌ Chunk strategy class name (current: `FixedChunker`, stable ID mode)
- ❌ Chunking parameters used (`RAG_CHUNK_MAX_TOKENS=512`, `OVERLAP=64`, `MIN=50`)

**Fix during P2:** Add an `ingest_runs` table to metadb capturing model name, strategy, params, and run timestamp. Ensures reproducibility when reindexing for Billy or re-embedding with a different model.

### Evaluation dataset

- 19,351 records across multiple JSONL files in `data/eval_data/`
- Golden set: `eval_v2.jsonl` (583 records, `corpus_version: "20251206"`)
- Format per record: `query_id`, `query` (German), `expected_answer`, `source_doc_id`, `relevant_chunks` (stable IDs), `retrieval_scores`
- Queries are in **German** — corpus is sevdesk (German accounting SaaS)

### graphdb tooling (needs research)

The graphdb store is future/non-blocking. Two candidate options:

| Option | Model | Deployment | Query language | Notes |
|---|---|---|---|---|
| **Neo4j** | Labeled property graph | Docker container (or Aura cloud) | Cypher | Mature, well-documented, familiar; heavier operationally |
| **Kuzu** | Property graph | Embedded (like DuckDB — no server) | Cypher-compatible | Much lighter, fits the local-first dev pattern; less tooling/UI |

Recommendation: spike Kuzu first (embedded, no ops overhead, Cypher so Neo4j knowledge transfers). If you need a visual graph explorer or production scale, swap to Neo4j. Not blocking Track 2 execution.

**Ingest pipeline** (`va-support-rag/ingest/`) runs offline, one-time per corpus update:
```
clara_raw/ → parse → chunk → embed → write → clara.duckdb + clara_meta.db (+ future: clara_graph/)
billy_raw/ → parse → chunk → embed → write → billy.duckdb + billy_meta.db
```

Both Track 1 and Track 2 are **read-only consumers** of the stores. No service writes to the index at runtime.

---

## Track 2 — `va-support-rag/` Migration

### Goal
Migrate `help-support-rag-agent` into playground as a runnable peer service. Keep the full 9-node LangGraph graph (planner → retriever → confidence gates → reranker → answer → eval → summarizer). Use it for experimentation and calibration on the sevdesk (`clara_raw`) corpus.

### Prerequisites
- [ ] Confirm `clara_raw` sources and existing DuckDB index location in `help-support-rag-agent/data/`
- [ ] Confirm existing eval test set location (`evals/` or `tests/evalsuite/`)

### Steps

**P0 — Scaffold**
1. Create `playground/va-support-rag/` directory
2. Copy `help-support-rag-agent/src/` → `va-support-rag/src/`
3. Copy `help-support-rag-agent/pyproject.toml` → `va-support-rag/pyproject.toml`; strip unused extras (`bedrock`, `openai`) and align dependency versions with `va-langgraph/pyproject.toml`
4. Copy `help-support-rag-agent/evals/` → `va-support-rag/evals/`
5. Copy `help-support-rag-agent/tests/` → `va-support-rag/tests/`
6. Move data: `help-support-rag-agent/data/` → `playground/data/stores/` under the three-store layout

**P1 — Cleanup (align to playground conventions)**

| What | Change |
|---|---|
| Delete `app/` mirror | Remove `src/../app/main.py` duplicate — keep `src/main.py` only |
| LLM factory | Replace multi-provider `LLM_PROVIDER` factory with `resolve_chat_model(size)` from `va-langgraph/shared/model_factory.py`; default Gemini 2.5 Flash |
| Model strings | No hardcoded model names — all from settings |
| Checkpointer default | Change default to Postgres; keep SQLite for local dev |
| Imports | Normalise to package-relative imports throughout |
| `print()` → structlog | Enforce structlog with dot-separated event names |
| Pydantic | Confirm all models use Pydantic v2 |
| `from __future__ import annotations` | Add to any module missing it |

**P2 — Ingest layer**
1. Create `va-support-rag/ingest/run_ingest.py` — CLI script that reads from `data/raw/clara_raw/`, runs the existing preprocessing + chunking + embedding pipeline, writes to `data/stores/vectordb/clara.duckdb` and `data/stores/metadb/clara_meta.db`
2. Update `src/rag/datastore/duckdb.py` paths to read from `data/stores/vectordb/`
3. Document ingest command in `va-support-rag/Makefile` (`make ingest-clara`)

**P3 — Docker integration**
1. Add `va-support-rag` service to `infrastructure/containers/docker-compose.va.yml`:
   - Mount `data/stores/` as read-only volume
   - Expose port (e.g. `:8002`)
   - Postgres checkpointer pointing at shared `va-postgres` service
2. Add `Dockerfile` at `infrastructure/containers/Dockerfile.va-support-rag`
3. Add `make va-rag-up` target to root Makefile (or extend `make va-up`)

**P4 — Smoke test**
1. Confirm `uv run pytest tests/ -v` passes
2. Confirm service starts and `/health` returns 200
3. Send one sevdesk support query via CLI runner; confirm answer + citations returned
4. Confirm eval harness runs: `uv run python evals/runner.py --suite capability`

**P5 — Confidence calibration (experimental, not blocking)**
1. Run eval suite against golden sevdesk dataset
2. Record escalation rate per threshold setting
3. Document findings in `va-support-rag/.claude/docs/calibration-notes.md`
4. Decision point: if escalation rate <5% on golden set, thresholds are reasonable; if >15%, recalibrate

---

## Track 1 — Billy MCP RAG tool (deferred)

**Blocked on:** `billy_raw` corpus (Billy help docs not yet scraped/exported).

When unblocked:

1. Run ingest pipeline on `billy_raw/` → `data/stores/vectordb/billy.duckdb`
2. In `mcp_servers/billy/app/tools/support_knowledge.py`:
   - Remove boto3, bedrock-agent-runtime, AWS credential handling
   - Replace with thin `rag_retrieve(query)` call: embed → DuckDB search → RRF → cross-encoder rerank → return `List[SupportPassage]`
   - Keep same return shape (rank, score, source_url, title, text) so `support_subgraph` in va-langgraph needs no changes
3. Remove `boto3` from `mcp_servers/billy/pyproject.toml`
4. Update `mcp_servers/billy/.env.example`: remove `BEDROCK_KNOWLEDGE_BASE_ID`, `AWS_REGION`, `AWS_PROFILE`; add `VECTORDB_PATH`, `RERANKER_BACKEND`
5. Point at `data/stores/vectordb/billy.duckdb` (shared volume with `va-support-rag`)

**Latency note:** Replaces ~100–200ms AWS network round-trip with ~30–80ms local DuckDB read. Net improvement even before reranking.

---

## Open Questions

| Question | Blocks | Status |
|---|---|---|
| Where is clara_raw data? | P0 step 6 | **Resolved** — `data/raptor_scraper/output/v2/*.jsonl` |
| Is DuckDB index already built? | P2 | **Resolved** — `data/vectorstore/rag_index.duckdb` (6.8MB, April 18) |
| graphdb tooling? | future | **Partially resolved** — spike Kuzu (embedded); fallback Neo4j |
| Billy help docs source? | Track 1 | **Open** — web scrape? Intercom export? Notion? |
| Embedding model used for current index? | P2 reproducibility | **Inferred** — likely `all-MiniLM-L6-v2` (384-dim); confirm from `.env` |

---

## What "experiment and compare" looks like (Phase 2)

Once both tracks are running against the same Billy corpus:

```
User support query
  ├─ va-langgraph/support_subgraph → Track 1 (thin RAG tool, ~1.2s)
  └─ va-support-rag API            → Track 2 (agentic RAG, ~1.5–2s)

Compare:
  - Answer quality (LLM judge, human spot-check)
  - Latency (P50, P95)
  - Escalation rate (how often confidence gating fires)
  - Retrieval metrics (hit rate, MRR, NDCG from eval harness)
```

Track 2 learnings graduate into Track 1 when the eval data supports it.
