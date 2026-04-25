---
title: LangGraph CRAG Pipeline
tags: [langgraph, rag, pattern]
summary: The Corrective RAG pattern implemented as a LangGraph StateGraph — deterministic graph with conditional retry loop, confidence gating, and typed state schema.
updated: 2026-04-24
sources:
  - raw/playground-docs/librarian-stack-audit.md
  - raw/playground-docs/rag-tradeoffs.md
  - raw/playground-docs/adk-orchestration-research.md
  - raw/claude-docs/playground/docs/archived/librarian-hardening/plan.md
  - raw/claude-docs/playground/docs/archived/librarian-prod-hardening/plan.md
---

# LangGraph CRAG Pipeline

## Graph Topology

```
START → condense → analyze → [3-way route]
                               |
                 +-------------+--------------+
                 v             v              v
             retrieve    snippet_retrieve  generate (direct)
                 |             |              |
                 v             +--→ generate  |
              rerank                         |
                 |                           |
                 v                           |
               gate ─── retry? ──→ retrieve  |
                 |                           |
                 v                           |
             generate ←────────────────────-+
                 |
                END
```

**Agent nodes:**
- `CondenserAgent` — rewrites multi-turn queries to standalone form (Haiku). **No-op for single-turn** — passes query through unchanged with zero added latency.
- `PlannerAgent` — intent classification + query expansion (rule-based, no LLM)
- `RetrieverAgent` — multi-query embedding + hybrid search + grading via `EnsembleRetriever`
- `RerankerAgent` — cross-encoder or LLM-listwise reranking
- `GeneratorAgent` — prompt assembly + LLM generation + citation extraction; returns `RAGResponse` Pydantic model
- `QualityGate` — confidence threshold check for CRAG retry decision

## State Schema

```python
class LibrarianState(TypedDict, total=False):
    query: str
    standalone_query: str    # CondenserAgent output; same as query on single-turn
    conversation_id: str     # groups multi-turn exchanges
    intent: str
    retrieved_chunks: list[RetrievalResult]
    graded_chunks: list[GradedChunk]
    reranked_chunks: list[RankedChunk]
    confidence_score: float
    confident: bool
    retry_count: int
    fallback_requested: bool
    escalate: bool           # not confident or fallback_requested → frontend handoff
    response: str
    messages: Annotated[list, add_messages]
```

Nodes return partial dicts; LangGraph merges them. No node can modify state outside its return value — the TypedDict schema is the contract.

## HistoryCondenser Node

See [[HistoryCondenser]] for full detail. The condenser is the **first node** after START. It rewrites the user's latest message into a standalone query using prior conversation history.

```python
class HistoryCondenser:
    async def condense(self, state: LibrarianState) -> dict:
        if len(state["messages"]) <= 1:
            return {"standalone_query": state["query"]}  # no-op — zero latency
        # Haiku call: "Rewrite the user's latest message as a standalone query..."
        return {"standalone_query": rewritten_query}
```

**Why Haiku:** the rewrite task is simple and latency matters here. Haiku adds ~200ms on multi-turn; single-turn adds zero.

**Known gap (from hardening review):** If callers bypass the factory and call `build_graph()` directly, the condenser defaults to the generation LLM client rather than a separate Haiku client — losing the cost-saving behavior. Always use `create_librarian()` from `factory.py`.

## CRAG Retry Logic

See [[CRAG Retry Logic]] for full detail. The CRAG gate compares `confidence_score` (from RerankerAgent) against `confidence_threshold` (default 0.3):
- `confidence_score >= threshold` → generate
- `confidence_score < threshold` AND `retry_count <= max_crag_retries` → loop back to retrieve with incremented `retry_count`
- `retry_count > max_crag_retries` → generate from whatever context is available

The retry re-enters at `retrieve`, not at the top of the pipeline — more surgical than `LoopAgent`.

Max retries: 1 (default). One retry adds ~400ms; set `confidence_threshold=0.0` to disable loop entirely.

## Intent Routing

`PlannerAgent` routes to one of three paths:
- `retrieve` — dense/hybrid path (COMPARE, EXPLORE, LOOKUP+moderate)
- `snippet_retrieve` — fast keyword FTS path (LOOKUP+simple, factual)
- `generate` — direct response, no retrieval (CONVERSATIONAL, OUT_OF_SCOPE)

## Why LangGraph Over ADK for This Pattern

| Dimension | LangGraph | ADK |
|---|---|---|
| Orchestration | Code-driven graph (deterministic) | LLM-driven tool calling |
| Retry loops | Conditional back-edge (mid-pipeline re-entry) | LoopAgent (restarts full sequence) |
| State | Typed TypedDict (auditable, testable) | Mutable session dict (flexible, untyped) |
| Claude support | First-class via `langchain-anthropic` | Requires adapters |
| Confidence gating | Hard gate from reranker score | Instruction-based (model can ignore) |

ADK is better when the agent needs to *decide* which tools to call. LangGraph is better when retrieval is always warranted and the pipeline is deterministic. See [[ADK vs LangGraph Comparison]].

## Observability

LangGraph callbacks fire on node entry/exit and LLM calls. Wire via:
```python
handler = build_langfuse_handler(session_id, trace_id)
config = make_runnable_config(handler)
await graph.ainvoke(state, config=config)
```

Key signals emitted per query: `confidence_score`, `retrieved_chunks`, `graded_chunks`, `reranked_chunks`, `failure_reason`, `retry_count`.

## Vocabulary Alignment (ADK-style naming)

The Librarian uses ADK-idiomatic naming for agent classes:
- Each class has `name`, `description`, and optionally `instruction` properties
- Each class exposes `as_node()` method for LangGraph wiring
- Equivalent ADK structure: `SequentialAgent([condenser, planner, LoopAgent([retriever, reranker, gate]), generator])`

## See Also
- [[Librarian RAG Architecture]]
- [[RAG Retrieval Strategies]]
- [[RAG Reranking]]
- [[Production Hardening Patterns]]
- [[ADK vs LangGraph Comparison]]
- [[ADK vs LangGraph Decision]]
