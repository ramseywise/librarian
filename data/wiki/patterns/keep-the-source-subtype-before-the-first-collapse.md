---
title: Keep the Source Subtype Before the First Collapse
tags: [patterns, foundations, pattern]
summary: "When a taxonomy loses precision, find the first lossy step on the live write path, not the bucketing the issue names. Keep the raw upstream identity as a namespaced fact column, guarded by a prefix-only CHECK rather than an enumerated one. Before adding a downstream column, check for one that is already read but never written."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis293-osm-place-subtype.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis293-osm-place-subtype.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis293-osm-place-subtype.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis293-osm-place-subtype.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis293-osm-place-subtype.md
  - data/raw/repos/librarian/.claude--docs--plans--2026-07-31-LIB-57-factstore-failure-attribution.md
---

# Keep the Source Subtype Before the First Collapse

From akira's OSM venue discovery (plan #293, 2026-09). Roughly 14,500 OpenStreetMap places
were discovered. Each carried a precise raw tag (`shop=books`, `leisure=escape_game`,
`historic=memorial`). By the time anything downstream (enrichment, review, benchmark
slicing) could use that identity, it had been reduced to a handful of buckets.

## The issue named the wrong collapse

The ticket blamed a 4-bucket `store_focus` grouping. Reading the code showed two things:

- `store_focus` was **not a column and not on the write path**. Its only caller built a
  CSV review sheet for a human.
- The real loss happened **one step earlier, on the live path**. A `deriveVenueKind()`
  step mapped about 1,400 OSM tag keys to 12 `venue_kind` values. A second step collapsed
  those to a 7-value activity type or a 3-value primary type before the content row was
  written.

Fixing the grouping the ticket named would have recovered nothing. Trace the value
forward from the source and find the **first** step that throws information away. That is
where the raw value has to be kept.

## The raw value survived only off-database

The full tag set existed for one discovery run, in memory, and in a gitignored JSON report
on one operator's machine. No table kept it. Once that file was gone, the only way back
was to query OSM again. So the backfill was written as **best-effort**: it matches
`(osm_type, osm_id)` against whatever report is on disk and exits 0 as a reported no-op
when there is none. New discovery runs fill the column from live tags, so no backfill is
needed for those.

## A column that is read but never written

Both content tables had had a `subcategory text[]` column since the original schema. The
enrichment prompt already printed it, and the raw-tags builders already folded it in. But
every real normaliser hard-coded it to `[]`, so it had never held a value on any row. That
changed the plan. Instead of adding a new downstream column, the plan **filled the inert
one**, at the single place the linked venue's kind already overrode the normalised record.
New columns went only on the two tables with nowhere to put the value: the proposal queue
and the accepted-venue table.

This is the mirror image of [[Write-Only Fields and the Reader Map]]. That page is about a
value written but never read. Here a reader existed and nothing ever wrote to it. A reader
audit should look for both.

## Shape of the kept value

- **A fact, not a second classifier.** `placeSubtype(tags)` takes the first present key
  in a fixed order (`amenity`, `shop`, `tourism`, `leisure`, `historic`, `natural`). It
  deliberately does not repeat the bucketing logic (sport special-cases, chain
  exclusions). The question it answers is "which tag did this element carry", not
  another classification decision.
- **Namespaced, not bare.** Values look like `shop:books`, not `books`. Bare values clash
  across namespaces (`shop=market` vs `amenity=market`), and the namespace carries
  meaning of its own.
- **A provenance-neutral name.** The column is `place_subtype`, not `osm_category`. A
  second discovery source will need the same idea, and provenance already has its own
  column.
- **The CHECK validates only the prefix.** `place_subtype is null or place_subtype ~
  '^(amenity|shop|tourism|leisure|historic|natural):'`. The upstream vocabulary has
  hundreds of values and grows outside the repo's control, so listing them would make the
  constraint go stale by design. The prefix check still catches the real bug class: a
  caller passing a bare value or the wrong separator. It does not catch an empty tail
  (`shop:`), and that was accepted.

## Ship the column with its reader

A risk the plan named outright: if the migration lands in one PR and its reader in another,
the column sits empty and unread. That is the same mistake as an earlier column added
before anything read it. So the migration and its one reader went in the same branch and
the same review ([[Every Column Names Its Reader]]).

The "done when" was also rewritten so it could be measured. The ticket's version ("every
OSM-sourced store carries its subtype") was checked against tables that held almost none
of these places yet. The rewritten checks target the proposal and venue tables that
actually get rows today. The content-table copy is listed as deferred until a crawl exists.

## Classify at parse time, before the raw text is discarded (librarian, 2026-07)

A telemetry factstore recorded failures as a bare `is_error` flag. Attribution (timeout,
permission, tool-not-found, and so on) needs the error text, which the parser threw away
after setting the flag. The plan classifies the error category at parse time and stores
it as a column. Backfill is best-effort only: the raw session JSONL is retained for about
15 days, so older rows stay unattributed.

## See Also
- [[Write-Only Fields and the Reader Map]] — extends (the reverse case: read but never written)
- [[Every Column Names Its Reader]] — instance-of (the new column shipped with its one reader in the same branch)
- [[Backfill Without the Forward Path]] — related (forward path first; here the backfill is best-effort because the raw value lived only in a local file)
- [[Frozen Ranking Baseline from a Pure Ranker]] — prerequisite-for (benchmark slicing by subtype needs the value to survive)
