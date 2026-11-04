---
title: "Partitioning Strategies and Hot Spots"
tags: [foundations, concept]
summary: "Range versus hash versus compound partition keys, why hot keys need salting, how secondary indexes fan out, and why rebalancing needs many fixed partitions rather than hash mod N."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--05-partitioning-and-replication.md
---

# Partitioning Strategies and Hot Spots

Partitioning decides which machine holds a row; replication (see [[Replication Lag, Failover and Read Anomalies]]) decides how many hold each copy. The same idea is a shard, region, tablet, vnode or vBucket depending on the product, and real systems combine both so a node leads some partitions and follows others. Uneven splitting is **skew**; a partition with a disproportionate share of load is a **hot spot**.

## Range vs hash vs compound

- **Range** assigns contiguous key ranges: cheap range queries, but a date key sends every new write to one partition (1 of 31 partitions took 31952 rows for the last day).
- **Hash** spreads evenly (busiest partition 2.2% of writes) but destroys order: a one-week query touched 7 partitions under range and all 31 under hash.
- **Compound** keys hash the first part and sort by the rest: a `(zone, day)` key reads one of 16 partitions and scans a sorted run in it.

A bad partition key usually causes a write hot spot or a query that fans out to everything.

## Hot keys

Hashing cannot help when one key is hot. The application must spread it, e.g. append a random two-digit suffix so writes spread over 100 keys. With 300,000 of a million events on one key, the busiest of 100 partitions fell from 307030 to 19127. The price: reads for that key fetch and combine 100 keys, so salt only the keys that need it. The same salting appears in the shuffle (see [[Shuffle Skew and Salting]]).

## Secondary indexes

| | Local (document-partitioned) | Global (term-partitioned) |
|---|---|---|
| Lives | Beside its partition's data | In its own partitions by indexed value |
| Writes | One partition | May touch several, often asynchronous |
| Reads | Scatter to all, gather | One index partition |

Scatter-gather waits for the slowest shard. In a simulation (median near 5 ms per shard), median and p99 went from 4.9 and 15.8 ms at 1 shard to 15.6 and 30.2 ms at 64 shards: nothing got slower, the query had more chances to draw a slow shard (see [[Latency Percentiles, Tail Amplification and Coordinated Omission]]).

## Rebalancing

Rebalancing should leave load fair, keep serving, and move no more than necessary. `hash(key) mod N` fails the third: going from 10 to 11 nodes moved 91.0% of 1,000,000 keys. With 1,024 fixed partitions and whole partitions reassigned, 9.8% moved, about the new node's share. Some stores split partitions dynamically as they grow. Be careful with the term "consistent hashing", used loosely. Automatic rebalancing on failure detection is risky: a slow node is declared dead, data moves, extra load makes others look dead. Keep a person in the loop.

Clients find the owner by asking any node, via a routing tier, or by knowing the map; all must agree on a changing assignment, so many systems use a coordination service or gossip (see [[Consensus and Coordination Services]]). A write touching several partitions cannot be made atomic by partitioning alone (see [[Atomic Commit and Why Two-Phase Commit Blocks]]).

## See Also
- [[Small Files, Prefix Layout and Storage Tiers]] — extends
- [[Replication Lag, Failover and Read Anomalies]] — related
- [[Faults, Load Parameters and Systems of Record]] — related (skewed load)
