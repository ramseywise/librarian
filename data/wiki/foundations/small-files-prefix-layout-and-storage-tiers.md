---
title: "Small Files, Prefix Layout and Storage Tiers"
tags: [foundations, concept]
summary: "On an object store, file count and size decide request cost and whether column pruning works, and cold storage tiers lose money for tables that are read often or made of small objects."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--01b-object-storage-and-the-data-lake.md
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--05-cost.md
---
# Small Files, Prefix Layout and Storage Tiers

## Small files, measured

One million rows stored as 1, 10, 100 and 1,000 Parquet files, one-column query, counted at the HTTP layer:

| Files | Stored MB | GETs | MB read | Query s |
|---|---|---|---|---|
| 1 | 20.8 | 2 | 1.8 | 0.01 |
| 10 | 21.9 | 20 | 2.2 | 0.03 |
| 100 | 24.7 | 200 | 5.2 | 0.20 |
| 1,000 | 30.3 | 2,000 | 22.1 | 2.01 |

Requests scale as two GETs per file. The surprise is bytes: each footer read fetches a fixed 16 KB tail, and at 30 KB per file that brings in over half of each file, so column pruning stops working when a file is about the size of the read. With the engine's file cache on, small files were fetched whole in one GET (100 GETs and 24.7 MB at 100 files): fewer requests, more bytes, same direction. Per-file footers also hurt compression. On local disk 3,000 files (24.9 MB, 136 ms) against one file (8.8 MB, 4 ms) shows the same effect.

Small files come from streaming sinks writing every minute, partitioning by too many columns, and per-task writes. The fix is compaction. On a bare lake that rewrite is itself an unsafe multi-key overwrite ([[Object Store Guarantees and the Partial-Write Problem]]); table formats commit it like any write.

## Hive-style prefixes

Putting the partition in the key (`month=05/`) lets engines skip prefixes, saving requests as well as bytes. On the 21.8 MB table: all months, all columns 24 GETs and 21.8 MB; one column 2.3 MB; one month and one column 3 GETs and 0.2 MB. Columns and partitions multiply, but only if the partition column is in the `WHERE`. See [[Partition Pruning, Clustering and Column Pruning]].

## Request prices and limits

At list prices read for one region: $0.0004 per 1,000 GETs, $0.005 per 1,000 PUT/COPY/POST/LIST, DELETE free. A scan every 15 minutes (96 runs a day) at 2 GETs per file costs $0.04 a month at 10 files, $2.33 at 1,000 and $231.85 at 100,000; rewriting 100,000 small files as 100 costs $0.08 once. Request rate is limited to at least 3,500 writes or 5,500 reads per second per prefix, scaling gradually with 503 Slow Down meanwhile: 100,000 files at 2 GETs each takes 36 s on one prefix before reading data. Operations cost is small next to compute; the real cost of a small-file layout is time.

Rules, roughly by savings: partition on what queries filter by; avoid high-cardinality partition columns; aim for files much larger than a footer read (hundreds of MB is common); sort within a partition; keep a stable prefix structure; separate raw, curated and mart data for different lifecycle and access rules.

## Storage tiers

Colder classes charge less to keep and more to read. Standard: $0.023 per GB-month, no retrieval fee. Standard-IA: $0.0125, $0.01 per GB read, 30-day minimum, 128 KB minimum billable size. Glacier Instant Retrieval: $0.004, $0.03 per GB read, 90-day minimum. Cost for 1,000 GB for a year by full scans a month (0, 1, 2, 5):

- Standard: 276 at every rate.
- Standard-IA: 150, 270, 390, 750.
- Glacier Instant Retrieval: 48, 408, 768, 1,848.

So Standard-IA wins only when data is read less than about once a month, and Glacier's saving vanishes below one full scan a month. Transitions charge per object: moving 1,000 GB of 256 KB objects (3,906,250 objects) costs $78.12, paid back in 4.1 months; a 10 KB object in Standard-IA is billed as 128 KB, 12.8x its size and 7.0x what Standard charges. Lifecycle rules skip objects under 128 KB by default. Compact before you tier, and check access logs before tiering a table people scan. A 500 GB table scanned twice a month and kept 3 years is cheapest in Standard.

## See Also
- [[Object Store Guarantees and the Partial-Write Problem]] — prerequisite-for
- [[Table Format as a Commit Log over Parquet]] — related
- [[Materialise or Query and Cost Tests]] — related
- [[Warehouse Cost Meters: Bytes, Slots and Egress]] — related
