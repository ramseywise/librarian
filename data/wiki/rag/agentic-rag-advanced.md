---
title: Agentic RAG — Advanced Patterns
tags: [rag, pattern, concept]
summary: Self-RAG vs CRAG distinction, Adaptive RAG complexity tiers, GraphRAG for relationship traversal, HyDE for lexical gap, Multi-Query RAG-Fusion, agentic latency budgets, and A2A protocol mapping to LangGraph.
updated: 2026-07-14
sources:
  - raw/claude-docs/playground/docs/research/rag/agentic-rag-patterns.md
  - raw/agent-skills/advanced-rag-patterns/SKILL.md
  - raw/agent-skills/langchain-rag/references/advanced-patterns.md
  - data/raw/repos/learn-ai-engineering/generative-ai--01-llm-fundamentals--rl.md
---

# Agentic RAG — Advanced Patterns

## Self-RAG vs CRAG

Commonly confused — they solve different problems:

| Pattern | Decision point | Who decides to retrieve |
|---|---|---|
| **CRAG** | Pre-generation: retrieve → grade chunks → retry if none pass | Graph topology |
| **Self-RAG** | Intra-generation: reflection tokens decide mid-generation | The LLM itself |

**CRAG:** every query triggers retrieval. The graph grades chunks and loops if confidence is low.

**Self-RAG:** LLM generates inline reflection tokens — `[Retrieve]` / `[No Retrieve]`, `[IsRel]`, `[IsSup]`, `[IsUse]` — and decides whether retrieval is needed. Allows LLM to skip retrieval for factual questions it already knows.

Use CRAG when you need predictable retrieval. Use Self-RAG when retrieval is expensive and many queries don't need it.

## Adaptive RAG (Complexity Routing)

Route queries by complexity tier to control cost and latency:

| Tier | Query type | Strategy |
|---|---|---|
| Simple | Single factual ("What is the VAT rate?") | Single retrieve, no reranking |
| Moderate | Multi-fact ("Compare invoice types") | CRAG with confidence gate |
| Complex | Synthesis ("Summarize all invoices for customer X") | Multi-step decompose + aggregate |

```python
def complexity_router(state):
    complexity = classify_complexity(state["query"])  # fast Haiku call
    return {"complexity": complexity, "next": complexity}  # routes to tier node
```

## GraphRAG

When vector search fails on **relationship traversal** questions — "What do all invoices for customer X have in common?" — vector similarity can't answer relationship-based questions.

GraphRAG approach:
1. Extract entities + relationships from corpus (LLM-assisted)
2. Build knowledge graph (nodes = entities, edges = relationships)
3. Community detection + summarization for subgraph retrieval
4. Use graph traversal (not vector search) to answer relationship queries

**When to use:** relationship questions, entity comparison, "all X that share property Y" queries.
**When NOT to use:** simple factual lookups — overkill, adds significant pipeline complexity.

**Lightweight alternative for personal KBs:** for a wiki-shaped corpus (like this Librarian wiki), `[[wikilinks]]` already provide a graph structure — prefer traversing those before reaching for a dedicated GraphRAG pipeline with LLM-extracted entities and community detection.

## HyDE (Hypothetical Document Embeddings)

Closes the lexical gap between user queries and document language.

**Problem:** User asks "how do I fix a late payment?" but the document says "Procedures for resolving overdue receivables." Vector similarity is low despite semantic equivalence.

**Fix:** Generate a hypothetical ideal document that would answer the query, then embed that instead:

```python
hypothetical_doc = haiku.invoke(f"Write a support document that answers: {query}")
embedding = embedder.embed(hypothetical_doc.content)  # embed the hypothetical, not the query
results = vector_search(embedding, top_k=5)
```

**Tradeoff:** adds one Haiku call per query (~100ms, ~$0.0002). Worthwhile when MRR improvement from closing the lexical gap is significant.

## Multi-Query Retrieval (RAG-Fusion)

Generate N query variants, retrieve for each, merge results:

```python
variants = haiku.invoke(f"Generate 3 different phrasings of: {query}")
# Retrieve in parallel
all_results = await asyncio.gather(*[retrieve(v) for v in variants])
# Flatten + deduplicate + re-rank
merged = global_dedup(flatten(all_results))
```

**Sweet spot:** 3 variants. Beyond 3, diminishing returns + cost grows linearly.
**Typical lift:** +10–15% recall over single query.

**Global dedup after merge:** sort by score descending, dedup by `chunk_id` or content fingerprint, highest score wins.

## Latency Budgets for Agentic RAG

| Pipeline | p50 | p95 | Notes |
|---|---|---|---|
| Simple single-retrieve | 300ms | 800ms | No reranking, no CRAG |
| Q&A with CRAG | 800ms | 2s | Includes grading |
| CRAG with retry | 1.5s | 4s | One retry loop |
| Action / plan+execute | 2s | 6s | Multi-step, HITL possible |

Budget breakdown for cross-encoder path:
- Query rewrite (Haiku): ~200ms
- Retrieval (hybrid): ~50–100ms
- CRAG grading (Haiku, 5 chunks): ~300ms
- Reranker (cross-encoder): ~50–100ms
- Generation (Sonnet, streaming): ~800–1500ms
- **Total: ~1.4–2.1s**

## A2A Protocol — LangGraph Mapping

Google's Agent-to-Agent (A2A) spec (April 2025) for inter-agent communication.

| A2A concept | LangGraph equivalent |
|---|---|
| Agent Card (`/.well-known/agent.json`) | FastAPI metadata endpoint |
| Task ID | `thread_id` in checkpointer |
| Task state (submitted/working/completed) | Checkpointer state |
| `input-required` state | `interrupt()` |
| Streaming updates | `astream_events()` → SSE |

```
# Task lifecycle
submitted → working → input-required ↔ working → completed / failed
```

**When to use A2A:** when sub-agents are deployed as separate services and need a standard protocol for handoff. Overkill for single-service multi-agent graphs.

## Adversarial / Safety Tests for Agentic RAG

Test these explicitly — they don't appear in standard QA evals:

| Attack | What to test |
|---|---|
| Prompt injection via retrieval | Malicious text in corpus that hijacks agent instruction |
| Tool call manipulation | Retrieved text that convinces agent to call unintended tools |
| Sensitive data exfiltration | Agent leaking retrieved PII in its response |
| Scope violation | Retrieved context from wrong domain used to answer off-domain question |

## See Also
- [[LangGraph BaseStore]] <!-- auto-linked -->
- [[Librarian RAG Architecture]] <!-- auto-linked -->
- [[CRAG Retry Logic]]
- [[RAG Retrieval Strategies]]
- [[RAG API Design Patterns]]
- [[Multi-Agent Orchestration Patterns]]
- [[A2A Agent Protocol]]
- [[VA vs HCA Retrieval Evaluation]]
- [[RAG Interview Study Guide]] — prerequisite-for
- [[RL for Retrieval Policies]] — extends (Self-RAG as a learned retrieval policy, alongside online RL and per-subtask modules)
