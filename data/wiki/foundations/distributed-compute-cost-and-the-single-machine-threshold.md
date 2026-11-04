---
title: "Distributed Compute Cost and the Single-Machine Threshold"
tags: [foundations, decision]
summary: "Choose a cluster only when one query's input after pruning exceeds what a large single machine can hold; DuckDB and Polars spill to disk and push down filters, and scaling curves can hide large overheads."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--08-distributed-compute.md
---

# Distributed Compute Cost and the Single-Machine Threshold

The relevant number is the data one query reads **after pruning**, not the size of the lake. Most analytic queries read recent, filtered, pruned data, so the working set is far smaller than the stored total. Test the query on one machine before reaching for a cluster.

## Single-machine engines
DuckDB (SQL) and Polars (lazy DataFrames) run in one process and do the same optimisation work as Spark's optimiser: column pruning and filter pushdown into the Parquet scan, giving identical results on the same query. Polars' pushdown happens in `scan_parquet` and the lazy API; eager `read_parquet` reads everything first.

Memory is less of a barrier than assumed because they spill, as `sort` does. DuckDB grouped a 640 MB compressed file of 40 million rows by 3,000,000 distinct keys under a 200 MB memory limit in 3.6 s on a laptop. On that 12-core machine it raised an out-of-memory error at 100 MB, and with one thread it finished at 25 MB in about the same time, since each thread keeps its own working blocks: the limit depends on parallelism as well as data size, so try `threads` before buying memory.

## Evidence that clusters carry overhead
A study defined COST as the configuration needed to outperform a competent single thread. For 20 PageRank iterations on a 1.47-billion-edge graph a single thread on a 2014 laptop took 300 s from SSD, against published figures of 857 s for Spark and 419 s for GraphX on 128 cores, and 249 s for GraphLab on 128 cores. Graph problems are a hard case for partitioning and these were 2014 versions, so it does not show Spark is slow on a modern scan; its lasting point is to measure absolute performance, not only scaling. A second argument, from a database vendor quoting figures from memory, says most customers had under 1 TB and, among those spending over $1,000 a year, 90% of queries touched under 100 MB: treat that as informed opinion, not measurement.

## Choosing
| | DuckDB | Polars | Spark |
|---|---|---|---|
| Interface | SQL | DataFrame, lazy | DataFrame and SQL |
| Runs on | one process | one process | local or a cluster |
| Larger than memory | spills to disk | streaming engine | spills, plus more nodes |
| Fault tolerance | re-run the query | re-run the query | task retry through lineage |
| Reach for it when | files and SQL, tests, small marts | Python pipelines | terabytes per job, many tenants, existing platform |
| Costs you | single-node limit, one writer process | single-node limit | a JVM, a shuffle to tune, cluster operations |

Spark is right when a job truly reads more than one machine holds, when retries must survive losing hardware during long jobs, or when the organisation already runs it. If the input after pruning fits on one large machine, a single node is the cheap default.

## See Also
- [[MapReduce, the Shuffle and Spark Lineage]] — extends
- [[Shuffle Skew and Salting]] — related
- [[Parquet Row Groups, Pruning and Sort Order]] — prerequisite-for
- [[Spark Shuffles and When One Machine Is Enough]] — related
- [[Choosing a Store from the Access Pattern]] — related
