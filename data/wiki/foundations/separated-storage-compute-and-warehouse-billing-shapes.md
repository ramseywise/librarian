---
title: "Separated Storage and Compute and Warehouse Billing Shapes"
tags: [foundations, comparison]
summary: "Why modern warehouses split storage from compute, how the main engines differ in layout and billing, and why Redshift-style distribution keys decide join cost."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--01-warehouse-and-store.md
---
# Separated Storage and Compute and Warehouse Billing Shapes

## Why separate them

A shared-nothing warehouse gives each node its own disks and a slice of each table. That couples compute and storage: loading and heavy queries want different hardware, a resize or node failure reshuffles data using the same machines that serve queries, and upgrades touch every node. In the cloud, membership changes are the norm. The common answer has three layers: data in object storage, virtual warehouses as compute, and a cloud-services layer as coordinator. This is a hybrid of shared-disk (one central repository every node can reach) and shared-nothing (each cluster caches part locally).

In miniature: three separate engine processes read one set of Parquet files at the same time with no copy, load or coordination. What it buys is mostly isolation and billing. A heavy job gets its own compute and cannot slow a dashboard; compute can stop at night while data stays; a bigger warehouse for one hour costs the same as a smaller one for two, if the work scales. Reads are the easy case: concurrent writes need [[Table Format as a Commit Log over Parquet]].

## The engines compared

The comparison reflects vendor documentation, not speed; no benchmark was run and vendor benchmarks are not a basis for choosing.

| | Billed by | Layout | Watch out for |
|---|---|---|---|
| Snowflake | Warehouse-seconds, 60 s minimum per start | Micro-partitions of 50 to 500 MB uncompressed, optional clustering key | Idle warehouse time |
| BigQuery | Bytes scanned, or slot-hours | Partitions and up to four clustering columns | One `SELECT *` on a big table |
| Redshift | Node-hours (Serverless: capacity used) | Distribution and sort keys, 1 MB blocks with min and max | Skewed distribution keys, fixed cluster cost |
| Databricks SQL | Warehouse usage | Delta tables on object storage | Several compute types to govern |
| ClickHouse | Your servers or cloud usage | Sorted parts, 8,192-row granules | Updates are mutations; plan for append |
| DuckDB | Your machine | Own row groups or Parquet | One machine's limits |

Billing shape sets the levers. On BigQuery on-demand ($6.25 per TiB list price at the time), layout is the bill: 1.6 GiB per run costs $0.00977 per run, or $9.77 a month at 1,000 runs; the partitioned 0.106 GiB costs $0.00065 per run, $0.65 a month. The same ratio on a 1.6 TiB table saves about $112,000 a year. On Snowflake, warehouse time dominates: 100 one-second queries a day on a 2-credit-an-hour warehouse cost 3.33 credits if each wakes the warehouse (60-second minimum) against 0.06 credits batched in one session.

A scheduler is not a warehouse alternative: an orchestrator schedules, retries and backfills work that often runs inside a warehouse.

## Distribution keys (Redshift)

Distribution style places rows on nodes: `AUTO`, `EVEN`, `KEY`, `ALL`. Arithmetic on keys in a four-node cluster with 1,000,000 fact rows joined on pickup zone:

- `EVEN` fact and dimension: 750,332 fact rows must be redistributed by key to run the join (the same shuffle as in [[Spark Shuffles and When One Machine Is Enough]]).
- `KEY` on the join column: 0 rows move (matching values collocated).
- `ALL` on the small dimension: 0 move, but 265 x 4 = 1,060 dimension rows are stored.
- The trap: a key with few values piles rows on a couple of nodes. `DISTKEY (vendor_id)` gave rows per node of [0, 299145, 700855, 0], and the query runs as slowly as the fullest node.

Sort keys are the other physical choice: they order blocks so min and max can skip them, as in [[Partition Pruning, Clustering and Column Pruning]]. AWS's example is a month out of five years sorted by date removing up to 98% of blocks. Choose distribution for joins and even spread, sort for filters. Compound sort keys are the documented default; interleaved keys take significantly longer to `VACUUM REINDEX`. `AUTO` is a reasonable starting point; the manual choices explain why a query got slow.

## See Also
- [[Partition Pruning, Clustering and Column Pruning]] — prerequisite-for
- [[Warehouse Cost Meters: Bytes, Slots and Egress]] — extends
- [[Lakehouse vs Warehouse Decision]] — related
- [[Spark Shuffles and When One Machine Is Enough]] — related
