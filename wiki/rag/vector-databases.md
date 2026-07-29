---
title: Vector Database Comparison
tags: [rag, infra, comparison]
summary: Side-by-side of vector stores used across RAG pipelines — DuckDB (embedded local), ChromaDB, pgvector, OpenSearch (Bedrock), Pinecone, GCP Discovery Engine — with when-to-use guidance and migration notes.
updated: 2026-07-06
sources:
  - raw/claude-docs/project-g/docs/rag/vector-databases.md
---

# Vector Database Comparison

## Current Usage

| Store | Where | Mode |
|---|---|---|
| OpenSearch | Bedrock KB (VA support agents) | Managed — Bedrock owns the index |
| DuckDB | hc_rag default vector backend | Embedded, self-managed, no server |
| ChromaDB | hc_rag optional backend | Embedded, persistent HNSW |
| pgvector | Chat agent local/dev | Self-managed PostgreSQL extension |
| GCP Discovery Engine | Chat agent production | Fully managed — GCP owns everything |

---

## Side-by-Side Comparison

| | DuckDB + VSS | ChromaDB | pgvector | OpenSearch | Pinecone | Bedrock KB |
|---|---|---|---|---|---|---|
| **Type** | Embedded in-process | Embedded / client-server | PostgreSQL extension | Dedicated search engine | Managed vector DB | Managed RAG service |
| **Hybrid search** | Dense only | Dense only | Manual (dense + BM25 plugin) | Native HNSW + BM25 | Dense only | Native hybrid (default) |
| **ANN algorithm** | Flat (exact) or HNSW | HNSW (cosine) | HNSW / IVFFlat | HNSW | HNSW | Managed |
| **Reranking** | Manual | Manual | Manual (cross-encoder) | Manual | Via Cohere plugin | `amazon.rerank-v1:0` built-in |
| **Operational overhead** | Zero | Zero | Low (rides your DB) | High | Zero | Zero |
| **Cost model** | Free | Free / Chroma Cloud | Storage + compute | Cluster cost | Per-vector + per-query | Per-query + storage |

---

## When To Use Which

### DuckDB
Two roles: **production local backend** (exact cosine search, no server, embedded in hc_rag) and **eval/offline HNSW** (via `vss` extension for retrieval sweeps).

Limitation: dense only — no BM25/hybrid. For keyword-heavy Danish queries (product names, billing codes), retrieval quality is lower than OpenSearch hybrid.

### pgvector
Best for dev, prototypes, teams already running Postgres.

**Key constraint:** Gemini `gemini-embedding-2-preview` outputs 3072 dims → exceeds pgvector's 2000-dim HNSW limit → **exact search only**. Fine at small corpus size, won't scale to millions of docs.

```sql
SELECT text, metadata, 1 - (embedding <=> %s::vector) AS score
FROM documents
ORDER BY embedding <=> %s::vector
LIMIT %s
```

### OpenSearch (Bedrock KB)
Best for: AWS-native production, multilingual corpora, hybrid search without extra infra.

Two-level hierarchy: leaf chunk (`AMAZON_BEDROCK_TEXT_CHUNK`) for matching + parent context (`AMAZON_BEDROCK_TEXT`) for LLM. Raw `_score` is **not exposed** by the Bedrock KB API (always 0.0 via API).

See [[GCP Vertex AI Search vs AWS Bedrock KB]] for full details.

### Pinecone
Best for pure-play semantic similarity with zero ops. **No native BM25 hybrid** — poor fit for multilingual support KB where keyword precision matters.

### ChromaDB
Optional backend — persistent HNSW. Prefer over DuckDB when you want ANN at larger corpus sizes (> 50k chunks). Not installed by default in the main project-g venv.

### GCP Discovery Engine (Vertex AI Search)
Best for: fully managed RAG on GCP. Two modes: Agentic RAG (Gemini ADK agentic loop) or Built-in Answer (`:answer` endpoint where GCP owns retrieval + generation). See [[GCP Vertex AI Search vs AWS Bedrock KB]].

---

## Embedding Model → Dimension → Store Compatibility

| Embedding model | Dim | pgvector HNSW? | Notes |
|---|---|---|---|
| `gemini-embedding-2-preview` | 3072 | ❌ (>2000 limit) | Exact search only in pgvector |
| `amazon.titan-embed-text-v2:0` | 1024 | ✅ | Used by Bedrock KB |
| `text-embedding-3-large` (OpenAI) | 3072 / 256 (MRL) | ✅ at 256 | Matryoshka allows dimension reduction |
| `intfloat/multilingual-e5-large` | 1024 | ✅ | Local, natively multilingual |

---

## Retrieval Quality Levers (Any Store)

1. **Hybrid search** — dense (semantic) + sparse (BM25). Bedrock auto; pgvector needs ParadeDB.
2. **Reranking** — cross-encoder as second pass. Bedrock: `amazon.rerank-v1:0`. Elsewhere: Cohere, Jina, BGE.
3. **Multi-query** — fire 2–3 reformulated queries, deduplicate by URL fingerprint.
4. **Parent-child chunking** — retrieve at leaf granularity, send parent context to LLM.
5. **CRAG** — grade retrieved docs, rewrite query if below threshold, retry. See [[CRAG Retry Logic]].

---

## Migration Notes

- **pgvector → OpenSearch:** Add BM25 hybrid config + Bedrock reranker. Main work is ingestion pipeline.
- **OpenSearch (Bedrock) → pgvector:** Lose hybrid search and managed reranking. Not recommended for production.
- **pgvector → Pinecone:** Lose keyword/hybrid, gain SaaS zero-ops. Only viable for purely semantic English corpora.
- **Any → GCP Discovery Engine:** Only viable if GCP-native. Retrieval is a black box — lose score calibration, chunk boundary visibility.

---

## See Also
- [[GCP Vertex AI Search vs AWS Bedrock KB]]
- [[RAG Retrieval Strategies]]
- [[Reciprocal Rank Fusion (RRF)]]
- [[RAG Reranking]]
- [[Agentic RAG — Advanced Patterns]]
