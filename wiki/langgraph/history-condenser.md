---
title: HistoryCondenser
tags: [rag, langgraph, context-management, concept]
summary: LangGraph node that rewrites the latest user query into a self-contained form given prior turns — prevents retrieval degradation on coreference-heavy multi-turn conversations.
updated: 2026-04-24
sources:
  - raw/playground-docs/librarian-stack-audit.md
  - raw/playground-docs/librarian-architecture-decisions.md
---

# HistoryCondenser

A LangGraph node that sits before the retriever in the [[LangGraph CRAG Pipeline]]. On multi-turn conversations, it rewrites the latest user query to be standalone — resolving pronouns, references, and ellipsis relative to prior turns. On single-turn queries, it is a no-op (zero added latency).

## The Problem It Solves

Without a condenser, a query like "What about the Python version?" gets sent verbatim to the retriever. The retriever has no conversation history — it returns results about Python in general, not the specific thing being compared. This looks like a hallucination in the final answer but is actually a retrieval miss.

## Mechanism

Uses Haiku (~$0.001/rewrite) to rephrase. The prompt is roughly:

```
Given this conversation history:
{prior_turns}

Rewrite this query to be fully self-contained:
{latest_query}

Self-contained query:
```

The rewritten query replaces the user's original before being passed to the retriever.

## When It Fires

```python
if len(state["messages"]) > 1:
    condensed = condenser_llm.invoke(condense_prompt)
    state["condensed_query"] = condensed
else:
    state["condensed_query"] = state["messages"][-1].content
```

Single-turn: skipped entirely. Multi-turn: always fires.

## Cost and Latency

Haiku call: ~$0.001 per rewrite, ~100–200ms added latency on multi-turn only. Negligible at scale.

## Contrast with Summarization

[[Summarization Node]] compresses *prior* history to fit in context. HistoryCondenser rewrites the *current* query using prior history. They address different problems and can coexist.

## See Also
- [[LangGraph CRAG Pipeline]]
- [[RAG Retrieval Strategies]]
- [[Summarization Node]]
- [[Bedrock KB vs LangGraph Decision]] — Bedrock KB silently degrades here; HistoryCondenser prevents it
