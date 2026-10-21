---
title: Listing Pages Masquerading as Records
tags: [patterns, foundations, pattern]
summary: A crawler that follows calendar and navigation links and then dates whatever it lands on through a permissive fallback tier produces "records" that are really listing pages — low precision is a property of the crawler, not the source; fix link selection and gate listings before extraction, treat the generic-title regex as a floor not a filter, and expect the same defect in both lanes.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-09-14-osm-sourcing-pipeline.md
  - data/raw/claude-docs/playground/docs/research/2026-09-14-osm-sourcing-pipeline.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/playground/docs/research/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/akira/docs/research/2026-09-20-listing-text-extractor-measurement.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-20-listing-text-extractor-measurement.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-20-listing-text-extractor-measurement.md
  - data/raw/claude-docs/akira/docs/research/2026-09-22-dis364-structural-tier-production-wiring.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-22-dis364-structural-tier-production-wiring.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-22-dis364-structural-tier-production-wiring.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-listing-text-extractor.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-listing-text-extractor.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-listing-text-extractor.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-listing-text-extractor.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-listing-text-extractor.md
---

# Listing Pages Masquerading as Records

Measurement of a two-lane sourcing pipeline for a city events product (repo
diskoe/akira): a curated catalogue of venue sites, and venues discovered from
OpenStreetMap via Overpass, each venue's `website` tag crawled for events. The document
styled itself "a snapshot, not a contract", and the headline numbers moved by a factor of
three during the measurement.

## The mechanism

A hand-labelled sample of 60 future events from the OSM lane found **16 (27%) named a
specific event**; the rest were listing, navigation or service pages — "Programme",
"Opening hours", "Quick links". The catalogue lane showed the same 30–45%. The cause was
not the source: link discovery followed listing pages, and the OpenGraph tier (93% of
OSM-lane events) obligingly gave each a date. On a listing page `start_at` is not an event
date, so even the "future" count was unreliable.

Reading the *whole* calendar instead of two keyword links — every JSON-LD Event the page
embeds, then up to eight detail links chosen by a selector that skips nav, pagination,
taxonomy, rental and archive URLs, deepest path first — and applying the index-page gate the
importer's review step already used, took precision from 27% to **≈87%**. Wiring the same
selector into the catalogue importer took its specific-event rate from 32% to 68%. Fewer
pages read, more of them events.

## Rules

- **Low precision is a crawler property until proven otherwise.** Both lanes failed the
  same way; blaming the open-data lane would have been wrong.
- **A regex for generic titles is a floor, not a filter.** It flagged 36% of OSM-lane
  events against 73% hand-labelled misses — undercounting by half.
- **Scope URL rules to the host that motivated them.** A `/en/programme`-without-`/detail/`
  rule written for one theatre matched every programme page of two other venues' real
  events (9 of 84 future pages). Now only a bare root or the original host counts.
- **A substring detector is a nav-link detector.** `a[href*="book"]` matched social-media
  pages, `/book-review` and every "Tickets" menu item — a "booking link" fill rate of
  ~60% was mostly noise. Match a whole path segment or a booking-platform host, never a
  social host; fill rate fell to ~20% and a hand sample was 38/40 real.
- **Match JSON-LD subtypes.** `@type: Event` only let `MusicEvent`, `TheaterEvent`,
  `Festival`, `ExhibitionEvent` fall through to OpenGraph and lose their dates — and the
  probe already had the broader check that production lacked ([[The Untested Copy Wins]]).
- **Headings inside page chrome are not titles.** The OpenGraph heading fallback now skips
  `nav`/`aside`/page `header`/`footer` — but not a `header` inside `article`/`main`, which
  on the first attempt lost 50 real events.
- **A probe that loses everything on a crash is not a probe.** Append per site, write
  `run.json` at start, support `--resume`.
- **A relative `source_url` on the write path aborts the whole corpus** on one bad row;
  resolve against the page URL as the image resolver already did.
- **Untrimmed titles were the write path, not the probe** — 61 stored rows carried
  leading newlines, so a backfill was needed, not just a fix.
- **A summary that reads columns the table lacks prints `unknown` on every row** — and when
  the prompt is a parity-tested port, the fix is a decision (summary reads the real
  columns, or the table gains them), not an edit.

## What the open-data lane actually adds

Venue attributes beat the product's own rows (coordinates 100%, kind, wheelchair tag on
most, opening hours on 65%), and 98% of venues placed in a district once coordinates count;
but events from those sites were 10–20 points less complete per field than catalogue events.
The cheapest high-value use was enriching venues already held — of which only 66 matched by
id or name-within-150 m, so entity matching was the next gap. What neither lane could read:
427 calendars whose programme is text on the page (needs a listing-text extractor) and 99
advertised iCal feeds nothing parsed.

## Measuring and Wiring the Repair Tier

**Pre-registered rule, short-circuited.** The extractor measurement wrote its decision rule
before reading numbers: adopt only if yield ≥ 70% *and* precision passes a hand check.
Yield came in at 47%, so the precision hand check was moot and was skipped. When one half
of a conjunctive rule already fails, stop. Low-count page kinds were admitted at a low
prior rather than excluded, because exclusion would have removed them from the
measurement. Follow-up findings went in as dated addenda, not edits.

**Raw structural output isn't records.** The structural tier produced titles welded to
dates, an invented year, and no description, so it can't be written as-is.

**Production wiring:**
- Eight free heuristic flags (no model call) mark suspects. A bounded LLM extractor runs
  **only on flagged suspects**.
- The fallback arm runs only when the normal crawl yields zero events, never alongside it.
- Flagged candidates that can't be repaired are **dropped, not written as draft**, because
  QC checks content quality, not extraction fidelity, so a mangled draft would pass. Each
  drop is logged with a closed-vocabulary outcome reason.

## See Also
- [[The Untested Copy Wins]] — instance-of (the probe's broader JSON-LD check vs production's narrow one; sibling keyword lists that disagreed)
- [[Change the Channel, Not the Count]] — related (the census that made the open-data lane a candidate)
- [[Named-Trigger Deferral]] — related (measure the structural tier before adding an LLM listing extractor)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — related (a probe that vacuously succeeds)
- [[Widen a Capped Vocabulary Without Displacing]] — extends (the keyword-reconciliation slice and its capped-list regression)
