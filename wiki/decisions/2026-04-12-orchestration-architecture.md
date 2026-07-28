---
title: Orchestration Architecture Decision
tags: [langgraph, adk, infra, decision]
summary: Three architecture options for the Librarian service deployment — full Bedrock, full LangGraph, or polyglot — with tradeoffs and the recommended migration path.
updated: 2026-04-24
sources:
  - raw/playground-docs/librarian-architecture-decisions.md
  - raw/playground-docs/orchestration-rollout-plan.md
---

# Orchestration Architecture Decision

**Date:** 2026-04-12  
**Status:** Decided — start A (Bedrock), migrate to C (Polyglot) once eval validates quality

## Option A — Full Bedrock (TS-Native Stack)

```
ts_google_adk (Next.js)
  └── accountingAgent (LlmAgent)
        └── fetch_support_knowledge → AWS Bedrock KB
```

No Python service. All knowledge retrieval delegated to Bedrock Knowledge Base.

**What you give up:** CRAG retry logic, caching layer, custom reranking, multi-query expansion, eval pipeline integration, deduplication and grading.

**What you gain:** zero infrastructure, AWS-native (CloudWatch, IAM, S3 ingest), low operational burden, simple auth (one AWS credential).

**Verdict:** right for early prototyping. Wrong long-term — retrieval quality can't be iterated on without rebuilding the KB. The eval data collected in playground becomes orphaned.

**When to choose:** the team doesn't own knowledge quality iteration.

## Option B — Full LangGraph (Python-Owned Stack)

```
py_copilot (FastAPI + Google ADK)
  └── accountingAgent (LlmAgent)
        └── fetch_support_knowledge → POST /query → playground FastAPI
                                          └── build_graph() (LangGraph CRAG)
```

Python service owns everything. TS prototype retired or becomes UI-only thin client.

**What you give up:** TS ADK ecosystem, proximity to UI, existing TS prototype investment.

**What you gain:** single orchestration language, eval pipeline directly measures production, LangGraph CRAG gives full control, full OTEL observability.

**Verdict:** highest retrieval quality ceiling, best observability, most operational complexity. Right when the team owns knowledge quality and has Python infra capacity.

## Option C — Polyglot (TS Copilot + Python Knowledge Service)

```
ts_google_adk (Next.js)
  └── accountingAgent (LlmAgent)
        └── fetch_support_knowledge → HTTP → Python librarian-service (FastAPI)
                                                └── LangGraph CRAG pipeline
```

TS handles execution tools + UI. Python handles knowledge retrieval. Clear boundary.

**Service contract:**
```
POST /query
{
  "queries": ["string"],     // 1-3 search queries from LLM
  "session_id": "optional",
  "org_id": "optional"
}

Response:
{
  "passages": [{"text": "...", "url": "...", "title": "...", "score": 0.87}],
  "retrieval_strategy": "crag|bedrock|hybrid",
  "query_count": 3,
  "latency_ms": 142
}
```

**What you give up:** single-service simplicity, ~20-50ms additional network hop, operational parity.

**What you gain:** TS does what it's good at (UI integration, async context, Zod schemas); Python does what it's good at (ML tooling, LangGraph, eval pipeline); Bedrock KB and LangGraph CRAG can be A/B tested by changing one env var; Python service can serve multiple clients.

**Verdict:** best long-term architecture. Matches "Copilot team owns orchestration, domain teams own execution" model.

## Immediate Actions (option-agnostic)

These should happen regardless of which direction is selected:

1. **Add `/query` endpoint to playground** — lets Python service be callable from TS even if staying on Bedrock by default. Low effort, high optionality.
2. **Add `ORCHESTRATION_STRATEGY` env var** — makes strategy switchable without code changes. Implement `service.py` stub.
3. **Add `BedrockRetriever` adapter to eval** — benchmark Bedrock KB against LangGraph CRAG on the same test set. This is the missing data point.
4. **Write `src/orchestration/README.md`** — 10-line explanation of why two strategies exist.
5. **Update `src/librarian/ARCHITECTURE.md`** — record that agent objects are the shared component layer.

## `src/orchestration/service.py` — Strategy-Agnostic Entry Point

```python
async def run_query(query: str, *, session_id: str | None = None) -> list[Passage]:
    """Run a query through the configured orchestration strategy.
    
    Strategy selected by `settings.orchestration_strategy`:
    - "langgraph": LangGraph CRAG graph
    - "adk": ADK CustomRAGAgent
    - "bedrock": Direct Bedrock KB (comparison baseline)
    """
    if settings.orchestration_strategy == "langgraph":
        return await _run_langgraph(query)
    elif settings.orchestration_strategy == "adk":
        return await _run_adk(query)
    elif settings.orchestration_strategy == "bedrock":
        return await _run_bedrock(query)
    raise ValueError(f"Unknown strategy: {settings.orchestration_strategy}")
```

The `/query` FastAPI endpoint calls `run_query()`. Switching strategies is one env var change.

## Multi-Agent Python Topology (when scaling up)

When the Python copilot needs to scale beyond single-agent (>12–15 tools degrades Gemini tool selection):

```
rootAgent (routes only, no tools, no output_schema)
  ├── accountingAgent  (invoices, bills, customers, products — ~13 tools)
  ├── analystAgent     (reports, VAT, transactions, status summary — ~7 tools)
  └── helpAgent        (fetch_support_knowledge — 1 tool)
```

ADK Python auto-generates tool schemas from type annotations and docstrings — lower schema quality than Zod's explicit `.describe()`. Degradation starts earlier in Python, so split from the start rather than deferring.

## See Also
- [[ADK vs LangGraph Decision]]
- [[Bedrock KB vs LangGraph Decision]]
- [[Librarian RAG Architecture]]
- [[ADK vs LangGraph Comparison]]
