---
title: "Row Stores vs Column Stores"
tags: [foundations, comparison]
summary: "OLTP and OLAP pull storage in opposite directions: row stores win on key lookups, column stores win on scans by about two orders of magnitude through pruning, compression, vectorisation and block skipping; includes rollups and the column-store write path."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--03-row-and-column-stores.md
---

# Row Stores vs Column Stores

| | OLTP | OLAP |
|---|---|---|
| Reads | A few rows, found by key | Aggregates over many rows |
| Writes | Random, low latency, from user input | Bulk load or event stream |
| Data represents | The latest state | History of events |
| Typical size | Gigabytes to terabytes | Terabytes to petabytes |

An analyst's long scan can hold a production database's disks hostage, so data is copied through a pipeline into a separate read-only warehouse. A transactional store is limited by seeks, an analytic one by bytes moved off disk per second. Parquet is the file-level form of the column layout (see [[Parquet Row Groups, Pruning and Sort Order]]).

## Measured gap

Same 1,000,000 rows in SQLite (row store) and DuckDB (column store), best of five on a busy laptop, so an order of magnitude only:

| | SQLite | DuckDB |
|---|---|---|
| File size | 54.6 MB | 6.6 MB |
| Analytic scan | 173.84 ms | 0.87 ms |
| Point lookup by key | 0.005 ms | 0.298 ms |

Each does what its layout makes cheap. A row store pulls every field of every row through memory to read one; fact tables often pass 100 columns while a query reads four or five. Summing one float column over a 128-byte row layout took 2.55 ms against 0.12 ms contiguous, about twenty times, with no disk involved. Interpreted one-value-at-a-time code is far slower still, so analytic engines use **vectorised execution** (DuckDB processes 1,024 values per vector): tight loops fit the L1 cache, avoid branch mispredictions and use SIMD.

Layout alone is not enough. Emulating a column store inside a row store (a narrow table or index per column) did not perform, because of tuple reconstruction and per-row overhead. In a column store, late materialisation (rebuilding rows as late as possible) improved performance by a factor of three, compression by about two on average and an order of magnitude on sorted data. The executor must be built to use the layout.

## Compression and sort order

- **Run-length encoding:** zone values in arrival order made 956,362 runs; sorted, exactly 260. A sorted first key can shrink to kilobytes; later keys help less.
- **Bitmap encoding** for few distinct values: one bit vector per value (125,000 bytes for a million rows); `IN` becomes OR and a conjunction becomes AND over bitmaps, agreeing with SQL (35,871 rows).
- Rows are sorted as whole rows or the positional link between columns breaks, so there is one physical order per copy. Date is the usual first key. A system that keeps several copies for fault tolerance can give each a different order (projections); clustering keys and materialised projections make the same trade of storage and load time for skippable queries.
- Trap: the "column families" of wide-column stores keep a row's columns together and are not column-oriented in this sense.

## Indexes lose to scans as selectivity falls

For 623 rows of a rare zone, SQLite with an index (0.37 ms) matched a DuckDB scan (0.47 ms). For the busiest zone (163,162 rows) the index took 24.83 ms against 0.59 ms, around 40 times slower, because each match is a random lookup. Warehouses therefore tend to skip secondary indexes: sorted compressed columns plus min/max per block skip data without slowing writes (see [[SQL Indexes and Query Plans]]).

## Rollups and cubes

A materialised view saves a query's result; a cube holds aggregates across dimensions with marginal totals (`GROUP BY CUBE`). A daily-by-zone rollup of 8,060 rows read about four times faster than the raw table, and its size scales with zone-days, not trips. The catch: it cannot answer about a dimension it dropped (share of fare from long trips). Keep the atomic table and use rollups as an acceleration layer; build them from questions people have asked.

## The write path

A compressed sorted column cannot take a mid-column insert without rewriting every column. The usual answer is log-structured: hold recent writes in memory and merge into the columns in bulk; reads combine both. In a test of one committed row at a time, SQLite took 0.250 ms and DuckDB 0.277 ms per row, so the textbook expectation of a wide loss did not show; the real penalty is concurrent writers and changes to compressed data. Measure your own cost before repeating a rule.

## Pitfalls
- Running analytics on the production OLTP database.
- `SELECT *` in a warehouse discards the layout's advantage and costs money where billing is per byte scanned.
- Adding an index to a slow warehouse query; sort or cluster on the filter column instead.
- Treating a rollup as source of truth.
- Loading row by row; load in bulk.

## See Also
- [[B-Trees vs LSM-Trees]] — related (the two index structures under row stores)
- [[Parquet Row Groups, Pruning and Sort Order]] — extends
- [[Choosing a Store from the Access Pattern]] — related
- [[SQL Indexes and Query Plans]] — related
