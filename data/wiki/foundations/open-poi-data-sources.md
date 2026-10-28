---
title: Open POI Data Sources
tags: [foundations, rag, comparison]
summary: Measured comparison of open point-of-interest sources for a city venue catalogue — OSM tags, Wikidata, Wikivoyage listings, Foursquare OS Places and Overture Maps — covering licence, channel, per-field fill rate, freshness and bias, with the conclusion that open POI data is a triage and proposal signal behind a human gate, never a write path.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/diskoe/docs/research/2026-09-19-dis314-open-first-poi-enrichment.md
  - data/raw/claude-docs/akira/docs/research/2026-09-19-dis314-open-first-poi-enrichment.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-19-dis314-open-first-poi-enrichment.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-19-dis314-fill-rate-measurement.md
  - data/raw/claude-docs/akira/docs/research/2026-09-19-dis314-fill-rate-measurement.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-19-dis314-fill-rate-measurement.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-19-dis316-foursquare-os-places.md
  - data/raw/claude-docs/akira/docs/research/2026-09-19-dis316-foursquare-os-places.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-19-dis316-foursquare-os-places.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-19-dis317-overture-places-crosscheck.md
  - data/raw/claude-docs/akira/docs/research/2026-09-19-dis317-overture-places-crosscheck.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-19-dis317-overture-places-crosscheck.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-19-dis316-dis317-berlin-poi-measurement.md
  - data/raw/claude-docs/akira/docs/research/2026-09-19-dis316-dis317-berlin-poi-measurement.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-19-dis316-dis317-berlin-poi-measurement.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-19-dis343-wikivoyage-listing-measurement.md
  - data/raw/claude-docs/akira/docs/research/2026-09-19-dis343-wikivoyage-listing-measurement.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-19-dis343-wikivoyage-listing-measurement.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-19-dis336-accommodation-census.md
  - data/raw/claude-docs/akira/docs/research/2026-09-19-dis336-accommodation-census.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-19-dis336-accommodation-census.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis314-open-first-poi-enrichment.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis314-open-first-poi-enrichment.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis314-open-first-poi-enrichment.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis314-open-first-poi-enrichment.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis314-open-first-poi-enrichment.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis316-foursquare-os-places.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis316-foursquare-os-places.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis316-foursquare-os-places.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis316-foursquare-os-places.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis316-foursquare-os-places.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-19-dis317-overture-places-crosscheck.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-19-dis317-overture-places-crosscheck.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-19-dis317-overture-places-crosscheck.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-19-dis317-overture-places-crosscheck.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-19-dis317-overture-places-crosscheck.md
---

# Open POI Data Sources

A run of research and live measurements in diskoe (2026-09-19/20) against a Berlin venue
catalogue (~46.5k OSM candidates, 90 accepted venues). The question each time: what does an
open POI source actually add, measured, to enrichment inputs and to the review funnel?

## Source by source

| Source | Licence | What it really gives | Measured catch |
|---|---|---|---|
| **OSM tags** (already fetched) | ODbL, attribution | `opening_hours`, phone, website, fee, cuisine on the element you already have | `opening_hours` on **86%** of candidates in the test district — and the pipeline was dropping it ([[Size the Chain to Its Join Key]]) |
| **Wikidata** (QID via OSM `wikidata` tag) | CC0 | Landmark facts, Commons images, notability | **Landmark-biased:** 0 of 15 sampled restaurants and 0 of 13 bars had a QID; only 2.9% of a district's candidates did |
| **Wikivoyage** listings | Facts extractable; prose CC BY-SA | Venues listed as `{{vCard}}` templates *inside district articles* (no per-venue pages, so sitelinks are always ~0) | 144 listings across two articles; structural ceiling 13.3% of candidates, 4.8% matched |
| **Foursquare OS Places** | Apache-2.0, attribution | Broad commercial POIs | Legacy no-account bucket **empty since the Oct 2025 portal cutover** — only channel is an account + second contract |
| **Overture Maps places** | Composite (CDLA-Permissive-2.0 / Apache-2.0 / CC0), attribution | Address 100%, phone 90%, website 89%, socials 64%; no hours, no ratings | 1,680 high-confidence culture/hospitality places OSM lacked; a website for 20.9% of "no website, nothing to crawl" rows |

