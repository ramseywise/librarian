---
title: Size the Chain to Its Join Key
tags: [patterns, rag, pattern]
summary: Before building a multi-slice enrichment chain, measure what fraction of real rows carry the join key it hangs off — six tested slices were built on a Wikidata QID that only 2.9% of production rows have, while the same field was on 86% of rows via a key the pipeline already held and dropped — and point fixtures at real database values, since tests that agree with each other can all disagree with production.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-09-20-dis343-open-facts-coverage.md
  - data/raw/claude-docs/akira/docs/research/2026-09-20-dis343-open-facts-coverage.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-20-dis343-open-facts-coverage.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-19-dis314-fill-rate-measurement.md
  - data/raw/claude-docs/akira/docs/research/2026-09-19-dis314-fill-rate-measurement.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-19-dis314-fill-rate-measurement.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-09-dis222-catalogue-expansion.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-09-dis222-catalogue-expansion.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-09-dis222-catalogue-expansion.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-09-dis222-catalogue-expansion.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-09-dis222-catalogue-expansion.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-09-dis222-catalogue-expansion.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-09-dis222-catalogue-expansion.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis343-venue-open-facts.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis343-venue-open-facts.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis343-venue-open-facts.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis343-venue-open-facts.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis343-venue-open-facts.md
---

# Size the Chain to Its Join Key

In diskoe (2026-09-20) a chain of six slices — fetch, read, shape, UI — was built to bring
open facts (hours, images, curation tags) to venues via a Wikidata QID. Slice 7, the write
path, was the first with a production caller. Pointing it at production surfaced three
things none of the six could: **the filter was wrong, the input was empty, and the input's
ceiling was 2.9%.**

## The three findings

1. **The fixtures agreed with each other, not with the database.** Every slice's fixtures
   used `'Kreuzberg'` as the district; production stored the borough name
   `'Friedrichshain-Kreuzberg'`. An equality filter returned 0 rows while 250 candidates sat in
   the district. Every test was green.
2. **Zero input rows.** The QID column existed and the discovery mapper filled it — but no
   discovery run had written since the mapping landed. 0 of 5,543 candidates and 0 of 90
   venues had a QID. A column with a writer is not a populated column until the writer runs.
3. **The ceiling.** Re-querying the district's 238 OSM elements: **7 (2.9%)** carry a
   `wikidata` tag; **204 (86%)** carry `opening_hours`. The chain had gone to a share-alike
   wiki, via a custom template parser, keyed on a QID 97% of rows lack, to fetch hours that
   were already on the OSM element the pipeline fetched and then dropped (the mapper kept
   seven fields).

## A rare key limits more than its own facts

The open-facts table was keyed on the QID. So a venue with no QID that *did* match a
Wikivoyage listing (matched by name/URL/geo, no QID needed) had **nowhere to store the match**.
Keying a table on a rare key limits which rows can hold *any* fact, not just the facts that key
provides.

## The fix and its rules

- **Map the dense field from the element you already have.** `opening_hours`, phone and `fee`
  became columns on both the candidate and the venue table — on both, because enrichment reads
  venues, and a column only on the candidate row goes invisible the moment a reviewer accepts it.
  A re-key of the QID table was rejected: it would migrate every reader to reach a fact that is
  a property of the discovered element.
- **A backfill never clears values; the sweep is the authority.** A backfill re-reads one
  element from one possibly-lagging mirror, so it only fills. The discovery sweep reflects what
  the element says today and does write nulls.
- **Tiered proposal, weakest curation first:** OSM hours (86% floor) → hand-curated wiki hours
  (2.9%) → the content row's own field (most specific, always wins). Works only with an
  `isPresent` gate: a later tier overwrites only when it has a value, so a null tier can't
  clobber a filled line.
- **Store source values verbatim.** OSM `fee=no` means "no entry fee"; rendering it as "free"
  is an interpretation that belongs to enrichment, not ingestion.

## The same check, applied before building

A catalogue-expansion plan (akira, 2026-09) ran the measurement first. An open city
location dataset was proposed as a venue source; matching its 424 location names against
existing venues found **0 matches**, so no write path was built and the slice was cut at the
measurement. The same plan caught a second trap: a name-similarity threshold (0.86) had been
tuned with one algorithm (SequenceMatcher ratio), and reusing that number with a different
one (token Jaccard) turns a measured threshold into a guess. A threshold belongs to the
algorithm it was measured under; re-measure when the algorithm changes.

## How to apply

Before slice 1 of any join-keyed chain: count rows carrying the key **in production**, and count
the same target field reachable by keys you already hold. Draw fixture values from a production
read, not from what the developer expects the value to look like.

## The plan that built the chain (dis343)

The six-slice plan this page's finding came from was refined **twice** and declared READY.
Its refine passes verified a lot: every file, symbol and line citation; the live
decision-number registry; the gate's 18-target list byte for byte; that no table name
collided; and that a grep guardrail kept fame signals out of the ranker. It even corrected
a false premise about the join key itself, choosing to key the facts table on the external
QID because the venue FK is null on every pre-acceptance row. What no pass asked was **how
many production rows carry that QID**. At execution, one acceptance criterion asked the
match tests to reproduce a measured 52/1,084 production match rate. The build substituted
per-rule tests on frozen fixtures and recorded this as a deviation. That was a reasonable
call, and also the moment the suite stopped being anchored to production numbers.
Refinement that checks citations against the tree is not the same as checking the data
volume the design hangs off.

## See Also
- [[Open POI Data Sources]] — extends
- [[Write-Only Fields and the Reader Map]] — extends
- [[Silence Reads as Clean]] — extends
- [[The Untested Copy Wins]] — extends (fixtures copied from each other, not from the DB)
- [[Silent Join Miss Reads as a Finding]] — extends (key-format drift that makes a 100% miss read as a result)
