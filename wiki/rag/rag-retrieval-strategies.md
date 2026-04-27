---
title: RAG Retrieval Strategies
tags: [rag, concept]
summary: Comprehensive reference for chunking, embedding, vector store, and hybrid search strategies — component choices, tradeoffs, and swap paths used in the Librarian pipeline.
updated: 2026-04-24
sources:
  - raw/playground-docs/rag-tradeoffs.md
  - raw/playground-docs/librarian-stack-audit.md
  - raw/playground-docs/rag-agent-template-research.md
  - raw/playground-docs/librarian-ts-parity-research.md
  - raw/claude-docs/playground/docs/archived/librarian-rag-upgrade/plan.md
  - raw/claude-docs/playground/docs/archived/librarian-hardening/plan.md
  - raw/claude-docs/playground/docs/archived/retrieval-pipeline-prod/plan.md
---

# RAG Retrieval Strategies

## Chunking

### Active: `HtmlAwareChunker` (heading-boundary recursive)

Splits at `##`/`###` headings first, then recursively at `\n\n`, `\n`, `. `, ` ` until chunks fit `max_tokens=512`. SHA256 doc IDs from `(url, section)`. Carries `overlap_tokens=64` across boundaries.

**Why:** Documentation corpora are heading-structured — splitting at headings preserves topic coherence. Recursive splitting avoids mid-sentence truncation.

### All implemented strategies

| Strategy | Class | Best for |
|---|---|---|
| ✅ Heading-boundary recursive | `HtmlAwareChunker` | HTML/markdown docs (default) |
| 🔧 Two-level child/parent | `ParentDocChunker` | Long docs; child indexed, parent for generation |
| 🔧 Recursive prose | `StructuredChunker` | Prose without markdown headings |
| 🔧 Overlapping windows | `OverlappingChunker` | Dense technical text; reduces boundary misses |
| 🔧 Fixed windows | `FixedChunker` | Baseline benchmarking only |
| 🔧 Adjacent + neighbour | `AdjacencyChunker` | Context expansion at query time |

**Skip:** sentence-level (too small for BM25), semantic chunking (expensive at ingest, inconsistent sizes).

---

## Embeddings

### Active: `multilingual-e5-large` (1024-dim)

Wrapped in `MultilingualEmbedder` with E5 prefix rule enforced at the Protocol level:
- `"query: "` prefix at search time
- `"passage: "` prefix at index time

**E5 prefix rule is non-negotiable** — violating it silently degrades recall ~15–20%.

### All implemented embedders

| Embedder | Dims | When to use |
|---|---|---|
| ✅ `MultilingualEmbedder` (`multilingual-e5-large`) | 1024 | Multi-language / default |
| 🔧 `MiniLMEmbedder` (`all-MiniLM-L6-v2`) | 384 | English-only, fast CI/local dev |
| 🔧 `MockEmbedder` | configurable | Deterministic unit tests |

**Alternatives:** `e5-large-v2` (English-only, 20% faster), `voyage-3` (best for code+docs, costs $), `BGE-M3` (claimed better multilingual, not yet benchmarked).

**Never use `all-MiniLM-L6-v2` for Danish/multilingual** — it silently fails on non-English.

---

## Vector Stores

### Active: ChromaDB (persistent, HNSW)

`PersistentClient` on disk (`.chroma/`). Collection uses cosine space. Hybrid score: `0.3 * term_overlap + 0.7 * cosine_similarity`. No Docker required.

### All implemented backends

| Backend | Strategy | Local | When to use |
|---|---|---|---|
| ✅ `ChromaRetriever` | HNSW + term-overlap | ✓ | Default local dev and small prod |
| 🔧 `DuckDBRetriever` | Brute-force cosine + term-overlap | ✓ | Already have DuckDB; SQL joins needed |
| 🔧 `InMemoryRetriever` | Linear scan + term-overlap | ✓ | Unit tests only |
| 🔧 `OpenSearchRetriever` | Native BM25 + k-NN | Docker/AWS | Production, multi-tenant |

**Select via:** `RETRIEVAL_STRATEGY=chroma|duckdb|inmemory|opensearch`

**Chroma limitations:** No native BM25, single-process write lock, no auth/multi-tenancy.

