---
title: Tighten a Visibility Gate by Backfilling the Visible State
tags: [infra, pattern]
summary: "When a new review-status column tightens a public read policy from `using (true)`, backfill existing rows to the state that keeps them visible and default only new rows to draft — otherwise the migration silently 404s every live public page, and nothing in the diff reads as the cause; find the anon-scoped readers by grepping every call site against its client constructor."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-29-venue-review-status-gate.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-29-venue-review-status-gate.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-29-venue-review-status-gate.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-29-venue-review-status-gate.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-29-venue-review-status-gate.md
---

# Tighten a Visibility Gate by Backfilling the Visible State

An akira catalogue had a `venues` table treated as reference data. Its public read policy
was `using (true)`, with a comment saying a venue was only a name and an address. Every
other standing-content table already gated on `review_status = 'published'`. Showing
enriched venues to visitors meant turning venues into gated content too: add the column,
and tighten the policy.

## The finding that set the backfill

The plan grepped all 36 `from('venues')` call sites and checked each one's client
constructor. Every reader used the service-role client, which bypasses RLS, except one: a
**live public route**, `/places/[slug]`, that read venues through the anon-key client with
no status predicate (the column did not exist yet). Nothing in the public list linked to it,
but it was reachable by direct URL.

So the moment the policy tightened, every venue not marked `published` would 404 on that
route. If existing rows were backfilled to `draft`, that meant every venue page reachable
that day. No code change would be flagged as the cause.

## The rule

- **Backfill existing rows to the state that keeps today's behaviour** (`published`).
  Nothing visible becomes invisible.
- **Default new rows to `draft`.** The gate is real for everything added from then on, and
  the insert path needs no change because it never set a status field.
- **Make the judgement on old rows a deliberate per-row downgrade** by an operator after
  the migration, not a silent mass-publish dressed up as review. The plan named that sweep as
  an operator follow-up.
- This repeats an earlier migration's posture: backfill from the best signal available to
  avoid a blackout, and enforce only going forward.
- **Rollback and forward state are behaviourally identical for every pre-existing row.**
  That is what makes the tightening safe to land.

## Companion decisions

- **One lifecycle column, mirrored shape.** The column, its CHECK vocabulary and its
  companions (`review_reason`, `review_notes`, `reviewed_by`, `reviewed_at`,
  `missing_fields`) copy the sibling tables exactly, so a reader finds the same shape on
  every standing-content table.
- **Sign-off is manual only.** No AI enrichment field auto-promotes a row to `published`.
  There is one admin-client Server Action on the existing operator page, behind the same
  admin-auth gate as its neighbours, with no new auth check invented.
- **Don't open a read policy with no reader.** The enrichment table stayed closed to anon
  until a slice actually renders enrichment to visitors. A policy nobody consumes is inert
  and only understandable by reading the plan, the policy version of
  [[Every Column Names Its Reader]].
- **Policy changes use drop-then-create.** The guard is on the policy name, not its
  definition.

## Contrast

[[Written-but-Inert RLS Policies]] records the opposite failure: a public policy gated on
`published` when no live row had that value, so it admitted nothing. Both are
predicate-vs-live-distribution checks. Before a policy changes, read the live value
distribution and the list of anon-scoped readers.

## See Also
- [[Written-but-Inert RLS Policies]] — related (a predicate no row satisfies, the inverse risk)
- [[RLS Gates Rows, Not Columns]] — related (another `using (true)` policy that a plan missed)
- [[Migration Done Means Pushed and Probed]] — related
- [[Every Column Names Its Reader]] — extends (applied to read policies)
- [[Advance-Only Machine Writes on a Shared Lifecycle]] — related (automation never writes `published`)
