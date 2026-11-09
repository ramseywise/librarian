---
title: Knowledge Graph Fundamentals and Cypher
tags: [graph, rag, reference]
summary: "A knowledge graph is an ever-evolving, domain-specific graph of typed entities and named relationships; build it purpose-first from the questions it must answer, choose LPG vs RDF by goal (LPG when edges need provenance), and write Cypher with bounded paths, MERGE-on-identity-key plus uniqueness constraints, and provenance on edges."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--09-kg-fundamentals-and-cypher.md
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-ch01-kg-llm-killer-combination.md
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-ch02-intelligent-systems-hybrid.md
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-ch03-first-kg-from-ontologies.md
  - data/raw/papers/2026-11-08-kg-and-llms-in-action-appendix-a-intro-to-graphs.md
  - data/raw/papers/2026-11-07-kg-and-llms-in-action-appendix-b-neo4j.md
  - data/raw/papers/2026-11-07-building-ai-agents-llms-rag-kgs-ch07-creating-connecting-knowledge-graph-ai-agen.md
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

## Evidence and worked examples from the Manning book chapters

These come from reading extractions of *Knowledge Graphs and LLMs in Action* (Negro and co-authors); the chapters are conceptual or walkthroughs, so the figures below are the book's own, not independent measurements.

- **Adoption barriers.** Chapter 1 gives three reasons KGs spread slowly: building them is expensive, they require multi-hop access, and answers end up spread over several nodes. It quotes a McKinsey estimate that tackling data fragmentation could lower yearly data spend by 5% to 15% in the near term; that is a general fragmentation number, not something measured for KGs.
- **"Just enough semantics".** Modern KGs borrow only part of the ontology toolkit and grow partial ontologies as needed. Chapter 1 advises considering an LLM whenever at least one of four needs holds (pulling facts from text, interpreting queries, a conversational interface, summarising), and says RDF suits interoperability and semantic consistency while LPG suits pathfinding and traversal.
- **LLM reasoning limits.** Chapter 2 relays a study (Wu et al.) over 11 task types in which LLMs did markedly and consistently worse on counterfactual variants of familiar tasks; the chapter gives no scores. The authors also tried one prompt, a simplified river-crossing puzzle, on Claude.ai 3.5 Sonnet and got a flawed answer that looked like memorised training data; they call this anecdotal. From their own experience they say KG projects built bottom-up often fail to get adopted.
- **A first KG from an ontology.** Chapter 3 loads the Human Phenotype Ontology (hp.owl, February 2025) and a phenotype annotation file into Neo4j 5.20.0 Enterprise with APOC and Neosemantics 5.20.0, which brings in 899,558 statements. It chooses LPG with Cypher over RDF so that source, creator and date can live on the relationship itself. In the clinical query, five features supplied by clinicians were matched by the top-ranked disease on all five. Its setup advice: create uniqueness constraints and indexes before loading, set a relationship property only if its source column has a value, and use `n10s.inference.nodesInCategory` over SUBCLASSOF to expose implicit annotations.
- **Graph basics.** Appendix A (excerpted from an earlier book) recommends adjacency lists for sparse graphs, whose memory grows with vertices plus edges, and adjacency matrices for small or dense graphs or quick edge-existence tests, whose memory grows with the square of the vertex count. Its homophily illustration is a third-party also-bought network of US political books: in 2008 two clusters had no bridging titles, by 2012 many books linked them (reported).
- **Neo4j setup.** Appendix B lists Java 21 or later for a server install, says the free Community Edition (GPLv3) covers all the book's code, prefers a local install over Aura for the exercises, and requires APOC and GDS versions to match the Neo4j version. Cleanup is `apoc.periodic.iterate` with `batchSize` 1000 plus `apoc.schema.assert({}, {})` to drop constraints. Testing was on Neo4j 2025.x.

### Limits of these chapters

- None of these chapters runs an experiment or benchmark. Chapter 1 offers assertions and cited claims, and its references are missing from the extraction; chapter 2 has a single anecdotal prompt; chapter 3 covers a single clinical scenario and reports no accuracy or recall figure and no study with clinicians.
- In chapter 3, matching works on exact labels, annotations are merged on the (disease, phenotype) pair alone, and one listing breaks if the whole ingestion including final cleaning is executed.
- Appendix A covers neither property graphs, RDF, Cypher nor KGs, and the extraction notes that figure numbers cited in its degree paragraphs look inconsistent.
- Appendix B is a minimal setup guide. It checks for APOC with `CALL dbms.procedures()` although it says 2025.x was tested, and its clustering text uses older master/slave wording.

## Construction stages and quality dimensions (Packt chapter 7)

Raieli and Iuculano's chapter, a survey-style overview with no experiments, defines a KG as directed edges stored as (head, relation, tail) triplets and sets out five construction stages: creation, assessment, cleaning, enrichment and deployment, with assessment and cleaning able to run together. Practices it lists:

- Fix the graph's purpose with stakeholders first, then choose ontologies top-down or bottom-up and reuse existing domain ontologies for interoperability.
- For LLM triplet extraction, write a prompt with do and do-not bullets, role context and few-shot examples, or use LangChain's `LLMGraphTransformer` for a few-line version; one LLM can extract while a smaller one corrects.
- Assess a graph on accuracy, completeness, conciseness (blank nodes are a warning sign), timeliness, accessibility, how readable it is, and security, privacy and traceability; an LLM can flag erroneous triplets such as a capital attached to the wrong country.
- Pick the store by use (relational, document, graph database, triplet store, or a layer over several), and keep pipelines for updates, quality monitoring, deletion for legal reasons and access control after deployment.

Limits: the full tutorial code lives in the publisher's repository, the model and library versions are not stated, and the chapter's `GraphCypherQAChain` and `LLMGraphTransformer` imports have since moved or been flagged. KG embeddings and GNNs get only an introduction there; see [[Graph Machine Learning and GNNs]].

## See Also
- [[Knowledge Graph Retrieval]] — prerequisite-for
- [[Knowledge Graph Entity Resolution]] — prerequisite-for
- [[Text-to-Cypher]] — prerequisite-for
- [[Graph Engineering]] — extends
- [[Compiled-Prose KB vs Graph-Native Store]] — extends
- [[Degree-Weighted Path Count (DWPC)]] — related (typed-path scoring over a built KG)
- [[GrailQA Three Levels of KBQA Generalization]] — instance-of (KBQA benchmark)
- [[ERNIE Knowledge-Enhanced Language Representation]] — related
- [[Reasoning on Graphs]] — related
