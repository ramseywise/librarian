---
title: "Partition Pruning, Clustering and Column Pruning"
tags: [foundations, concept]
summary: "Layout decides what an analytical query reads: named columns, partition filters and sort order each cut bytes scanned, and the savings multiply."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--01-warehouse-and-store.md
---
# Partition Pruning, Clustering and Column Pruning

The same question asked of the same table can read 1.6 GB or about 106 MB; the only difference is how the bytes were laid out beforehand. Analytical stores (OLAP) differ from transactional ones (OLTP) in what drives cost: OLTP pays for rows touched by key, OLAP pays for bytes scanned in the columns selected. Layout therefore sets the bill on every query. See [[Warehouse Cost Meters: Bytes, Slots and Egress]] for the pricing side.

## Column pruning

Column storage reads only the columns a query names. Parquet records the compressed size of each column chunk in its footer, so the saving can be computed without reading data. On a synthetic table of 3,000,000 rows (103 MB on disk) with one wide column nobody queries, that column held 51.1% of the bytes. `SELECT *` read 102.9 MB; selecting two columns read 32.8 MB (3.1x less). The ratio depends on the schema, and badly compressing text columns inflate it.

## Partition pruning

A partition is a directory (or storage segment) per value of one column, usually the event date. A filter on that column lets the engine skip every other partition without opening it.

- In a warehouse, partitioning a table by pickup date turned a one-month filter from a 1.6 GB scan into about 106 MB.
- On a synthetic year, 366 day partitions of which June is 30: the bytes of one column fell from 417 KB to 34 KB (12.3x less). The ratio is just 366 / 30; real data with seasonality gave about 15 times on a two-year table.
- A partition is known before the query runs, so the cost estimate reflects the pruning.

Do not partition a small table: under about 1 GB the per-partition metadata costs more than it saves. The count of partitions per table is also capped (in the thousands).

## Clustering and sort order

Clustering sorts rows by up to four columns. Each block carries min and max statistics, and a block whose range excludes the filter value is skipped. In an unsorted file nearly every row group spans every zone, so none can be skipped; after sorting by the filter column each group holds a narrow slice.

- Row groups skippable for `pu_zone = 132` in a 30-group file: 0 unsorted, 29 sorted.
- In a warehouse, adding clustering on vendor to a date-partitioned table dropped a scan from 1.1 GB to 864.5 MB.
- Clustering savings show only after the run; the dry-run estimate is an upper bound, because which blocks the statistics exclude is decided at run time. Compare bytes billed after the run.
- Clustering needs no maintenance beyond automatic re-clustering as data is appended, and has no partition-count limit.

The order of rules: select columns, filter on the partition, cluster the next filter. Partitioning plus sorting inside each partition multiply, because they act on independent dimensions. Smaller row groups let more groups be skipped but grow the file, since each group adds metadata and compresses less well.

## How it fails

- **Filtering on a function of the partition column.** Pruning needs a filter the planner can map to partitions. A derived expression or a different date column can scan the whole table and return the right answer, so nobody notices until the bill.
- **Over-partitioning.** A partition per user or per hour on a small table makes thousands of tiny files whose metadata cost exceeds the pruning gain ([[Small Files, Prefix Layout and Storage Tiers]]).
- **Reading the estimate on a clustered table as the price.**

## See Also
- [[Separated Storage and Compute and Warehouse Billing Shapes]] — related
- [[Small Files, Prefix Layout and Storage Tiers]] — related
- [[Iceberg Metadata Tree and Hidden Partitioning]] — extends
- [[Materialise or Query and Cost Tests]] — related
- [[Data Engineering Foundations]] — related