**DuckDB note:** O(n) scan — acceptable up to ~50K chunks, then switch to Chroma or OpenSearch.

---

## Hybrid Search

### Active: RRF (Reciprocal Rank Fusion)

**Production choice.** See [[Reciprocal Rank Fusion (RRF)]] for full mechanism. Rank-based fusion avoids sensitivity to score distribution differences between BM25 and vector search:

```python
def rrf_score(bm25_rank: int, vector_rank: int, k: int = 60) -> float:
    return 1.0 / (k + bm25_rank) + 1.0 / (k + vector_rank)
```

**Why RRF beats linear weighting:** Linear combination (e.g. `0.3 * bm25 + 0.7 * cosine`) requires careful calibration — BM25 and vector scores have different distributions, making weights fragile. RRF is parameter-free (only the `k=60` constant from the original paper) and typically bumps hit_rate by 3–8%.

Config fallback: `HYBRID_SCORING=rrf|linear` if you need linear for A/B comparison.

**Why hybrid beats either alone:**
- Vector-only: misses exact keyword matches (product names, error codes, version numbers)
- BM25-only: misses semantic paraphrases
- Hybrid: catches both classes of match

### Production benchmark (from RAPTOR v1 — Danish market)

| Strategy | Hit Rate |
|---|---|
| Dense only | 45% |
| Sparse (BM25) | 50% |
| Hybrid (RRF) | 58% |
| **Hybrid + cross-encoder reranker** | **68%** |

Adding the cross-encoder on top of hybrid adds +10pp. Both are worth doing.

### Alternatives

| Alternative | Notes |
|---|---|
| **Native hybrid** (OpenSearch BM25+kNN) | Better than approximation; requires OpenSearch |
| **SPLADE learned sparse** | Outperforms BM25 on BEIR; requires fine-tuned model |

---

## EnsembleRetriever — Multi-Query Fan-Out

The `EnsembleRetriever` encapsulates the full multi-query retrieval pattern as a reusable class, replacing ad-hoc query variant management in `RetrieverAgent`:

```python
class EnsembleRetriever:
    """Multi-query, multi-retriever fusion with fingerprint dedup."""

    def __init__(
        self,
        retrievers: list[Retriever],
        embedder: Embedder,
        *,
        score_threshold: float = 0.4,
        max_queries: int = 3,
    ) -> None: ...

    async def retrieve(
        self,
        queries: list[str],   # 1–3 query variants
        k: int = 10,
    ) -> list[GradedChunk]: ...
```

**Key behaviors:**
- `asyncio.gather` runs all queries × all retrievers in parallel (matrix)
- **Fingerprint dedup:** `sha256(f"{url}|{text[:200].lower().strip()}")` → keeps highest-scored copy across queries
- Score threshold filtering: drops chunks below `score_threshold`
- RRF fusion across all result lists using `fuse_rankings()`
- Returns `list[GradedChunk]` — same interface the reranker expects

The `EnsembleRetriever` collapses ~60 lines in `RetrieverAgent.run()` to ~5. It's also the interface for LLM-driven multi-query: expose `queries: List[str]` on the `/query` API and callers send 2–3 reformulations directly.

---

## Async Parallel Embedding

Multi-query expansion should embed all variants in parallel, not sequentially:

```python
# Before (sequential — blocks event loop)
for variant in variants:
    query_vector = self._embedder.embed_query(variant)
    results = await self._retriever.search(...)

# After (parallel — asyncio.gather)
vectors = await asyncio.gather(
    *(self._embedder.aembed_query(v) for v in variants)
)
results_lists = await asyncio.gather(
    *(self._retriever.search(v, vec, k=top_k)
      for v, vec in zip(variants, vectors))
)
```

For `MultilingualEmbedder` (local SentenceTransformer), `aembed_query` wraps sync in `asyncio.to_thread()`. For cloud embedders (Voyage, Cohere), it would be native async httpx.

**Important:** when `aembed_query` is a sync method (not a coroutine), check `inspect.isawaitable(result)` — if False, return the result directly. Do not fall through to a second `asyncio.to_thread` call or you'll discard the first embedding and block the loop.

---

## Query Result Cache

