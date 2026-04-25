# Plan: Retrieval Pipeline Productionize
Date: 2026-04-11
Based on: direct codebase inspection (code review session 2026-04-11)

## Goal
Fix all correctness bugs, async I/O hazards, and factory dispatch gaps in the
`src/librarian` retrieval pipeline to make every component truly swappable via config
and safe under concurrent production load.

## Approach
Two phases with a review gate between them. Phase 1 is pure bug fixes — nothing
architecturally changes, it just works correctly. Phase 2 completes the modularity
promises that are already implied by the config fields but not yet wired. Each step is
independent of the others within its phase except where noted.

## Out of Scope
- Infra fixes (separate `triage_infra_security_fixes` plan)
- Adding new retrieval strategies (GraphRAG, ColBERT, etc.)
- Evaluation harness refactoring
- RRF parameter tuning or retrieval quality improvements
- Test coverage for `ChromaRetriever`, `DuckDBRetriever`, `OpenSearchRetriever`
  (noted as gap but adding integration tests requires Docker — separate task)

---

## Phase 1: Correctness + Async Safety
*Steps 1–7. Fix before any production deploy. Steps 3–7 are independent of each other
and can be executed in parallel.*

---

### Step 1: ✅ Fix broken import paths in `analyzer.py` and `routing.py`
**Files**: `src/librarian/pipeline/plan/analyzer.py` (lines 8–12),
`src/librarian/pipeline/plan/routing.py` (line 10)

**What**: All five imports in `analyzer.py` use `agents.librarian.plan.*` — missing the
`pipeline` segment. There is no `agents.librarian.plan` package; the actual location is
`agents.librarian.pipeline.plan.*`. Any code path that instantiates `QueryAnalyzer`
(which is every query through the graph) raises `ModuleNotFoundError` at runtime.
`routing.py:10` has the same wrong path under `TYPE_CHECKING` (safe at runtime, breaks
mypy/pyright).

**Snippet** — `analyzer.py:8-12`:
```python
# before
from agents.librarian.plan.decomposition import decompose_query
from agents.librarian.plan.entities import extract_entities
from agents.librarian.plan.expansion import expand_terms
from agents.librarian.plan.intent import classify_intent
from agents.librarian.plan.routing import select_retrieval_mode

# after
from agents.librarian.pipeline.plan.decomposition import decompose_query
from agents.librarian.pipeline.plan.entities import extract_entities
from agents.librarian.pipeline.plan.expansion import expand_terms
from agents.librarian.pipeline.plan.intent import classify_intent
from agents.librarian.pipeline.plan.routing import select_retrieval_mode
```

**Snippet** — `routing.py:10`:
```python
# before
    from agents.librarian.plan.analyzer import QueryAnalysis

# after
    from agents.librarian.pipeline.plan.analyzer import QueryAnalysis
```

**Test**: `uv run pytest tests/librarian/unit/test_query_understanding.py tests/librarian/unit/test_graph.py -v`
**Done when**: Both test modules collect and pass without `ModuleNotFoundError`.

---

### Step 2: ✅ Fix `_embed_variant` sync result discard in `RetrievalSubgraph`
**Files**: `src/librarian/orchestration/nodes/retrieval.py` (lines 96–102)

**What**: When `aembed_query` is a sync method (not a coroutine), the function calls it,
gets a result, checks `inspect.isawaitable(result)` → False, then falls through to
`asyncio.to_thread(self._embedder.embed_query, variant)` without returning. The first
embedding is silently discarded and computed a second time, blocking the event loop in
the process.

**Snippet** — `retrieval.py:96-102`:
```python
# before
        async def _embed_variant(variant: str) -> list[float]:
            aembed_query = getattr(self._embedder, "aembed_query", None)
            if callable(aembed_query):
                result = aembed_query(variant)
                if inspect.isawaitable(result):
                    return await result
            return await asyncio.to_thread(self._embedder.embed_query, variant)

# after
        async def _embed_variant(variant: str) -> list[float]:
            aembed_query = getattr(self._embedder, "aembed_query", None)
            if callable(aembed_query):
                result = aembed_query(variant)
                if inspect.isawaitable(result):
                    return await result
                return result  # sync aembed_query — use result directly
            return await asyncio.to_thread(self._embedder.embed_query, variant)
```

