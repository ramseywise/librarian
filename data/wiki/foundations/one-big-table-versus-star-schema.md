---
title: "One Big Table versus Star Schema"
tags: [foundations, comparison]
summary: "A pre-joined wide table reads somewhat faster and costs more storage, but a one-label change rewrites every affected row or file and a second grain has nowhere to go; treat it as a rebuildable cache of a star, never the source of truth."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--02-ingest-and-modelling--notes--03-data-vault-and-obt.md
---

# One Big Table versus Star Schema

One Big Table (OBT) pre-joins every dimension onto the fact so each attribute is a column and every question a filter and group-by. It became reasonable with columnar storage: repeated values compress to almost nothing and unread columns cost almost no I/O.

## Read side

- Local test, 1,000,000 rows, Parquet with zstd: star 5.6 MB, OBT 7.0 MB (25% more). Same question: 4.4 ms star, 3.5 ms OBT. Margin too small to matter at this size.
- A public benchmark (ten BI-style queries, a TPC-DS subset at scale 100, three cloud warehouses): the denormalised table was 25-30% faster excluding compile time on one, about 25% on another (the star won three simple queries), about 49% on the third. Storage on one: 60,250 MB against 29,778 MB for the fact, and total disk from a bit over 30 GB to over 90, a likely worst case because column encodings could not be applied. Evidence of a useful, not spectacular, read gain on those queries, not that stars are obsolete.
- Sorting the OBT by zone shrank the file from 7.0 MB to about 6.4 MB (longer runs help run-length encoding; modest because those columns were already small under dictionary encoding).

## Write side: the real cost

Changing one zone's label: star, 1 row (0.4 ms); OBT, 29,249 rows (4.4 ms), or the whole file when it lives as Parquet on object storage, since files cannot be updated in place. Open table formats reduce rewriting without removing it. Further costs, all from a dimension value being copied into every row:

- History is frozen at whatever was joined at build time; both views need two columns or the dimension anyway.
- A second fact at a different grain cannot live in the table without fan-out, so "one" lasts until the second fact arrives.
- A dimension member with no facts is absent, so a report that should show zero shows nothing.

## Cache or source of truth

An OBT rebuilt in full from a star or vault is a cache: nothing is lost when it is wrong. One that has become the only copy of a definition is a denormalised source of record, an accidental model, and every correction is a many-row rewrite.

## Choosing

| | Star | Data Vault | OBT |
|---|---|---|---|
| Who queries | Analysts, BI tools | Engineers; marts for others | Anyone |
| Joins per question | 1 per dimension | Several per attribute | None |
| Label change | 1 row, or new row (type 2) | 1 satellite row | Every affected row |
| Adding a source | Redesign conformed dimensions | Add a satellite | Rebuild |
| Wins when | Several facts share dimensions | Many changing sources, audit duty | One consumer, one grain, stable labels |

Sensible default: staged raw, then a star holding the definitions, then a few wide tables as materialised views for dashboards that need them. Check how often labels change first: a monthly reorganisation on a wide table is a monthly full rebuild.

## See Also
- [[Dimensional Model Grain and the Four Design Steps]] — alternative-to
- [[Data Vault Hubs, Links and Satellites]] — alternative-to
- [[Conformed Dimensions, the Bus Matrix and Drilling Across]] — related
- [[Data Engineering Foundations]] — related
