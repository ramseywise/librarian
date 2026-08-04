---
title: Wiki Graph Engineering — Edge Quality Over Edge Count
tags: [meta, rag, decision]
summary: Why librarian's link graph under-connects, why the typed-relationship subgraph is the layer worth querying, and the design choices behind one-hop retrieval expansion.
updated: 2026-08-04
sources:
  - data/wiki/_relink_suggestions.md
  - data/wiki/_bridge_suggestions.md
---

# Wiki Graph Engineering — Edge Quality Over Edge Count

Measured 2026-08-04 against the live wiki (281 pages):

| Signal | Count |
|---|---|
| Total wikilink edges | 6,887 (~24/page) |
| Typed relationship edges | 543 (7%) |
| Pages with ≥1 typed out-edge | 189 / 281 |
| Median typed out-degree (of those) | 2 |
| Bridge gaps (>5 pages each, <3 cross-links) | 57 |

## The Two Edge Populations Behave Differently

The raw link graph is **dense and low-precision**. At ~24 edges per page it is
mostly mentions, prose references, and `_index.md` rows. Expanding retrieval
along it is useless: a 10-result search becomes a 240-page neighbourhood.

The typed subgraph — `## See Also` entries annotated `— extends`,
`— prerequisite-for`, etc. — is **sparse and high-precision**. It is
author-asserted rather than incidental: someone decided the relationship held
and named it. At 7% of edges but two-thirds page coverage, it is the layer
worth traversing.

The practical rule: **edge quality, not edge count.** Adding more links does not
improve retrieval; annotating existing ones does.

## Why the Graph Under-Connects

Both edge sources have the same blind spot. Wikilinks encode *what the author
remembered to link*, which correlates with recency and with sitting in the same
directory. Cosine-similarity backfill (`core/relinker.py`) adds edges between
pages sharing vocabulary. Neither can connect two pages that are genuinely
related but use different words and were written weeks apart.

That is the exact signature of the 57 bridge gaps — `context ↔ interview` at 0
cross-links, `foundations ↔ graph` at 0. These are not link failures to patch
individually. A gap between two well-populated domains usually means a **missing
bridge page**: the concept that connects them does not exist yet. The gap report
is better read as a generative prompt ("what page is missing here?") than as a
lint queue.

## One-Hop Retrieval Expansion (spike, 2026-08-04)

`search_wiki(..., expand=True)` returns pages one typed hop from the primary
results. Design choices:

**Only `prerequisite-for` and `extends` are traversed** (375 of 543 typed edges).
Both express directional dependency — "what else do I need to understand this
hit?" `alternative-to` and `contradicts` are excluded: useful to a human reader,
but they pull in competing approaches, which is noise when the caller asked
about one thing.

**Traversal is bidirectional, but reverse edges are relabelled.** This was the
non-obvious defect the spike surfaced. The annotation is written from the
*linking* page's point of view: `[[Transformer Architecture]] — prerequisite-for`
on the inference-economics page means *the transformer page is a prerequisite
for this one*. Following that edge backwards is still valuable — a foundation
should surface what builds on it — but reporting it with the same label inverts
the hierarchy. Reverse traversal is therefore labelled `builds-on` /
`extended-by`. Without this the expansion tells a reader that a study guide is a
prerequisite for the pipeline it summarises.

**Neighbours are ranked by distinct-seed reach.** A page reached from several
primary hits is more likely central to the query than one reached from a single
hit. Capped (default 5) to bound context cost.

**Expansion quality is bounded by primary-hit quality.** A weak primary result
produces a weak neighbourhood — observed in testing: a spurious hit on
`Claude Workflow System` for "prefix caching" dragged `SKILL.md Pattern` in with
it. Expansion amplifies the ranker; it does not correct it.

## What Was Considered and Rejected

**A property-graph database (Neo4j).** At a few hundred pages the bottleneck is
edge quality, not query performance. Migrating storage does not improve edge
quality. DuckDB handles multi-hop at this scale.

**Community detection / GraphRAG clustering.** Blocked on entity resolution —
`Reward Hacking` and `Reward Hacking and Overoptimization` currently resolve as
distinct nodes. Clustering over aliases measures nothing. Canonical-entity
resolution is the prerequisite.

**Claim-level triple extraction.** The larger idea: make the *claim* the
primitive rather than the page, extracting `(DPO, alternative-to, RLHF)` and
scope qualifiers like `(Timebox-Scaled Deliverable Bar, holds-at, 1–6h async)`
into a triple store alongside the markdown. This would make conflict resolution
machine-visible — the 2026-08-04 test-coverage resolution was a *scoping*
judgement that currently lives as prose in `_conflicts.md` and is invisible to
retrieval. Deferred deliberately: it adds a second obligation to every ingest,
which is the kind of thing that gets built and then quietly unmaintained. Wait
until a query demands it.

## See Also
- [[Karpathy LLM Wiki Pattern]] — extends (the compile model this refines)
- [[Librarian RAG Architecture]] — extends (retrieval stack this modifies)
- [[Documentation Boundary — Machine vs Human Docs]] — prerequisite-for (who may write what)
