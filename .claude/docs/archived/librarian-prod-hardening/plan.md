# Plan: Librarian Production Hardening

Source: engineering risks surfaced in `.claude/docs/research/librarian-vs-bedrock-kb.md`
Scope: PoC 2 (Librarian / LangGraph pipeline) — no new features, no schema changes


---


## Priority levels


- **P0** — Blocking for production. Will cause silent failures or severe UX degradation.
- **P1** — High. Causes operational pain at scale; fix before sustained traffic.
- **P2** — Medium. Technical debt with a known failure mode; schedule after P1.


---


## Step 1 ✓ DONE — 2026-04-12 — Embedder warm-up on startup `[P0]`


**Risk:** Cold start.


**Root cause:** `_load_model()` in `src/librarian/ingestion/embeddings/embedders.py:13-19` uses lazy loading — the 560MB `multilingual-e5-large` model is not loaded until the first `embed_query` call. `init_graph()` in `src/interfaces/api/deps.py:26-52` creates the graph but never calls the embedder. The first real request after a Fargate task cold-start takes 30–60s while the model loads.


**Fix:** Add an explicit warm-up call in `init_graph()` immediately after `create_librarian()`. The graph holds a reference to the resolved embedder; call `embedder.embed_query("warmup")` in the lifespan so the model is hot before the first request is served.


**Files to change:**
- `src/interfaces/api/deps.py` — call warm-up after graph construction in `init_graph()`
- `src/librarian/factory.py` — return `(graph, embedder)` from `create_librarian()` or expose embedder separately so `deps.py` can reach it, OR add a `warmup()` method to the graph/factory


**Test:** Add a test asserting that `_MODEL_CACHE` is populated after `init_graph()` completes (mock the model load, assert `_load_model` was called).


---


## Step 2 ✓ DONE — 2026-04-12 — LangGraph persistent checkpointer `[P0]`


**Risk:** Multi-turn checkpoint storage.


**Root cause:** `src/orchestration/graph.py:267` calls `graph.compile()` with no `checkpointer` argument. There is no persistent state between `ainvoke` calls — the API layer must pass the full `messages` history on every request. This works in a single process but fails silently across Fargate task restarts: the user's conversation history is lost on deploy or scale event.


**Fix:**
1. Add a `checkpointer` parameter to `build_graph()` in `src/orchestration/graph.py` — pass it to `graph.compile(checkpointer=checkpointer)`.
2. Add a `DuckDB`-backed saver for local dev (DuckDB is already a dependency — `src/storage/tracedb/duckdb.py` uses it). LangGraph ships `langgraph-checkpoint-sqlite` which is a drop-in for local; use that with the existing `duckdb_path`.
3. Add a `CHECKPOINT_BACKEND=memory|sqlite|postgres` env var to `LibrarySettings` in `src/librarian/config.py`.
4. Wire the checkpointer construction in `src/librarian/factory.py:create_librarian()`.
5. For production (ECS/Fargate), wire `AsyncPostgresSaver` using the existing Terraform RDS or a small Postgres instance. Add `CHECKPOINT_POSTGRES_URL` to `src/librarian/config.py` and `infra/terraform/secrets.tf`.


**Files to change:**
- `src/orchestration/graph.py` — `build_graph()` signature + `compile(checkpointer=...)`
- `src/librarian/config.py` — `checkpoint_backend`, `checkpoint_postgres_url`
- `src/librarian/factory.py` — `_build_checkpointer(cfg)` helper + wire in `create_librarian()`
- `infra/terraform/secrets.tf` — `CHECKPOINT_POSTGRES_URL` secret (prod only)


**Test:** Integration test: invoke graph with a message, then invoke again in a new graph instance using the same `thread_id` — assert the second call has access to the first turn's `messages`.


---


## Step 3 ✓ DONE — 2026-04-12 — Anthropic API retry / backoff `[P0]`


**Risk:** Rate limiting / throttling.