## Findings that generalize

- **Check the channel, not just the licence.** Foursquare's licence was fine; the free channel
  had silently gone. 21.4% of Overture's in-city records were Foursquare-sourced anyway, so a
  direct integration would buy an increment that can't even be sized without paying for it.
  No-go.
- **Overture has no freshness signal.** `operating_status` populated on 0.19% of records;
  `update_time` is release-level (every row stamps the release month). No closed flag means
  nothing tells you a bar shut — the strongest argument for never letting it near served
  tables without a human gate.
- **No corroboration inside an aggregate.** Each Overture record carries exactly one upstream
  source; "OSM + Foursquare + Overture agree" has to be built across datasets.
- **Confidence is a usable triage proxy, labelled as one.** Overture confidence is monotone
  with OSM-match rate (0.9–1.0 band matches 28.5%), and website hosts agree on 90.7% of pairs —
  high enough to *propose*, too low to write.
- **Match on URL host, not just name.** For Wikivoyage, name-only matching undercounted by
  roughly a third; parse vCards with a **brace-depth-aware scanner** (a naive regex truncates on
  nested templates). German-language articles held the district pages; English had none.
- **Curation vs fame.** Wikivoyage presence showed a ≈3× lift among human-reviewed venues
  (15% vs 4.8% base) — a real curation signal, but confounded with fame. Page views and fame
  stay **triage signals, never ranking inputs**, so they don't fight a discovery-value
  guardrail that boosts lesser-known places.
- **Never store share-alike prose**, nor a model paraphrase of it; extract facts only.

**Decision shape:** Overture GO narrowly — triage signal (fill the websiteless funnel, order the
review queue), never a write path. Foursquare direct NO-GO. Everything still enters through
the reviewed candidate ledger.

## Open POI data as B2B prospect data

An OSM hotel/hostel census reused the same discovery code for a different reader — sales
prospecting. Lessons: it belongs in its own schema cluster (never on the guest read path; see
[[Data Clusters by Writer and Trust]]); OSM-derived firmographics (name, address, room count,
website) are not personal data, but any named individual or personal contact is; ODbL
attribution triggers only when a derived figure is published externally; and German UWG §7(2)
prohibits unsolicited bulk email to businesses without consent — the census is a worklist for
manual, named outreach, **never a mailing list**.

## Plan-stage findings (2026-09-19 plans)

The three implementation plans that followed the research added these lessons:

- **A stale hand-maintained type mirror misled a parallel research pass.** A hand-written row
  type lagged the generated database types. A concurrent research pass read it and concluded
  that a provenance column did not exist. Read the generated types or the schema, never a mirror.
- **Ambiguous matches are skipped, not guessed.** Fuzzy name matching against open POI records
  produced false positives. The plans resolved them as an explicit `ambiguous` outcome that
  goes to no one, rather than as a best-guess match.
- **Supply already exceeded review throughput by about 60×.** Adding open sources could not
  improve the funnel by volume. Their value is in ordering and filling the review queue.
- **Confidence and page views stay out of scoring unless a dated decision says otherwise.**
  The plans repeated the triage-only rule so that a discovery-value guardrail is not eroded a
  little at a time by successive plans each adding a small ranking weight.

## See Also
- [[Change the Channel, Not the Count]] — extends
- [[Size the Chain to Its Join Key]] — extends
- [[Data Clusters by Writer and Trust]] — extends
- [[Listing Pages Masquerading as Records]] — extends
- [[Decision-ID Reservation Across Concurrent Plans]] — extends (the three plans reserved decision IDs in parallel)
