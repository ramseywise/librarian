---
title: Production Hardening Patterns
tags: [infra, rag, langgraph, pattern]
summary: Checklist of production hardening fixes for the Librarian service — P0/P1/P2 issues, async I/O safety, SQL injection prevention, CORS, and Docker packaging.
updated: 2026-04-24
sources:
  - raw/claude-docs/playground/docs/archived/librarian-prod-hardening/plan.md
  - raw/claude-docs/playground/docs/archived/retrieval-pipeline-prod/plan.md
  - raw/claude-docs/playground/docs/archived/infra-security-triage/plan.md
  - raw/claude-docs/playground/docs/archived/librarian-hardening/plan.md
---

# Production Hardening Patterns

Concrete fixes for common failure modes when moving from dev to production with a LangGraph CRAG pipeline. Items are priority-ranked from the actual Librarian production review.

## P0 — Blocking for Production

### Embedder Warmup on Startup

See [[Embedder Warmup]] for full detail. **Problem:** `SentenceTransformer` (multilingual-e5-large, 560MB) uses lazy loading. First request after a Fargate cold-start takes 30–60s while the model loads.

**Fix:** Call `embedder.embed_query("warmup")` in the FastAPI lifespan `init_graph()` function, immediately after `create_librarian()`. The graph holds a reference to the resolved embedder — warmup it there.

```python
# deps.py
async def init_graph():
    graph, embedder = await create_librarian(cfg)
    embedder.embed_query("warmup")  # force model load before first request
    return graph
```

**ECS requirement:** Memory default must cover the loaded model. `multilingual-e5-large` needs ~1.5GB. Set Fargate task memory to **4096 MiB** (not 1024). Health check `startPeriod` to **60s** (model loads ~45s).

---

### LangGraph Persistent Checkpointer

**Problem:** `graph.compile()` with no `checkpointer` means conversation history is lost on Fargate restart or scale event. Multi-turn state lives only in memory.

**Fix:**

```python
# config.py
checkpoint_backend: str = "sqlite"  # memory | sqlite | postgres
checkpoint_postgres_url: str = ""   # for prod Fargate

# factory.py
def _build_checkpointer(cfg):
    if cfg.checkpoint_backend == "postgres":
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
        return AsyncPostgresSaver.from_conn_string(cfg.checkpoint_postgres_url)
    if cfg.checkpoint_backend == "sqlite":
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
        return AsyncSqliteSaver.from_conn_string(cfg.duckdb_path)
    from langgraph.checkpoint.memory import MemorySaver
    return MemorySaver()
```

`MemorySaver` for local dev, SQLite for single-instance, `AsyncPostgresSaver` for multi-instance Fargate. Same thread_id → same conversation state across restarts.

---

### Anthropic API Retry/Backoff

**Problem:** No retry on transient `RateLimitError` (HTTP 429) or `APIConnectionError`. A single transient error propagates as a 500 to the user.

**Fix:** Use the Anthropic SDK's built-in `max_retries` parameter — no `tenacity` needed:

```python
client = AsyncAnthropic(max_retries=3)  # exponential backoff, capped at 30s
```

Retry on: `RateLimitError`, `APIConnectionError`, `InternalServerError`. **Do not** retry `AuthenticationError` or `BadRequestError` — those are caller errors.

---

## P1 — High Priority (Fix Before Sustained Traffic)

### Chroma Single-Writer Guard

**Problem:** `chromadb.PersistentClient` holds a process-level write lock on `.chroma/`. Two concurrent ingest workers → lock error.

**Fix:** Add an `asyncio.Lock()` to serialize concurrent upserts within a process. Document that multi-worker ingest requires `RETRIEVAL_STRATEGY=opensearch` (OpenSearch supports concurrent writes natively).

```python
_WRITE_LOCK = asyncio.Lock()

async def upsert(self, chunks):
    async with _WRITE_LOCK:
        await asyncio.to_thread(self._collection.upsert, ...)
```

---

### Escalation Signal in API Response

**Problem:** `LibrarianState` has `confident: bool`, `confidence_score: float`, and `fallback_requested: bool` — but these aren't surfaced to the API caller. The frontend has no signal to trigger human handoff.

**Fix:** Add to API response model:

```python
class ChatResponse(BaseModel):
    response: str
    citations: list[Citation]
    confidence_score: float
    confident: bool
    escalate: bool  # = not confident or fallback_requested
```

For SSE streaming, emit `escalate` as a final event after `[DONE]`.

---

## P2 — Scheduled (After P0/P1)

### Embedding Model Version Pinning

**Problem:** `SentenceTransformer("intfloat/multilingual-e5-large")` downloads the latest revision from HuggingFace on each cold start or Docker build. Silent model drift if maintainers push a new revision.

**Fix:**

```python
# config.py
embedding_model_revision: str = ""  # pin to HuggingFace commit SHA for prod
```

Pass `revision=cfg.embedding_model_revision or None` to `SentenceTransformer()`. Bake the model into the Docker image so prod never downloads at runtime:

