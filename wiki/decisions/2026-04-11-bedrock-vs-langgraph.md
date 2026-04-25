---
title: Bedrock KB vs LangGraph Decision
tags: [rag, infra, decision]
summary: Decision framework for Bedrock Knowledge Bases vs. LangGraph CRAG pipeline — quality, observability, cost, and migration path analysis.
updated: 2026-04-24
sources:
  - raw/playground-docs/bedrock-kb-research.md
  - raw/playground-docs/librarian-architecture-decisions.md
---

# Bedrock KB vs LangGraph Decision

**Date:** 2026-04-11  
**Status:** Decision framework established — start with Bedrock for TS prototype, migrate to Polyglot (Option C) once eval validates LangGraph CRAG quality

## Head-to-Head

### Retrieval Quality

**Bedrock KB:** AWS-managed dense vector only — no BM25 hybrid, no keyword fallback, fixed chunking, no reranking. Single-strategy black box.

**LangGraph (Librarian):** Hybrid BM25 + vector (configurable weights), multi-query expansion (RRF across N reformulations), cross-encoder reranker (+10–20% hit_rate improvement vs cosine-only), CRAG retry loop.

**Verdict:** Librarian is measurably better for domain-specific or technical corpora where term overlap matters (code, product names, version numbers, jargon).

### Multi-Turn Accuracy

**Bedrock KB:** `sessionId` parameter passes history, but no explicit query reformulation. "What about the Python version?" sent verbatim to retriever — silently degrades on coreference.

**LangGraph:** `HistoryCondenser` node rewrites latest user query to be self-contained given prior turns. Only fires on multi-turn (single-turn: zero added latency). Uses Haiku (~$0.001/rewrite).

**Verdict:** Bedrock KB's session handling silently degrades on coreference-heavy conversations. The condenser prevents retrieval misses that look like hallucinations.

### Observability and Failure Diagnosis

**Bedrock KB:** Response: answer text + citations list. Nothing else. "Why did it give a wrong answer?" → no answer.

**LangGraph:** Full structured logs per node, `confidence_score` (0–1), `retrieved_chunks`/`graded_chunks`/`reranked_chunks` in state, `failure_reason` in eval traces, `FailureClusterer` for batch diagnosis, optional LangFuse.

**Verdict:** When Bedrock KB fails, you can't tell why. When Librarian fails, you can diagnose it to the exact node and fix it. This compounds over time.

### Latency

| Step | Bedrock KB | Librarian (warm, streaming) |
|---|---|---|
| Embed query | ~100ms (AWS-managed) | ~100–200ms (local) |
| Vector retrieve | ~200ms (OpenSearch Serverless) | ~50ms (Chroma local) |
| Rerank | None | ~200–500ms (cross-encoder CPU) |
| Generate (Claude) | Included in API call | ~400–800ms TTFT |
| **Total** | **1–2.5s (blocking, no stream)** | **~800ms–1.5s TTFT (streaming)** |

Bedrock KB's `RetrieveAndGenerate` is a single blocking call — no streaming token delivery. Librarian streams from the generation node.

### Cost Structure

**Bedrock KB:** ~$0.0005–0.001/query (OpenSearch Serverless + embedding). Gets expensive at >10K queries/day. Zero fixed infra.

**Librarian on ECS/Fargate:** Fixed ~$50–80/month for always-on 2vCPU/4GB task. Variable: Claude model tokens only (no embedding API cost with local model). Cheaper above ~5K queries/month.

### Vendor Lock-In

**Bedrock KB:** AWS OpenSearch Serverless (proprietary), AWS-managed vector store (not portable), re-embedding required to switch.

**LangGraph:** Chroma (portable) or OpenSearch (self-managed), any embedding provider, runs anywhere Python runs.

## When Bedrock KB is Right

1. Corpus is stable and well-structured — standard prose documents, not code or mixed-language
2. No budget for always-on infra — serverless, zero fixed cost
3. Speed to launch is the priority — no model to run, no pipeline to configure
4. Acceptable to accept black-box retrieval — you don't need to explain why answers were wrong
5. Low query volume (<5K/month)

## When LangGraph is Right

1. Retrieval quality matters — technical docs, code, domain-specific jargon, version numbers
2. Multi-turn conversations are core UX — coreference resolution critical
3. Need to improve over time — can't improve what you can't observe
4. Higher volume (>5K/month) — fixed cost amortises
5. Corpus requires custom chunking or access tiers
6. Streaming perceived latency matters — blocking Bedrock vs. token-streaming Librarian

## The Migration Path

```python
# TS tool: one function change
async function fetch_support_knowledge(query: string): Promise<Passages> {
  if (process.env.ORCHESTRATION_STRATEGY === "bedrock") {
    return await queryBedrock(query);
  }
  // Migrate to Python service
  return await queryLibrarianService(query);
}
```

Add `/query` endpoint to playground → change `fetch_support_knowledge` from Bedrock SDK to HTTP call → keep Bedrock call behind env flag for rollback. **This is one function change in one file.**

## The Tradeoff Matrix

| Dimension | Full Bedrock (A) | Full LangGraph (B) | Polyglot (C) |
|---|---|---|---|
| Retrieval quality | Fixed (Bedrock default) | Configurable CRAG | Configurable CRAG |
| Latency | ~100-200ms | ~150-300ms | ~200-400ms (+1 hop) |
| Operational complexity | Low | Medium | Medium-High |
| Eval pipeline usability | None | Full | Full |
| Knowledge iteration speed | Slow (S3 sync + KB rebuild) | Fast | Fast |
| Observability | CloudWatch only | Full OTEL | Full OTEL |
| Infrastructure | Zero | One service | Two services |
| Long-term scalability | Constrained by Bedrock | High | High |
| Migration risk | Low | Medium | Low (A→C is 1 fn change) |

## Recommendation

**Start with Option A (Bedrock) for the TS prototype, migrate to Option C (Polyglot) once eval validates LangGraph CRAG quality.**

The eval gate: add `BedrockRetriever` adapter to the eval pipeline so Bedrock KB can be benchmarked against LangGraph CRAG on the same test set (hit_rate, MRR, faithfulness). This is the missing data point that should drive the A vs C decision.

## See Also
- [[ADK vs LangGraph Decision]]
- [[Orchestration Architecture Decision]]
- [[Librarian RAG Architecture]]
- [[RAG Evaluation]]
- [[Evaluation & Improvement Project (VIR)]] — concrete use case: Billy → Bedrock KB ingestion for HC Virtual Assistant MVP