**Test**: `uv run pytest tests/librarian/unit/test_retrieval_subgraph.py -v`
**Done when**: Tests pass; adding a mock sync `aembed_query` to the test embedder no
longer causes a second `embed_query` call.

---

### Step 3: ✅ Fix OpenSearch — variable shadowing, null embedding guard, verify_certs
**Files**: `src/librarian/tools/storage/vectordb/opensearch.py`
(lines 44–46, 49–66, 96–104)

**What**: Three independent issues in this file:

**3a** — `verify_certs=False` (line 44) is hardcoded, disabling TLS validation in all
environments including production.

**3b** — `upsert` (lines 49–66) silently indexes chunks with `embedding=None`. OpenSearch
stores the null vector; kNN queries then silently return corrupted results. The other two
backends (Chroma, DuckDB) already guard against this.

**3c** — In `search` (line 99), the dict comprehension `for k, v in metadata_filter.items()`
shadows the outer parameter `k: int = 10`. The `"size": k` on line 104 is evaluated
after the loop and receives the last string key from `metadata_filter` instead of the
integer result count.

**Snippet** — 3a, `opensearch.py:37-47` (`_get_client`):
```python
# before
        self._client = AsyncOpenSearch(
            hosts=[settings.opensearch_url],
            http_auth=(settings.opensearch_user, settings.opensearch_password),
            use_ssl=settings.opensearch_url.startswith("https"),
            verify_certs=False,
        )

# after
        self._client = AsyncOpenSearch(
            hosts=[settings.opensearch_url],
            http_auth=(settings.opensearch_user, settings.opensearch_password),
            use_ssl=settings.opensearch_url.startswith("https"),
            verify_certs=self.verify_certs,
        )
```

Add `verify_certs: bool = True` to `__init__` parameters (after `vector_weight`):
```python
# before
    def __init__(
        self,
        index: str | None = None,
        bm25_weight: float = 0.3,
        vector_weight: float = 0.7,
    ) -> None:

# after
    def __init__(
        self,
        index: str | None = None,
        bm25_weight: float = 0.3,
        vector_weight: float = 0.7,
        verify_certs: bool = True,
    ) -> None:
```
Store `self.verify_certs = verify_certs` in `__init__`.

**Snippet** — 3b, `opensearch.py:49-66` (`upsert`), add null-embedding guard after line 52:
```python
# before
        for chunk in chunks:
            actions.append({"index": {"_index": self.index, "_id": chunk.id}})
            actions.append(...)

# after
        for chunk in chunks:
            if chunk.embedding is None:
                log.warning("opensearch.upsert.missing_embedding", chunk_id=chunk.id)
                continue
            actions.append({"index": {"_index": self.index, "_id": chunk.id}})
            actions.append(...)
```

**Snippet** — 3c, `opensearch.py:97-104` (rename loop variable):
```python
# before
        if metadata_filter:
            query["bool"]["filter"] = [
                {"term": {f"metadata.{k}": v}} for k, v in metadata_filter.items()
            ]

        resp = await client.search(
            index=self.index,
            body={"query": query, "size": k},
        )

# after
        if metadata_filter:
            query["bool"]["filter"] = [
                {"term": {f"metadata.{field}": val}}
                for field, val in metadata_filter.items()
            ]

        resp = await client.search(
            index=self.index,
            body={"query": query, "size": k},
        )
```

**Test**: `uv run pytest tests/librarian/unit/test_storage.py -v -k opensearch`
**Done when**: Tests pass; `upsert` with a `None`-embedding chunk logs a warning and
skips; `search` with a `metadata_filter` passes the correct integer `k` as `"size"`.

---

### Step 4: ✅ Fix DuckDB — dead `params` variable and SQL injection
**Files**: `src/librarian/tools/storage/vectordb/duckdb.py` (lines 164–183)

**What**: Two issues in `search`:

**4a** — `params` (line 165) is built but never used. The `conn.execute()` call on
line 183 constructs a different inline parameter list
`[query_vector] + list((metadata_filter or {}).values()) + [k * 3]`. The dead variable
creates a maintenance trap: if someone edits `params` thinking it's the one being used,
the query silently receives wrong values.

**4b** — Metadata filter column names are interpolated directly into the SQL as
`f"{col} = ?"`. A caller passing `{"'; DROP TABLE rag_chunks; --": "x"}` produces
destructive SQL. Fix: validate each key against the known `ChunkMetadata` field names.

