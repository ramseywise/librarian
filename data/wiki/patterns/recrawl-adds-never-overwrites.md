---
title: Re-Crawl Adds, Never Overwrites
tags: [patterns, infra, pattern]
summary: "Once a content row exists, a re-crawl may only add occurrences and dates; a genuine title or description change is flagged for review, not written. A same-URL overwrite silently renames, hides and reverts published rows, and makes any later skip-gate compare against a baseline newer than the enrichment."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-dis264-enrichment-input-shaping.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-dis264-enrichment-input-shaping.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-dis264-enrichment-input-shaping.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-dis264-enrichment-input-shaping.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-dis264-enrichment-input-shaping.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-dis264-enrichment-input-shaping.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-dis264-enrichment-input-shaping.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-30-dis425-title-matches-venue.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-30-dis425-title-matches-venue.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-30-dis425-title-matches-venue.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-30-dis425-title-matches-venue.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-30-dis425-title-matches-venue.md
---

# Re-Crawl Adds, Never Overwrites

From an akira plan that started as "stop re-enriching recurring events" and ended as an
architecture rule for the importer. The rule: **a crawl is raw input. Once a row exists, a
re-crawl never rewrites its content.** It may add occurrences and dates. A real change to title or
description is flagged for a human, and the enrichment handoff is withheld.

## Why the skip gate kept failing

The first design compared each incoming record against the stored row and skipped enrichment
when nothing that matters had changed. Three traps appeared, one per refine pass.

1. **The hash covered the wrong things.** The content hash ran over the whole handoff, including
   `source_url`, start/end dates and the raw extraction. Every recurrence or date change missed the
   hash and paid for a full re-enrichment. Dropping dates from the hash was rejected: it invalidates
   every stored hash, so the next crawl re-enriches the entire catalogue.
2. **The comparison baseline was lossy.** A legal-safety sanitizer nulled any description over 280
   characters. Comparing post-sanitize columns calls two *different* long descriptions equal (both
   `null`) and skips a genuinely changed event. Compare the unsanitized text kept in `raw_data`.
   Where only the sanitized legacy value exists, let the fallback **fail toward enrich**. The only
   legacy case that skips is "both sides empty".
3. **The baseline was newer than the enrichment.** The same-URL upsert overwrote the row *before*
   the handoff. If crawl N changed the page, overwrote the row, and then produced no enrichment
   (spend cap, failed model result, handoff disabled by default, batch item failed at collect),
   crawl N+1 compared against crawl N's text, found no change, and skipped. The enrichment stayed
   built from crawl N−1 indefinitely. The enrichment row stored only a hash, and `updated_at` was
   bumped by a trigger on every write, so nothing could reconstruct what the enrichment was built
   from.

Gap 3 has no clean fix while the row can be overwritten. Closing it required the rule itself: if
the row never changes after insert, the stored row is always exactly the enrichment's input.

## What the overwrite was already breaking

Tracing the same-URL upsert listed what a routine re-crawl silently did to a **published** row:

- renamed its public URL, because the slug embeds the start date;
- hid it, because `needs_review` was recomputed from confidence and date presence, and visibility
  requires it false;
- blanked `start_at` when the page lost its date, failing the visibility gate;
- reset editorial defaults (district, priority, fit);
- reverted values operators had corrected by hand or fixed with backfill scripts.

The no-overwrite rule closes all of these as a side effect.

## The write path

1. **One existence read per record.** Its row is the single comparison baseline.
2. **New rows insert with `ON CONFLICT DO NOTHING`.** If a concurrent insert wins, re-read and
   treat the row as existing. Nothing in the importer can issue a content `UPDATE` to a
   *reviewed* row. One scoped exception came later: on a natural-key match, a merge may refresh
   descriptive fields (coalesced, rank-ruled for provenance) while `review_status` is still
   `draft` or `needs_review`, before any human has signed off. Once reviewed, never overwrite.
   See [[Coalesce Against a Never-Null Source]].
