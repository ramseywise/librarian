---
title: Append-Only Human Labels
tags: [eval, pattern]
summary: Persist rater judgments as append-only rows keyed to the exact enrichment row they judged, with an instrument column and a fixed rater picklist — never update, never collapse to consensus, because agreement statistics need every rating that was ever made.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-15-dis275-human-label-persistence.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-15-dis275-human-label-persistence.md
  - data/raw/claude-docs/akira/docs/research/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/akira/docs/research/2026-09-03-divergence-since-waslosheute-mvp.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-divergence-since-waslosheute-mvp.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-divergence-since-diskoe-mvp.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-divergence-since-diskoe-mvp.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-15-dis275-human-label-persistence.md
  - data/raw/claude-docs/playground/docs/research/2026-09-15-dis275-human-label-persistence.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-15-dis275-human-label-persistence.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-15-dis275-human-label-persistence.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-15-dis275-human-label-persistence.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-15-dis275-human-label-persistence.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-15-dis275-human-label-persistence.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-15-dis275-human-label-persistence.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-15-dis275-human-label-persistence.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis289-relevance-benchmark-corpus.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis289-relevance-benchmark-corpus.md
---

# Append-Only Human Labels

Design decisions for persisting human enrichment labels and relevance judgments on an
LLM-enriched product (akira), where an admin rating tool had been writing labels only to a
browser-downloaded JSONL — every session one export away from loss.

## Decisions

| Question | Choice | Why |
|---|---|---|
| Table cluster | interaction / measurement; admin or service-role write only | A label is evidence, not product state; see [[Data Clusters by Writer and Trust]] |
| Label key | the specific enrichment row, not the content item | A later re-enrichment must not silently reinterpret an old judgment |
| Multi-vertical key | `(content_kind, enrichment_id)` + validation trigger | Three enrichment tables; a single FK rejects two of them |
| Re-rating | **append, never update; latest-wins at read time** via `is_current` | Agreement scripts must consume *all* rows — intra-rater consistency is only measurable if every rating survives; a composite PK + `updated_at` destroys the history the measurement needs |
| Rater identity | self-declared id from a **fixed picklist**, not free text, not accounts | Free text silently splits one rater into two on a typo; accounts over-collect for a handful of trusted raters |
| Instrument | explicit `instrument` column (`absolute` / `pairwise`) | Two instruments on the same attributes must be filterable; the schema must not conflate them |
| Prompt join | store the prompt hash the label judged | Needs the enrichment row to carry prompt identity — a prerequisite that blocked half the done-criterion |
| Group vs individual | `source: 'poll_vote'` kept separable from `'rater'` | A poll vote answers "would this group go?", not "is this relevant to one rater's moment"; the two are never pooled, and a 3-way ballot has no mapping to a 4-way grade's "borderline" |

## Instrument parity

For two label sets to be comparable, the scale, attribute set, and anchors must match
exactly what the enrichment stores — the same ordinal values, the same tag vocabulary, an
anchor string at every scale point ("unanchored scales inflate apparent disagreement").
Set-valued labels use MASI / Krippendorff's alpha; the statistic was already built, only
the write location changed.

## What the build plan added

The plan that built this table refined three of the decisions above. **Rater ids became
opaque codes** (`r01`…) enforced by a DB CHECK, because an append-only table makes real
names permanent. **Supersession is scoped to an assignment occurrence**, so a deliberately
repeated item does not retire the rater's first judgment. **Prompt identity is snapshotted
only on pairwise rows.** Blind absolute rows carry an evidence hash instead, enforced by a
CHECK. Export is split into a parity export (current rows, in the agreement script's exact
shapes) and a raw export (every row). See [[Blind Labels Judge No Prompt]].

## The judge's trust ceiling

From the same product's decision log: an LLM judge's agreement with humans cannot be
trusted above the human–human agreement measured on the same instrument. The judge is a
**regression detector, never a launch gate**; items the judge cannot classify fail safe to
`needs_human_review`; a fixed fraction (~25%) of judge critiques is sampled for human
review on an ongoing basis. See [[LLM-as-Judge Evaluation]].

## See Also
- [[HITL Annotation Pipeline]] — extends (the storage layer under the annotation queue)
- [[LLM-as-Judge Evaluation]] — prerequisite-for (human labels set the judge's ceiling)
- [[Data Clusters by Writer and Trust]] — instance-of
- [[Frozen Version Stamps on Logged Results]] — complements (which versions a label must be joined to)
- [[Frozen Ranking Baseline from a Pure Ranker]] — prerequisite-for (the judgment rows feed the baseline; agree the field contract first)
- [[One-Sided Label Control]] — extends (a labelling UI that can only write one verdict makes precision unmeasurable)
- [[Blind Labels Judge No Prompt]] — extends (the instrument split enforced in the schema)
- [[Prove Discovery Before Evaluating Enrichment]] — related (the discovery-precision sample shares this table's shape)
- [[Stratified Judgment Pool for a Ranker Benchmark]] — extends (the relevance-judgment corpus built on these rules)
