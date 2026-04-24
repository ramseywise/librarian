# Plan: Phase 5a — RAG Core Adaptation
Date: 2026-04-06 (revised)
Predecessor: Phase 4b (memory) — DONE
Next: Phase 5b (intent routing + query understanding)

---

## Context & What Exists

`rag_core/` was built for a **Danish customer support assistant** using OpenSearch.
Key differences from listen-wiseer:

| Aspect | Current (help-assistant) | Target (listen-wiseer) |
|--------|--------------------------|------------------------|
| Vector store | OpenSearch (async, knn_vector) | **DuckDB vss** (`rag_chunks` table in `listen_wiseer.db`) |
| Embedder | `multilingual-e5-large` (1024-dim, E5 prefix) | `all-MiniLM-L6-v2` (384-dim, already in settings) |
| Data source | Scraped HTML docs | Wikipedia + Tavily (on-demand fetch, Tavily optional) |
| Language | Danish prompts + intents | English |
| Intent enum | HOW_TO / TROUBLESHOOT / REFERENCE / CHIT_CHAT / OUT_OF_SCOPE | ARTIST_INFO / GENRE_INFO / HISTORY / CHIT_CHAT / OUT_OF_SCOPE |
| Reranker | Stub (NotImplementedError) | Stub OK for now |

**Goal**: Adapt `rag_core/` for listen-wiseer — swap retrieval backend to DuckDB vss
(same DB file, new `rag_chunks` table), adapt embedder, add music intents, rewrite
prompts in English for music context, and expose a `get_artist_context` tool to the agent.
Keep the Registry pattern and modular chunker strategies — these are correct and reusable.

**Why DuckDB vss over ChromaDB/Weaviate/OpenSearch**:
- Zero new dependencies — DuckDB 1.5.0 already installed, `vss` extension loads at runtime
- Same `listen_wiseer.db` file — no separate `data/vectorstore/` directory
- Consistent connection patterns with existing `etl/db.py` (`get_connection`, `init_schema`)
- `track_embeddings` already stores `DOUBLE[64]` arrays — proven pattern
- `array_cosine_similarity()` for brute-force, HNSW index when scale warrants it
- For our scale (<10k chunks), brute-force cosine is fast enough — skip HNSW for now

**Production principle**: The agent tool calls a thin orchestrator
(`src/rag_core/orchestration/music_rag.py`) that wires the modules directly —
no full LangGraph sub-graph overhead for a single tool call.
The existing `graph.py` pipeline is useful for notebooks and eval harness, not production.

---

## Out of Scope

- Spotify `/recommendations` API — Phase 6
- Long-term memory changes — Phase 4b (done)
- Eval harness — Phase 5c
- Reranker implementation (Cohere / cross-encoder) — deferred, stub is fine
- HNSW index on `rag_chunks` — add later if >10k chunks
- `query_understanding.py` adaptation (Danish → English music-domain) — deferred to Phase 5b (intent routing). Production path (`MusicRAG`) does not use `QueryAnalyzer`; it's only used by the eval/notebook `graph.py` pipeline

---

## Steps

### Step 1: Add `rag_chunks` table to DuckDB schema + DuckDBVectorClient ✓ DONE — 2026-04-06

**Files**:
- `src/etl/db.py` (add `rag_chunks` table to `_DDL`)
- `src/rag_core/retrieval/duckdb_client.py` (new)
- `src/rag_core/registry.py` (replace OpenSearch registration with DuckDB)
- `tests/unit/rag/test_duckdb_client.py` (new)

**What**: Add a `rag_chunks` table to the existing schema, following the same
`CREATE TABLE IF NOT EXISTS` pattern. Implement `DuckDBVectorClient` that uses
`array_cosine_similarity()` for search and standard INSERT/UPDATE for upsert.
Uses the existing `get_connection()` from `etl.db`.

