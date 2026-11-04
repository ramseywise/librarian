---
title: "B-Trees vs LSM-Trees"
tags: [foundations, comparison]
summary: "The two ways stores keep an index: B-trees update fixed pages in place behind a write-ahead log, LSM-trees append immutable sorted segments and merge them; trade-offs in write cost, read cost and tail latency."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--03-row-and-column-stores.md
---

# B-Trees vs LSM-Trees

An index is derived data: it can be dropped and rebuilt from the table, and every index speeds some reads and slows every write. Most stores keep one in one of two ways, and the sources a pipeline extracts from are built on them.

## B-tree

Divides the disk into fixed pages (usually 4 KB) and updates them in place. With a branching factor of 500, four levels address 256 TB, so a lookup costs few reads. Overwriting a page is not crash safe, so every change also goes to a write-ahead log first and is written at least twice. Each key lives in exactly one place, so range locks can attach directly to the tree, which serializable databases use against phantoms (see [[Transaction Isolation Levels and Anomalies]]). A concatenated index has a limit: like a phone book sorted by last name then first, it cannot find everyone with a given first name.

## LSM-tree

Never overwrites. Writes collect in a sorted in-memory table, flushed as an immutable sorted segment and merged with neighbours in the background. A delete is a tombstone record that a merge eventually acts on. A toy size-tiered version (1,000-row memtable, merge when four segments pile up) over 500,000 random writes to 50,000 keys wrote 3.4 rows to disk per row updated, about 338 bytes per update at 100 bytes a row, against 4,096 bytes for a B-tree rewriting its page on every commit (that figure is a worst case that ignores the log and batching). The read cost: 12 segments on disk, a read opened 7.3 on average and 12 at worst, and a key that does not exist opens all 12. That case is what a Bloom filter avoids.

## Choosing

Log-structured stores tend to write faster and B-trees read faster, but benchmarks are sensitive to workload, so test with yours. Two costs hide from means: compaction competes with live requests and shows at high percentiles (see [[Latency Percentiles, Tail Amplification and Coordinated Omission]]), and on a write-heavy load compaction can fall behind while the database keeps accepting writes.

A lakehouse table behaves like an LSM-tree at larger scale: immutable files, new data in small ones, a background job that compacts them.

## See Also
- [[Row Stores vs Column Stores]] — related
- [[Transaction Isolation Levels and Anomalies]] — related
- [[SQL Indexes and Query Plans]] — related
