---
title: Idempotency Lives on the Link Column, Not the Synthetic Key
tags: [infra, pattern]
summary: "A unique index over a sequence-defaulted key does not make a backfill re-runnable, because every run draws a fresh value and the duplicate passes the index — guard on the column that links the synthesized row to its subject (skip any subject already linked, whoever linked it), land synthesized rows in their terminal state outside review denominators, and tag them with a distinguishable creator so rollback is one delete."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-venue-page-and-candidate-reparenting.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-venue-page-and-candidate-reparenting.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-venue-page-and-candidate-reparenting.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-venue-page-and-candidate-reparenting.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-venue-page-and-candidate-reparenting.md
---

# Idempotency Lives on the Link Column, Not the Synthetic Key

A venue catalogue (repo akira, 2026-09-25) had 97 curated `venues` rows. Only 7 of them had
a home in `venue_candidates`, the table the discovery and refresh pipeline and the per-venue
funnel dashboard read. The fix was a backfill that synthesizes one candidate row per
unlinked venue. Most of the design work went into making it safe to re-run.

## The trap: the unique index looks like a guard

`venue_candidates` had a unique index on `(osm_type, osm_id)`. Manual rows take
`osm_type = 'manual'` and a negative `osm_id` drawn from a sequence default. So a second run
draws a new negative id for the same venue, and both rows pass the unique index. The index
protects real OSM identities. It says nothing about "does this venue already have a
candidate".

**The guard goes on the link column.** Read every non-null `venue_candidates.venue_id`
first (one paged read), then skip any venue whose id is in that set. It doesn't matter
which path created the link: this backfill, an OSM accept, or a manual accept. Re-running
after a partial run, or after more venues become eligible, creates rows only for the newly
eligible ones. The planner is a pure function, and its test feeds the first call's created
ids back in as `linkedVenueIds` and asserts the second call creates nothing.

## Synthesized rows land terminal and outside denominators

- **`status = 'accepted'`, not `'proposed'`.** A synthesized row that entered the review
  queue would ask a reviewer to approve a venue that is already live.
- **`review_batch = null`.** The rows were never proposed, so they stay out of the scope
  constant's review batches. Counting them would corrupt the review-progress denominator
  that a shared scope module exists to protect.
- **Expect a side effect in a neighbouring view.** An "accepted but unsourced" panel
  (accepted candidates with no content source) would grow by about 90 rows the moment the
  write ran. That is probably useful, since it surfaces exactly the venues needing a source.
  The plan flagged it before the write so nobody would read the jump as a regression.

## Provenance without a migration

The `source` CHECK allowed three values, and none of them described "synthesized from an
existing row". The migration's own comment said `source` is provenance only, never a second
lifecycle column, and the brief ruled out a migration. So the backfill reused
`source = 'manual_admin'` and set `created_by` / `reviewed_by` to a distinguishable tag
(`'<ticket>-venue-backfill'`) instead of an admin email. That makes the rows searchable, and
rollback is a single delete on `source` + `created_by`. That clean rollback is the reason
the tag exists.

## Two corrections the plan made against the tree

- **A constraint the plan relied on had been dropped by a later migration.** An early draft
  skipped 4 venues with null coordinates because the original migration declared `lat` /
  `lon NOT NULL`. A later migration had dropped that constraint table-wide for another
  import path, the generated types already showed `lat?: number | null`, and the UI already
  null-guarded both fields. All 90 venues went in, and geocoding stayed a separate follow-up.
  Read the generated types or the latest migration, not the table's first migration.
- **No fuzzy merge.** Two of the 90 had a name match within 150 m of an existing `proposed`
  candidate. The backfill gave them new rows anyway and printed both ids for a human to
  review. A wrong merge is harder to undo than a harmless duplicate.

The backfill also did not satisfy the issue's navigation gate. The review map filters on
`status = 'proposed'` and one district, so accepted rows never show a pin. The issue closed
on a recorded operator decision that browsing the full catalogue was no longer needed, and
slug resolution on the existing detail route replaced the deleted catalogue page.

## See Also
- [[Backfill Without the Forward Path]] — extends (the sequencing and dry-run discipline this backfill followed)
- [[Natural Key Without a Discriminator Collapses Rows]] — related (the opposite failure: a key that matches too much)
- [[Advance-Only Machine Writes on a Shared Lifecycle]] — related (synthesized rows enter the lifecycle in a state the machine is allowed to own)
- [[Every Column Names Its Reader]] — related (provenance-only columns are not a second lifecycle)
- [[Kiez Project]] — instance-of
