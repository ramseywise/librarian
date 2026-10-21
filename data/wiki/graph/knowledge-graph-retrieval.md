---
title: Knowledge Graph Retrieval
tags: [rag, llm, concept]
summary: "Vector search finds things that sound like your question; graphs find things that are connected to your answer — but traversal depth compounds error, which makes entity resolution the load-bearing sub-problem."
updated: 2026-10-17
sources:
  - data/raw/articles/2026-07-19-knowledge-graphs-for-rag.md
  - data/raw/claude-docs/playground/docs/support-agents/accounting-knowledge.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--graph-engineering.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--README.md
  - data/raw/claude-docs/project-g/docs/support-agents/accounting-knowledge.md
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

## Where a graph earns its keep in support knowledge (playground notes)

An accounting-support corpus splits into three knowledge layers. **Procedural** how-to
content is served well by flat retrieval. **Regulatory rules** and **entity relationships**
(which form applies to which entity type under which threshold) are where multi-hop
questions live, and that is the only place a graph adds value. Design notes:

- The graph is small (hundreds of nodes), so a JSON adjacency file or a community-edition
  graph DB is enough. No graph platform is needed.
- Query it hybrid-style: Cypher for the structural hop, vector search for the text.
- Each jurisdiction is a separate graph, so every node needs a locale scope. Without one,
  a rule from one country answers a question about another.
- A graph adds nothing to the semantic cache. The cache keys on query similarity, not on
  structure.

## Course notes: construction noise, two-stage hybrid, GraphRAG

From a knowledge-graphs-for-RAG short course:

- **Construction is a noisy pipeline** — NER, relation extraction, coreference resolution,
  entity dedup, load — and every stage adds error, so retrieval quality is bounded by
  extraction quality. **Schema-constrained graphs** over a known entity schema (e.g.
  regulatory filings) outperform open-domain construction.
- **Two-stage hybrid:** vector search returns candidate chunks → entities extracted from
  those chunks anchor a Cypher query → the LLM receives both the unstructured chunks and the
  structured facts. This is the multi-hop pattern over heterogeneous data.
- **Know the relation types before querying.** A Cypher pattern like
  `MATCH (n:Entity)-[:RELATION]->(m)` is only useful if the schema's relation types are known.
- **GraphRAG (community summaries):** community detection over the graph produces
  summaries at several granularities; global questions are answered from community
  summaries, local questions from entity neighbourhoods — the synthesis-across-many-entities
  case flat vector search cannot serve.

## See Also
- [[Graph Engineering]] — part-of
- [[Knowledge Graph as Shared Agent Memory]] — extends (the same structure used as write-path memory)
- [[Graph Topology Primitives]] — complements (typed edges)
- [[RAG Retrieval Strategies]] — alternative-to (similarity retrieval vs connection retrieval)
- [[Reciprocal Rank Fusion (RRF)]] — complements (fusing graph and vector result lists)
- [[Compiled-Prose KB vs Graph-Native Store]] — alternative-to
