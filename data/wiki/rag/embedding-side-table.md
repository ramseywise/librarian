---
title: Embedding Side Table, Not Column
tags: [rag, decision]
summary: Store embeddings in a side table keyed by (content_kind, content_id, embedding_model, input_recipe_version) rather than as a vector column on the enrichment row — it keeps "did the content change" and "did we try a new embedding recipe" as separate version axes, lets several recipes coexist for comparison, and keeps unrelated writebacks from churning the HNSW index.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-24-dis386-semantic-retrieval.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-24-dis386-semantic-retrieval.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-24-dis386-semantic-retrieval.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-dis386-lexical-rrf.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-dis386-lexical-rrf.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-dis386-lexical-rrf.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-dis386-lexical-rrf.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-dis386-lexical-rrf.md
---

# Embedding Side Table, Not Column

A storage decision from adding a semantic retrieval arm (pgvector + HNSW) next to an
existing structured filter and lexical search in an events-discovery product (repo
akira, 2026-09-24).

## The decision

Use a dedicated `content_embeddings(content_kind, content_id, embedding_model,
input_recipe_version, embedding, …)` table. Don't add an `embedding` column to the
existing `*_ai_enrichments` rows.

## Why

- **Embedding versions are multi-valued by nature.** The issue required comparing
  embedding inputs (joined descriptors vs. generated description vs. site-text excerpt)
  as well as models. A column holds one vector per row. A side table holds one row per
  `(model, recipe)` pair, so "measure both" needs no migration per candidate recipe.
- **Two version axes must stay orthogonal.** Enrichment rows were already versioned by
  `is_current`, with re-enrichment superseding a row when the content evidence changes.
  Stacking a second axis (model × recipe) onto that row conflates two questions: did
  the content change, or did we just try a new recipe on the same content? Keying the
  side table on its own version columns makes each axis explicit (the same idea as
  [[Frozen Version Stamps on Logged Results]]).
- **HNSW wants a quiet, single-purpose table.** Re-probe writebacks touch enrichment rows
  on every run. A vector column there would be invalidated and reindexed on writes that
  have nothing to do with the vector.
- **No nullable-column sprawl.** The alternative is one vector column per recipe tried,
  or a JSON blob, which defeats the typed pgvector column and HNSW.

Every column named its reader before it was proposed: `embedding` is read by the
semantic query stage, and the model and recipe columns by the comparison tooling (see
[[Every Column Names Its Reader]]).

## How the arm plugs in

- Structured filter → lexical arm + semantic arm → [[Reciprocal Rank Fusion (RRF)]] →
  the existing scoring pipeline, **unchanged**. RRF decides pool order and inclusion. It
  is never a scoring dimension, and the controlled-vocabulary filter is never bypassed.
- "Semantic arm returns nothing" is a **designed degraded mode**: RRF runs on the
  remaining arms, logged and non-fatal. It isn't an error path to invent later.
- Embeddings stay off the request path for the catalogue side, in line with
  [[Offline Annotation over Online Inference]].

## Build dark, flip on a gated metric

Slices 1–7 (schema, backfill, both arms, RRF stage) could all be built and reviewed
behind a flag. The live flip waits on a **gated retrieval metric over an independently
sourced query set**: at least 30 judgments across at least 5 moments, from either a
human grading pass or poll votes. Both sources had 0 rows. Wiring retrieval into ranking
without that would repeat a known co-fitting mistake (see
[[UNGATED Metric Convention]]).

Two side findings:

- The PRD's 🟢 "built" markers for hybrid search were inherited from feasibility docs
  and were stale. The live path was filter queries only. Verify status markers against
  the tree.
- A proposal to drop the `energy_level` enrichment field because retrieval would cover
  it was re-measured first. Its unknown rate halved from 40.7% to 19.5% once site text
  reached the prompt, so the field stayed, and the work was split into its own issue.

## The lexical arm went the other way

The semantic arm needed a side table because an embedding is model-versioned and
async. The lexical arm built next to it is a pure derivation of the row (`tsvector`
over name and tags), so it went into generated columns on the row instead (see
[[Pure Derivation Is a Generated Column]]). The same build-dark guard applied: a
grep-test proves the hybrid module is not imported by any serving path.

## See Also
- [[Reciprocal Rank Fusion (RRF)]] — prerequisite-for (the fusion step the side table feeds)
- [[Offline Annotation over Online Inference]] — complements (where model work belongs)
- [[Frozen Version Stamps on Logged Results]] — instance-of (version axes as explicit columns)
- [[Vector Database Comparison]] — related
- [[Kiez Project]] — instance-of
- [[Pure Derivation Is a Generated Column]] — alternative-to (generated columns for the pure lexical derivation)
- [[Per-Row Content Hash Misses Cross-Row State]] — related (a content hash without a model key lets embeddings drift)
