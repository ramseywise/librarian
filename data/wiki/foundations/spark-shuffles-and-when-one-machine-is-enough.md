---
title: "Spark Shuffles and When One Machine Is Enough"
tags: [foundations, concept]
summary: "What a groupBy and a join cost in a distributed engine, which Spark habits to avoid, and when DuckDB or Polars on one machine is the better answer."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--01-warehouse-and-store.md
---
# Spark Shuffles and When One Machine Is Enough

A distributed batch engine is what you reach for when one machine cannot hold the transformation. Its expensive step is the shuffle, so most guidance is about avoiding or shrinking it.

## What the physical plan costs

| Operation | Plan | Cost |
|---|---|---|
| `groupBy(...).sum()` | Partial aggregate per partition, shuffle by key, final aggregate | The shuffle (network and disk) |
| Join of two large tables | Sort-merge join: shuffle both sides by key | Two shuffles |
| Join of large to small | Broadcast the small table to every executor | No shuffle of the large side |

The partial aggregate is why a `groupBy` is cheaper than it sounds. Counting on 1,000,000 rows across four executors and 265 keys: without partial aggregation 749,627 rows cross the network; with it, 795 partial sums cross (of 1,060 per-executor-per-key sums). Equal keys must still meet on one executor; only the unit shipped shrinks. A rewrite with `reduceByKey` on an RDD shows the same plan by hand.

## Habits that matter

- **Explicit schema, not `inferSchema`.** Inference reads the data twice and guesses; an explicit schema is a contract that fails loudly.
- **`repartition(24)` before writing Parquet** turns one CSV into 24 files so 24 executors can read in parallel later.
- **`coalesce(1)` on a large result** funnels everything through one task and turns skew into a straggler. Fine for a small result.
- **UDFs run row-at-a-time in Python**, losing vectorised execution and the optimiser's view. Use built-in functions first; use `mapPartitions` when a model must run, so rows are batched into a DataFrame and the model is called once per partition instead of once per row.
- Write jobs with input and output arguments so one file runs locally, on a standalone cluster and on a managed one.

## When one machine is enough

DuckDB is an in-process OLAP engine (SQLite for analytics) that queries Parquet, CSV and object storage directly with vectorised columnar execution. For single-node workloads up to hundreds of GB it largely replaces both local Spark and a warehouse round trip. Polars is a Rust DataFrame library with a lazy optimiser and multi-threaded execution; it pushes filters into the scan the way Spark does. Use Spark when data or concurrency forces you to; on one node there is no shuffle and no cluster to pay for.

The business logic is portable: the same monthly-revenue aggregate runs as Spark SQL, as a dbt model or as near-identical DuckDB SQL, so the engine is a cost and scale decision. For jobs needing a distributed engine, the usual modern default is Spark on Delta or Iceberg tables ([[Table Format as a Commit Log over Parquet]]).

## In-warehouse models

A warehouse can train a model in SQL without moving data (BigQuery ML). Casting zone and payment-type IDs to strings first makes the engine one-hot encode them instead of treating zone 264 as bigger than zone 1. It is the cheapest path to a baseline; a tracking-and-registry path is what scales to custom models.

## See Also
- [[Separated Storage and Compute and Warehouse Billing Shapes]] — related
- [[Partition Pruning, Clustering and Column Pruning]] — prerequisite-for
- [[Data Engineering Foundations]] — related
