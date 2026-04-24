# Research: RAG System — Component Tradeoffs

Decision log for the Librarian agent. One section per pipeline stage.

Legend:
- **✅ Active** — currently wired as the default in `LibrarySettings`
- **🔧 Implemented** — code exists, selectable via config, not the default
- **📋 Stub** — scaffolded but not production-ready
- **💡 Documented** — trade-off noted, not yet implemented

---

## 1. Preprocessing / Chunking

### ✅ Active: `HtmlAwareChunker` (`preprocessing/html_aware.py`)

**How it works:** Splits at `##`/`###` headings first (semantic boundaries from HTML-converted docs), then recursively at `\n\n`, `\n`, `. `, ` ` until chunks fit `max_tokens=512`. SHA256 doc IDs from `(url, section)`. Carries `overlap_tokens=64` across boundaries.

**Why:**
- Documentation corpora are heading-structured — splitting at headings preserves topic coherence better than fixed-size windows.
- Recursive splitting avoids mid-sentence truncation without requiring a tokenizer.
- SHA256 doc IDs mean chunks are independently addressable and deduplication is exact.

**All implemented strategies** (`preprocessing/chunker.py`):

| Strategy | Class | Best for |
|---|---|---|
| ✅ Heading-boundary recursive | `HtmlAwareChunker` | HTML/markdown docs (default) |
| 🔧 Two-level child/parent | `ParentDocChunker` | Long docs; child indexed, parent for generation |
| 🔧 Recursive prose | `StructuredChunker` | Prose without markdown headings |
| 🔧 Overlapping windows | `OverlappingChunker` | Dense technical text; reduces boundary misses |
| 🔧 Fixed windows | `FixedChunker` | Baseline benchmarking; FAQ/snippet bodies |
| 🔧 Adjacent with neighbour lookup | `AdjacencyChunker` | Context expansion at query time |

**Other trade-offs:**

| Alternative | Notes |
|---|---|
| **Sentence-level** (spaCy / NLTK) | Chunks too small for BM25; adds NLP dependency; poor on code/URLs |
| **Semantic chunking** (embedding-based split) | Expensive at ingest; inconsistent chunk sizes hurt BM25 |
| **Source-type aware** (FAQ=single chunk, blog=large sections) | Implemented in `preprocessing/indexer.py` via `build_indexer_for_source()` |

---

## 2. Preprocessing / Parsing & Cleaning

### 🔧 Implemented: `parsing.py` (`preprocessing/parsing.py`)

**Components:**

| Function | What it does |
|---|---|
| `clean_text()` | Normalise whitespace, strip email footers/noise patterns |
| `remove_boilerplate()` | Domain-specific regex removal (pass patterns explicitly) |
| `detect_language()` | Heuristic script detection (Cyrillic, CJK, Arabic vs Latin) |
| `filter_by_language()` | Drop non-Latin documents from corpus |
| `deduplicate_exact()` | MD5 hash dedup — O(n), keeps first/last occurrence |
| `deduplicate_fuzzy()` | Cosine similarity dedup — requires embedder + scikit-learn |
| `enrich_documents()` | Add word_count, source category, content_type from URL/text |
| `preprocess_corpus()` | Full pipeline: clean → filter → dedup → enrich |

**When to use:** Called optionally by `ChunkIndexer.index_documents(preprocess=True)`. Disabled by default so ingestion pipelines control data quality explicitly.

---

## 3. Preprocessing / Indexer

### 🔧 Implemented: `ChunkIndexer` (`preprocessing/indexer.py`)

**How it works:** Wires Chunker + Embedder + Retriever into a single async pipeline. Embeds in configurable batches (default 64), calls `retriever.upsert()`. `build_indexer_for_source(source_type)` selects the right chunker per source (html, blog, faq, snippet, parent_doc, etc.).

**Not active by default** — used at ingest time, not at query time.

---

## 4. Embeddings

