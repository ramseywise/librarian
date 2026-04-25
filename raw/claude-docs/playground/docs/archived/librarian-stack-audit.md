# Librarian — Stack Audit & Agent Architecture Reference

> Comprehensive technical documentation of the librarian RAG agent's tools, strategies, and component interactions across all five agents.

Date: 2026-04-10

---

## 1. Plan Agent (Query Understanding + Orchestration)

**Location:** `orchestration/query_understanding.py`, `orchestration/graph.py`

**Job:** Classify user intent, decompose complex queries, expand terms, select retrieval strategy, and route to the right pipeline path.

### Tools

| Tool | Implementation | What it does |
|---|---|---|
| **Intent Classifier** | `QueryAnalyzer._classify_intent()` | Keyword-match against ordered rule lists — first hit wins. 5 intents: `LOOKUP`, `EXPLORE`, `COMPARE`, `CONVERSATIONAL`, `OUT_OF_SCOPE` |
| **Entity Extractor** | `QueryAnalyzer._extract_entities()` | Regex patterns for `version` (e.g. `v3.2.1`), `date`, `quantity` (e.g. `500ms`, `10GB`), `identifier` (e.g. `AUTH_TOKEN`) |
| **Sub-query Decomposer** | `QueryAnalyzer._decompose()` | Splits on `?` then on conjunctions (`and`, `also`, `furthermore`, etc.) to detect multi-part questions |
| **Complexity Scorer** | `QueryAnalyzer._score_complexity()` | `simple` / `moderate` / `complex` based on sub-query count + entity diversity. Thresholds: >=3 = complex, >=2 = moderate |
| **Term Expander** | `QueryAnalyzer._expand_terms()` | Dictionary-based synonym expansion (e.g. `auth` -> `authentication`, `authorization`, `login`, `token`, `oauth`). Includes domain-specific terms (tech + music genres) |
| **Retrieval Mode Selector** | `QueryAnalyzer._select_retrieval_mode()` | Maps (intent x complexity) -> `dense` / `hybrid` / `snippet`. Rules: LOOKUP+simple=snippet, LOOKUP+moderate=hybrid, COMPARE=hybrid, EXPLORE=dense |
| **Query Router** | `QueryRouter.route()` | 3-way routing: `retrieve` / `direct` / `clarify`. Direct = conversational/out_of_scope. Clarify = confidence < 0.5 threshold |

### Strategies

- **Rule-based first, LLM second**: All classification is deterministic keyword/regex — zero LLM calls at planning time. A `planning_mode: llm` config option exists as an upgrade path but isn't built yet
- **First-match-wins intent ordering**: COMPARE checked before EXPLORE because "compare" keywords are more specific — avoids false EXPLORE matches on comparative queries
- **3-way graph routing**: After analysis, the LangGraph state machine routes to `retrieve` (dense/hybrid path), `snippet_retrieve` (fast keyword FTS), or `generate` (direct response, no retrieval). This is the `_route_after_analyze()` conditional edge

---

## 2. Retrieval Agent

**Location:** `retrieval/`, `orchestration/subgraphs/retrieval.py`, `ingestion/`

**Job:** Turn queries into relevant document chunks via embedding + vector search + keyword matching, with multi-query expansion and deduplication.

### Tools

| Tool | Implementation | What it does |
|---|---|---|
| **Bi-encoder Embedder** | `MultilingualEmbedder` wrapping `intfloat/multilingual-e5-large` (1024-dim) | Embeds queries and passages with E5 prefix rule: `"query: "` for search-time, `"passage: "` for indexing. Supports 100+ languages |
| **ChromaDB Vector Store** | `ChromaRetriever` (default) | Persistent local HNSW index with cosine distance. No Docker needed. Lazy-initialized via `PersistentClient` |
| **OpenSearch Vector Store** | `OpenSearchRetriever` (production) | kNN + BM25 native hybrid. Connects via `opensearch-py`. Auth optional |
| **DuckDB Vector Store** | `DuckDBRetriever` | Lightweight SQL-based retrieval. Shares the same `.duckdb` file as metadata + snippet storage |
| **InMemory Retriever** | `InMemoryRetriever` (test-only) | Pure Python — brute-force cosine + term overlap. Mirrors the hybrid interface exactly so tests transfer to prod backends |
| **Snippet Retriever** | `SnippetRetriever` -> `SnippetDB` (DuckDB FTS) | Keyword-based full-text search over pre-extracted sentences. Bypasses embedding + reranking entirely — fast path for simple factual lookups |
| **Hybrid Scorer** | `scoring.term_overlap()` + `scoring.cosine_similarity()` | `hybrid_score = 0.3 * term_overlap + 0.7 * cosine_similarity`. Applied identically in Chroma and InMemory backends for parity |
| **Chroma Distance Converter** | `_chroma_distance_to_score()` | Converts Chroma's cosine distance `[0, 2]` -> similarity `[0, 1]` via `1 - distance` |
| **Multi-query Expander** | `RetrievalSubgraph.run()` | Runs retrieval for each query variant (from plan or term expansion), concatenates results, then deduplicates |
| **CRAG Grader** | `_grade_chunks()` | Marks each chunk `relevant=True/False` based on `score >= 0.1` threshold. Deduplicates by chunk ID |

