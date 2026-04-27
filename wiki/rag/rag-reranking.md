---
title: RAG Reranking
tags: [rag, concept]
summary: Reranking strategies for RAG pipelines — cross-encoder vs LLM listwise, confidence scoring, and when each is appropriate.
updated: 2026-04-24
sources:
  - raw/playground-docs/rag-tradeoffs.md
  - raw/playground-docs/librarian-stack-audit.md
  - raw/playground-docs/rag-agent-template-research.md
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

## See Also
- [[LangGraph CRAG Pipeline]]
- [[RAG Retrieval Strategies]]
- [[RAG Evaluation]]
- [[CRAG Retry Logic]]
- [[Reciprocal Rank Fusion (RRF)]]
