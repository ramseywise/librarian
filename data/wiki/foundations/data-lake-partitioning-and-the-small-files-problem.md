---
title: "Data Lake Partitioning and the Small Files Problem"
tags: [foundations, pattern]
summary: "Partition a lake by the column you backfill or delete by and sort within files by the column you filter on; partitioning too finely creates thousands of tiny files that make scans hundreds of times slower."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--05-partitioning-and-replication.md
---

# Data Lake Partitioning and the Small Files Problem

The folder layout in object storage obeys the same rules as database partitioning. Hive-style `key=value` folders make the layout readable to any engine.

## Partition pruning
A million trips written `PARTITION_BY (day)` made 31 files averaging 438 KB. A filter on one day reported `Scanning Files: 1/31`: the engine read the folder names and opened one file. This is the footer-statistics pruning of [[Parquet Row Groups, Pruning and Sort Order]] one level higher, so the partition key should be what most queries filter on, usually a date.

## Going too far
Partitioning by day and zone made 8060 files averaging 2.6 KB. The same rows took 21.0 MB against 13.6 MB (footer overhead) and a full scan went from 3.0 ms to 705.5 ms, because the engine opens thousands of tiny files and reads a footer for each. This is the **small files problem**, common with streaming sinks or over-eager partition keys; each folder also costs a list call on object storage.

## Rule
Keep partition keys low in cardinality and leave finer selectivity to sorted row groups inside each file: **partition by what you delete or backfill by, sort by what you filter on**. For a workload where 90% of queries filter by day and 50% also by zone: partition by day, sort by zone within files. If you partition by ingest timestamp while queries filter on event time, pruning does nothing for them. Remedy for tiny files: compact, or partition more coarsely.

## See Also
- [[Partitioning Strategies and Hot Spots]] — related
- [[Parquet Row Groups, Pruning and Sort Order]] — prerequisite-for
- [[B-Trees vs LSM-Trees]] — related (compaction of many small immutable files)
- [[Small Files, Prefix Layout and Storage Tiers]] — related (overlaps; candidate merge for /compact-wiki)
