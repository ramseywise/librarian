---
name: advanced-rag-patterns
description: >
  Advanced RAG patterns beyond basic retrieve-and-generate — CRAG, Self-RAG, GraphRAG,
  Adaptive RAG, multi-hop reasoning, Plan-and-Execute. Use when basic RAG quality is
  insufficient or when queries require multi-step reasoning over retrieved content.
metadata:
  domains: [rag, langgraph, adk, eval]
---

# Advanced RAG Patterns

For basic RAG setup see `langchain-rag`. This skill covers patterns for improving RAG quality when simple retrieval is insufficient.

## Pattern Decision Tree

```
Query requires multi-hop? → GraphRAG or Plan-and-Execute
Retrieval quality varies? → CRAG (confidence-gated retry)
Need to verify before generating? → Self-RAG
Query is ambiguous? → Adaptive RAG (classify first)
Need structured decomposition? → Query decomposition + parallel retrieval
```

## CRAG — Corrective RAG

The pattern already used in `playground/src/orchestration/graph.py`. Grade retrieved chunks; if confidence < threshold, reformulate the query and retrieve again.

```python
# LangGraph CRAG loop
graph.add_conditional_edges(
    "grade_documents",
    decide_to_generate,  # returns "generate" or "reformulate"
    {"generate": "generate", "reformulate": "transform_query"},
)
```

**Threshold:** grade ≥ 0.7 → generate. Below → reformulate and re-retrieve (max 2 retries).

## Self-RAG

The agent decides at generation time whether to retrieve at all, and grades its own output after generating. Three special tokens: `[Retrieve]`, `[IsRel]`, `[IsSup]`.

More expensive than CRAG (3-5x LLM calls) but better for open-domain questions. Not recommended for FAQ/support use cases — use CRAG instead.

## Adaptive RAG

Classify the query before retrieval to select the retrieval strategy:

| Intent | Strategy |
|--------|---------|
| `LOOKUP` / `simple` | Snippet retrieval (BM25, top-3) |
| `EXPLORE` / `moderate` | Dense vector retrieval (top-10) |
| `COMPARE` / `complex` | Hybrid retrieval + reranking |
| `CONVERSATIONAL` | Skip retrieval, answer directly |

Already partially implemented in `playground/src/orchestration/query_understanding.py`.

## GraphRAG

Build a knowledge graph from the corpus; use graph traversal for multi-hop queries. Heavy infra cost (graph construction + GDS). Only worth it if:
- Queries regularly require 3+ hops through entities
- Corpus has clear entity relationships (people, orgs, events)

For a personal KB like librarian, wiki `[[wikilinks]]` provide a lightweight graph — use those before reaching for GraphRAG.

## Multi-Query Expansion

Generate 3-5 rephrasings of the original query, retrieve for each, deduplicate results, then rerank the union.

```python
queries = llm.invoke(f"Generate 4 rephrasings of: {original_query}")
all_chunks = [retriever.invoke(q) for q in queries]
deduped = deduplicate_by_content(all_chunks)
reranked = cross_encoder.rerank(original_query, deduped)
```

Already in `RetrieverAgent` in playground. Missing from rag_poc ADK tools.

## Plan-and-Execute

For complex, multi-step queries: plan the retrieval steps first, execute each, synthesise.

```python
plan = planner_llm.invoke(f"What steps are needed to answer: {query}")
results = [execute_step(step, retriever) for step in plan.steps]
answer = synthesiser_llm.invoke(f"Given these results, answer: {query}\n{results}")
```

Best suited for research-style queries, not FAQ/support.

## References

| File | Contents |
|------|----------|
| `references/crag-implementation.md` | Full CRAG graph with grader, reformulator, and confidence thresholds |
| `references/adaptive-routing.md` | Intent classification → retrieval strategy mapping |

> **References not yet populated.** Will be filled from `wiki/agents/` pages after ingest of RAG-tagged sources in `raw/playground-docs/`.
