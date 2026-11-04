---
title: "Parquet Row Groups, Pruning and Sort Order"
tags: [foundations, concept]
summary: "How Parquet's footer statistics enable column pruning and predicate pushdown, why pushdown only works when physical sort order matches the filter, and how Parquet (compressed, at rest) differs from Arrow (uncompressed, in memory)."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--02-encoding-and-files.md
---

# Parquet Row Groups, Pruning and Sort Order

Parquet stores values column by column. A file holds **row groups**; a row group holds one **column chunk** per column; a chunk holds **pages**, the unit of encoding and compression. The **footer** at the end holds the schema, each chunk's offset and encoding, and min and max statistics. A reader seeks to the end, reads the footer, then fetches only the byte ranges it needs, which is cheap on object storage.

## Two savings

- **Column pruning:** read only named columns. Reading one column of seven took 1.3 ms against 7.7 ms for all seven.
- **Predicate pushdown:** use chunk min/max to skip whole row groups without decompressing. This depends on physical order.

With 1,000,000 trips in 20 row groups, a tight range on a monotonically rising `trip_id` overlapped 1 of 20 groups. A filter on `fare_usd`, scattered through time, overlapped 20 of 20 because every group's min and max spanned the range. Statistics always exist but help only when data order matches the filter.

## Sorting is a physical design decision

Per-column encoding differs: a three-value `payment_type` compressed to 0.16 MB while near-random fares barely compressed. Sorting by zone then payment type shrank those two columns from about 1 MB and 163 KB to about 5 KB each, because long runs collapse. But `pickup_at` grew by 70% since it lost its order, and the whole file grew from 7.7 to 9.0 MB. Only one sort order can be physical, so choose the one serving the filters you run, and compare whole-file size and the query mix.

Row group size is the other knob: small groups give finer skipping but more footer metadata; large groups compress better and suit big scans. Library defaults differ (the default here put all million rows in one group), so read the metadata rather than assuming. A zero minimum on a float column is recorded as `-0.0` deliberately, so a comparison cannot wrongly skip a group.

## Arrow: the same idea in memory

Arrow also lays out columns contiguously but makes the opposite trade. On disk, I/O is slow, so Parquet spends CPU to save bytes. In memory, CPU is slow, so Arrow keeps values uncompressed and fixed-width, giving computable addresses and zero-copy sharing (NumPy wrapped a column's 8,000,000-byte buffer without copying). The Arrow file was 44.9 MB against 7.7 MB for Parquet (nearly six times) but opened in 1.16 ms against 10.04 ms because memory-mapping needs no decoding. Its other purpose is a shared layout: DuckDB, Polars and pyarrow pass tables across a library boundary without per-pair converters. Keep Parquet at rest and Arrow in memory or for short-lived exchange.

| Format | Layout | Best at | Bad at |
|---|---|---|---|
| CSV | Row, text | Exchange with anyone | Types, nesting, partial reads |
| Avro | Row, binary | Streams, dumps, evolution | Analytic scans |
| Parquet | Column, compressed | Analytic scans at rest | Row updates, single-row reads |
| Arrow | Column, uncompressed | In-process exchange | Long-term compact storage |

Rule: data at rest in Parquet sorted by the main filter column; between engines Arrow; records in motion Avro or Protobuf with a registry.

## See Also
- [[Row Stores vs Column Stores]] — extends (the same mechanism seen from inside a database)
- [[Encoding Compatibility and Schema Evolution]] — prerequisite-for
- [[Small Files, Prefix Layout and Storage Tiers]] — related (what file layout costs on an object store)