3. **Existing rows** get the occurrence upsert, the earliest/latest date sync (now on both branches,
   matching the documented contract), and one pure decision:
   - identity unchanged → handoff allowed, subject to the other gates;
   - same-URL identity changed → append `source_content_changed` to a review-reason array once,
     withhold the handoff;
   - natural-key sibling with a different description → count it, withhold;
   - id listed in an operator refresh variable → rewrite content columns, re-enrich.
4. **Every insert column is classified once, in code** (identity, content, editorial, review,
   occurrence/volatile). A test fails when a new payload key is unclassified, so the rule cannot
   erode silently when a sibling plan adds a column.
5. **The flag lives where it cannot change visibility.** The review-reason column had no reader in
   the feed, visibility helpers or RLS, so appending to it was provably inert. `needs_review` was
   rejected: it had four writers, the next of which would clear the flag, and on a published row it
   unpublishes. A new admin section became the flag's reader.

Terminal URLs (rejected, duplicate) are also filtered *before* fetch, so they stop consuming slots
in the per-source detail-link cap. Archived URLs are still fetched, because archive was documented
as reversible by a new occurrence.

## Costs, named

- **A real page correction now waits for a human.** That is the accepted tradeoff.
- **Extractor improvements no longer reach old rows** on their own. With no snapshot store, an
  operator refresh or a backfill is the only route (see
  [[Insert-Only Upserts Strand Normalizer Fixes]]). The first crawl after deploy can flag rows whose
  stored text differs only because the extractor changed.
- **Every column a sibling plan adds must be classified**, or existing rows never receive it. A
  date column marked authoritative from the importer has to be listed volatile, or only new rows get
  dates.
- **A wrong skip loses an enrichment update, not data.** Fail-open reads cost spend, never content,
  and each read failure is a warn line plus a run-summary counter.

## Recovering a row the gate wrongly rejected (akira #425, 2026-09-30)

An extractor kept only the venue suffix of a templated `og:title` (`– Galerie …`, an EN
DASH and a space before the venue name). The QC title-equals-venue gate compared titles
with trim-only exact equality, so it let these through. 49 rows were later moved to
`rejected` with a `title_extraction_defect` reason. The plan assumed the existing refresh
switch (`REFRESH_CONTENT_IDS`) could re-crawl them. Reading the code showed it could not:

- The importer drops every URL whose stored row is **terminal** (`rejected`, `duplicate`)
  from the fetch list *before fetching*. That filter is keyed only on the stored review
  status and never consults the refresh list.
- The refresh function is only reachable after a page is fetched and matched, and by
  design it never writes `review_status`. So even if it ran, it would not un-reject a row.

**Recovery is two operator steps, in order.** First, a reviewed SQL flip from terminal back
to `draft`, with a narrow `WHERE` (the specific reason tag plus `rejected`) and a
`count(*)` against the expected number before it runs. Then a re-crawl with the refresh ids
set, and only after the widened gate is deployed, so a still-junk title is re-rejected
instead of re-accepted.

**The non-decision is named.** Making the terminal skip refresh-aware would let a future
crawl reach into rejected rows implicitly, which cuts against this page's invariant. The
plan put it out of scope explicitly rather than leaving it unmentioned.

Two related moves in the same plan:

- The widened predicate became one shared, exported helper. The two inline copies had not
  drifted; *both* were too narrow. It copied the separator set an extractor had already
  proven on that host, rather than importing across the dependency rule.
- The slug-to-title extraction fix was split out, because it needs a live fetch to confirm
  the pages carry no heading.

## See Also
- [[Insert-Only Upserts Strand Normalizer Fixes]] — prerequisite-for (the consequence for normalizer fixes)
- [[Advance-Only Machine Writes on a Shared Lifecycle]] — extends (the same principle for content columns: machine writes never undo human state)
- [[Event–Occurrence Split, Added Behind the Old Column]] — extends (resolves the cost named there: the hash covered dates)
- [[Input-Starved Enrichment]] — related (the same plan's input-shaping phase)
- [[Every Column Names Its Reader]] — related (the review-reason column needed a reader before the flag meant anything)
- [[Coalesce Against a Never-Null Source]] — extends (the in-review exception: descriptive fields refresh on a natural-key match only before review)