**Snippet** — `duckdb.py:164-183`:
```python
# before
            where_clause = ""
            params: list[Any] = [query_vector, k * 3]

            if metadata_filter:
                conditions = [f"{col} = ?" for col in metadata_filter]
                where_clause = " AND " + " AND ".join(conditions)
                params.extend(metadata_filter.values())

            rows = conn.execute(
                f"""
                SELECT chunk_id, text, url, title, section, doc_id,
                       language, namespace, topic, parent_id,
                       array_cosine_similarity(embedding, ?::FLOAT[{self._embedding_dims}]) AS vec_score
                FROM {self._table_name}
                WHERE embedding IS NOT NULL
                {where_clause}
                ORDER BY vec_score DESC
                LIMIT ?
                """,
                [query_vector] + list((metadata_filter or {}).values()) + [k * 3],
            ).fetchall()

# after
            # Allowlist prevents SQL injection via metadata filter key names.
            _ALLOWED_FILTER_COLS = frozenset(
                {"url", "title", "section", "doc_id", "language", "namespace", "topic", "parent_id"}
            )
            where_clause = ""
            filter_values: list[Any] = []

            if metadata_filter:
                bad = set(metadata_filter) - _ALLOWED_FILTER_COLS
                if bad:
                    raise ValueError(f"Invalid metadata filter keys: {bad}")
                conditions = [f"{col} = ?" for col in metadata_filter]
                where_clause = " AND " + " AND ".join(conditions)
                filter_values = list(metadata_filter.values())

            rows = conn.execute(
                f"""
                SELECT chunk_id, text, url, title, section, doc_id,
                       language, namespace, topic, parent_id,
                       array_cosine_similarity(embedding, ?::FLOAT[{self._embedding_dims}]) AS vec_score
                FROM {self._table_name}
                WHERE embedding IS NOT NULL
                {where_clause}
                ORDER BY vec_score DESC
                LIMIT ?
                """,
                [query_vector] + filter_values + [k * 3],
            ).fetchall()
```

**Test**: `uv run pytest tests/librarian/unit/test_storage.py -v -k duckdb`
Also add inline assertion: `pytest -k "duckdb and filter"` with a fixture that passes
`{"'; DROP TABLE": "x"}` and expects `ValueError`.
**Done when**: Tests pass; `search` with an invalid filter key raises `ValueError`;
`search` with valid filter keys produces correct SQL and results.

---

### Step 5: ✅ Wrap blocking Chroma I/O in `asyncio.to_thread`
**Files**: `src/librarian/tools/storage/vectordb/chroma.py` (lines 70–95, 97–145)

**What**: Both `upsert` and `search` are `async def` but call blocking Chroma APIs
(`collection.upsert`, `collection.query`, `collection.count`) directly on the event loop.
Under concurrency (multiple simultaneous requests) this stalls all other coroutines for
the duration of each Chroma round-trip.

**Snippet** — `chroma.py:70-95` (`upsert`), replace the blocking collection call:
```python
# before
        if ids:
            collection.upsert(
                ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas
            )
            log.info("chroma.upsert.done", n=len(ids), collection=self._collection_name)

# after
        if ids:
            await asyncio.to_thread(
                collection.upsert,
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )
            log.info("chroma.upsert.done", n=len(ids), collection=self._collection_name)
```

**Snippet** — `chroma.py:112-118` (`search`), wrap `count` and `query`:
```python
# before
        candidate_count = max(1, collection.count())
        resp = collection.query(
            query_embeddings=[query_vector],
            n_results=min(max(k * 3, k), candidate_count),
            where=where,
            include=["documents", "metadatas", "distances"],
        )

# after
        candidate_count = max(1, await asyncio.to_thread(collection.count))
        resp = await asyncio.to_thread(
            collection.query,
            query_embeddings=[query_vector],
            n_results=min(k * 3, candidate_count),
            where=where,
            include=["documents", "metadatas", "distances"],
        )
```
Note: `min(max(k * 3, k), ...)` simplifies to `min(k * 3, ...)` since `k > 0` always.
Add `import asyncio` at the top if not already present.

**Test**: `uv run pytest tests/librarian/unit/test_storage.py -v -k chroma`
**Done when**: Tests pass; blocking calls no longer execute on the event loop thread
(verifiable with `asyncio.get_event_loop().run_in_executor` mock in tests).