### Strategies

- **Hybrid search everywhere**: Every backend blends vector similarity with BM25-like term overlap (0.7/0.3 weighting). Not just vector, not just keyword — the hybrid catches both semantic matches and exact-term matches
- **Multi-query expansion**: Query variants from the plan agent are each searched independently, then results are merged and deduplicated by chunk ID. This broadens recall without sacrificing precision (the reranker handles precision downstream)
- **Protocol-based backend swapping**: `Retriever` is a `@runtime_checkable Protocol` with two methods (`search`, `upsert`). Switch backends via a single env var `RETRIEVAL_STRATEGY=chroma|opensearch|duckdb|inmemory`
- **Dual-path retrieval**: Dense/hybrid path (embed -> vector search -> rerank) for complex queries; snippet path (keyword FTS only) for simple factual lookups. Routed by the plan agent's retrieval mode selector

### Ingestion Pipeline

| Step | Tool | Details |
|---|---|---|
| Dedup | SHA-256 checksum in MetadataDB | Idempotent — skips docs already ingested |
| Chunk | `HtmlAwareChunker` | Heading-boundary recursive splitting. Respects HTML/Markdown structure |
| Embed | `MultilingualEmbedder.embed_passages()` | Batch embedding with `"passage: "` prefix |
| Index | `Retriever.upsert()` | Batched (default 64) writes to vector store |
| Snippet | Regex sentence splitting | Extracts sentences 30-400 chars, strips headings, writes to DuckDB FTS |
| Metadata | `MetadataDB.insert_document()` | DuckDB table: doc_id, title, word_count, chunk_count, checksum |

---

## 3. Re-Ranker Agent

**Location:** `reranker/`, `orchestration/subgraphs/reranker.py`

**Job:** Take the broad recall set from retrieval and apply fine-grained relevance scoring to select the top-k most relevant chunks with a confidence signal.

### Tools

| Tool | Implementation | What it does |
|---|---|---|
| **Cross-Encoder Reranker** (default) | `CrossEncoderReranker` wrapping `cross-encoder/ms-marco-MiniLM-L-6-v2` | Scores each (query, chunk.text) pair through a cross-attention model. Raw logits -> sigmoid -> `[0, 1]` relevance score. Model loaded once, cached process-wide via `_MODEL_CACHE` |
| **LLM Listwise Reranker** (experimental) | `LLMListwiseReranker` using Haiku | Sends all chunks as a numbered list to an LLM, asks for JSON ranking. Parses `[{"rank": N, "doc_index": N, "relevance_score": 0-1}]`. Partial-parse fallback appends missing chunks at score 0.5. Total-parse failure -> input order at 0.5 |
| **Relevance Filter** | `RerankerSubgraph.run()` | Pre-filters: only passes `relevant=True` graded chunks to the reranker. Falls back to all chunks when none are marked relevant (avoids empty rerank) |
| **Confidence Scorer** | `RerankerSubgraph.run()` | `confidence_score = max(relevance_score)` across reranked chunks. If no chunks survive -> `0.0` (triggers CRAG retry) |

### Strategies

- **Cross-encoder as default, LLM as experiment**: Cross-encoder is fast (~50ms for 10 pairs), runs locally, no API cost. LLM listwise is for high-value queries where you want LLM judgment — swap via `RERANKER_STRATEGY=cross_encoder|llm_listwise`
- **Sigmoid normalization**: Cross-encoder raw logits are unbounded. The sigmoid maps them to `[0, 1]` so the confidence gate has a consistent threshold to compare against
- **Graceful LLM parse degradation**: The LLM reranker has 3 fallback levels: (1) full parse = use LLM ranking, (2) partial parse = use what parsed + append missing at 0.5, (3) total failure = return input order at 0.5. Never crashes, always returns results
- **Relevance pre-filter**: Only chunks already graded `relevant=True` by the retrieval CRAG grader go to the reranker. This protects against wasting reranker compute on clearly irrelevant noise

---

## 4. Generation Agent

**Location:** `generation/`, `orchestration/subgraphs/generation.py`

**Job:** Synthesize a grounded, cited response from the reranked chunks, with intent-aware prompting and a confidence gate for the CRAG loop.

### Tools