**Root cause:** `src/core/clients/llm.py:69-86` `generate()` and `src/core/clients/llm.py:118-135` `stream()` have no retry logic. A transient `anthropic.RateLimitError` (HTTP 429) or `anthropic.APIConnectionError` propagates directly to the user as a 500. At moderate query volume, transient rate limits are a near-certainty.


**Fix:** Wrap the API calls in `AnthropicLLM.generate()`, `generate_sync()`, and `stream()` with `tenacity` retry:
- Retry on: `anthropic.RateLimitError`, `anthropic.APIConnectionError`, `anthropic.InternalServerError`
- Strategy: exponential backoff, base 1s, max 3 attempts, cap at 30s
- Log each retry as `llm.retry` with attempt count and exception type
- Do NOT retry on `anthropic.AuthenticationError` or `anthropic.BadRequestError` — those are caller errors


`tenacity` is not in the current deps; add it. Alternatively, use the Anthropic SDK's built-in `max_retries` parameter on `AsyncAnthropic(max_retries=3)` — this is simpler and already supported by the SDK.


**Files to change:**
- `src/core/clients/llm.py` — pass `max_retries=3` to both `AsyncAnthropic` and `Anthropic` constructors
- `pyproject.toml` — no change needed (SDK retry is built-in)


**Test:** Mock `AsyncAnthropic.messages.create` to raise `RateLimitError` twice then succeed; assert the response is returned and the retry count is logged.


---


## Step 4 ✓ DONE — 2026-04-12 — Chroma single-writer guard `[P1]`


**Risk:** Ingest concurrency / Chroma write lock.


**Root cause:** `src/storage/vectordb/chroma.py` uses `chromadb.PersistentClient` which holds a process-level write lock on `.chroma/`. If two processes write simultaneously (e.g., parallel ingest workers or an ingest triggered during a running API server), the second writer will get a lock error. The `ChunkIndexer.index_documents()` loop in `src/librarian/ingestion/indexing/indexer.py:97-106` is sequential within a single process but callers could spawn parallel processes.


**Fix — two parts:**
1. **Runtime guard:** In `ChromaRetriever._get_collection()` (`src/storage/vectordb/chroma.py:58-69`), log a `chroma.singlewriter.warning` when `upsert` is called if `RETRIEVAL_STRATEGY=chroma`. Add a comment in `create_ingestion_pipeline()` (`src/librarian/factory.py:223`) documenting the single-writer constraint.
2. **Prod path:** Document in `LibrarySettings` that `retrieval_strategy=opensearch` is required for multi-worker ingest. The OpenSearch retriever is already implemented at `src/storage/vectordb/opensearch.py` — this is a config change, not a code change, for prod.


**Files to change:**
- `src/storage/vectordb/chroma.py` — add warning log on upsert when multiple concurrent upserts are detected (use a module-level `_WRITE_LOCK = asyncio.Lock()` to serialize within a process)
- `src/librarian/factory.py` — docstring note on single-writer constraint for Chroma
- `src/librarian/config.py` — add comment on `retrieval_strategy` documenting multi-worker requirement


**Test:** Confirm that two concurrent `await chroma_retriever.upsert(...)` calls in the same process do not race (they should be serialized by the asyncio lock).


---


## Step 5 ✓ DONE — 2026-04-12 — Surface escalation signal in API response `[P1]`


**Risk:** Escalation path (product risk, but the fix is in the API layer).


**Root cause:** `src/librarian/schemas/state.py:38-40` already has `confident: bool`, `confidence_score: float`, and `fallback_requested: bool` in `LibrarianState`. These are computed and stored in state but not returned to the API caller — the response model only exposes `response` and `citations`. The frontend has no signal to trigger human handoff.


**Fix:** Add `confidence_score: float`, `confident: bool`, and `escalate: bool` to the API response model. `escalate = not confident or fallback_requested`. The frontend can render an escalation CTA (e.g., "Connect to support") when `escalate=True`.


