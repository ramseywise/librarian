---
title: Knowledge Graph Retrieval
tags: [rag, llm, concept]
summary: "Vector search finds things that sound like your question; graphs find things that are connected to your answer — but traversal depth compounds error, which makes entity resolution the load-bearing sub-problem."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--graph-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--README.md
---

# Knowledge Graph Retrieval

The **second sense** of graph in [[Graph Engineering]]: a graph as *retrieval structure*
rather than as execution topology. Nodes are entities (people, places, concepts), edges are
typed relationships, and the graph encodes structured world knowledge that a RAG pipeline
queries instead of — or alongside — a vector index.

Keeping the two senses distinct matters, because they share a word and almost nothing else:

| | Agent graph | Knowledge graph |
|---|---|---|
| Nodes are | Units of computation | Entities |
| Edges are | Permitted transitions | Typed relationships |
| The graph is | Execution topology | Data structure for retrieval |
| Runtime concern | Routing, state, cost | Traversal, entity resolution |

## Why it beats vector-only

> **"Vector search finds things that sound like your question. Graphs find things that are
> connected to your answer."**

That is the whole case, and it is a case about **multi-hop** questions specifically.
Reported multi-hop accuracy: **53.4% for graph retrieval vs 42.9% for vector-only.**

Single-hop lookups do not need a graph — semantic similarity already answers them. The
graph earns its cost where the answer requires following relationships the question does
not name.

## The compounding-error caveat

The number above comes with a caveat that is more useful than the number:

> At 85% per-hop accuracy, **"a 5-hop traversal is only 44% trustworthy."**

`0.85^5 ≈ 0.44`. **Traversal depth compounds error multiplicatively**, so deep traversal is
not a feature you turn on — it is a budget you spend. Two consequences:

1. **Bound traversal depth explicitly.** Unbounded traversal on a large graph produces
   confident nonsense at depth 5+.
2. **Entity resolution is the load-bearing sub-problem, not an implementation detail.**
   Per-hop accuracy *is* entity-resolution accuracy for most of the pipeline. Improving the
   retrieval model while entity resolution stays at 85% moves nothing.

## Typed edges carry the knowledge

> **"The edge type IS the knowledge."**

An untyped edge asserts only that two things are related, which is barely more than
co-occurrence. See [[Graph Topology Primitives]] for the six-edge-type production minimum
(`SUPERSEDES`, `DEPENDS_ON`, `DECIDED_BY`, `CAUSED`, `IMPLEMENTS`, `REFERENCES`).

## You do not need a graph database

The community consensus on what actually matters:

> *"Small typed core, cheap indexing, hybrid retrieval, temporal supersession. **All four
> of those are implementable on markdown files you own.**"*

This wiki is an existence proof: `[[wikilink]]` edges with `— type` suffixes are a small
typed core; the relinker is cheap indexing; the MCP server's search is hybrid retrieval;
tombstone pages are temporal supersession. **The graph-database question is an
implementation detail downstream of getting those four right.**

## Hybrid, not replacement

Graph retrieval sits *alongside* vector search rather than replacing it — it is another
entry in the strategy table of [[RAG Retrieval Strategies]]: semantic similarity for "what
sounds relevant," graph traversal for "what is connected." Routing between them is a
decision the retrieval layer makes per query, not a global architecture choice.

## See Also
- [[Graph Engineering]] — part-of
- [[Knowledge Graph as Shared Agent Memory]] — extends (the same structure used as write-path memory)
- [[Graph Topology Primitives]] — complements (typed edges)
- [[RAG Retrieval Strategies]] — alternative-to (similarity retrieval vs connection retrieval)
- [[Reciprocal Rank Fusion (RRF)]] — complements (fusing graph and vector result lists)
