---
title: "Shuffle Skew and Salting"
tags: [foundations, pattern]
summary: "Joins and group-bys are shuffles; broadcast joins avoid moving the big side, and because hashing cannot split one key, a hot key makes one reducer the straggler, which salting plus a second aggregation stage reduces."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--08-distributed-compute.md
---

# Shuffle Skew and Salting

## Joins are shuffles
Most warehouse queries are joins, so the join strategy is the first thing to read in a distributed plan.

| Join | How | Needs | Moves |
|---|---|---|---|
| Sort-merge or shuffle hash | partition both sides by join key, join each partition | nothing | both tables |
| Broadcast hash | send the small table to every worker holding the big one | small side fits in memory | the small table, once per worker |
| Partitioned or bucketed | join pre-partitioned files directly | both sides partitioned the same way on the key | nothing |

With random placement on a 10-node cluster about 9 of every 10 bytes must move to reach the right node for a partitioned join; broadcasting a small dimension instead moved a factor of a few hundred less (a back-of-the-envelope count, not a benchmark). Optimisers therefore try hard to broadcast dimensions, and a stale statistic hiding a table's size can make a plan fall back to a shuffle: read the plan and look for an `Exchange` on the small side. The optimiser also has to know the physical layout, one job of a metastore.

## Skew
Hash partitioning spreads keys but cannot spread one key, so a slow reducer is usually a skewed key, not a slow machine: check input size per task before adding workers. In a synthetic dataset of a million rows with a heavy-tailed key distribution over 8 reducers, the busiest reducer held 1.85 times the mean input.

**Salting.** Split the known hot key across reducers with a random salt (append one of N values to the key), aggregate partially, then merge the partial results in a second stage. Here salting the single hottest key cut the ratio from 1.85 to 1.54; the rest was ordinary hash collisions from other busy keys, so salting one key is rarely the whole answer. Salting more hot keys moves the ratio closer to 1 at 8 reducers; with 32 reducers and only 8 salt values each hot key still lands on at most 8 partitions, so the salt count should grow with the reducer count, and the reduce step must re-aggregate across salts. Some systems handle this natively, with a sampling-based skewed join or separate handling of hot keys, and adaptive execution can split skewed partitions. A straggling reducer in a Spark job is very often this. The same hot-key idea in storage is in [[Partitioning Strategies and Hot Spots]].

## See Also
- [[MapReduce, the Shuffle and Spark Lineage]] — prerequisite-for
- [[Partitioning Strategies and Hot Spots]] — related
- [[SQL Join Patterns]] — related
