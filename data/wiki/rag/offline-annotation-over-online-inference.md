---
title: Offline Annotation over Online Inference
tags: [rag, infra, llm, decision]
summary: Decision to spend all model work at ingest time — enrich each catalogue row once into a fixed taxonomy — and serve with a plain WHERE clause plus in-memory scoring over ≤1,000 rows, with no embeddings, pgvector or GPU; the serving path becomes deterministic, cheap and replayable, and the dominant cost lever moves to caching the static taxonomy prefix of the enrichment prompt rather than gating re-runs.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/playground/docs/research/2026-08-27-schema-audit.md
  - data/raw/claude-docs/diskoe/docs/notion/ai-enrichment.md
  - data/raw/claude-docs/playground/docs/notion/ai-enrichment.md
  - data/raw/claude-docs/akira/docs/technical-feasibility.md
  - data/raw/claude-docs/diskoe/docs/technical-feasibility.md
  - data/raw/claude-docs/playground/docs/technical-feasibility.md
  - data/raw/claude-docs/kiez-archive/docs/technical-feasibility.md
---

# Offline Annotation over Online Inference

**Decision (diskoe, 2026-08):** the LLM's job in a recommendation product is offline
annotation, not online inference.

## Context

A local-events recommender with a catalogue of hundreds to low thousands of live items
and a structured request form (time, district, format, vibe, companions, budget). The
tempting architecture was retrieval-style: embed listings, embed the request, nearest
neighbours, rerank.

## Decision

- Every row is **enriched once** at ingest into a fixed taxonomy (format, category, vibe,
  context, plan role, audience, accessibility, uncertainty flags).
- Serving is a **`WHERE` clause** over the hard constraints plus **in-memory scoring**
  of the ≤1,000 surviving rows with a deterministic rubric
  (see [[Specificity-Adaptive Ranking and Slate Composition]]).
- **No embeddings, no pgvector, no GPU, no model call on the request path.**

## Why

- The request is already structured; there is no free-text query whose meaning needs
  recovering at serve time. Similarity search would be solving a problem the form
  removed.
- A deterministic serving path can be **replayed exactly** from a logged request and
  pool, which is what every later eval depends on (see [[Replayable Slate Ranker]]) and
  what makes a position-randomisation slice cheap to ship.
- The catalogue is small enough that per-request scoring is microseconds; the cost of an
  online model call would dominate every request for no measurable gain.

## Cost consequences

Once the model is only in the enrichment stage, the cost shape changes:

- Input tokens were ~97% of enrichment cost, and most of that input is the **static
  taxonomy and instructions**, identical across every call. Caching that prefix
  (see [[Prefix Caching]]) is a larger lever than the content-hash re-run gate
  (see [[Spend Gate Before the Model Call]]), which only saves calls on unchanged rows.
- Earlier dollar projections for the stage were **retracted** — they were derived from a
  baseline that a later measurement contradicted — and the audit kept only the ratios.
- Self-hosting a model was ruled out below millions of calls per month; the fixed cost
  of operating it exceeds the API bill by a wide margin at this scale.

## Tradeoffs

- Nothing new is learned at serve time; taxonomy gaps show up as items that *cannot* be
  matched until the next enrichment run.
- Taxonomy changes imply re-enrichment of the catalogue (bounded by the content-hash
  gate and prefix cache).
- Free-text requests, if ever added, would need a separate path — most likely a model
  call that maps text onto the same structured form, keeping the serving path intact.

## The deterministic-core test (feasibility study, 2026-10)

No LLM on the request path; models enrich and repair offline. This became the test for every
tooling question — *if it must run during a request, the answer is no.* Consequences: an
agent framework is not justified for a single-shot structured-extraction call (defer the
choice until a real plan-act-observe agent exists, then compare candidates); batch plus
prefix caching gives ~3× savings before any vendor change; the eval harness must exist before
a model swap. Graph vs vector is a false choice — vector search generates candidates,
relational tables hold the neighbourhood used as enrichment evidence; a graph DB waits until
>10⁷ edges and multi-hop queries dominate.

## See Also
- [[RAG Retrieval Strategies]] — alternative-to (metadata filtering plus rubric scoring instead of similarity retrieval)
- [[Specificity-Adaptive Ranking and Slate Composition]] — prerequisite-for
- [[Prefix Caching]] — extends (why the taxonomy prefix is the dominant cost lever)
- [[Spend Gate Before the Model Call]] — related (the per-row gate this decision reframes as the smaller lever)
- [[Two AI Cost Economies: Durable Once, Contextual On Demand]] — instance-of (enrichment is the durable-once economy)
- [[Graded-Uncertainty Enrichment Contract]] — related (what the offline annotation produces)
- [[Embedding Side Table, Not Column]] — related (catalogue embeddings computed offline, versioned in their own table)
- [[Relevance Is the Score, Enrichability Is the Gate]] — related (choosing which rows get the offline annotation)
