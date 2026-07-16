Plan: Migrate VectorStore from NumPy to pgvector (PostgreSQL)

 Context

 The current vector_store.py stores embeddings as a NumPy .npz file and metadata as
 documents.json on disk, then loads everything into RAM at startup. The goal is to replace
 this with a PostgreSQL + pgvector backend so embeddings are stored in a proper database,
 enabling persistent, scalable, and queryable vector search without loading all data into
 memory.

 The public API of VectorStore must be preserved so main.py, tools.py, and intercom_loader.py
  need zero changes.

 ---
 Files to Change

 ┌─────────────────┬───────────────────────────────────────────────────┐
 │      File       │                      Change                       │
 ├─────────────────┼───────────────────────────────────────────────────┤
 │ vector_store.py │ Full rewrite of storage/retrieval to use pgvector │
 ├─────────────────┼───────────────────────────────────────────────────┤
 │ config.py       │ Add DATABASE_URL config value                     │
 ├─────────────────┼───────────────────────────────────────────────────┤
 │ pyproject.toml  │ Add psycopg[binary] and pgvector dependencies     │
 └─────────────────┴───────────────────────────────────────────────────┘

 ---
 Implementation Plan

 1. config.py — Add DB config

 Add one line:
 DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost:5432/agentic_rag")

 2. pyproject.toml — Add dependencies

 "psycopg[binary]>=3.1",
 "pgvector>=0.3.0",

 3. .env — User adds their DB connection string

 DATABASE_URL=postgresql://user:password@localhost:5432/agentic_rag

 4. vector_store.py — Rewrite storage layer

 Keep unchanged:
 - _embed_texts() — Gemini batch embedding
 - _embed_query() — Gemini query embedding
 - _parse_qa_chunks() — Markdown QA parser
 - _parse_intercom_chunks() — Intercom article parser

 Change __init__:
 - Replace numpy arrays + documents list with a psycopg connection
 - Install pgvector extension + register vector type
 - Create the documents table if it doesn't exist:
 CREATE EXTENSION IF NOT EXISTS vector;
 CREATE TABLE IF NOT EXISTS documents (
     id SERIAL PRIMARY KEY,
     text TEXT NOT NULL,
     metadata JSONB NOT NULL,
     embedding vector(3072) NOT NULL
 );

 Change build_from_kb:
 - Parse chunks the same way (unchanged logic)
 - Clear old data: DELETE FROM documents
 - Embed texts in batches (unchanged _embed_texts)
 - Bulk insert rows using executemany with (text, metadata, embedding)
 - Set self.is_loaded = True

 Change search:
 - Embed query with _embed_query (unchanged)
 - Use pgvector cosine distance operator <=>:
 SELECT text, metadata, 1 - (embedding <=> %s::vector) AS score
 FROM documents
 WHERE (%s IS NULL OR metadata->>'category' = %s)
 ORDER BY embedding <=> %s::vector
 LIMIT %s
 - Return same format: [{"text", "metadata", "score"}]
 - Filter out scores below 0 (same as current)

 Change save:
 - No-op — data is already persisted in DB during build_from_kb
 - Print a message confirming data is in the DB

 Change load:
 - Open DB connection, check if documents table has rows
 - Set self.is_loaded = True if rows exist, raise FileNotFoundError otherwise

 Change stats:
 - Query DB for counts instead of iterating in-memory list:
 SELECT metadata->>'category', COUNT(*) FROM documents GROUP BY 1;
 SELECT metadata->>'intent', COUNT(DISTINCT metadata->>'intent') FROM documents;
 SELECT COUNT(*) FROM documents;

 ---
 pgvector Index (optional but recommended)

 After bulk insert in build_from_kb, create an IVFFlat index for fast approximate search:
 CREATE INDEX IF NOT EXISTS documents_embedding_idx
 ON documents USING ivfflat (embedding vector_cosine_ops)
 WITH (lists = 100);

 ---
 Prerequisites for the User

 1. PostgreSQL installed and running
 2. pgvector extension available (CREATE EXTENSION vector requires it to be installed on the
 server)
 3. DATABASE_URL set in .env
 4. Run: pip install "psycopg[binary]" pgvector (or uv sync after updating pyproject.toml)

 ---
 Verification

 1. Set DATABASE_URL in .env
 2. Run python vector_store.py — should build the vector store and write to PostgreSQL
 3. Run python main.py — should load from DB and answer queries correctly
 4. Run python evaluate.py — metrics should match the numpy baseline
