# RAG Pipeline Component Tradeoffs

**Source:** rag-tradeoffs.md, rag-agent-template-research.md  
**Relevance:** Decision log per pipeline stage — what to pick and why at each layer

---

## Chunking

| Strategy | Best for | Notes |
|----------|---------|-------|
| **Heading-boundary recursive** (`HtmlAwareChunker`) | HTML/markdown docs | Split at `##`/`###` first, recursive fallback. Best for structured help docs. |
| **Parent/child** (`ParentDocChunker`) | Long docs | Small child chunks indexed, parent returned for generation. Best precision + context. |
| **Overlapping windows** | Dense technical text | Reduces boundary misses. More redundant embeddings. |
| Fixed windows | Baseline benchmarking only | Hard word splits, no overlap. Don't use in prod. |
| Adjacent with neighbour lookup | Context expansion at query time | Stores positional IDs for `neighbors(chunk_id)`. |
| Sentence-level (spaCy/NLTK) | Skip | Chunks too small for BM25; NLP dependency; poor on code/URLs. |
| Semantic (embedding-based) | Skip | Expensive at ingest; inconsistent chunk sizes hurt BM25. |
| Proposition (LLM per chunk) | Skip | LLM per chunk at ingest is too expensive. |

**Key finding:** `min_tokens=50` default drops very short section bodies. Multi-sentence content required. `HtmlAwareChunker` re-detects headings from plain text via regex — a section-aware chunker consuming `doc["sections"]` directly would be more reliable.

---

## Embeddings

| Model | Dims | Multilingual | Notes |
|-------|------|-------------|-------|
| `intfloat/multilingual-e5-large` | 1024 | ✓ (100 langs) | **Recommended default.** Proven in production. E5 prefix rules required. |
| `all-MiniLM-L6-v2` | 384 | ✗ | Silent fails on non-English — **never use for Danish/multilingual.** |
| `BGE-M3` | 1024 | ✓ (100 langs) | Claimed better; not yet benchmarked vs E5. |
| `voyage-3` (Anthropic) | — | ✓ | Best-in-class for code+docs; API cost; data leaves infra. |
| `text-embedding-3-*` (OpenAI) | — | ✓ | High MTEB on English; API cost. |

**Critical:** E5 prefix rules are non-negotiable. `"query: "` prefix at search time, `"passage: "` prefix at index time. Violating them silently degrades recall 15–20%. Enforce at protocol level, not implementation.

---

## Vector Store

