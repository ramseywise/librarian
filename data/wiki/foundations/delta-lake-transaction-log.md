---
title: Delta Lake Transaction Log
tags: [foundations, pattern]
summary: Delta Lake keeps a write-ahead log of table membership as files in the object store itself, giving ACID tables over Parquet data with no server holding table state.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-armbrust-2020-delta-lake.md
---

# Delta Lake Transaction Log

Armbrust and colleagues (Databricks, CWI, Berkeley, Stanford; PVLDB 13(12), 2020) describe Delta Lake as ACID table storage over cloud object stores. Benchmarks are the authors' own (self-reported) and were run by Databricks on its own runtime.

## Problem

Object stores offer cheap, scalable key-value access but no multi-object atomicity, and listing is slow: the paper says an S3 LIST call returns no more than 1000 keys and takes tens to hundreds of milliseconds, so a sequential scan of a table with millions of objects can run for minutes. The authors say, anecdotally and for 2014-2016, that about half of Databricks cloud support escalations came from corruption, consistency or performance problems tied to cloud storage strategies, and that Delta Lake reduced this to nearly none.

## Mechanism

- **Layout.** Data lives in Parquet objects. Table membership lives in a log of numbered JSON records under a `_delta_log` prefix in the same object store; no servers maintain state.
- **Read.** Read the last-checkpoint pointer, list log records from that id, rebuild the table state from the checkpoint plus later records, use per-file min/max statistics to prune, then read data. It tolerates eventually consistent listing, and a stale checkpoint pointer is harmless.
- **Checkpoints.** Clients write a Parquet checkpoint of the non-redundant log actions by default every 10 transactions. A failure during checkpointing affects performance only, not correctness.
- **Write.** Optimistic concurrency. A commit atomically creates the next log record. Writes are serializable in log order and read-only transactions get snapshot isolation.
- **Atomic commit depends on the store.** GCS and Azure Blob offer put-if-absent, HDFS and ADLS offer atomic rename, and S3 offers neither, so Databricks adds a small coordination service just for log writes. The open-source Spark connector holds that state inside each driver, so it does not cover concurrency across clusters.
- **Rate.** Commit latency of tens to hundreds of milliseconds limits write transactions to a few per second, which the authors judge enough for current uses.
- **Time travel and repair.** Because old files remain until cleaned, a table can be queried as of an earlier time, and a MERGE from a past snapshot can undo a bad update.
- **Layout optimisation.** OPTIMIZE compacts toward a 1 GB default object size; Z-ordering clusters on several columns.

## Reported results (self-reported)

- Metadata scale: 16-node AWS clusters of 8-vCPU VMs, tables of 33M rows with 1,000 to 1,000,000 partitions, a simple sum query. Hive and Presto (an unnamed hosted vendor service) took over an hour at 10,000 and 100,000 partitions respectively. Databricks listing Parquet took 450 s at 100,000 partitions. Delta took 108 s at 1,000,000 partitions, or 17 s with the log cached on SSD.
- Z-order on a synthetic 100-object table of random values: at least 43% of objects skipped on each of four columns (54% average) versus 25% for a single sort order, where a global sort skipped 99% on its own column and 0% on the others. On a 500 TB network dataset, 93% of data skipped.
- TPC-DS, 1 TB on S3, 8 workers, mean of 3 runs: Delta was fastest overall, mainly on longer queries. Loading 400 GB showed write time similar to plain Parquet (no numbers given).
- Scale claim: thousands of customers and exabytes per day, with speedups of up to 100x in extreme cases.

## Limits

- Serializability holds within a single table only; streaming latency cannot beat the object store's own; there are no secondary indexes beyond min/max statistics; a few commits per second.
- The support-escalation figure is explicitly anecdotal. Benchmarks are vendor-run against an unnamed service; the Z-order test is synthetic; Z-order, auto-optimise and the SSD cache were service features rather than open-source ones at the time.
- Dated: the S3 listing consistency and lack of put-if-absent described were true in 2020. The extraction notes TPC-DS bar values were only partly legible and the mapping of values to systems should be checked against the figure.

## See Also

- [[Lakehouse vs Warehouse Decision]] — prerequisite-for
- [[Iceberg Metadata Tree and Hidden Partitioning]] — alternative-to
- [[Copy-on-Write vs Merge-on-Read]] — related
- [[Parquet Row Groups, Pruning and Sort Order]] — related (the data-file format underneath)
