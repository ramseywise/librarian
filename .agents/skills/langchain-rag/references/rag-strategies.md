# RAG Strategies — Patterns and Decisions

> Source: `.claude/docs/backlog/rag-agent-template/research.md`
> Date: 2026-04-09. Drawn from help-assistant + listen-wiseer production experience.

---

## Multi-turn conversation

### The core problem
Single-turn RAG can't handle pronouns, follow-ups, or topic continuations.

### Approaches

| Approach | Tradeoff |
|---|---|
| Full history in context | Simple, degrades at ~10 turns |
| Summarized history | Adds latency, loses detail |
| **History-aware query rewriting** | Best retrieval quality — small Haiku call before retrieve |
| Retrieval-augmented memory | Cross-session recall — Phase 2 |

### Implemented pattern
`rewrite_query` node fires when coreference signals detected (`" it "`, `" they "`, `"the artist"`).
Resolves last 5 turns into standalone question. Single Haiku call, ~200ms.

### LangGraph memory options
- `MemorySaver` — in-process, tests and single-instance
- `AsyncRedisSaver` (TTL 24h) — Fargate / multi-instance prod
- `BaseStore` with namespaced vectors — episodic memory across sessions

---

## Chunking strategies

| Strategy | Mechanism | Verdict |
|---|---|---|
| `html_aware` | Heading-boundary split → recursive fallback | **Primary** — best for structured help docs |
| `fixed` | Hard word splits, no overlap | Baseline benchmark only |
| `overlapping` | Fixed + configurable overlap | Better recall, more redundant embeddings |
| `parent_doc` | Small child chunks indexed, parent returned | Best precision + context; needs two-level index |
| `section_aware` | Consumes `doc["sections"]` from scraper | Future — higher fidelity |
| `proposition` | LLM rewrites each fact as standalone | Skip — too expensive at ingest |

**Key gotcha:** `min_tokens=50` drops very short section bodies — test corpus needs multi-sentence content.

---

## Retrieval strategies

| Strategy | How | Verdict |
|---|---|---|
| **Hybrid BM25 + k-NN** (OpenSearch) | Server-side score fusion | **Default** — beats Python-side merging |
| Dense only (k-NN) | Pure vector similarity | Lower recall on keyword queries |
| Sparse only (BM25) | TF-IDF | Poor on semantic/paraphrase |
| **Multi-query (RAG-Fusion)** | N variants → retrieve each → dedup | +10–15% recall |
| **HyDE** | Generate hypothetical answer → embed that | Good for factual queries; adds 1 LLM call |
| Step-back | Abstract to broader question first | Good for procedural; not evaluated |
| A-RAG tool routing | Keyword/semantic/chunk-level as LLM tools | +5–13% QA accuracy; adds agentic overhead |

### Current implementation
`hybrid_search(query_text, query_vector, k=5, bm25_weight=0.3, vector_weight=0.7)`
3 query variants from `QueryAnalyzer`, deduped by chunk.id.

### Embedder
`intfloat/multilingual-e5-large` (1024-dim). **E5 prefix rule is critical:**
- `"query: "` prefix for queries
- `"passage: "` prefix for indexed documents

This rule must live in the abstract `Embedder` protocol, not the implementation.

### BM25 Danish stemmer
BM25 with default (English) stemmer silent-fails on Danish. Configure explicitly:
```python
from bm25s.tokenization import Tokenizer
tokenizer = Tokenizer(stemmer=Stemmer("danish"))
```

---

## CRAG (Corrective RAG)

```
query → retrieve → grade all chunks → sufficient? → generate
                         ↓ none pass
                  rewrite + re-retrieve (1 retry) → generate anyway
```

Haiku grades each chunk (score ≥ 0.5 = relevant). `retry_count` cap = 1 in prod.

**Gotcha:** `grade_docs` increments `retry_count` before returning (first run = count 1).
`check_sufficient` allows retry when `retry_count < 2` — exactly one actual retry. Document clearly.

---

## Reranking