| Tool | Implementation | What it does |
|---|---|---|
| **Intent-Aware Prompt Library** | `prompts.py` -> `SYSTEM_PROMPTS` dict | 5 system prompts keyed by intent. LOOKUP: "answer directly, cite inline, don't speculate." EXPLORE: "synthesize across sources, highlight contradictions." COMPARE: "use structured format (table/bullets)." CONVERSATIONAL: "respond naturally." OUT_OF_SCOPE: "explain what you can help with." |
| **Context Assembler** | `generator.build_prompt()` | Joins top-k reranked chunks as `[Source: {url}]\n{text}` blocks separated by `---`. Injects into the last human message as "Use the following sources to answer..." Preserves full conversation history from `state["messages"]` |
| **LLM Caller** | `generator.call_llm()` | `ChatAnthropic(model=claude-sonnet-4-6).ainvoke()` via LangChain. Prepends system prompt as `SystemMessage`, passes conversation history. Returns raw text |
| **Citation Extractor** | `generator.extract_citations()` | Deduplicates `{url, title}` from reranked chunks in rank order. Produces the `citations` list attached to the response |
| **Confidence Gate** | `GenerationSubgraph.confidence_gate()` | Compares `confidence_score` (from reranker) against `confidence_threshold` (default 0.3). Below threshold -> sets `fallback_requested=True` -> triggers CRAG retry in the graph |

### Strategies

- **No retrieval for direct intents**: CONVERSATIONAL and OUT_OF_SCOPE queries skip the context block entirely — no "use the following sources" injection, just the system prompt + conversation history. This avoids confusion when there are no sources
- **Grounded message replacement**: The last human message in history is replaced with the context-augmented version. This means the LLM sees sources as part of the user's question, not as a separate injection — aligns with how Claude handles context
- **CRAG loop**: The confidence gate is a separate node from generation. If confidence is low, the graph loops back to retrieval (with incremented `retry_count`) instead of generating. After `max_crag_retries` (default 1), it generates from whatever context is available. This catches **search failures** (wrong chunks) without infinite looping
- **Citations by reference, not by extraction**: Citations come from the reranked chunk metadata (URL + title), not from parsing the LLM output. This is more reliable — LLMs sometimes mangle URLs. The chunks are already ranked, so citation order matches relevance

---

## 5. Eval Suite

**Location:** `eval_harness/`, `tests/librarian/evalsuite/`

**Job:** Measure retrieval quality, answer quality, and failure patterns — split into cheap CI-safe regression tests and expensive LLM-based capability tests.

### Tools

| Tool | Implementation | What it does |
|---|---|---|
| **Golden Dataset** | `evalsuite/conftest.py` -> `GOLDEN` (5 samples) | Hand-curated `GoldenSample` objects: query + expected doc URL + relevant chunk IDs + category. Aligned corpus (`CORPUS`) with keyword-matched chunks for deterministic retrieval |
| **Retrieval Evaluator** | `evaluate_retrieval()` | Runs each golden query through a retrieve function, computes hit_rate@k and MRR. Returns `(RetrievalMetrics, list[FailureCluster])` |
| **Pipeline Tracer** | `PipelineTracer` + `PipelineTrace` | Creates per-query traces with spans for retrieval, reranking, generation. Tracks latency, token counts, confidence scores, failure reasons. Exports to JSON |
| **Failure Clusterer** | `FailureClusterer` | Classifies failures into 11 types: `retrieval_failure`, `ranking_failure`, `generation_failure`, `grounding_failure`, `coverage_gap`, `complexity_failure`, `zero_retrieval`, `low_confidence`, `context_noise`, `timeout`, `unknown`. Groups by type, finds common query patterns (length, frequent terms), suggests fixes |
| **Answer Judge** | `AnswerJudge` (LLM-as-judge, Haiku) | Scores (question, context, answer) on 3 dimensions: faithfulness, relevance, completeness. Returns `JudgeResult` with `is_correct`, `score` (0-1), and reasoning. Cost-gated by `CONFIRM_EXPENSIVE_OPS` |
| **Closed-Book Baseline** | `ClosedBookBaseline` | Same questions, no retrieval context — LLM answers from parametric knowledge only. Compare against RAG answers to measure **retrieval lift**: `lift = rag_score - closed_book_score` |
| **LangFuse Score Push** | `_log_langfuse_scores()` | Opt-in: logs hit_rate and MRR as LangFuse scores attached to a trace ID. No-op if unconfigured |
| **Eval Run Config** | `EvalRunConfig` | Snapshots prompt version, model ID, corpus version, dataset label, top_k — logged alongside metrics for reproducibility |

### Test Tiers

