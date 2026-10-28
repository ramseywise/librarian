---
title: Fixed-Rule Clusters With a Degeneracy Gate
tags: [patterns, eval, pattern]
summary: "To show what enrichment learned about a small corpus (~200 enriched rows), group items by a small fixed set of named rule hypotheses instead of k-means or embeddings, reject degenerate outputs by construction (one cluster holding everything, singleton clusters), gate that shape check at 1.0 with fixtures hand-authored from the rule text, and give un-enriched items their own labelled group so nothing silently disappears."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-enriched-clustered-venue-feed.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-enriched-clustered-venue-feed.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-enriched-clustered-venue-feed.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-enriched-clustered-venue-feed.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-enriched-clustered-venue-feed.md
---

# Fixed-Rule Clusters With a Degeneracy Gate

From replacing a flat five-card venue shelf in an internal review feed with named
clusters built from AI enrichment (repo akira, 2026-09-25). The scope held about 1,084
candidate venues, and only about 200 had a current enrichment row.

## Why rules, not an algorithm

A general clustering algorithm (k-means, embedding similarity) was ruled out. With about
200 rows there was no measured basis to tune it against, and its output could not be
gated without the grader running the clusterer as its own oracle. Instead, a **small
fixed hypothesis set**:

1. `high_energy`: `energyLevel === 'high'` only.
2. Top-frequency vibe and context tag buckets, with a minimum count of 3, counting a tag
   once per row even when it appears in both tag lists.

Each cluster carries a title and a one-line "why this hypothesis" so the reviewer sees
the rule, not just the grouping.

## Degeneracy rejected by construction

- A venue may sit in several clusters, but **never in all of them**. A rule that would
  put every enriched candidate in one cluster is rejected before it renders.
- A cluster of size 1 is dropped.
- Un-enriched rows never enter enrichment clusters. They are not silently mixed in.

A heuristic metric checks these shapes. Its fixtures are hand-authored
cluster-membership shapes taken from the rule text, and the grader **never imports or
runs** the real clustering function. That is why it could be **GATED at 1.0** rather
than registered UNGATED (see [[UNGATED Metric Convention]]). The build session confirmed
the grader does not import the function before keeping the gate.

## Honest leftovers

- The roughly 880 un-enriched candidates go in one final **"not yet enriched"** group,
  capped at the old shelf size and kept in the old priority order. Every candidate stays
  reachable, and most of the page's value is that honesty about coverage.
- Enriched rows that no rule places fall out of both sets. The result type's docblock
  says so explicitly rather than leaving the gap implicit.
- AI descriptors render as a **third, visually distinct chip group** with confidence and
  a low-evidence marker, separate from OSM facts and the taste-profile chips. Provenance
  is structural, not only a colour (see [[Graded-Uncertainty Enrichment Contract]]).

## Treat `unknown` as a value, not a null

The energy vocabulary is enforced in code at the sanitize stage, which is the only
writer. There is no DB `CHECK`. The legal values are `low`, `medium`, `high` and
`unknown`. Sanitize writes `unknown` when the model declines or fails the confidence
cut, so it is a real fourth value. Grouping it with a genuine `low` would be a defect.
An out-of-vocabulary legacy string is routed the same defensive way as `unknown`. The
plan's first guess of `{high, lively}` named a value that existed nowhere in the
vocabulary. **Read the enforced vocabulary before writing a rule against it.**

## Scope guard

Clusters are a per-page-load presentational grouping. They are never a ranker input,
and nothing in the shelf is read by the scoring package. The loader catches its own
failures and returns a three-state result (`readOk: false` shows a visible notice,
genuinely empty renders nothing, populated renders clusters), with one log site (see
[[Degrade the Render, Surface the Failure]]).

## See Also
- [[UNGATED Metric Convention]] — extends (when a hand-fixtured shape check may gate)
- [[Graded-Uncertainty Enrichment Contract]] — related (`unknown` as an explicit abstention value)
- [[Degrade the Render, Surface the Failure]] — related (three-state shelf result)
- [[One Facet Per Fact]] — related (the enrichment tags the clusters group on)
- [[Kiez Project]] — instance-of
