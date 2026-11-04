---
title: "MVCC Row Versions and Snapshots"
tags: [foundations, concept]
summary: "Multi-version concurrency control keeps old row versions so readers never block writers; a held-open snapshot pins versions and bloats tables, and table formats repeat the design at file scale."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--04-transactions-and-isolation.md
---

# MVCC Row Versions and Snapshots

**Snapshot isolation** (Postgres calls it repeatable read) gives every query in a transaction the database as of the transaction's start. It is implemented by multi-version concurrency control: writes never destroy a row. An update marks the old version deleted by this transaction and creates a new version, so readers never block writers and writers never block readers.

## The bookkeeping in Postgres
Hidden columns show it: `xmin` is the transaction that created a version, `xmax` the one that deleted it, `ctid` its physical location. After an update, the new version sits at `(0,2)` and the old at `(0,1)` with `xmax` set to the writer. While the writer is uncommitted everyone else still reads the old version. After commit new transactions see the new one, while an older snapshot keeps seeing the old value. Visibility is a rule evaluated per row version against a transaction's snapshot. Nothing was locked and nobody waited.

Read committed instead takes a fresh snapshot per statement, so a transaction can see different states (read skew); see [[Transaction Isolation Levels and Anomalies]].

## The cost: version retention
Garbage collection reclaims versions only once no transaction can see them. With one snapshot held open, 5000 updates to a single row grew an 8192-byte table to 188416 bytes; `vacuum full` returned it to 8192. One idle analytics session holding a snapshot for hours can bloat a busy OLTP database, a reason not to run long warehouse extracts against a primary (use a replica or change data capture).

## The same design at file scale
Append-only B-trees write a new root per commit and the root is a consistent snapshot. A table format is the same idea built from immutable files: Parquet files are never edited, a commit publishes a new snapshot, readers keep the snapshot they started with. Time travel and vacuum are row-version visibility and garbage collection at the level of files.

## See Also
- [[Transaction Isolation Levels and Anomalies]] — prerequisite-for
- [[B-Trees vs LSM-Trees]] — related (append-only B-trees)
- [[Three Ways to Be Serializable]] — related