---

### Step 6: ✅ Wrap blocking DuckDB I/O in `asyncio.to_thread`
**Files**: `src/librarian/tools/storage/vectordb/duckdb.py` (lines 91–137, 139–234),
`src/librarian/pipeline/retrieval/snippet.py` (line 36)

**What**: `DuckDBRetriever.upsert` and `DuckDBRetriever.search` open connections and
execute queries synchronously inside `async def` methods. `SnippetRetriever.search`
also calls `self._db.search_snippets` synchronously. All three block the event loop
on every call.

The cleanest fix is to wrap the entire connection-scoped block in `asyncio.to_thread`
since `duckdb` connections are not thread-safe and must not be shared across threads
anyway.

**Snippet** — `duckdb.py` (`upsert`), replace the connection block:
```python
# before
    async def upsert(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return

        conn = self._connect()
        try:
            self._ensure_table(conn)
            ...
        finally:
            conn.close()

# after
    async def upsert(self, chunks: list[Chunk]) -> None:
        if not chunks:
            return
        await asyncio.to_thread(self._upsert_sync, chunks)

    def _upsert_sync(self, chunks: list[Chunk]) -> None:
        conn = self._connect()
        try:
            self._ensure_table(conn)
            ...  # (identical body, no changes inside)
        finally:
            conn.close()
```

Apply the same extraction for `search`:
```python
    async def search(self, ...) -> list[RetrievalResult]:
        return await asyncio.to_thread(self._search_sync, query_text, query_vector, k, metadata_filter)

    def _search_sync(self, ...) -> list[RetrievalResult]:
        conn = self._connect()
        try:
            ...  # (identical body from Step 4 after the SQL injection fix)
        finally:
            conn.close()
```

**Snippet** — `snippet.py:36`:
```python
# before
        rows = self._db.search_snippets(query_text, k=k)

# after
        rows = await asyncio.to_thread(self._db.search_snippets, query_text, k=k)
```
Add `import asyncio` if not already present.

**Test**: `uv run pytest tests/librarian/unit/test_storage.py tests/librarian/unit/test_retrieval.py -v`
**Done when**: Tests pass; `upsert` and `search` no longer block the event loop.

---

### Step 7: ✅ Wrap blocking cross-encoder in `asyncio.to_thread`
**Files**: `src/librarian/pipeline/reranker/cross_encoder.py` (line 49)

**What**: `self._model.predict(pairs)` is a CPU-bound call on a sentence-transformers
cross-encoder. It is called directly in an `async def rerank` method, blocking the
entire event loop for the duration of inference (hundreds of ms on CPU).

**Snippet** — `cross_encoder.py:49`:
```python
# before
        raw_scores = self._model.predict(pairs)

# after
        raw_scores = await asyncio.to_thread(self._model.predict, pairs)
```
Add `import asyncio` at the top if not already present.

**Test**: `uv run pytest tests/librarian/unit/test_reranker.py -v`
**Done when**: Tests pass; `rerank` no longer blocks the event loop on inference.

---

## ← REVIEW GATE — run `/plan-review review` before Phase 2 →

---

## Phase 2: Factory Completion + Config Hardening
*Steps 8–11. These complete the modularity promises already implied by the config.
Each step is independent.*

---

### Step 8: ✅ Forward `bm25_weight`/`vector_weight` from settings to retriever constructors
**Files**: `src/librarian/factory.py` (lines 59–81)

**What**: `LibrarySettings` exposes `bm25_weight = 0.3` and `vector_weight = 0.7` but
`_build_retriever` never passes them to `ChromaRetriever` or `DuckDBRetriever`. Both
backends use their own module-level `_BM25_WEIGHT = 0.3` constants. Changing the weights
via env var has no effect — the setting is silently ignored.

**Snippet** — `factory.py:_build_retriever`, update Chroma and DuckDB branches:
```python
# before (chroma branch)
    from agents.librarian.tools.storage.vectordb.chroma import ChromaRetriever
    return ChromaRetriever(
        persist_dir=cfg.chroma_persist_dir,
        collection_name=cfg.chroma_collection,
    )

# after
    from agents.librarian.tools.storage.vectordb.chroma import ChromaRetriever
    return ChromaRetriever(
        persist_dir=cfg.chroma_persist_dir,
        collection_name=cfg.chroma_collection,
        bm25_weight=cfg.bm25_weight,
        vector_weight=cfg.vector_weight,
    )
```

