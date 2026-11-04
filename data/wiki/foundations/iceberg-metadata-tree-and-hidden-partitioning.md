---
title: "Iceberg Metadata Tree and Hidden Partitioning"
tags: [foundations, concept]
summary: "Iceberg stores a tree of metadata, manifest lists and manifests under an atomic catalog pointer, which enables planning-time pruning, hidden partitioning, partition evolution and schema tracking by field ID."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--02-table-formats.md
---
# Iceberg Metadata Tree and Hidden Partitioning

Where [[Table Format as a Commit Log over Parquet]] uses an ordered log, Iceberg stores a tree: table metadata points to a current snapshot, a snapshot to a manifest list, a manifest list to manifests, and each manifest names data files with partition values and column metrics. A commit writes new metadata and atomically swaps the pointer, and the atomic operation lives in a **catalog** (a local SQLite database in the worked example).

## Structure in practice

Two appends and a delete produced three snapshots (append, append, overwrite; the overwrite is the delete, where the data file holding the row was rewritten). On disk: 4 `metadata.json` files, 3 manifest lists, 4 manifests. The tree helps planning: a query prunes first at the manifest list using its partition ranges, so most manifests are never read, which matters on tables with very many files.

## Three features worth the machinery

**Hidden partitioning.** The table was partitioned by `day(pickup)` but a query filtering on the `pickup` timestamp itself still found the right directory. In a Hive-style layout the user must know to filter on a separate derived date column, and a filter on the timestamp alone scans everything. Iceberg records the transform in metadata so neither producers nor consumers see a derived column.

**Partition evolution.** Adding a month field produced two partition specs with no rewrite: old files keep the old spec, new files use the new one. In a directory-layout lake, changing the scheme means rewriting the table and every query.

**Schema by ID.** Columns are tracked by field ID, not name or position, so a rename cannot silently attach an old file's column to a new meaning.

## Failure modes

- **Treating the catalog as an afterthought.** It holds the atomic pointer; two jobs using two different catalogs for one table can corrupt it.
- Managed table buckets that store Iceberg tables change who runs compaction, not the reasoning.

## See Also
- [[Partition Pruning, Clustering and Column Pruning]] — related
- [[Copy-on-Write vs Merge-on-Read]] — related
- [[Table Format as a Commit Log over Parquet]] — alternative-to