| Backend | Strategy | When to use |
|---------|----------|-------------|
| **ChromaDB** (persistent, local) | HNSW + term-overlap | Default for dev and small prod. Zero infrastructure. |
| DuckDB | Brute-force cosine + term-overlap | Already using DuckDB for analytics; SQL joins needed. O(n) — fine up to ~50k chunks. |
| **OpenSearch** | Native BM25 + k-NN | Production, multi-tenant. True BM25 (Chroma's is an approximation). |
| InMemory | Linear scan | Unit tests only. |

**Chroma limitations:** no native BM25 (term overlap is an approximation), single-process write lock, no auth/multi-tenancy.

---

## Retrieval Strategy (Hybrid Search)

| Strategy | Notes |
|----------|-------|
| **Hybrid BM25 + vector** (0.3/0.7 weights) | **Recommended.** Covers both keyword-exact and semantic queries. |
| Vector-only | Misses exact keyword matches (product names, error codes). |
| BM25-only | Misses semantic paraphrases; query must share vocabulary with doc. |
| RRF (Reciprocal Rank Fusion) | More principled fusion; no weight tuning; needs ranked lists. |
| SPLADE learned sparse | Outperforms BM25 on BEIR; requires fine-tuned model. |

**Production benchmarks (RAPTOR v1, Danish market):**

| Strategy | Precision@5 | Recall@5 | Hit Rate |
|----------|------------|---------|---------|
| Dense only | 0.15 | 0.18 | 45% |
| Sparse (BM25) | 0.12 | 0.25 | 50% |
| Hybrid (RRF) | 0.20 | 0.28 | 58% |
| **Hybrid + cross-encoder reranker** | **0.28** | **0.32** | **68%** |

Hybrid alone is +13pp hit rate over dense-only. Adding cross-encoder reranker adds another 10pp.

**Danish BM25 note:** configure language-specific stemmer explicitly — default (English) stemmer silently degrades on Danish morphology.

---

## Reranking

| Option | Latency | Quality | Notes |
|--------|---------|---------|-------|
| **Cross-encoder** (`ms-marco-MiniLM-L-6-v2`) | 50–100ms | High | **Recommended default.** ~22MB, no API key. |
| `BAAI/bge-reranker-large` | ~200ms | Higher | State-of-the-art on BEIR; 4× larger. Worth it for production. |
| LLM listwise (Haiku) | 400–800ms | High | Best quality; use for A/B eval, not prod default. |
| Cohere Rerank API | 100–300ms | Highest | Managed; costs $; data leaves infra. |
| RRF | ~0ms | Medium | No model; combine multiple ranked lists. Use as baseline. |
| No reranking | ~0ms | — | Fine when retrieval quality is already high. |

**n-candidates rule:** retrieve k=10 → CRAG grade → 3–6 relevant → rerank → top 3 for generation. Don't send 10 chunks to LLM reranker — it will blow the latency budget.

**Caveat:** at small corpus sizes (<1K chunks), cross-encoder reranking can degrade quality by overfitting to surface-level similarity. Test on actual corpus before committing.

---

## Query Planning

| Approach | Latency | Notes |
|----------|---------|-------|
| **Rule-based regex** | ~0ms | **Recommended default.** Zero cost, deterministic, regression-testable. |
| LLM classifier (Haiku structured output) | ~200ms | Higher accuracy on ambiguous/multi-intent queries. Add as `planning_mode="llm"` option. |
| Fine-tuned classifier (DistilBERT/SetFit) | Fast | Requires labelled data; overkill for <10 intent classes. |
| Semantic similarity to exemplars | Medium | No training data; add as fallback when rule confidence < threshold. |

---

## Observability

| Tool | Notes |
|------|-------|
| **Langfuse (self-hosted)** | Native ragas + deepeval integrations. Free. Self-host for GDPR. **Start here.** |
| LangSmith | Native LangGraph integration, annotation queues, prompt playground. Enterprise for on-prem. Switch when annotation queues are needed. |
| Prometheus + Grafana | Add when serving HTTP in production. |
| OpenTelemetry | Vendor-neutral distributed tracing. Add for cloud deployment. |

---

## Eval Frameworks

| Tool | Use for |
|------|---------|
| **ragas** | Corpus-level quality benchmarks (`faithfulness`, `context_precision`, `context_recall`). Run after corpus changes. Native Langfuse integration. |
| **deepeval** | CI regression testing. pytest plugin. `HallucinationMetric`, `FaithfulnessMetric`, `GEval`. |

Use both: ragas for experiments, deepeval for CI.

---

## Latency Budget (Full Pipeline)

| Component | Latency | Notes |
|-----------|---------|-------|
| Query rewrite (Haiku) | ~200ms | Skip if single-turn or no coreference signals |
| Retrieval (OpenSearch hybrid) | ~50–100ms | Cannot skip |
| CRAG grading (Haiku, 5 chunks) | ~300ms | Skip for `chit_chat` intent |
| Reranker (cross-encoder) | ~50–100ms | Configurable |
| Reranker (LLM listwise) | ~400–800ms | Experiment only |
| Generation (Sonnet, streaming) | ~800–1500ms | Use streaming to hide latency |
| **Cross-encoder path total** | **~1.4–2.1s** | Acceptable |

---

## Production Chunk Metadata Schema

Minimum fields for template; production fields additive (all `None` by default):

```python
class ChunkMetadata(BaseModel):
    # Template minimum
    url: str
    title: str
    section: str | None = None
    language: str = "da"
    doc_id: str
    parent_id: str | None = None

    # Production additions
    market: str | None = None            # "dk", "de", "nl" — for market filtering
    product_area: str | None = None      # "billing", "tax_filing" etc
    content_type: str | None = None      # "faq", "guide", "policy"
    plan_tier: str | None = None         # "starter", "pro", "enterprise"
    last_updated: str | None = None      # ISO 8601 — freshness
    completeness_score: float | None = None  # quality gate at ingest
```

Pass user context (market, language, plan_tier) from authenticated session to filter at ANN query time, not post-retrieval.

---

## See Also
- [agentic-rag-patterns.md](agentic-rag-patterns.md) — Self-RAG, CRAG, GraphRAG, HyDE
- [rag-integration-strategy.md](rag-integration-strategy.md) — RAG as a service vs subgraph
- [../evaluation-and-learning/eval-harness.md](../evaluation-and-learning/eval-harness.md)