```python
# before (duckdb branch)
    from agents.librarian.tools.storage.vectordb.duckdb import DuckDBRetriever
    return DuckDBRetriever(db_path=cfg.duckdb_path)

# after
    from agents.librarian.tools.storage.vectordb.duckdb import DuckDBRetriever
    return DuckDBRetriever(
        db_path=cfg.duckdb_path,
        bm25_weight=cfg.bm25_weight,
        vector_weight=cfg.vector_weight,
    )
```

Also update `_build_retriever` for `opensearch` branch to pass weights and
`verify_certs` (added in Step 3):
```python
# before
    return OpenSearchRetriever(index=cfg.opensearch_index)

# after
    return OpenSearchRetriever(
        index=cfg.opensearch_index,
        bm25_weight=cfg.bm25_weight,
        vector_weight=cfg.vector_weight,
    )
```

**Test**: `uv run pytest tests/librarian/unit/test_factory.py -v`
**Done when**: `create_librarian(cfg=LibrarySettings(bm25_weight=0.5, vector_weight=0.5))`
passes the custom weights to the underlying retriever instance.

---

### Step 9: ✅ Add embedder strategy dispatch to `_build_embedder`
**Files**: `src/librarian/factory.py` (lines 53–56),
`src/librarian/utils/config.py` (lines 39)

**What**: `_build_embedder` always returns `MultilingualEmbedder` regardless of config.
The `embedding_model` field only sets the model name but there is no way to swap the
embedder class (e.g. to an OpenAI or Cohere embedder) via config alone — you must pass
an override at construction time. Add an `embedding_provider` config field
(`"local"` | `"openai"` | `"cohere"`) and dispatch on it so the factory is fully
config-driven.

**Snippet** — `config.py` (add after `embedding_model`):
```python
# before
    embedding_model: str = "intfloat/multilingual-e5-large"

# after
    embedding_model: str = "intfloat/multilingual-e5-large"
    embedding_provider: str = "local"  # local | openai | cohere
```

**Snippet** — `factory.py:_build_embedder`:
```python
# before
def _build_embedder(cfg: LibrarySettings) -> Embedder:
    from agents.librarian.pipeline.ingestion.embeddings.embedders import MultilingualEmbedder
    return MultilingualEmbedder(model_name=cfg.embedding_model)

# after
def _build_embedder(cfg: LibrarySettings) -> Embedder:
    if cfg.embedding_provider == "openai":
        from agents.librarian.pipeline.ingestion.embeddings.embedders import OpenAIEmbedder
        return OpenAIEmbedder(model=cfg.embedding_model)

    if cfg.embedding_provider == "cohere":
        from agents.librarian.pipeline.ingestion.embeddings.embedders import CohereEmbedder
        return CohereEmbedder(model=cfg.embedding_model)

    # Default: local HuggingFace (multilingual-e5-large)
    from agents.librarian.pipeline.ingestion.embeddings.embedders import MultilingualEmbedder
    return MultilingualEmbedder(model_name=cfg.embedding_model)
```

Note: `OpenAIEmbedder` and `CohereEmbedder` classes need to be added to `embedders.py`
if they don't exist. Check `src/librarian/pipeline/ingestion/embeddings/embedders.py`
first — if absent, this step is a **blocker** until those classes are implemented or
the plan is scoped to `local` only.

**Test**: `uv run pytest tests/librarian/unit/test_factory.py -v`
**Done when**: `create_librarian(cfg=LibrarySettings(embedding_provider="local"))` works;
`embedding_provider="unknown"` falls through to `MultilingualEmbedder` (default).

---

### Step 10: ✅ Wire `ingestion_strategy` in `create_ingestion_pipeline`
**Files**: `src/librarian/factory.py` (lines 185–222)

**What**: `LibrarySettings.ingestion_strategy` is documented as `"html_aware"` but
`create_ingestion_pipeline` always constructs `HtmlAwareChunker()` regardless of what
the config says. The following chunkers already exist in `pipeline/ingestion/chunking/`:
`FixedChunker`, `OverlappingChunker`, `StructuredChunker`, `HtmlAwareChunker`,
`AdjacencyChunker`, `ParentDocChunker`. Wire them via a dispatch.