| Option | Latency | Quality | Notes |
|---|---|---|---|
| **Cross-encoder** (MiniLM-L-6-v2, ~22MB) | 50–100ms | High | **Default** — same dep as embedder |
| **LLM listwise** (Haiku) | 400–800ms | High | ~$0.001/query — experiment only |
| Cohere Rerank API | 100–300ms + network | Highest | Data leaves infra |
| ColBERT | ~20ms with index | Very high | Heavy ops (PyColBERT/Vespa) |

**n-candidates rule:** retrieve k=10 → CRAG grade → 3–6 relevant → rerank → top 3 for generation.

**Protocol:**
```python
class Reranker(Protocol):
    def rerank(self, query: str, chunks: list[GradedChunk], top_k: int) -> list[RankedChunk]: ...
```

**Caveat:** at small corpus sizes (<1K chunks), cross-encoder can degrade quality by overfitting to surface similarity. Test on actual corpus first.

---

## Intent classification and routing

### Rule-based (default, zero cost)
Keyword/regex matching → `{factual, procedural, exploratory, troubleshooting}`.
`TERM_EXPANSIONS` dictionary for domain terminology. Complexity: `simple/moderate/complex`.

**Where it breaks:** ambiguous queries, multi-intent, cross-lingual.

### LLM-based (optional via `planning_mode` config)
```python
class QueryPlan(BaseModel):
    intent: Literal["how_to", "troubleshoot", "reference", "chit_chat", "out_of_scope"]
    tools_to_use: list[Literal["rag", "snippets_db", "direct"]]
    needs_clarification: bool
    confidence: float

plan = await haiku.with_structured_output(QueryPlan).ainvoke(query)
```
~200ms, ~$0.001/query. Handles ambiguous / multi-intent naturally.

---

## Observability: LangFuse vs LangSmith

| | LangFuse | LangSmith |
|---|---|---|
| ragas native integration | ✓ | ✗ (custom evaluator needed) |
| deepeval native integration | ✓ `DeepEvalCallbackHandler` | ✗ |
| LangGraph tracing | Via callback handler | First-class (graph state transitions) |
| Self-hostable | ✓ Docker Compose | ✗ (enterprise for on-prem) |
| GDPR | ✓ | ✗ |
| Annotation queues | ✗ | ✓ |

**Decision: LangFuse for MVP.** Switching later is a one-line import change.

LangFuse must be optional — `LANGFUSE_ENABLED=true` activates it. structlog as always-on baseline.

---

## Latency budget (p95 targets)

| Component | Latency | Notes |
|---|---|---|
| Query rewrite (Haiku) | ~200ms | Skip if single-turn |
| Retrieval (OpenSearch hybrid) | ~50–100ms | — |
| CRAG grading (Haiku, 5 chunks) | ~300ms | Skip for `chit_chat` |
| Reranker (cross-encoder) | ~50–100ms | Configurable |
| Reranker (LLM listwise) | ~400–800ms | Experiment only |
| Generation (Sonnet) | ~800–1500ms | Use streaming to hide |
| **Total (cross-encoder path)** | **~1.4–2.1s** | Acceptable |

---

## Production benchmarks (from RAPTOR v1 — Danish market)

| Strategy | Hit Rate | Precision@5 |
|---|---|---|
| Dense only | 45% | 0.15 |
| Sparse (BM25) | 50% | 0.12 |
| Hybrid (RRF) | 58% | 0.20 |
| **Hybrid + cross-encoder** | **68%** | **0.28** |

Baseline (v1) hallucination rate was 48% — root cause was corpus gaps, not the model.

**Response style finding:** RAPTOR suggestions were ignored by human agents despite correct content
because they were 3× too long with hedging language. Generation prompts must enforce direct,
actionable language with max length configured.

---

## Eval framework

- **ragas** — RAG-specific batch benchmarking: `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`
- **deepeval** — CI regression: pytest plugin, `GEval`, `HallucinationMetric`
- Both log to LangFuse via native handlers
