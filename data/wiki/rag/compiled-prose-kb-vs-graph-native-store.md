---
title: Compiled-Prose KB vs Graph-Native Store
tags: [rag, memory, comparison]
summary: "librarian compared itself with two reference architectures: a graph-native, LLM-free knowledge store and an agent-memory service. They sit at different layers, and that difference explains the gaps in both directions. Compiled prose wins on synthesis, operational weight and eval discipline. It loses on per-claim provenance, automated conflict detection, temporal modelling and visible degradation."
updated: 2026-10-17
sources:
  - data/raw/repos/librarian/.claude--docs--research--2026-08-22_semantica-parity.md
  - data/raw/repos/librarian/.claude--docs--research--2026-08-20_retrieval-parity_tencentdb.md
---

# Compiled-Prose KB vs Graph-Native Store

Two parity reviews (2026-08) read external systems as reference architectures to find what
librarian was structurally missing. One was a graph-native "context and decision
provenance" store aimed at regulated domains: RDF plus a labelled property graph,
ontology governance, and deterministic extractors with no LLM. The other was an
agent-memory service whose knowledge component is a wiki plus a code-graph engine.

**Headline: they are not competitors; they sit at different layers.** In librarian the
graph is a side effect of an LLM writing linked prose. In the graph-native store the prose
is a rendering of the graph. librarian bets that good linked prose beats structured
extraction. The graph-native store bets that "why" must be answerable deterministically,
with no LLM in the loop. Both bets are defensible, and the useful findings are in how each
one fails.

| | Compiled-prose KB (librarian) | Graph-native store |
|---|---|---|
| Knowledge unit | markdown page (~290) | triple / node |
| Writer | LLM as compiler | deterministic extractors |
| Structure | hand-authored wikilinks + typed suffixes | extracted ontology (OWL/SHACL/SKOS) |
| Substrate | local files + DuckDB | triplestore + graph DB + vector backends |
| Code size | ~100 files | ~350 files |

## Where compiled prose loses

1. **Provenance is a filename list, not a record.** `sources:` says which files a page came
   from. It cannot say which claim came from which source, or whether that claim has been
   invalidated since. The graph-native store records property-level provenance (W3C
   PROV-O). This gap hits the core use case: a reader cannot tell whether "0.5/0.3/0.2
   works" came from a measured eval or a scraped blog. *Cheap version:* inline `[^src]`
   citations that resolve against `sources:`, plus a lint rule for assertion-shaped
   sentences with no citation.
2. **Conflict detection is a prompt instruction, not a pipeline step.** "Scan for
   contradictions" lives in CLAUDE.md. Under context pressure it degrades silently, and
   nothing checks that it ran. The README promises "conflicts are flagged, never silently
   overwritten" and nothing enforces it. *Narrow port:* embed claim-bearing sentences at
   ingest, fetch the nearest existing claims above a threshold, send each pair to an LLM
   contradiction judge, and write the hits to the conflicts file.
3. **No temporal model.** A per-page `updated:` date plus a staleness lint cannot answer
   "what did we believe in June, and what changed?" The graph-native store keeps
   bitemporal facts. *Cheap version:* claim-delta tombstones in
   [[Evidence-Driven Wiki Compaction]].
4. **Dedup is monthly and manual.** This is an accepted cost, not a defect. Concept drift
   builds up between compaction passes.
5. **Degradation is silent.** When FTS is unavailable, search falls back to per-term LIKE
   matching and only logs it to stdout. The tool response carries no `degraded` flag. The
   repo's own baselines show the size of the drop: MRR 0.905 with FTS, 0.295 without.
   Cheapest fix: return `degraded` and index staleness in the result.
6. **The rerank blend is arbitrary, but fixing it alone does nothing.** See
   [[Embeddings That Only Rerank Cannot Recall]].

Two more walls from the memory-service review: **any single-page edit triggers a full
corpus rebuild** (DROP, recreate, re-embed; fine at 284 pages, a wall later). And **the one
HTTP write path had no authentication**: localhost and a single user made the risk low,
but it deserved an explicit decision rather than an inherited default.

## Where compiled prose wins (keep these)

- **Compile-time synthesis.** Extraction cannot produce a named mechanism with a
  narrative, like the pages in `patterns/`. Without an LLM writer there is no path to
  them.
- **Eval discipline.** Baselines carry golden-set hashes, embedding model IDs and
  pre-registered parameters, plus a documented null result
  ([[Typed-Graph Retrieval Ablation]]). The graph-native store's eval directory held one
  empty `__init__.py`. Treat a README's accuracy claims as unverified when no retrieval
  eval harness backs them.
- **Measured graph scope.** Expansion is typed-only (2 relations), 1 hop, capped at 5,
  with decay 0.5, and off by default. The memory service's broader BFS is unmeasured.
- **Private-page boundary.** Fails closed, resolves symlinks first, returns "not found"
  rather than "denied" ([[MCP Server Security Patterns]]).
- **Operational weight.** Obsidian as the UI is free. The graph-native store needs a graph
  store, a vector store and a triplestore.

## Not worth porting

Ontology governance, RDF export, rule-engine reasoning and compliance-grade decision
provenance. They serve regulated-enterprise audit and would import a compliance apparatus
with no compliance requirement. Fixed-size chunking with overlap is also out, because here
the page *is* the chunk and its boundaries are an authoring decision.

## Recommended order (as recorded)

1. `degraded` flag (hours, no dependencies).
2. Vector recall arm together with RRF, gated on both eval baselines.
3. Claim-level citations plus lint.
4. Conflict detector (needs a plan).
5. Claim-delta tombstones.

Sequencing caveat: a sibling platform was already moving retrieval to Postgres + pgvector
with RRF. Decide whether to adopt that outcome before fixing retrieval locally. Do not
solve it twice.

## See Also
- [[Knowledge Graph Retrieval]] — alternative-to (graph-native retrieval)
- [[Karpathy LLM Wiki Pattern]] — extends (the compiled-prose bet, stress-tested)
- [[Embeddings That Only Rerank Cannot Recall]] — extends
- [[Evidence-Driven Wiki Compaction]] — extends (manual dedup as a deliberate trade)
- [[Typed-Graph Retrieval Ablation]] — extends (the eval discipline cited as the main lead)