**Schema addition** (`etl/db.py` — append to `_DDL`):
```sql
-- RAG chunks for artist/genre context (Phase 5a)
-- Embeddings are 384-dim float arrays from all-MiniLM-L6-v2
CREATE TABLE IF NOT EXISTS rag_chunks (
    chunk_id    VARCHAR PRIMARY KEY,
    subject     VARCHAR NOT NULL,  -- normalized: lower(strip(artist_name))
    section     VARCHAR DEFAULT 'bio',
    source_url  VARCHAR DEFAULT '',
    text        VARCHAR NOT NULL,
    embedding   FLOAT[384],
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Note: `array_cosine_similarity` is a core DuckDB function (since v0.10), NOT part of the
vss extension. We do NOT need `INSTALL vss` / `LOAD vss` for brute-force cosine search.
The vss extension is only needed for HNSW indexes, which we're deferring.

**Client snippet** (`src/rag_core/retrieval/duckdb_client.py`):
```python
class DuckDBVectorClient:
    """DuckDB retrieval backend — stores chunks in rag_chunks table.

    Uses array_cosine_similarity (core DuckDB function) for brute-force cosine search.
    Shares listen_wiseer.db with the rest of the app via etl.db.get_connection.
    No vss extension needed at this scale (<10k chunks).
    """

    def __init__(self) -> None:
        self._conn = get_connection(read_only=False)

    def search(
        self,
        query_vector: list[float],
        k: int = 5,
        subject_filter: str | None = None,
    ) -> list[RetrievalResult]: ...

    def upsert_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None: ...

    def has_subject(self, subject: str) -> bool:
        """Check if any chunks exist for normalized subject."""
        ...