**Snippet** — `factory.py:create_ingestion_pipeline`, replace the hardcoded chunker:
```python
# before
    from agents.librarian.pipeline.ingestion.chunking.html_aware import HtmlAwareChunker
    ...
    resolved_chunker = chunker or HtmlAwareChunker()

# after
    resolved_chunker = chunker or _build_chunker(cfg)
```

Add `_build_chunker` helper before `create_ingestion_pipeline`:
```python
def _build_chunker(cfg: LibrarySettings) -> Chunker:
    from agents.librarian.pipeline.ingestion.chunking.strategies import (
        FixedChunker,
        OverlappingChunker,
        StructuredChunker,
        AdjacencyChunker,
    )
    from agents.librarian.pipeline.ingestion.chunking.html_aware import HtmlAwareChunker
    from agents.librarian.pipeline.ingestion.chunking.parent_doc import ParentDocChunker

    dispatch = {
        "fixed": FixedChunker,
        "overlapping": OverlappingChunker,
        "structured": StructuredChunker,
        "adjacency": AdjacencyChunker,
        "parent_doc": ParentDocChunker,
        "html_aware": HtmlAwareChunker,
    }
    cls = dispatch.get(cfg.ingestion_strategy, HtmlAwareChunker)
    return cls()
```

**Test**: `uv run pytest tests/librarian/unit/test_ingestion.py -v`
**Done when**: `create_ingestion_pipeline(cfg=LibrarySettings(ingestion_strategy="fixed"))`
returns a pipeline wrapping `FixedChunker`; unknown strategy falls back to `HtmlAwareChunker`.

---

### Step 11: ✅ Harden API CORS origins default
**Files**: `src/librarian/utils/config.py` (line 64)

**What**: `api_cors_origins: list[str] = ["*"]` allows any origin in production.
Change the default to `["http://localhost:3000", "http://localhost:8501"]` (local dev
surfaces) so production deployments must explicitly set `API_CORS_ORIGINS` in the
environment. The FastAPI CORS middleware already reads this field.

**Snippet** — `config.py:64`:
```python
# before
    api_cors_origins: list[str] = ["*"]

# after
    api_cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8501"]
    # Override via API_CORS_ORIGINS env var for staging/prod (comma-separated or JSON list)
```

**Test**: `uv run pytest tests/librarian/unit/test_api.py -v`
Also verify: `LibrarySettings().api_cors_origins` == `["http://localhost:3000", "http://localhost:8501"]`.
**Done when**: Tests pass; a fresh `LibrarySettings()` no longer has `["*"]`.

---

## Test Plan
1. After Step 1: `uv run pytest tests/librarian/unit/ -v --tb=short` — this should
   unblock most of the unit test suite
2. After each subsequent step: run the targeted test command listed in the step
3. After all Phase 1 steps: `uv run pytest tests/librarian/unit/ -v` — full unit suite
4. After all Phase 2 steps: `uv run pytest tests/librarian/ -v` — unit + eval suite

## Risks & Rollback
- **Step 6 (DuckDB sync extraction)**: The `_upsert_sync` / `_search_sync` refactor
  must preserve the `finally: conn.close()` pattern exactly — DuckDB single-writer lock
  means a leaked connection will deadlock subsequent calls. Rollback: revert to original
  async body with the Step 4 SQL fix retained.
- **Step 9 (embedder dispatch)**: `OpenAIEmbedder` and `CohereEmbedder` may not exist in
  `embedders.py`. Check before implementing — if absent, implement local-only dispatch
  first and file a follow-up for the cloud providers.
- **Step 11 (CORS)**: Any existing deployment using the wildcard default will break until
  `API_CORS_ORIGINS` is set in its environment. Communicate before deploying.

## Open Questions
1. Do `OpenAIEmbedder` and `CohereEmbedder` exist in `embedders.py`? If not, Step 9
   should be scoped to only the `local` provider for now.
2. Is `ParentDocChunker` in `chunking/parent_doc.py`? The file listing shows it but
   verify the class name before Step 10.
3. Should `embedding_provider` accept a custom class path (e.g. `"mypackage.MyEmbedder"`)
   for plugin-style extensibility, or is a fixed enum sufficient for now?