```dockerfile
RUN python -c "from sentence_transformers import SentenceTransformer; \
    SentenceTransformer('intfloat/multilingual-e5-large')"
```

---

## Async I/O Safety

All blocking I/O in `async def` methods must be wrapped in `asyncio.to_thread()`. Failure to do so stalls the entire event loop.

### Pattern: Vector Store Backends

```python
# Chroma — collection.upsert and collection.query are blocking
await asyncio.to_thread(collection.upsert, ids=ids, ...)
candidate_count = await asyncio.to_thread(collection.count)
resp = await asyncio.to_thread(collection.query, ...)

# DuckDB — extract full connection block to sync helper
async def upsert(self, chunks):
    await asyncio.to_thread(self._upsert_sync, chunks)

def _upsert_sync(self, chunks):
    conn = self._connect()
    try: ...
    finally: conn.close()  # DuckDB single-writer lock — must close
```

### Pattern: Cross-Encoder Inference

```python
# cross_encoder.py — model.predict is CPU-bound, blocks event loop
raw_scores = await asyncio.to_thread(self._model.predict, pairs)
```

---

## SQL Injection Prevention (DuckDB)

**Problem:** DuckDB metadata filter keys were interpolated directly into SQL — `f"{col} = ?"`. A malicious caller could inject `"'; DROP TABLE rag_chunks; --"` as a key.

**Fix:** Allowlist key validation:

```python
_ALLOWED_FILTER_COLS = frozenset({
    "url", "title", "section", "doc_id", "language", "namespace", "topic", "parent_id"
})

if metadata_filter:
    bad = set(metadata_filter) - _ALLOWED_FILTER_COLS
    if bad:
        raise ValueError(f"Invalid metadata filter keys: {bad}")
```

---

## OpenSearch Hardening

Three independent issues in production OpenSearch usage:

1. **TLS verification:** `verify_certs=False` was hardcoded. Add `verify_certs: bool = True` param to `__init__`, pass to `AsyncOpenSearch`.

2. **Null embedding guard:** Silently indexing `embedding=None` causes corrupted kNN results. Add check:
   ```python
   if chunk.embedding is None:
       log.warning("opensearch.upsert.missing_embedding", chunk_id=chunk.id)
       continue
   ```

3. **Variable shadowing:** In `search()`, a `for k, v in metadata_filter.items()` loop shadowed the outer `k: int = 10` result count. Rename loop variable to `field, val`.

---

## CORS Hardening

Default `api_cors_origins: list[str] = ["*"]` allows any origin. Production deployments must set `API_CORS_ORIGINS` explicitly.

```python
# config.py — safe default forces prod to be intentional
api_cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8501"]
```

---

## Docker Frontend Packaging

**Problem:** Frontend Dockerfile reused the API image and ran `pip install streamlit` at container start — unpinned, slow, fails if PyPI is down.

**Fix:** Dedicated `Dockerfile.frontend` with multi-stage build:

```dockerfile
FROM python:3.12-slim AS builder
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --extra librarian --extra frontend

FROM python:3.12-slim
COPY --from=builder /app/.venv /app/.venv
RUN useradd -m appuser && chown -R appuser /app
USER appuser
CMD ["streamlit", "run", "frontend/librarian_chat.py", ...]
```

Requires a `[project.optional-dependencies] frontend` group in `pyproject.toml` with pinned `streamlit>=1.35,<2`.

---

## Streamlit Frontend Issues

Three common bugs in Streamlit frontends:

1. **Health check blocking:** Wrap API health check in `@st.cache_data(ttl=30)` — without caching, a blocking HTTP call fires on every keypress/widget interaction.

2. **Session state order:** Initialize `st.session_state` keys *before* any sidebar widget reads them, or Streamlit raises `KeyError`.

3. **Citation URL injection:** Validate scheme before rendering:
   ```python
   _url = c.get("url", "#")
   if not isinstance(_url, str) or not _url.startswith(("http://", "https://")):
       _url = "#"
   ```

---

## Subgraph Checkpointer Scoping (from langgraph-persistence)

When compiling a subgraph, `checkpointer` controls how state is persisted:

| Feature | `checkpointer=False` | `None` (default) | `True` |
|---|---|---|---|
| Interrupts (HITL) | No | Yes | Yes |
| Multi-turn memory | No | No | Yes |
| Multiple calls (same subgraph in parallel) | Yes | Yes | **No** (namespace conflict) |

Use `checkpointer=False` when the subgraph needs neither; `None` for interrupt support with fresh-per-call state; `True` for cross-invocation memory. See [[LangGraph State Reducers]] for the subgraph namespace isolation pattern.

---

## See Also
- [[Librarian RAG Architecture]]
- [[LangGraph CRAG Pipeline]]
- [[Librarian Project]]
- [[Observability — LangFuse vs LangSmith Decision]]
- [[LangGraph State Reducers]]
- [[Orchestration Architecture Decision]]
