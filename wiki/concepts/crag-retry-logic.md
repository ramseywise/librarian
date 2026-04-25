---
title: CRAG Retry Logic
tags: [rag, langgraph, concept]
summary: The confidence-gated conditional back-edge in a CRAG pipeline that re-enters retrieval when the reranker's top score falls below threshold — preventing low-confidence answers from reaching the user.
updated: 2026-04-24
sources:
  - raw/playground-docs/librarian-stack-audit.md
  - raw/playground-docs/rag-agent-template-research.md
---

# CRAG Retry Logic

CRAG (Corrective RAG) adds a quality gate after reranking. If the best-scored chunk doesn't meet a confidence threshold, the pipeline loops back to the retriever with a reformulated query rather than generating a low-confidence answer.

## The Mechanism

```
retrieve → rerank → [confidence gate] → generate  (if score >= threshold)
                          ↓
                     reformulate → retrieve → ...  (if score < threshold)
```

The gate evaluates `max(relevance_score)` across reranked chunks. The threshold is typically `0.4` (configurable). On failure, a reformulation step rewrites the query (usually via Haiku) and re-enters retrieval.

## In LangGraph

Implemented as a conditional edge:

```python
def route_after_rerank(state: LibrarianState) -> str:
    if state["confidence_score"] >= CONFIDENCE_THRESHOLD:
        return "generate"
    elif state["retry_count"] < MAX_RETRIES:
        return "reformulate"
    else:
        return "generate_with_low_confidence"

graph.add_conditional_edges("rerank", route_after_rerank)
```

`retry_count` prevents infinite loops. `MAX_RETRIES=2` is a sensible default.

## The Confidence Score

Produced by [[RAG Reranking]] — specifically, the max relevance score from the cross-encoder after sigmoid normalization. Values are [0,1]. A score of `0.4` means "the best chunk is moderately relevant."

The same score appears in:
- The API response `escalate` signal (frontend can surface uncertainty)
- [[RAG Evaluation]] metrics (low confidence → retrieval or ranking failure)
- [[HITL Annotation Pipeline]] signal-based queue (confidence < 0.4 → human review)

## Cost of Retry

Each retry adds: ~100ms Haiku reformulation + ~150ms retrieval + ~300ms reranking. Budget for CRAG retry latency target: P95 ≤ 4s (vs 2s for single-pass).

## See Also
- [[LangGraph CRAG Pipeline]]
- [[RAG Reranking]]
- [[RAG Evaluation]]
- [[Reciprocal Rank Fusion]]