### ✅ Active: `MultilingualEmbedder` → `intfloat/multilingual-e5-large` (1024-dim) (`preprocessing/embedder.py`)

**How it works:** SentenceTransformer wrapper with E5 prefix rule enforced at Protocol level — `"query: "` prefix at search time, `"passage: "` prefix at index time. Model loaded once, cached process-wide.

**Why:**
- E5-large outperforms smaller models on MTEB retrieval tasks while staying fully local (no API key).
- Multilingual variant handles mixed-language corpora without re-indexing.
- E5 prefix rules are non-negotiable for this model family — violating them silently degrades recall ~15–20%.
- 1024-dim vectors give Chroma/OpenSearch enough resolution for tight cosine neighbours.

**All implemented embedders:**

| Embedder | Dims | Prefix required | Best for |
|---|---|---|---|
| ✅ `MultilingualEmbedder` (`multilingual-e5-large`) | 1024 | ✓ E5 | Multi-language / default |
| 🔧 `MiniLMEmbedder` (`all-MiniLM-L6-v2`) | 384 | ✗ | English-only, fast CI/local dev |
| 🔧 `MockEmbedder` | configurable | ✗ | Deterministic unit tests |

**Other trade-offs:**

| Alternative | Notes |
|---|---|
| `intfloat/e5-large-v2` (English-only) | ~20% faster; switch when corpus is confirmed English-only |
| `voyage-3` (Anthropic/Voyage) | Best-in-class for code+docs; costs $; API key |
| `text-embedding-3-*` (OpenAI) | Higher MTEB on English; costs $; requires API key |
| **ColBERT** | Token-level late interaction → better recall; much larger index footprint |

---

## 5. Vector Store / Retrieval Backend

### ✅ Active: `ChromaRetriever` (persistent, local) (`retrieval/chroma.py`)

**How it works:** ChromaDB `PersistentClient` on disk (`.chroma/`). Collection uses cosine space (`hnsw:space: cosine`). Hybrid score: `0.3 * term_overlap + 0.7 * cosine_similarity`. No Docker required — `uv add chromadb`.

**Why:**
- Zero infrastructure: installs as a Python package, persists to a local directory.
- HNSW index gives sub-linear query time (vs. linear scan in `InMemoryRetriever`).
- Same `Retriever` Protocol as all other backends → tests and prod share the same interface.

**All implemented backends:**

| Backend | Class | Strategy | Local/Free | When to use |
|---|---|---|---|---|
| ✅ `ChromaRetriever` | `retrieval/chroma.py` | HNSW + term-overlap | ✓ | Default local dev and small prod |
| 🔧 `DuckDBRetriever` | `retrieval/duckdb.py` | Brute-force cosine + term-overlap | ✓ | Already have DuckDB; SQL joins needed |
| 🔧 `InMemoryRetriever` | `retrieval/inmemory.py` | Linear scan + term-overlap | ✓ | Unit tests only |
| 🔧 `OpenSearchRetriever` | `retrieval/opensearch.py` | Native BM25 + k-NN | Docker/AWS | Production, multi-tenant |

**Select via:** `RETRIEVAL_STRATEGY=chroma|duckdb|inmemory|opensearch`

**Chroma limitations:**
- No native BM25 — term overlap is an approximation; move to OpenSearch for true BM25.
- Single-process write lock — cannot write from multiple workers simultaneously.
- No auth/multi-tenancy — fine locally, not for shared deployments.

**DuckDB note:** Added as an alternative for setups that already use DuckDB for analytics (no second dependency). O(n) scan at query time — acceptable up to ~50k chunks, then switch to Chroma or OpenSearch.

---

## 6. Retrieval Strategy (Hybrid Search)

### ✅ Active: BM25-weighted term overlap + cosine vector (weights: 0.3 / 0.7)