An LRU cache on retrieval results avoids redundant embedding + vector search for repeated queries in a session:

```python
class RetrievalCache:
    """Thread-safe LRU cache. Keyed on (sha256(query), retrieval_strategy)."""
    def __init__(self, max_size: int = 256, ttl_seconds: int = 300): ...
    def get(self, query: str, strategy: str) -> list[RetrievalResult] | None: ...
    def put(self, query: str, strategy: str, results: list[RetrievalResult]) -> None: ...
```

**Config:**
```python
cache_enabled: bool = True
cache_max_size: int = 256
cache_ttl_seconds: int = 300
```

**Invalidation:** `IngestionPipeline` calls `cache.clear()` after successful corpus update so stale results don't persist after new documents are indexed. Cache is injected via factory — disabled in tests.

---

## Ingestion Pipeline

| Step | Tool | Details |
|---|---|---|
| Dedup | SHA-256 checksum in MetadataDB | Idempotent — skips docs already ingested |
| Chunk | `HtmlAwareChunker` | Heading-boundary recursive splitting |
| Embed | `MultilingualEmbedder.embed_passages()` | Batch embedding with `"passage: "` prefix |
| Index | `Retriever.upsert()` | Batched (default 64) writes to vector store |
| Snippet | Regex sentence splitting | Extracts sentences 30-400 chars, writes to DuckDB FTS |
| Metadata | `MetadataDB.insert_document()` | DuckDB table: doc_id, title, word_count, chunk_count, checksum |

---

## Query Understanding / Planner

### Active: Rule-based `QueryAnalyzer` + `QueryRouter`

Intent classification via `\b`-anchored keyword regex. Intent ordering: COMPARE → CONVERSATIONAL → OUT_OF_SCOPE → EXPLORE → LOOKUP (default). Entity extraction (ticket IDs, dates, amounts). Sub-query decomposition. Term expansion via synonym dictionary.

**Zero latency** — no LLM call for routing. Deterministic — regression tests assert exact intent.

**Upgrade path:** `planning_mode="llm"` config flag wired (stub) — uses Haiku structured output for ~200ms, ~$0.001/query.

### Retrieval mode selection

| Intent × Complexity | Mode |
|---|---|
| LOOKUP + simple | `snippet` (DuckDB FTS, no embedding) |
| LOOKUP + moderate | `hybrid` |
| COMPARE | `hybrid` |
| EXPLORE | `dense` |

## DuckDB vss — Zero-Dependency Vector Store

For projects already using DuckDB, the `vss` extension provides vector search without adding a new service:

```sql
CREATE TABLE rag_chunks (
    chunk_id  VARCHAR PRIMARY KEY,
    subject   VARCHAR NOT NULL,   -- normalized: lower(strip(artist_name))
    section   VARCHAR DEFAULT 'bio',
    source_url VARCHAR DEFAULT '',
    text      VARCHAR NOT NULL,
    embedding FLOAT[384],         -- all-MiniLM-L6-v2
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Search via `array_cosine_similarity()`:

```python
conn.execute("""
    SELECT chunk_id, text, array_cosine_similarity(embedding, $1::FLOAT[384]) AS score
    FROM rag_chunks WHERE subject = $2
    ORDER BY score DESC LIMIT $3
""", [query_embedding, subject, top_k])
```

**When to use:** `<10k chunks`, same database already in use, want zero extra infra. Add HNSW index when scale warrants it. For larger corpora or multi-tenant workloads, prefer dedicated vector stores.

**Lazy ingestion pattern** (used in listen-wiseer for artist bios):
1. Agent calls `get_artist_context(artist_name)`
2. Check `rag_chunks` for cached passages for this artist
3. On cache miss: fetch Wikipedia → chunk → embed → upsert → return top-k
4. On cache hit: return top-k directly

This avoids pre-ingesting all artists upfront and handles the corpus freshness gap naturally.

## See Also
- [[LangGraph CRAG Pipeline]]
- [[RAG Reranking]]
- [[RAG Evaluation]]
- [[Librarian RAG Architecture]]
- [[Production Hardening Patterns]]
- [[Bedrock KB vs LangGraph Decision]]
- [[RAG API Design Patterns]]
- [[Listen-Wiseer Project]]
