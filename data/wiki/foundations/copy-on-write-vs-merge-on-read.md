---
title: "Copy-on-Write vs Merge-on-Read"
tags: [foundations, decision]
summary: "Updating a lake table either rewrites whole files (copy-on-write) or appends delete and delta records merged later (merge-on-read); choose by update distribution, and compare Delta, Iceberg and Hudi as of their release snapshot."
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--02-table-formats.md
---
# Copy-on-Write vs Merge-on-Read

Every table format must decide how an update reaches immutable files.

- **Copy-on-write (CoW).** An update rewrites the base file into a new one. Reads are simple and fast; writes pay. Recommended for batch ETL and warehouse-like tables.
- **Merge-on-read (MoR).** An update appends to a delta or delete log beside the base file, and a compaction merges them later. Writes are light and commits can come every minute or so. Readers either merge at query time for fresh results or use a read-optimised query that sees only compacted base files.

The Hudi project asks you to choose one per table up front. Delta and Iceberg have grown merge-on-read styles too: Iceberg defines position deletes, equality deletes and (in newer format versions) deletion vectors; Delta has deletion vectors. The real question is which side of a write-amplification trade the workload sits on.

## The arithmetic

Update 1% of rows per commit in a 1 TB table made of 1 GB files (1,000 files of 10,000,000 rows):

- Random updates touch 1,000 of 1,000 files. CoW rewrites 1.00 TB per commit; MoR appends 0.01 TB.
- If updates cluster in 2% of files, CoW rewrites 0.02 TB; in 10%, 0.10 TB. Clustered updates (most changes hitting recent days) bring CoW close to MoR.

MoR savings are not free: every reader pays until compaction runs, so a neglected compaction job turns a fast write path into slow reads, and delete files accumulate. Know the update distribution before choosing.

## Format comparison (a snapshot)

| | Delta Lake | Iceberg | Hudi |
|---|---|---|---|
| Metadata | Ordered JSON log with Parquet checkpoints | Tree: metadata, manifest list, manifests | Timeline of actions on file groups |
| Atomic commit via | Put-if-absent or coordinator | Catalog pointer swap | Timeline plus concurrency control |
| Hidden partitioning | Not default; partition columns visible | Core feature | Partition paths, configurable |
| Write style | CoW, deletion vectors optional | CoW or MoR per operation | CoW or MoR at table creation |
| Strength | Tight Spark integration | Multi-engine neutrality, very large tables | Upsert-heavy ingestion, incremental pulls |

These projects copy each other's ideas every release. A 2020 or 2021 statement that Hudi lacks concurrent writers describes that period and should not be repeated without checking current docs. Choose by the engines you must support and what your catalog does, then confirm the feature in current documentation.

## See Also
- [[Table Format as a Commit Log over Parquet]] — prerequisite-for
- [[Iceberg Metadata Tree and Hidden Partitioning]] — related
- [[Small Files, Prefix Layout and Storage Tiers]] — related
- [[Delta Lake Transaction Log]] — related (a table format that rewrites files)
