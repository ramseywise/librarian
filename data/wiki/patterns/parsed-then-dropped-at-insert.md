---
title: Parsed Then Dropped at the Insert Mapper
tags: [patterns, rag, pattern]
summary: A crawl parses price, hours and descriptions, keeps them in memory through normalisation, then silently discards them in the typed insert mapper because the Insert type mirrors the table — and a natural-key merge discards the losing listing's fields the same way, so the data is computed and unrecoverable.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-19-activity-schedule-price-crawl.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-19-activity-schedule-price-crawl.md
  - data/raw/claude-docs/akira/docs/research/2026-09-16-dis295-event-edition-identity.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-16-dis295-event-edition-identity.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-19-activity-schedule-price-crawl.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-26-2a-log-completeness.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-26-2a-log-completeness.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-26-2a-log-completeness.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-26-2a-log-completeness.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-26-2a-log-completeness.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-26-2a-log-completeness.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-26-2a-log-completeness.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-activity-schedule-price-crawl.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-activity-schedule-price-crawl.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-activity-schedule-price-crawl.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-activity-schedule-price-crawl.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-activity-schedule-price-crawl.md
---

# Parsed Then Dropped at the Insert Mapper

From two akira research passes on why venue and event records looked sparse. The data
was not missing upstream. It was extracted, carried, and thrown away at the last seam.

## The mechanism

- **Extraction parses** price, opening hours and description from the source page.
- **Normalisation keeps** them on the in-memory object.
- **The insert mapper drops** them. `toActivityInsert` / `toBarRestaurantInsert` build a
  typed `Insert` object, and the Insert type mirrors the table. A field with no column has
  nowhere to go, so the compiler happily lets the mapper omit it. Nothing errors, nothing
  logs.
- **A downstream prompt reads columns that never existed.** The enrichment prompt
  referenced price/hours fields, so they arrived as unknown on 100% of rows, and the model
  was asked to judge without the evidence the crawler had already fetched.

A per-vertical enrichment runner had the same shape: `RunEnrichmentResult` computed a
row and the caller discarded it.

## The merge variant

Event editions merged on a natural key recorded only start, end and `source_url`. When two
listings described the same edition, the losing listing's description, price, ticket URL
and image were computed during the merge and discarded. Because the raw page is not
stored, that is unrecoverable — a later re-crawl may no longer show it. Series and
organizer columns were populated on 0 of 486 rows for the same reason.

Recommended merge rule: newest crawl wins, with **field-level null-coalescing** while the
row is still draft/needs-review (a non-null value from either side survives), and log a
field diff for every merge so the loss is at least visible.

## How to catch it

Trace one field from page to column (see [[Single-Subject End-to-End Trace]]). If the
in-memory object has more keys than the insert payload, each missing key is either a
deliberate drop with a reason or this bug. A type that mirrors the table cannot tell you;
only a diff between "parsed" and "written" can.

## Serve-Log Variant (akira, 2026-08)

The same shape appears on the write side of a serve-time log, not only on ingest:

- Seven per-dimension scores were computed, then collapsed to a single total before the
  served-item type was built. The fix stored them as one JSONB object inside each item, so
  adding a dimension needs no migration.
- The pool size, the eligible count and the exclusion reasons existed inside the request
  handler and were dropped at the HTTP boundary.
- The recorder's `insert(rows: unknown)` signature meant a missing field was not a type error.
  Only a spy test that asserts the row shape catches it.

## Fix Shape (akira activity-crawl plan, 2026-09)

The plan that followed the research split the fix into two slices. The ordering is the lesson.

- **Slice 1 fixes the mapper before any new fetch.** The insert mappers were changed to carry
  fields that were already parsed: description and price text for activities. The same audit
  found that bars dropped a menu URL and a reservation URL. Those were **existing columns with
  a real reader** (a call-to-action resolver), so the fix was pure plumbing. Look for that case
  first: no migration, no new reader, immediate visible value.
- **Slice 2 adds a one-hop second-page fallback, field by field.** It runs only when the
  primary page left a specific field null, and it follows one anchor from the same site. It
  reuses the existing robots-aware fetcher and skips PDFs. The anchor URL is read from the
  in-memory record, not stored in a new column.
- **The re-crawl must not overwrite.** The new columns join the content class that a re-crawl
  fills only when empty, and a classification-completeness test fails if a new column is left
  unclassified (see [[Re-Crawl Adds, Never Overwrites]]).
- **Size the slice to the measured gap.** The only field the fallback measurably improved was
  bars' opening hours, which were 89% unknown. The plan scoped the second-page work to that
  field rather than to "richer records" in general.

## See Also
- [[Write-Only Fields and the Reader Map]] — extends (the opposite seam: a field written with no reader; here a field parsed with no writer)
- [[Single-Subject End-to-End Trace]] — related (the method that surfaces the drop)
- [[Silence Reads as Clean]] — instance-of (a dropped field produces no error)
- [[Mislabelled Column Is Worse Than Missing]] — related (a dropped value plus a wrong name)
- [[Re-Crawl Adds, Never Overwrites]] — prerequisite-for (the write rule the second-page fallback must respect)
- [[A Second Write Path Meets the First Path's Hidden Gates]] — related (silent drop at a downstream allowlist)