| Tier | Location | Cost | What it tests |
|---|---|---|---|
| **Unit tests** | `tests/librarian/unit/` | Free — mocks only | Each component in isolation: schemas, chunker, retriever, reranker, generator, graph wiring, factory, storage, query understanding |
| **Regression tests** | `evalsuite/regression/` | Free — InMemory + MockEmbedder | `hit_rate@5 >= 0.6`, `MRR >= 0.4` against golden dataset. Also: metrics shape validation, no catastrophic failures (zero_retrieval absent), empty golden raises ValueError |
| **Capability tests** | `evalsuite/capability/` | Cheap (mocks) to expensive (LLM) | End-to-end routing correctness, CRAG termination, state key propagation. `AnswerJudge` grading with cost gate, error handling for parse/API failures |

### Strategies

- **Regression floors only go up, never down**: `HIT_RATE_FLOOR = 0.6`, `MRR_FLOOR = 0.4` — the comment says "update these (never lower them) when quality improves." This is a ratchet
- **Failure clustering as a diagnostic tool**: Not just "did it fail" but "why did it fail, how often, and what's the pattern." The `_suggest_fix()` method maps each failure type to actionable next steps
- **Cost-gated LLM evals**: `CONFIRM_EXPENSIVE_OPS` must be explicitly set to `True` to run `AnswerJudge` or `ClosedBookBaseline`. Default is `False`, enforced never to be committed as `True`. Estimated ~$0.01-0.03 per sample with Haiku
- **Retrieval lift measurement**: The `ClosedBookBaseline` is a clean experimental control — same questions, same model, no context. If RAG scores aren't meaningfully higher than closed-book, your retrieval isn't adding value
- **Golden sample tiering**: Each `GoldenSample` has `validation_level` (gold/silver/bronze/synthetic) and `difficulty` (easy/medium/hard). Supports stratified evaluation — track metrics by difficulty tier to see where the system breaks

---

## Cross-cutting: LangGraph State Machine

All five agents are wired together via a single `StateGraph(LibrarianState)`:

```
START -> analyze -> [3-way route]
                     |
          +----------+--------------+
          v          v              v
      retrieve   snippet_retrieve  generate (direct)
          |          |              |
          v          +---> generate |
       rerank                       |
          |                         |
          v                         |
        gate --- retry? ---> retrieve
          |                         |
          v                         |
       generate <-------------------+
          |
         END
```

The state (`LibrarianState` TypedDict) is the shared contract — every agent reads from and writes to it. No agent calls another directly. The graph topology is the only coupling, and it's defined in one 240-line file.

---

## Component Choice Summary

| Stage | Selected | Local/Free | Swap path |
|---|---|---|---|
| Chunking | `HtmlAwareChunker` (heading-boundary recursive) | Yes | `ParentDocChunker` for long docs |
| Embeddings | `intfloat/multilingual-e5-large` (1024-dim) | Yes | `e5-large-v2` (English-only), Voyage (cloud) |
| Vector store | ChromaDB (persistent, HNSW) | Yes | OpenSearch (prod), Qdrant (scale) |
| Hybrid retrieval | Term-overlap + cosine (0.3/0.7) | Yes | Native BM25+kNN in OpenSearch |
| Reranking | `ms-marco-MiniLM-L-6-v2` cross-encoder | Yes | `bge-reranker-large`, Cohere API |
| Generation | Claude Sonnet 4.6 (LangChain) | API key | Haiku (cheap), Ollama (free) |
| Query planner | Rule-based intent classifier | Yes | LLM classifier (`planning_mode=llm`) |
| Orchestration | LangGraph CRAG state machine | Yes | Custom pipeline |
| Observability | structlog + LangFuse (opt-in) | Yes | LangSmith, OpenTelemetry |

---

## Dependency Map

| Package | Used by | Purpose |
|---|---|---|
| `langgraph>=0.4.0` | Orchestration | State machine graph |
| `langchain-core>=0.3.0` | Generation | `SystemMessage`, `HumanMessage`, `AIMessage` types |
| `langchain-anthropic>=0.3.0` | Generation | `ChatAnthropic` wrapper |
| `sentence-transformers>=3.0.0` | Retrieval, Reranker | E5 embedder + cross-encoder |
| `chromadb>=0.6` | Retrieval | Local vector store (default) |
| `opensearch-py>=2.7.0` | Retrieval | Production vector store |
| `duckdb>=1.0` | Storage | Metadata + snippet FTS |
| `ragas>=0.2.0` | Eval | RAG evaluation (batch benchmarks) |
| `deepeval>=2.0.0` | Eval | RAG evaluation (CI regression) |
| `langfuse>=2.0.0` | Observability | Trace-level debugging (opt-in) |
| `numpy>=1.26` | Retrieval | Numerical operations |
| `scikit-learn>=1.4` | Eval/Retrieval | ML utilities |
