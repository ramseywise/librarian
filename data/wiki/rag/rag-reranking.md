---
title: RAG Reranking
tags: [rag, concept]
summary: Reranking strategies for RAG pipelines — cross-encoder vs LLM listwise, confidence scoring, and when each is appropriate.
updated: 2026-11-09
sources:
  - data/raw/claude-docs/playground/docs/archived/rag-tradeoffs.md
  - data/raw/claude-docs/playground/docs/archived/librarian-stack-audit.md
  - data/raw/claude-docs/playground/docs/archived/rag-agent-template-research.md
  - data/raw/agent-skills/langchain-rag/references/rag-strategies.md
  - data/raw/papers/2026-11-08-lakshmanan-hapke-genai-design-patterns-ch04-adding-knowledge-syncopation.md
---

# RAG Reranking

Reranking takes the broad recall set from retrieval and applies fine-grained relevance scoring to select the top-k most relevant chunks, with a confidence signal for the [[LangGraph CRAG Pipeline]] gate.

## Active: Cross-Encoder (`ms-marco-MiniLM-L-6-v2`)

`CrossEncoderReranker` scores each `(query, chunk.text)` pair through a cross-attention model. Raw logits → sigmoid → `[0, 1]` relevance score. Model loaded once, cached process-wide.

**Why cross-encoder as default:**
- Fast: ~50ms for 10 pairs on CPU
- Runs locally, no API cost
- Sigmoid normalization gives consistent `[0, 1]` scale for confidence gate comparison

**Sigmoid normalization:** cross-encoder raw logits are unbounded. The sigmoid maps them to `[0, 1]` so the CRAG confidence gate has a consistent threshold to compare against.

## Implemented Rerankers

| Reranker | Cost | Quality | When |
|---|---|---|---|
| ✅ `CrossEncoderReranker` (`ms-marco-MiniLM-L-6-v2`) | Local CPU | High | Default |
| 🔧 `LLMListwiseReranker` (Haiku) | Tokens/query | Highest | High-value queries; best quality |

**Select via:** `RERANKER_STRATEGY=cross_encoder|llm_listwise`

## LLM Listwise Reranker

Sends all chunks as a numbered list to Haiku, asks for JSON ranking: `[{"rank": N, "doc_index": N, "relevance_score": 0-1}]`.

**Graceful degradation (3 levels):**
1. Full parse → use LLM ranking
2. Partial parse → use what parsed + append missing chunks at score 0.5
3. Total failure → return input order at 0.5

Never crashes, always returns results.

**Cost:** ~$0.001/query at Haiku. **Latency:** 400–800ms. Use for experiment, not prod default.

## Relevance Pre-Filter

Only chunks marked `relevant=True` by the retrieval CRAG grader go to the reranker. This protects against wasting reranker compute on clearly irrelevant noise.

**Fallback:** when none are marked relevant, all chunks pass to the reranker (avoids empty rerank).

## Confidence Score

`confidence_score = max(relevance_score)` across reranked chunks. If no chunks survive → `0.0` (triggers [[CRAG Retry Logic]]). This flows to the `QualityGate` node.

## n-Candidates Rule of Thumb

Retrieve k=10 → CRAG grade → 3–6 relevant → rerank → top 3 for generation.

Too many into reranker → latency spike. Too few → no gain over CRAG grading alone.

## Alternatives

| Alternative | Notes |
|---|---|
| `BAAI/bge-reranker-large` | State-of-the-art on BEIR; 4× larger; worth it for production |
| `cross-encoder/ms-marco-MiniLM-L-12-v2` | Slightly better precision; 2× slower |
| **Cohere Rerank API** | Best managed reranking; costs $; data leaves infra |
| **RRF** | No model; combine multiple ranked lists; no learned scoring |
| **No reranking** | Set `confidence_threshold=0.0` to disable CRAG loop |

**Reranker caveat:** at small corpus sizes (<1K chunks), cross-encoder reranking can *degrade* quality by overfitting to surface-level similarity. Test on actual corpus before committing to reranking.

## Node postprocessing options (Lakshmanan and Hapke, ch. 4)

The chapter's Pattern 10 inserts a step between retrieval and generation. Options: use a reranker, LLM-based or fine-tuned, because an embedding must squeeze a chunk into one vector; merge two retrievers when the store lacks hybrid search; compress each chunk to the query-relevant text; filter obsolete chunks by metadata such as latest year rather than pairwise LLM checks (N*(N-1) calls versus N-1 when each chunk is checked only against the first); add conversation summary and user history for personalization. Each model call per node raises latency and cost; a single structured-output call can do compression, disambiguation and scoring together, which saves calls but excludes a dedicated fine-tuned reranker. In a geology example (two old textbooks, one query) top_k=2 and top_k=4 both answered wrongly, and compressing plus reranking fixed it.

Limits of this section:
- Every example is one illustrative query on one corpus; no metric or baseline. The claim that rerankers beat embedding models is uncited.

## See Also
- [[Text-to-SQL as a Retrieval Strategy]] <!-- auto-linked -->
- [[Agentic RAG — Advanced Patterns]] <!-- auto-linked -->
- [[LangGraph CRAG Pipeline]]
- [[RAG Retrieval Strategies]]
- [[RAG Evaluation]]
- [[CRAG Retry Logic]]
- [[Reciprocal Rank Fusion (RRF)]]
- [[Specificity-Adaptive Ranking and Slate Composition]] — alternative-to (a deterministic rubric over catalogue rows instead of a learned reranker)
- [[Borderline-Band Sufficiency Probe]] — extends (rerank scores as ordinal signals with an LLM tiebreak in the uncertain band)
- [[RA-DIT Dual Instruction Tuning]] — related (tunes the retriever's query encoder from the LM)
- [[Soft Context Compression for RAG (CLaRa and REFRAG)]] — alternative-to (a generator-trained scorer in place of a separate reranker)
- [[Pairwise Ranking Prompting (PRP)]] — instance-of (prompted pairwise comparison as the reranker)
- [[RankZephyr Listwise Reranker Distillation]] — instance-of (an open listwise reranker distilled from GPT models)
- [[RAG Survey Taxonomies]] — related (survey vocabulary for re-ranking versus filtering)
- [[monoBERT duoBERT Multi-Stage Ranking]] — instance-of (pointwise then pairwise BERT rerankers)
- [[KnowledGPT Unsupervised Knowledge Selection]] — alternative-to (learned sentence selection)
- [[RankRAG]] — instance-of (generator also reranks)
- [[FollowIR Instruction-Following Retrieval Benchmark]] — related (benchmark for instruction-following in rankers)
- [[HtmlRAG HTML as Retrieval Format]] — related (prunes HTML blocks by embedding and generative scores)
