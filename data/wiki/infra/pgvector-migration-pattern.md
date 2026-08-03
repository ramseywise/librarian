---
title: PGVector Migration Pattern
tags: [infra, rag, pattern]
summary: Migrating a vector store from in-memory NumPy arrays to PostgreSQL + pgvector — preserving the public API, using cosine distance operator, adding an IVFFlat index, and moving embeddings to Cloud SQL without re-embedding.
updated: 2026-08-03
sources:
  - raw/claude-docs/chat-agent/docs/architecture/PGVector_migration.md
  - raw/claude-docs/chat-agent/docs/TODO_production.md
  - raw/claude-docs/chat-agent/docs/architecture/queries.md
  - raw/claude-docs/chat-agent/docs/architecture/VertexAI.md
  - raw/claude-docs/chat-agent/docs/plans/aif32_code_review_fixes.md
---

# PGVector Migration Pattern

A common evolution path: start with numpy `.npz` + JSON on disk, hit the limits of in-memory search, migrate to PostgreSQL + pgvector. The key constraint is preserving the public `VectorStore` API so callers need zero changes.

---

## Why Migrate from NumPy

| Problem | NumPy + disk | pgvector |
|---|---|---|
| Scalability | Loads all embeddings into RAM at startup | Query-time DB fetch, no RAM overhead |
| Persistence | Manual save/load; file lock risks | ACID transactions, crash-safe |
| Filtering | Python-side post-filter | SQL `WHERE` clause on metadata JSONB |
| Multiple instances | Each process loads its own copy | Shared DB across all workers |
| Cloud deployment | `.npz` files need to be baked into image | DB is external; image stays small |

---

## Table Schema

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
    id       SERIAL PRIMARY KEY,
    text     TEXT    NOT NULL,
    metadata JSONB   NOT NULL,
    embedding vector(3072) NOT NULL
);
```

`metadata` as `JSONB` enables arbitrary key filtering:

```sql
-- Category filter (previously Python-side post-filter)
WHERE metadata->>'category' = 'INTERCOM'
```

---

## Cosine Similarity Query

pgvector's cosine **distance** operator is `<=>`. To convert to similarity (higher = better):

```sql
SELECT
    text,
    metadata,
    1 - (embedding <=> %s::vector) AS score
FROM documents
WHERE (%s IS NULL OR metadata->>'category' = %s)
ORDER BY embedding <=> %s::vector
LIMIT %s
```

Return format is identical to the in-memory version: `[{"text", "metadata", "score"}]`. Callers see no change.

---

## IVFFlat Index for Approximate Nearest Neighbour

After bulk insert, create an ANN index:

```sql
CREATE INDEX IF NOT EXISTS documents_embedding_idx
ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

`lists = 100` is a reasonable default for a few hundred documents. For larger datasets, use `lists ≈ sqrt(n_rows)`. The index trades a small accuracy loss for a large speed gain — acceptable for RAG use cases where reranking corrects minor ranking differences.

---

## Migration: Move Existing Embeddings Without Re-Embedding

If embeddings already exist in a local PostgreSQL instance, migrate via `pg_dump` + `pg_restore` through the Cloud SQL Auth Proxy. **No re-embedding cost.**

```bash
# 1. Export from local
pg_dump -h localhost -U postgres -d agentic_rag \
  --table=documents \
  -F c -f documents_export.dump

# 2. Start Cloud SQL Auth Proxy
cloud-sql-proxy PROJECT_ID:REGION:INSTANCE &

# 3. Restore into Cloud SQL
pg_restore -h 127.0.0.1 -p 5432 \
  -U appuser -d agentic_rag \
  --table=documents documents_export.dump

# 4. Verify
psql -h 127.0.0.1 -U appuser -d agentic_rag \
  -c "SELECT COUNT(*) FROM documents;"
```

This pattern works for any pgvector migration — not just Cloud SQL.

---

## API Preservation Contract

The `VectorStore` class must keep its public methods unchanged so no callers need updating:

| Method | Old behaviour | New behaviour |
|---|---|---|
| `build_from_kb()` | Parse → embed → write `.npz` | Parse → embed → `INSERT INTO documents` |
| `search(query, top_k)` | Embed → numpy cosine sort | Embed → pgvector `<=>` query |
| `load()` | `np.load(.npz)` | Open DB connection, check row count |
| `save()` | `np.savez()` | No-op (data persisted on insert) |
| `stats()` | Iterate in-memory list | `GROUP BY metadata->>'category'` |

Unchanged methods (no migration needed):
- `_embed_texts()` — Gemini batch embedding
- `_embed_query()` — Gemini query embedding
- `_parse_*_chunks()` — markdown/Intercom parsers

**Follow-up dedup (AIF-32 code review):** `_parse_intercom_chunks()` here and `eval/dataset/article_parser.py::_parse_content()` had independently duplicated the same Intercom section-splitting/header-extraction logic — any format change to the Intercom KB file had to be applied twice. Extracted into a shared `intercom_parser.py::parse_intercom_content()` used by both; public interfaces of both callers unchanged. See [[Synthetic Dataset Generation for RAG Eval]] for the eval-side caller.

---

## Useful pgAdmin Queries

```sql
-- Count documents
SELECT COUNT(*) FROM documents;

-- Browse stored content
SELECT id, metadata->>'title' AS title, metadata->>'category' AS category
FROM documents LIMIT 10;

-- Filter by category
SELECT metadata->>'title' AS title
FROM documents
WHERE metadata->>'category' = 'INTERCOM';

-- Verify embedding dimensions
SELECT id, vector_dims(embedding) AS dims FROM documents LIMIT 1;
```

Direct similarity search (without embedding) is not possible from pgAdmin — requires Python to call the embedding model first.

---

## Vertex AI Embeddings Decision

Switching from Gemini API (`text-embedding-004`) to Vertex AI (`text-embedding-005`) for a small-scale support RAG system is **not worth the migration cost**:

- Quality difference is negligible for customer support domains
- Switching models requires re-embedding the entire corpus (embeddings from different models are incompatible)
- Existing embeddings are generated at index-build time only — not at runtime

Consider Vertex AI embeddings when: already on GCP with ADC auth, processing at massive scale with better rate limits, or when unified GCP billing is a hard requirement.

---

## See Also
- [[Cloud Run + Cloud SQL Pattern]]
- [[RAG Retrieval Strategies]]
- [[Production Hardening Patterns]]
- [[Embedder Warmup]]
- [[Langfuse ADK Tracing Patterns]]
- [[Synthetic Dataset Generation for RAG Eval]]
- [[Split Service Deployment]] — related (Supabase Postgres as shared vector + app store)
