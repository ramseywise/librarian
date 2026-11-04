---
title: "MapReduce, the Shuffle and Spark Lineage"
tags: [foundations, concept]
summary: "MapReduce splits a job into map, a hash-partitioned sort-and-copy shuffle and reduce, tolerating failure through immutable inputs and atomic output; Spark keeps the shape but recovers by recomputing partitions from lineage."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--08-distributed-compute.md
---

# MapReduce, the Shuffle and Spark Lineage

Distributed compute exists because some jobs do not fit on one machine, and it costs more than the cluster bill: every join becomes a shuffle, every failed worker a recovery plan, and the slowest task sets the finish time. It is the design of a chain of Unix tools (uniform interface, inputs never modified, stages inspectable) spread over many machines. `sort` itself spills sorted runs to disk and merges them, so it handles data beyond RAM, whereas an in-memory dictionary of counts is limited by distinct keys.

## MapReduce
Two functions you write, with a framework doing everything between. **Map** emits key-value pairs; the framework **partitions** by hash of key, sorts, and copies pairs to reducers (the **shuffle**); **reduce** sees all values for one key. Mappers effectively send messages to reducers with the key as the address, separating logic from network concerns. The shuffle is the expensive stage: it crosses the network and sorts.

The partition hash must be **stable across processes**. A hash that differs per process (Python's `hash()` of a string is salted) splits one key across reducers and gives silently wrong totals; a stable checksum hash does not. Hashing cannot split a key, so a hot key makes reducers unequal (see [[Shuffle Skew and Salting]]). Partial aggregation before the shuffle (a combiner) must pass along sums and counts: an average of averages is wrong when groups differ in size.

## Fault tolerance from two habits
Inputs are immutable and output appears all at once (write to a temporary name, rename on success), so a failed attempt leaves nothing and a retry cannot double-count. If bad code ships you can roll back, re-run and overwrite the output: human fault tolerance. Two shortcuts break it:
- Calling a production database per record as a join is slow, can overwhelm it, and gives answers that depend on when it ran; copy a snapshot into the cluster and join against that.
- Writing results row by row into a production database loses all-or-nothing, since a failed or speculative duplicate task has already had its effect. Build the database files in the job and switch to them atomically, so a bad run is undone by switching back.

Automatic retry is safe only because the input never changes and a failed attempt's output is discarded. This restricted model also hides partial failure: a task declared dead may still run, and a speculative copy runs on purpose, but with no side effects and one output kept, the code need not care (see [[Fencing Tokens and Zombie Writers]] for when it does).

**Stragglers and preemption.** A sort of about a terabyte (10^10 100-byte records on about 1,800 machines) took 891 seconds, and 44% longer with speculative backup tasks disabled. When about a 5% chance of an hour-long task being killed holds, a 10-minute task is killed with 0.85% probability and at least one of 100 such tasks with 57%. That is why each stage is written to disk: restarting one task is cheap. Older parallel databases aborted the query and had the user rerun it, reasonable for short queries.

## Spark: keep the shape, drop the disk
Dataflow engines (Spark, Tez, Flink) treat the whole workflow as one job, skipping needless sorts and map stages and holding intermediate state in memory or local disk. Without durable intermediate output, Spark recovers via **lineage**: it logs the coarse-grained transformations that built each partition and recomputes a lost one, instead of replicating data. The paper reports up to 20 times faster than Hadoop on iterative applications. A `ShuffledRDD` line in the lineage marks a stage boundary. Recomputation is safe only if operators are **deterministic**; random numbers, current time or unordered iteration can give different data the second time and force downstream tasks to re-run. Recomputation is also not always right: if intermediate data is much smaller than its source or expensive to compute, write it down (`.cache()` and `.checkpoint()` trade this).

A declarative DataFrame API with an optimiser (Catalyst) lets the engine rearrange a query. A physical plan reads bottom up: a scan of only the needed columns with the filter pushed into Parquet, a partial aggregate per partition (the combiner idea, chosen automatically), an `Exchange` (the shuffle) into 200 partitions by default, then a final aggregate. 200 is a lot for a million rows; adaptive execution can coalesce at run time. Pruning and pushdown are the same as in [[Parquet Row Groups, Pruning and Sort Order]].

**Lake vs warehouse.** Parallel databases demanded a model before a load; Hadoop accepted any bytes first and left interpretation to the reader (schema-on-read; see [[Relational, Document and Graph Models and Schema on Read]]), moving the burden from the producer to every consumer. Then both sides converged: dataflow engines adopted declarative joins and columnar execution, warehouses took on arbitrary code.

## See Also
- [[Shuffle Skew and Salting]] — extends
- [[Distributed Compute Cost and the Single-Machine Threshold]] — related
- [[Spark Shuffles and When One Machine Is Enough]] — related
- [[Small Files, Prefix Layout and Storage Tiers]] — related
- [[Idempotent Retries and Request IDs]] — related