**Files to change:**
- `src/interfaces/api/models.py` — add `confidence_score`, `confident`, `escalate` to the chat response model
- `src/interfaces/api/routes.py` — extract these fields from graph state and include in response
- `src/interfaces/api/streaming.py` — emit `escalate` signal as a final SSE event (after `[DONE]`) for the streaming path


**Test:** Assert that when `confidence_score < confidence_threshold`, the API response includes `escalate: true`.


---


## Step 6 ✓ DONE — 2026-04-12 — Embedding model version pinning `[P2]`


**Risk:** Model drift (embedder).


**Root cause:** `src/librarian/config.py:36` sets `embedding_model: str = "intfloat/multilingual-e5-large"` — no revision pinned. `SentenceTransformer(model_name)` in `src/librarian/ingestion/embeddings/embedders.py:18` downloads from HuggingFace at runtime if not locally cached. If the model maintainer pushes a new revision, the downloaded model silently changes on next cold-start or Docker build.


**Fix:** Pin the model revision in `LibrarySettings`:
```python
embedding_model: str = "intfloat/multilingual-e5-large"
embedding_model_revision: str = ""  # HuggingFace commit SHA — pin for reproducibility
```


Pass `revision=cfg.embedding_model_revision or None` to `SentenceTransformer()`. Bake the model into the Docker image (add a `RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('intfloat/multilingual-e5-large')"` layer to `infra/docker/Dockerfile`) so prod never downloads at runtime. This also eliminates the HuggingFace network dependency at query time.


**Files to change:**
- `src/librarian/config.py` — `embedding_model_revision` field
- `src/librarian/ingestion/embeddings/embedders.py` — pass `revision` to `SentenceTransformer()`
- `infra/docker/Dockerfile` — pre-bake model into image


**Test:** Assert that `SentenceTransformer` is called with the pinned revision when `embedding_model_revision` is set.


---


## Step 7 ✓ DONE — 2026-04-12 — Architecture decision record `[P2]`


**Risk:** Bus factor / knowledge risk.


**Root cause:** The graph topology, CRAG loop logic, confidence gating, and DI wiring are non-obvious to someone new. `graph.py` and `factory.py` have good docstrings but there is no single document mapping the system's moving parts to their rationale.


**Fix:** Write `src/librarian/ARCHITECTURE.md` covering:
1. State machine diagram: `condense → analyze → [retrieve → rerank → gate] ↺ → generate`
2. CRAG loop: when it fires, what it rewrites, what `max_crag_retries` controls
3. Confidence gating: how `confidence_score` is computed (reranker max logit → sigmoid), what the threshold means
4. DI wiring: `factory.py` is the single assembly point — all component swap points and their env vars
5. Key invariants: E5 prefix rule, Chroma single-writer, embedder lazy load
6. Checkpointer model: how `thread_id` maps to conversation state


This is documentation only — no code changes.


---


## Execution order


| Step | Risk addressed | Priority | Effort | Files changed |
|---|---|---|---|---|
| 1. Embedder warm-up | Cold start | P0 | Small | `deps.py`, `factory.py` |
| 2. LangGraph checkpointer | Multi-turn state loss | P0 | Medium | `graph.py`, `config.py`, `factory.py`, `secrets.tf` |
| 3. API retry/backoff | Anthropic rate limits | P0 | Small | `llm.py` |
| 4. Chroma write guard | Ingest concurrency | P1 | Small | `chroma.py`, `factory.py` |
| 5. Escalation signal | No human handoff path | P1 | Small | `models.py`, `routes.py`, `streaming.py` |
| 6. Model version pinning | Embedder drift | P2 | Small | `config.py`, `embedders.py`, `Dockerfile` |
| 7. Architecture ADR | Bus factor | P2 | Docs only | `ARCHITECTURE.md` |


Steps 1 and 3 are independent and can execute in parallel.
Step 2 depends on nothing but is the largest change — do it in isolation.
Steps 4, 5, 6, 7 can be taken in any order after the P0s are merged.
