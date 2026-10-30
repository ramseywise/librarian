---
title: Knowledge Graph Entity Resolution
tags: [graph, rag, pattern]
summary: "Building a KG from text with LLMs: extraction is the easy part — the graph is only as good as entity resolution, so keep raw mentions in a reversible metagraph, resolve with relational evidence (WCC, LLM clustering with descriptions, ontology NED), and gate loads on false-merge rate weighted above false-split."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--10-building-kgs-with-llms.md
---

# Knowledge Graph Entity Resolution

One false merge silently joins two people, and every multi-hop answer passing through the join
is wrong. Extraction is the easy part of building a knowledge graph; **resolution is the
load-bearing step**.

## Why: errors compound with depth

If each hop is independently correct with probability *p*, an *n*-hop answer is correct with
*pⁿ*. At 85% per hop: 72% at 2 hops, 61% at 3, **44% at 5**. Hops aren't truly independent, but
the shape holds, and most per-hop errors are resolution errors (two entities merged, or one
split). Deep traversal is only worth it when resolution is good — see
[[Knowledge Graph Retrieval]].

## The pipeline

```
chunk → extract (mentions) → normalise → resolve (ER / NED) → assemble (+provenance) → evaluate (gate) → load
```

A model tier per stage, as in Anthropic's KG-construction cookbook: a small fast model
(Haiku-class) extracts into Pydantic models, a stronger model (Sonnet-class) resolves and
queries, assembly is deterministic (a NetworkX `MultiDiGraph` with `source_docs` on nodes and
`source_doc` on edges), and entity P/R is scored against a gold set. Use the model only where
judgement is needed — "spend agency per node" from [[Graph Topology Primitives]].

## Extraction lessons

- **Type names are instructions.** Renaming an entity type from "Topic" to "Occupation" improved
  extraction.
- **Schema-constrained output** (structured outputs, tool schemas, Pydantic), not free text plus
  a parser.
- **Temperature 0, then test stability**: run the same document several times; instability means
  an ambiguous prompt.
- **Prompt unit tests** on small inputs with known outputs, run on every prompt change.
- **Build a mini-KG from ~10 documents and look at it** before scaling; missing edge types and
  junk hubs are obvious.
- **Don't trust LLM character offsets** — recompute spans deterministically.
- **Fine-tune only when prompting plateaus**, and only once the evaluation gold set exists.

Traditional pipelines (spaCy/scispaCy) are cheap, deterministic and come with domain linkers
(UMLS IDs, which an LLM cannot assign by itself) but are weak at relations; LLMs are strong at
relations and new types. A common hybrid: a traditional linker where a domain KB exists, an LLM
for relations and long-tail types.

## ER vs NED

- **Entity resolution (ER):** which mentions are the same thing?
- **Named-entity disambiguation (NED):** which entry in a reference knowledge base does a mention
  denote? Use NED when an ontology exists (medicine, law, finance identifiers), ER when it
  doesn't.

### Keep mentions; resolution is reversible

```
(:Document)-[:HAS_PAGE]->(:Page)-[:MENTIONS]->(:Entity)    ← metagraph: raw mentions
(:Entity)-[:META_SIMILAR]->(:Entity)                        ← resolution evidence
(:Entity)-[:RESOLVES_TO]->(:Canonical)                      ← the KG proper
```

Extraction writes mentions; resolution writes similarity edges and canonical nodes on top.
Nothing is deleted, so the KG can be rebuilt whenever resolution changes. This reversibility is
what [[Knowledge Graph as Shared Agent Memory]] depends on.

### Graph-based ER

1. Normalise names (titles, case, punctuation).
2. Collect evidence: string similarity (obvious and risky) plus **relational signals** — same
   employer, same topics, same Louvain community, embedding proximity.
3. Write `META_SIMILAR` where evidence is strong enough.
4. Run **WCC** over `META_SIMILAR`; each component becomes one canonical entity.
5. Send borderline clusters to a **human review queue**. In the worked archive example, a
   physiologist turned up inside a physics subgraph because the extractor had respelled his
   surname to match a physicist on the same page — only a person looking at the graph caught it.

String similarity alone causes false merges; relational evidence tells two same-named people
apart.

### LLM-based ER

Give the model the unique names of one type **with their extraction descriptions** and ask for
`{canonical, aliases[]}` clusters. The descriptions are what prevent merging two different
people who share a surname. Failure modes: **dropped names** (fall back to a singleton cluster)
and **over-merging** (a numbered mission folded into its parent programme).

### NED against an ontology

1. **Candidate selection** via fuzzy full-text search over the ontology, filtered by NER type —
   **no LLM here**: candidates must come from the ontology, not model memory.
2. **Ranking:** find shortest paths between candidates and the document's other entities,
   **dropping hub nodes** that connect everything, verbalise and summarise the paths, then let
   the LLM choose. "Zika" next to "microcephaly" resolves to congenital Zika infection.
3. **Integration:** the resolved entity gains its ontology neighbourhood.

### Measure what normalisation did

Compare WCC counts and shortest-path distributions before and after. Three spellings of one
disease had split it into three nodes; after normalisation related nodes sit closer. If
resolution has no measurable structural effect, it probably isn't doing anything.

## Evaluation gate

Hand-label a gold set (50–100 mentions to start) and measure entity P/R, edge P/R over
(subject, type, object), **false-merge rate**, false-split rate and run-to-run stability.
**Weight false merges above false splits**: a split loses a connection; a merge invents
connections that traversal then follows confidently. Gate the load step on these the way CI
gates a deploy ([[Run-Then-Assert Eval CI]]).

## Assembly and integration

- **`MERGE` on a shared identity key is how sources are fused** — and only works once identities
  are resolved. Pair it with uniqueness constraints ([[Knowledge Graph Fundamentals and Cypher]]).
- **Curate before you scale**: a few task-relevant sources beat many loosely related ones.
- Structured-source integration swaps extraction for **identity mapping** onto shared codes
  (UMLS, Disease Ontology), **schema alignment** of edge semantics, and **validation** (counts,
  orphans, degree distributions) after each load.
- Generic clustering (WCC, Louvain) and domain-subgraph metrics (largest component, density,
  conductance) answer different questions; raw path counts favour hubs, which DWPC discounts
  ([[Graph Machine Learning and GNNs]]).

## See Also
- [[Knowledge Graph Fundamentals and Cypher]] — extends
- [[Knowledge Graph Retrieval]] — prerequisite-for
- [[Knowledge Graph as Shared Agent Memory]] — prerequisite-for
- [[Memory Lifecycle]] — extends
- [[Text-to-Cypher]] — related