**How it works:** Both signals computed independently, linearly combined. Weights configurable per retriever constructor; default favours vectors (semantic) over keywords (exact). Multi-query expansion (up to `max_query_variants=3`) increases recall; variants deduplicated by chunk ID.

**Trade-offs:**

| Alternative | Notes |
|---|---|
| **Vector-only** | Misses exact keyword matches (product names, error codes) |
| **BM25-only** | Misses semantic paraphrases; query must share vocabulary with doc |
| **RRF (Reciprocal Rank Fusion)** | More principled fusion; no weight tuning; Chroma doesn't expose ranked lists natively |
| **Native hybrid** (OpenSearch BM25+kNN) | Better than approximation; requires OpenSearch |
| **SPLADE learned sparse** | Outperforms BM25 on BEIR; requires fine-tuned model |

---

## 7. Reranking

### ✅ Active: `CrossEncoderReranker` → `cross-encoder/ms-marco-MiniLM-L-6-v2` (`reranker/cross_encoder.py`)

**How it works:** Cross-encoder scores every `(query, chunk.text)` pair jointly. Raw logit → sigmoid → [0, 1]. Top-`reranker_top_k` (default 3) returned. `confidence_score = max(relevance_scores)` feeds the CRAG gate.

**All implemented rerankers:**

| Reranker | Class | Cost | Best for |
|---|---|---|---|
| ✅ `CrossEncoderReranker` (`ms-marco-MiniLM-L-6-v2`) | Local | — | Default; fast, good precision |
| 🔧 `LLMListwiseReranker` | `reranker/llm_listwise.py` | Tokens/query | High-value queries; best quality |

**Other trade-offs:**

| Alternative | Notes |
|---|---|
| `BAAI/bge-reranker-large` | State-of-the-art on BEIR; 4× larger; worth it for production |
| `cross-encoder/ms-marco-MiniLM-L-12-v2` | Slightly better precision; 2× slower |
| **Cohere Rerank API** | Best managed reranking; costs $; easy swap via `Reranker` Protocol |
| **RRF** | No model; combine multiple ranked lists; no learned scoring |
| **No reranking** | Skip when retrieval quality is high and `confidence_threshold=0.0` |

---

## 8. Generation

### ✅ Active: `ChatAnthropic` (LangChain) → `claude-sonnet-4-6` (`generation/generator.py`)

**How it works:** LangChain `ChatAnthropic` wraps the Anthropic SDK. Prompt built from `reranked_chunks` + citation extraction. `ANTHROPIC_API_KEY` required. Intent-aware system prompts from `generation/prompts.py`.

**Why:**
- Claude Sonnet 4.6 has strong instruction-following and citation fidelity.
- LangChain wrapper enables LangSmith/LangFuse tracing with zero code change.
- Haiku available for cheaper routing of conversational/out-of-scope intents.

**Trade-offs:**

| Alternative | Notes |
|---|---|
| `claude-haiku-4-5-20251001` | 10× cheaper, 3× faster; lower reasoning; good for `conversational`/`out_of_scope` |
| **GPT-4o** | Competitive quality; swap via LangChain `ChatOpenAI` |
| **Local LLM** (Ollama) | No API cost; lower quality; replace `ChatAnthropic` with `ChatOllama` |
| **Anthropic SDK direct** | Less overhead; loses LangChain callback tracing |

---

## 9. Query Understanding / Planner

### ✅ Active: Rule-based `QueryAnalyzer` + `QueryRouter` (`orchestration/query_understanding.py`)

**How it works:** Intent classification via `\b`-anchored keyword regex (`_INTENT_RULES` ordered: COMPARE → CONVERSATIONAL → OUT_OF_SCOPE → EXPLORE → LOOKUP default). Entity extraction, sub-query decomposition, term expansion. `QueryRouter` routes to `"retrieve"`, `"direct"`, or `"clarify"`.

**Why:**
- Zero latency — no LLM call for routing.
- Deterministic — regression tests can assert exact intent.
- `\b` word-boundary anchoring prevents false positives.
- Rule ordering: domain-specific out-of-scope before broad syntactic patterns.

