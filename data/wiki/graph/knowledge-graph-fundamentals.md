---
title: Knowledge Graph Fundamentals and Cypher
tags: [graph, rag, reference]
summary: "A knowledge graph is an ever-evolving, domain-specific graph of typed entities and named relationships; build it purpose-first from the questions it must answer, choose LPG vs RDF by goal (LPG when edges need provenance), and write Cypher with bounded paths, MERGE-on-identity-key plus uniqueness constraints, and provenance on edges."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--09-kg-fundamentals-and-cypher.md
---

# Knowledge Graph Fundamentals and Cypher

"Graph" means two different objects in agent engineering. An **agent graph** is execution
topology (nodes compute, edges route — see [[Graph Topology Primitives]]). A **knowledge graph**
is a data structure for retrieval (nodes are entities, edges typed relationships). Keep them
apart until [[Knowledge Graph as Shared Agent Memory]], where the KG becomes the state the
execution graph coordinates through.

## Definition and the four pillars

A KG is an **ever-evolving graph of typed entities, their attributes and the named relationships
between them, built for a specific domain**. It rests on four pillars: **evolution** (never
"done"), **semantics** (types and relation names carry meaning, often from an ontology),
**integration** (several sources fused onto shared entities) and **learning** (supports
inference and [[Graph Machine Learning and GNNs]]).

## Why KGs pair with LLMs

| LLM drawback | KG contribution |
|---|---|
| Hallucination | Explicit facts to ground answers in |
| Staleness | A store you update without retraining |
| Opacity | Paths and edges shown as the reason for an answer |
| Private data | Domain facts the model never saw |

In the other direction, LLMs help **build** KGs ([[Knowledge Graph Entity Resolution]]),
**query** them ([[Text-to-Cypher]]) and summarise results.

The two sides reason differently. A KG is acquired explicitly and reasons **deductively** —
sound, but only as complete as the knowledge base, so purely deductive engines stall on real
(incomplete) data. An LLM (or graph ML) reasons **inductively and probabilistically** —
generalises from gaps, and can reach false conclusions from true premises. A hybrid is more
robust under uncertainty; neither supplies common sense. The target system is an **advisory**
one that supports a human decision rather than acting alone.

**Consider a KG when** questions are relational or multi-hop, answers must trace to sources,
several systems share entities, or the domain already has an ontology. For "find the paragraph
about Y", a vector index is cheaper.

## Purpose-driven, not bottom-up

Start from the questions the graph must answer, not the data you happen to have. Bottom-up
integration ("load everything and see what connects") usually fails: sources are heterogeneous
and mostly irrelevant to any one task. Run construction as a CRISP-DM cycle — business
understanding → data understanding → schema modelling → building → evaluating against the
original questions. Same rule as "curate before you scale".

## Graph basics that matter later

- **Degree** and **hubs** (very high-degree nodes). Hubs create spurious short paths that
  corrupt disambiguation and path scoring.
- **Paths**: shortest path and variable-length path are the core traversals.
- **Weakly connected components (WCC)** do the clustering step in graph-based entity resolution.

## LPG vs RDF

| | Labelled property graph | RDF |
|---|---|---|
| Unit | Nodes and relationships with properties | Triples |
| Identity | Internal IDs plus your keys | Global IRIs |
| Edge properties | Native | Workarounds (n-ary nodes, RDF-star, named graphs) |
| Schema / inference | Optional constraints and indexes | RDFS/OWL ontologies with reasoning |
| Query | Cypher / GQL | SPARQL |

**Choose by goal.** RDF/OWL when standard ontologies, interchange and formal inference are the
point; LPG when edges need provenance, confidence and timestamps — which covers most
LLM-extracted graphs. You can have both: Neosemantics (n10s) imports OWL into Neo4j and keeps
the subclass hierarchy as traversable edges.

## Typed edges: the edge type is the knowledge

A graph where every edge is `RELATED_TO` says two things connect but not how. Name edges by
meaning (`SUPERSEDES`, `DEPENDS_ON`, `DECIDED_BY`, `CAUSED`, `IMPLEMENTS`, `REFERENCES`). A query
can only filter on distinctions the schema records. (A vendor claim that typed edges improve
reasoning accuracy by ~18% has no primary source — don't quote it.)

## Cypher habits

Cypher draws patterns in ASCII: `(n:Label {prop: $value})-[r:TYPE]->(m)`.

- **Parameters, never string concatenation** — safety and plan caching.
- **Always bound variable-length paths** (`*1..3`, not `*`). Unbounded traversal over a hub can
  visit the whole graph.
- **Pair `MERGE` with a uniqueness constraint.** `MERGE` alone creates duplicates when writers
  race; the constraint turns that into a visible error — the single-writer rule applied at the
  database.
- **`MERGE` on the identity key only, then `SET` the rest.** Merging on `{id, name}` creates a new
  node whenever the name is spelled differently.
- **Provenance on edges** (`source`, `run_id`, `extracted_at`) — needed for rollback.
- `EXPLAIN` checks a query without running it (the validator in [[Text-to-Cypher]]);
  `db.schema.visualization()` and `apoc.meta.schema` give schema input; full-text and vector
  indexes back hybrid retrieval. **APOC** supplies batching (`apoc.periodic.iterate`),
  introspection and import helpers.

## See Also
- [[Knowledge Graph Retrieval]] — prerequisite-for
- [[Knowledge Graph Entity Resolution]] — prerequisite-for
- [[Text-to-Cypher]] — prerequisite-for
- [[Graph Engineering]] — extends
- [[Compiled-Prose KB vs Graph-Native Store]] — extends
