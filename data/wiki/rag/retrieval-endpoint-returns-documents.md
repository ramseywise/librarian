---
title: Retrieval Service Returns Documents, Not Answers
tags: [rag, decision]
summary: When several agents share one RAG service, expose a retrieval-only endpoint (plan, retrieve, rerank, gate, then return documents) and let each calling agent own context injection and answer synthesis; latency profiling showed the answer LLM call dominates anyway.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/docs/plans/support-rag-orchestration.md
  - data/raw/repos/playground/.claude--docs--plans--support-rag-orchestration.md
  - data/raw/claude-docs/playground/docs/plans/rag-latency-optimization.md
  - data/raw/claude-docs/playground/docs/research/rag/rag-integration-strategy.md
  - data/raw/repos/playground/.claude--docs--plans--rag-latency-optimization.md
---

# Retrieval Service Returns Documents, Not Answers

A refactor in the playground repo (2026-04). One support-RAG service was called by two
virtual-assistant orchestrators, one built on LangGraph and one on Google ADK.

## Before

Both orchestrators called a `/chat` endpoint, and the RAG service ran its whole graph:
planner, retriever, reranker, answer, post-answer evaluation. The assistants got back a
finished answer. That meant two orchestration layers each doing routing, retries and
synthesis, and the caller couldn't add what only it knew (page URL, user intent,
conversation state) to the prompt.

## Decision

Split ownership at the documents:

- **The RAG service owns** query planning, retrieval, reranking and quality gates. A new
  retrieval subgraph stops after the rerank gate and returns a typed
  `RetrievalOutput {query, documents, confidence_score, escalated, latency_ms}` from
  `/retrieval`.
- **The calling agent owns** routing, context injection, answer synthesis and retry. The
  LangGraph caller puts the documents into `tool_results` and its format node writes
  the answer. The ADK caller's knowledge-search tool returns a document summary, and
  the support agent's LLM writes the answer.
- **The full `/chat` pipeline stays** for direct users and evals. Backward compatibility
  costs nothing here.

Benefits claimed: retrieval strategies can change without touching synthesis, each
stage can be tested on its own, and the retrieval-only call skips the answer LLM.

## Why it also pays on latency

Profiling the full pipeline on one support query gave about **336 ms for retrieval**
(embedding, ANN search and cross-encoder rerank), against about **5.7 s for answer
generation**: roughly 6.1 s in total. Most of the 11 graph nodes were sub-millisecond
policy checks. *The graph was not the problem; the LLM call was.* So:

- **Streaming the answer** (async `astream` in the answer node) was the first and
  cheapest win. It cut perceived time-to-first-token from about 6 s to about 1 s without
  changing total latency.
- Next on the list were a smaller answer model, fewer context chunks
  (`RAG_ANSWER_CONTEXT_MAX_CHUNKS` 3 vs 5) and skipping the reranker on high-confidence
  retrievals. All were measured against a golden set (hit rate, MRR, latency) before
  adoption.
- Moving synthesis to the caller means the caller, which owns the user-facing stream,
  is the one streaming tokens.

## Dual track before the refactor

An earlier integration-strategy review framed the choice as two tracks that share one
retrieval library and one index. Track 1 was a thin retrieval tool behind the existing MCP
signature, with no gates and no multi-node graph. Track 2 was the full agentic RAG graph,
kept as an experiment for calibrating thresholds and testing whether reranking and the
post-answer evaluator earn their latency. Complexity moves from Track 2 into Track 1 only
when eval data supports it. The review also found the agent's HITL gates useless in
autonomous mode: see [[HITL Gate Without a Resumer]].

## See Also
- [[Librarian RAG Architecture]] — related (same retrieval-as-tool contract on the librarian side)
- [[ADK vs LangGraph Comparison]] — related (two orchestrators sharing one retrieval backend)
- [[RAG Retrieval Strategies]] — extends
- [[Borderline-Band Sufficiency Probe]] — related (the quality gates the retrieval service keeps)
- [[HITL Gate Without a Resumer]] — related (why the retrieval service dropped its interrupt gates for autonomous callers)