**Trade-offs:**

| Alternative | Notes |
|---|---|
| **LLM classifier** (Claude Haiku) | Higher accuracy on ambiguous queries; `planning_mode="llm"` config flag wired, not yet implemented |
| **Fine-tuned classifier** (DistilBERT/SetFit) | Fast + accurate; requires labelled data; overkill for <10 classes |
| **Semantic similarity to exemplars** | No training data; moderate accuracy; add as fallback when rule confidence < threshold |
| **ReAct plan-and-execute** | Best for multi-step complex queries; high latency/cost; planned for `EXPLORE` intent |

---

## 10. Orchestration / Graph

### ✅ Active: LangGraph `StateGraph` with CRAG loop (`orchestration/graph.py`)

**How it works:** Nodes: `analyze → retrieve → rerank → gate → generate`. Conditional edges: (1) direct intents skip to `generate`; (2) CRAG retry sends back to `retrieve` if `confidence_score < threshold` and `retry_count ≤ max_crag_retries`. State is `LibrarianState` TypedDict with `add_messages` reducer.

**Why:**
- LangGraph makes graph topology explicit and auditable.
- CRAG reduces hallucination on low-confidence retrievals.
- State is serialisable — enables checkpointing (Redis) for multi-turn.
- `retry_count` incremented inside gate *node* return dict — LangGraph only persists state from node return values (not in-place edge mutation).

**Trade-offs:**

| Alternative | Notes |
|---|---|
| **LangChain LCEL** | Linear chains only; harder CRAG loops |
| **Custom async pipeline** | Full control; no checkpointing/streaming built-in |
| **LlamaIndex** | Strong doc-centric tooling; high switching cost |
| **No CRAG** | Simpler graph; set `confidence_threshold=0.0` to disable loop |

---

## 11. Observability

### ✅ Active: structlog + optional LangFuse (`utils/logging.py`)

**How it works:** All modules use `get_logger(__name__)`. Dot-separated `module.action` event names. LangFuse opt-in via `langfuse_enabled=True`; retrieval metrics pushed as LangFuse scores from eval harness.

**Trade-offs:**

| Alternative | Notes |
|---|---|
| **LangSmith** | Deep LangGraph integration; free tier; add when LangFuse insufficient |
| **Prometheus + Grafana** | Production latency metrics; add when serving HTTP |
| **OpenTelemetry** | Vendor-neutral distributed tracing; add when deploying to cloud |
| **Arize Phoenix** | Open-source LLM observability; good LangFuse alternative |

---

## Summary Table

| Stage | Active | Implemented (not default) | API Key |
|---|---|---|---|
| Chunking | `HtmlAwareChunker` | Fixed, Overlapping, Structured, Adjacency, ParentDoc | — |
| Parsing | — (opt-in) | `preprocess_corpus()` clean/dedup/enrich | — |
| Indexer | — (ingest-time) | `ChunkIndexer` + `build_indexer_for_source()` | — |
| Embeddings | `multilingual-e5-large` (1024-dim) | `MiniLMEmbedder` (384-dim, English) | — |
| Vector store | ChromaDB (HNSW, local) | DuckDB (SQL, brute-force), OpenSearch (prod), InMemory (tests) | — |
| Hybrid retrieval | term-overlap + cosine (0.3/0.7) | Native BM25+kNN (OpenSearch) | — |
| Reranking | `ms-marco-MiniLM-L-6-v2` | `LLMListwiseReranker` | — |
| Generation | Claude Sonnet 4.6 | Haiku (cheap routing) | Anthropic ✓ |
| Query planner | Rule-based regex | LLM classifier (`planning_mode=llm`, stub) | — |
| Orchestration | LangGraph CRAG | — | — |
| Observability | structlog + LangFuse (opt-in) | LangSmith, OTel | LangFuse (opt) |
