---
title: Backfill Without the Forward Path
tags: [infra, pattern]
summary: "A backfill that repairs existing rows while the ingestion path still writes the old shape regresses on the very next row — the next hand-added bar would have reproduced the missing venue link the migration just closed — so sequence it writer first, backfill second, gate ratchet third: fix the forward path, run a dry-run-default backfill with exact matching and a post-write re-query, then flip the warn-only check to fail."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-09-dis221-venue-model.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-09-dis221-venue-model.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-09-dis221-venue-model.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-09-dis221-venue-model.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-09-dis221-venue-model.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-09-dis221-venue-model.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-09-dis221-venue-model.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-10-dis158-relative-image-urls.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-10-dis158-relative-image-urls.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-10-dis158-relative-image-urls.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-10-dis158-relative-image-urls.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-10-dis158-relative-image-urls.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-10-dis158-relative-image-urls.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-10-dis158-relative-image-urls.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-11-dis158-relative-image-urls.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-11-dis158-relative-image-urls.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-11-dis158-relative-image-urls.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-11-dis158-relative-image-urls.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-11-dis158-relative-image-urls.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-11-dis158-relative-image-urls.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-11-dis158-relative-image-urls.md
---

# Backfill Without the Forward Path

The inverse of [[Insert-Only Upserts Strand Normalizer Fixes]]: there, a writer fix never
reaches old rows; here, an old-row fix is undone by an unfixed writer. Both come from the
akira catalogue, from two plans a day apart.

## The finding

The venue-model migration added `venue_id` to hospitality rows and backfilled all 37. But
the single-page ingestion path had no way to set one: its normalized record type had no
venue field, the upserts could not write one even after the column existed, and the
source registry had no venue link to read it from. **Left unfixed, the very next manually
added bar reproduces the exact defect the issue closes.** One source's override comment
already said "keep this out of the event importer until hospitality moves to its own
model" — a live instance of the gap.

So closing the forward gap — a `venue_id` on the source registry, populated in the same
backfill pass, read by the single-page path and passed through — was made a **required
step of the same phase**, not a follow-up ticket. A later phase (serving these rows) was
gated on it, because a partially-backfilled or newly-added row would silently pass the
venue-repetition cap ([[Widen a Narrow Type, Re-Home Its Constraints]]).

## The ordering: writer, backfill, ratchet

The relative-image-URL fix (extractors persisting site-relative `og:image` paths that
never render) shows the full sequence:

1. **Fix the writer first**, at the choke point that already has the base URL — both
   extractors received the fetched page URL, so one shared `resolveImageUrl` helper
   (try `new URL(value, pageUrl)`, drop on failure) fixed every new row.
2. **Backfill in a separate, separately reviewed session** — data mutation is not
   reversible without a snapshot. It resolves each row against its own stored
   `source_url`, so no re-fetch and no network dependency.
3. **Ratchet the gate last.** The image-host check only *warned* on relative URLs. Flipping
   it to fail before the backfill would redden `make gate` on every unrelated branch until
   the data was clean; the flip is a named follow-up conditioned on the production count
   reaching zero ([[Observe-Mode Gate With a Named Enforce Trigger]]).

## Backfill shape that held up

- **Dry-run by default, `--write` to apply**, with a pure, tested plan function
  (`resolve` / `drop` lists) and a thin CLI main. Not SQL inside the migration: reconciling
  duplicates needs matching logic that does not belong in DDL running unattended.
- **Exact normalized-name matching only, no fuzzy threshold.** A wrong merge silently
  fuses two businesses; a missed one leaves a duplicate a human can see. Log every match,
  not just creates.
- **Verify by re-query, not by eyeballing** — after `--write`, assert zero rows still in the
  bad shape. Production result: 57 → 90 venues, 37 linked, 0 unlinked, 0 dangling FKs, 0
  duplicate names; the four known duplicates linked to their pre-existing rows.
- **A mechanical failure is a drop, not a review-queue entry.** An unresolvable image
  value becomes null (fall through to venue cover art), never a `review_reason` — the
  review queue is for judgment calls.
- **Label provenance honestly**: every backfilled venue got `discovery_source = manual`,
  so nothing was falsely claimed as machine-proposed.

## What was left undone, and named

The new classifier column (`venue_kind`) was added but null on all 90 rows — nothing
populated it. Recorded as the gate on the next phase rather than discovered there.

## See Also
- [[Insert-Only Upserts Strand Normalizer Fixes]] — alternative-to (the mirror case: writer fixed, old rows stranded)
- [[Widen a Narrow Type, Re-Home Its Constraints]] — prerequisite-for (the serving phase gated on this)
- [[Observe-Mode Gate With a Named Enforce Trigger]] — related (warn-only check ratcheted after the backfill)
- [[De-Dupe Before You Normalize]] — related (matching discipline for reconciliation)
- [[Keep the Source Subtype Before the First Collapse]] — related (best-effort backfill from a local report that may not exist)
- [[Idempotency Lives on the Link Column, Not the Synthetic Key]] — extends (re-runnable backfill guarded on the link column)
