---
title: Taste vs Defect Verdict Split
tags: [llm, eval, pattern]
summary: "A reviewer's verdict on a generated item conflates two facts — \"is this good enough to serve\" (taste, one value) and \"what is wrong with it\" (defects, a list mapped to the pipeline stage that owns each field) — and splitting them into a verdict plus `defect_fields text[]` is what makes the review log usable for attribution; alongside it, log the counterfactual (`shelves_eligible`: what the item would have qualified for) so the serving rule can be evaluated without re-running it."
updated: 2026-10-16
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-dis353-verdict-split-shelf-log.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-dis353-verdict-split-shelf-log.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-dis353-verdict-split-shelf-log.md
  - data/raw/claude-docs/akira/docs/research/2026-09-21-review-loop-taste-intake-language.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-21-review-loop-taste-intake-language.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-21-review-loop-taste-intake-language.md
---

# Taste vs Defect Verdict Split

From an events-discovery product (repo akira) where humans reviewed model-enriched
rows before publication. The review table stored one verdict per row. A reviewer who
thought a row was fine but had a wrong price had no way to say both.

## The split

| Column | Carries | Type |
|---|---|---|
| verdict | the taste judgment — serve / do not serve | one enum value |
| `defect_fields` | which fields are wrong | `text[]`, each value a field name |

Each field name maps to the **pipeline stage that owns it** (extraction owns `price`,
enrichment owns `energy_level`, …). So a defect count per field is a defect count per
stage, which is the attribution the quality dashboard needed and could not get from a
single verdict column. A row can be "serve, with two defects" or "do not serve, no
specific defect" — both are real and both were previously unrepresentable.

Two constraints on the migration:

- **Legacy row semantics preserved.** Existing single-verdict rows are not rewritten;
  `defect_fields` defaults to empty and old rows read as "no defect recorded", not "no
  defects".
- **Every new column names its reader before it is added.** The plan listed the
  dashboard query and the eval fixture exporter as readers of `defect_fields` before the
  migration was written. See [[Every Column Names Its Reader]].

## The counterfactual log

The same plan added `shelves_eligible` to the serve log: for each served item, the list
of shelves (result sections) it *would have* qualified for under the current rules, not
just the one it was placed on. This makes the composition rule evaluable offline —
"would a different rule have served this item?" is a query, not a re-run — and it has to
be logged at serve time because it cannot be reconstructed once the rules change.

## A bundling footnote

The admin UI that wrote the verdict was a client component; importing the shared review
module would have pulled server-only code into the browser bundle. The fix was a thin
`'use client'` door module re-exporting only the client-safe surface — a reminder that
"share the module" has a cost at the server/client boundary.

## Four Vocabularies, One Rater, No Join

An audit of the review loop found four separate verdict vocabularies written by the same
single rater, and no query that joins them. Findings:

- **`not_mine` is neutral by contract.** Reading it as a negative label would rewrite the
  meaning of every historical row.
- **A questionnaire is the wrong instrument for stable taste.** Pick-cards (choose from a
  shown set) give negatives with known exposure: you know what was shown and passed over.
- **An audience attribute with unknown coverage is a modifier, not a hard filter.** An
  accessibility-style hard filter failed closed on unknown values and emptied the pool.
- The instrumentation already existed. Nobody had read it.

## See Also
- [[HITL Annotation Pipeline]] — extends (what the annotation row should carry)
- [[Every Column Names Its Reader]] — depends-on
- [[One Check Shape for Quality Verdicts]] — prerequisite-for (the split is what the unified verdict store generalises)
- [[Ship Logging Before Features]] — related (the counterfactual log is non-backfillable)
- [[Trajectory Over Outcome]] — related (defect-by-stage is trajectory attribution for a pipeline)
- [[Build the Knobs, Not the Choice]] — extends (the same split applied to scoring claims)