```

Key design decisions:
- `subject` is stored normalized (`.strip().lower()`) for case-insensitive filtering
- `has_subject()` replaces the "search then check count" pattern — cheaper than embedding a query just to check cache
- Uses `WHERE subject = ?` filter + `ORDER BY array_cosine_similarity(...) DESC LIMIT ?`
- Connection opened/closed per operation (not held as long-lived singleton) to avoid blocking DuckDB's single-writer lock during sync or training operations

**Registry** (`registry.py`): Replace OpenSearch registration with DuckDB:
```python
from retrieval.duckdb_client import DuckDBVectorClient
Registry.register("client", "duckdb")(DuckDBVectorClient)
```
Remove `from retrieval.client import OpenSearchClient` import and `Registry.register("client", "hybrid")` line.
Keep `client.py` file intact (dead code, may be useful for eval comparison later).
Update `tests/unit/rag/test_registry.py` — assert `"duckdb"` instead of `"hybrid"`.
Update `tests/unit/rag/test_opensearch_client.py` — skip or remove (OpenSearch is no longer registered).

**Tests** (`tests/unit/rag/test_duckdb_client.py`):
- Use `:memory:` DuckDB connection via monkeypatch (no file I/O)
- Test upsert + search round-trip
- Test `has_subject` returns True after upsert, False before
- Test subject normalization (case-insensitive matching)
- Test empty results for unknown subject

**Run**: `uv run pytest tests/unit/rag/test_duckdb_client.py -v`

**Done when**: upsert + search round-trip passes; `Registry.list_modules()` shows `"duckdb"`.

---

### Step 2: Adapt embedder — add `MiniLMEmbedder` ✓ DONE — 2026-04-06

**Files**:
- `src/rag_core/retrieval/embedder.py` (add `MiniLMEmbedder`, keep `MultilingualEmbedder`)
- `src/rag_core/registry.py` (register `MiniLMEmbedder`)
- `tests/unit/rag/test_embedder.py` (update existing tests)

**What**: Add `MiniLMEmbedder` wrapping `all-MiniLM-L6-v2` (384-dim, no prefix required).
Keep `MultilingualEmbedder` for backwards compatibility / eval comparison.
`MiniLMEmbedder` is the default for listen-wiseer.

```python
class MiniLMEmbedder:
    """Wraps all-MiniLM-L6-v2 (384 dims). No prefix required."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        self.model = SentenceTransformer(model_name)

    def embed_query(self, text: str) -> list[float]:
        return self.model.encode(text, convert_to_numpy=True).tolist()

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, convert_to_numpy=True).tolist()
```

**Tests** (mock `SentenceTransformer` — no real model download in unit tests):
- Mock `SentenceTransformer.encode` to return numpy arrays of correct shape (384-dim)
- Verify `embed_query` returns `list[float]` of length 384
- Verify `embed_passages` returns `list[list[float]]` with correct batch size
- Verify registry registration under `"minilm"`

```python
def test_minilm_embed_query_shape(monkeypatch):
    mock_model = MagicMock()
    mock_model.encode.return_value = np.random.rand(384).astype(np.float32)
    monkeypatch.setattr("rag_core.retrieval.embedder.SentenceTransformer", lambda *a, **kw: mock_model)
    embedder = MiniLMEmbedder()
    vec = embedder.embed_query("Aphex Twin")
    assert len(vec) == 384
```

**Run**: `uv run pytest tests/unit/rag/test_embedder.py -v`

**Done when**: `MiniLMEmbedder` returns 384-dim vectors (mocked); registered in Registry.

---

### Step 3: Adapt schemas — music intents + default language English ✓ DONE — 2026-04-06

**Files**:
- `src/rag_core/schemas/retrieval.py` (replace Intent enum with music-specific values)
- `src/rag_core/schemas/chunks.py` (change `language` default from `"da"` to `"en"`)
- `src/rag_core/schemas/conversation.py` (update `initial_state` default from `Intent.HOW_TO` to `Intent.ARTIST_INFO`)
- `tests/unit/rag/test_schemas.py` (new)
- `tests/unit/rag/test_models.py` (update Intent assertions: `HOW_TO` → `ARTIST_INFO`, etc.)
- `tests/unit/rag/test_graph_nodes.py` (update all Intent references to new enum values)

**What**: Replace generic intents with music-specific ones.
Keep `CHIT_CHAT` and `OUT_OF_SCOPE` — they're universal.
Fix `ChunkMetadata.language` default to `"en"`.

Update ALL downstream references in the same step to keep tests green:
- `conversation.py:30` — `Intent.HOW_TO` → `Intent.ARTIST_INFO`
- `test_models.py` — assert on new enum values
- `test_graph_nodes.py` — replace `Intent.HOW_TO`/`TROUBLESHOOT` with music equivalents

```python
class Intent(StrEnum):
    ARTIST_INFO = "artist_info"    # "who is Aphex Twin?", "tell me about Radiohead"
    GENRE_INFO = "genre_info"      # "what is zouk?", "explain bossa nova"
    HISTORY = "history"            # "what have I been listening to?", "my recent plays"
    CHIT_CHAT = "chit_chat"        # greetings, small talk
    OUT_OF_SCOPE = "out_of_scope"  # unrelated to music
```

**Done when**: Intent has music values; `ChunkMetadata` defaults to `language="en"`;
`conversation.py` uses new default; all tests in `tests/unit/rag/` pass with new enum values.

---

### Step 4: Data fetchers — Wikipedia + Tavily (optional) ✓ DONE — 2026-04-06

**Files**:
- `src/rag_core/preprocessing/fetchers.py` (new)
- `src/utils/config.py` (add `tavily_api_key`)
- `.env.example` (add `TAVILY_API_KEY=`)
- `tests/unit/rag/test_fetchers.py` (new)

**What**: Implement `fetch_wikipedia` and `fetch_tavily` — on-demand content
fetchers for the lazy-ingestion pipeline. Pure functions, not classes.

Wikipedia is the primary source. Tavily is an optional fallback (requires API key).
If neither returns content, the orchestrator returns a "no info found" message.

Exception handling:
- `fetch_wikipedia`: catch `wikipedia.exceptions.DisambiguationError` (try first option),
  `wikipedia.exceptions.PageError`, `wikipedia.exceptions.WikipediaException`
- `fetch_tavily`: catch `(ConnectionError, TimeoutError, ValueError)` — no bare `except Exception`

**Dependency**: `tavily-python` is NOT in `pyproject.toml`. Use lazy import guard in
`fetch_tavily` so it's truly optional — if `tavily` isn't installed, return None gracefully.
Do NOT add `tavily-python` to `pyproject.toml` as a hard dependency.

**Config addition** (`src/utils/config.py`):
```python
tavily_api_key: str = ""
```

**Tests** (all mocked — no network calls):
- Wikipedia happy path
- Wikipedia disambiguation fallback
- Tavily returns None when no API key set
- Wikipedia PageError → returns None

**Run**: `uv run pytest tests/unit/rag/test_fetchers.py -v`

**Done when**: Both fetchers importable and tested with mocks.

---

### Step 5: Music RAG orchestrator ✓ DONE — 2026-04-06

**Files**:
- `src/rag_core/orchestration/music_rag.py` (new)
- `tests/unit/rag/test_music_rag.py` (new)

**What**: Thin production orchestrator — no LangGraph overhead.
Wires: `MiniLMEmbedder` → `DuckDBVectorClient` → lazy-fetch → ingest → return passages.
This is what the agent tool calls.

Key flow:
1. Normalize subject → `subject.strip().lower()`
2. Check `client.has_subject(subject)` — cheap SQL count, no embedding needed
3. If cached: embed query → search → return top_k passages
4. If not cached: fetch Wikipedia (fallback Tavily) → chunk → embed → upsert → search → return

This avoids the old plan's issue of embedding a query just to check if we have cached data.

```python
class MusicRAG:
    def __init__(self) -> None:
        self._embedder = MiniLMEmbedder()
        self._client = DuckDBVectorClient()
        self._chunker = StructuredChunker(_CHUNK_CONFIG)

    def get_context(self, subject: str, top_k: int = 3) -> str:
        normalized = subject.strip().lower()
        if not self._client.has_subject(normalized):
            self._ingest(subject, normalized)
        ...
```

**Tests** (all mocked — no network, no real DB):
- Cache miss → Wikipedia fetch → ingest → returns passages
- Cache hit → skips fetch → returns passages
- No content found → returns fallback message

**Run**: `uv run pytest tests/unit/rag/test_music_rag.py -v`

**Done when**: All tests pass.

---

### Step 6: Wire `MusicRAG` into agent as tool ✓ DONE — 2026-04-06

**Files**:
- `src/agent/tools.py` (add `get_artist_context_tool`, update `ALL_TOOLS`)
- `src/agent/nodes.py` (update system prompt to mention new tool)
- `tests/unit/agent/test_tools.py` (extend)

**What**: Expose `MusicRAG.get_context` as a `StructuredTool`. Agent calls it
for "who is X?" and "tell me about X" queries. `MusicRAG` is instantiated lazily
(no SentenceTransformer load at import time).

```python
get_artist_context_tool = StructuredTool.from_function(
    _get_artist_context,
    name="get_artist_context",
    description=(
        "Retrieve biographical info and interesting facts about a musician or band. "
        "Use when the user asks who an artist is, what they're known for, "
        "their history, influences, or style."
    ),
)
```

**System prompt addition** (`nodes.py`):
```
- get_artist_context: use for "who is X?", "tell me about X", artist trivia, history, influences
```

**Tests**:
- Verify tool is in `ALL_TOOLS`
- Verify tool callable with mocked `MusicRAG`

**Run**: `uv run pytest tests/unit/agent/ -v`

**Done when**: Tool registered and callable; system prompt updated.

---

### Step 7: English prompts + music system prompts ✓ DONE — 2026-04-06

**Files**:
- `src/rag_core/generation/generator.py` (replace Danish prompts with English music prompts)
- `src/rag_core/orchestration/graph.py` (update Danish strings to English, update INTENT_MAP)
- `tests/unit/rag/test_generator.py` (update — new Intent enum values in assertions)
- `tests/unit/rag/test_graph_nodes.py` (update — Danish query assertions → English music equivalents)

**What**: Replace all Danish strings in `generator.py` and `graph.py` with English
music-context equivalents. Update prompts to use new `Intent` enum values.

This includes:
- `SYSTEM_PROMPTS` dict in `generator.py` (Danish → English, keyed to new Intent)
- `build_prompt` user prompt template (`"Dokumentation:"` → `"Context:"`, `"Spørgsmål:"` → `"Question:"`)
- `NO_ANSWER_MESSAGE` in `graph.py` (Danish → English)
- `_rewrite_query` prompt in `graph.py` (Danish → English)
- `_grade_docs` prompt in `graph.py` (Danish → English)
- `INTENT_MAP` keys in `graph.py` (update to map to new Intent values)

Note: `query_understanding.py` is NOT updated here — it's deferred to Phase 5b.
The `INTENT_MAP` in `graph.py` will map the old QueryAnalyzer output strings
("factual", "procedural", etc.) to new Intent values as a bridge until Phase 5b.

**Done when**: No Danish strings remain in `generator.py` or `graph.py`; all RAG tests pass.

---

### Step 8: End-to-end smoke + regression ✓ DONE — 2026-04-06

**Manual smoke** (run `make app`):
1. `"who is Aphex Twin?"` → `get_artist_context` → Wikipedia passages
2. `"what is zouk music?"` → `get_artist_context` with "zouk" → genre info
3. `"recommend zouk tracks"` → `recommend_by_genre` → still works (regression)

**Regression**:
```bash
uv run pytest tests/unit/ --tb=short -q
```

**Done when**: All 3 smoke queries return useful responses; test count >= 280 (pre-phase baseline).

---

## Test Plan

| Step | Command | Verifies |
|------|---------|----------|
| 1 | `uv run pytest tests/unit/rag/test_duckdb_client.py -v` | DuckDB vss upsert + cosine search |
| 2 | `uv run pytest tests/unit/rag/test_embedder.py -v` | MiniLM 384-dim vectors |
| 3 | `uv run pytest tests/unit/rag/test_schemas.py -v` | Music Intent enum + English defaults |
| 4 | `uv run pytest tests/unit/rag/test_fetchers.py -v` | Wikipedia + Tavily (mocked) |
| 5 | `uv run pytest tests/unit/rag/test_music_rag.py -v` | Full orchestrator (mocked) |
| 6 | `uv run pytest tests/unit/agent/ -v` | Tool wiring + ALL_TOOLS count |
| 7 | `uv run pytest tests/unit/rag/ -v` | Full RAG test suite |
| 8 | `uv run pytest tests/unit/ --tb=short -q` | Full regression |

---

## Dependency Map

```
Step 1 (DuckDBVectorClient) <- independent
Step 2 (MiniLMEmbedder) <- independent
Step 3 (schemas) <- independent; Steps 5, 7 depend on it
Step 4 (fetchers) <- independent
Step 5 (MusicRAG) <- needs Steps 1 + 2 + 4
Step 6 (agent tool) <- needs Step 5
Step 7 (prompts) <- needs Step 3
Step 8 (smoke) <- needs Steps 5 + 6 + 7
```

Steps 1, 2, 3, 4 can be done in any order.
Step 5 is the main integration point.
Steps 6 and 7 are independent of each other but both need Step 5 / Step 3.

---

## Risks & Rollback

### DuckDB `array_cosine_similarity` (Step 1)
- **Risk**: Function not available in older DuckDB versions (<0.10)
- **Mitigation**: We're on DuckDB 1.5.0, function is core (not an extension). Verified locally.
- **Rollback**: N/A — if DuckDB is installed, the function exists. No extension download needed.

### DB write contention (Step 1)
- **Risk**: DuckDB is single-writer. If agent writes rag_chunks while sync writes tracks, one blocks.
- **Mitigation**: RAG writes are rare (only on first query per artist) and fast (<100ms). Acceptable.
- **Rollback**: Not a code bug — operational. Could move to separate DB file if contention becomes real.

### Model download (Step 2)
- **Risk**: `all-MiniLM-L6-v2` not cached locally -> slow first import
- **Mitigation**: Already used by `recommend/` pipeline — should be in HuggingFace cache
- **Rollback**: Not applicable (download, not a code bug)

### Wikipedia DisambiguationError (Step 4)
- **Risk**: "Genesis", "Prince", "The Weeknd" -> disambiguation page
- **Mitigation**: Catch `DisambiguationError`, try first option, fall back to Tavily
- **Rollback**: Fix exception handling — no data affected

### Import-time MusicRAG (Step 6)
- **Risk**: `_music_rag` instantiation at first call loads SentenceTransformer -> slow
- **Mitigation**: Lazy singleton (`_music_rag is None` guard); not loaded at import
- **Rollback**: `git revert HEAD --no-edit` on `tools.py`

### Global rollback
```bash
git revert HEAD~N..HEAD --no-edit
uv run pytest tests/unit/ --tb=short -q
```
