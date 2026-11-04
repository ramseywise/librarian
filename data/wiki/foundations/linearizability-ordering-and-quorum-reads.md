---
title: "Linearizability, Ordering and Quorum Reads"
tags: [foundations, concept]
summary: "Linearizability is a recency guarantee on one object, distinct from serializability; strict quorums with w + r > n do not deliver it, CAP is better read as consistent-or-available under partition, and causality gives only a partial order."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--07-consistency-and-consensus.md
---

# Linearizability, Ordering and Quorum Reads

**Eventual consistency** promises only that replicas converge at some unspecified time once writes stop; it says nothing about what a read returns meanwhile.

## Linearizability
It makes a system appear to hold a single copy of the data, with every operation atomic on it. The defining property is **recency**: once one client has read a new value, every later read must see it, so values cannot go backwards. A history is linearizable if some total order of the operations respects real time (an operation that finished before another began comes first) and each read returns the latest write before it. During a write's lifetime a read may return either value; a read of the new value followed by a later-starting read of the old one has no valid order. Checking by searching every order is expensive, so real tests are too.

**Not the same as serializability.** Serializability is an isolation property of multi-object transactions: they behave as if in *some* serial order, possibly not the real-time one. Linearizability is a recency guarantee on a single register. A database with both is **strictly serializable**. Two-phase locking and actual serial execution are typically linearizable; serializable snapshot isolation is not, by design, because a snapshot read misses newer writes (see [[Three Ways to Be Serializable]]).

**When it is needed:**
- leader election and locks, which need exactly one current holder;
- uniqueness constraints such as usernames;
- cross-channel timing, where two paths carry related information (an event saying "new file ready" can arrive before an object store's listing shows the file, a real bug class where listings lag writes).

## Which systems are linearizable
Single-leader replication can be if reads go to the leader and it really is the leader; consensus algorithms are ([[Consensus and Coordination Services]]); multi-leader is not; leaderless often is not despite appearances. **Strict quorums with `w + r > n` do not suffice**: a write reaches replicas at different moments, so one reader can catch the new value on one replica and a later reader miss it. In a simulation of n=3, w=3, r=2 with reads running while the write was in flight, 22% of runs were not linearizable (37% for n=5, w=5, r=3); reading from a single leader gave 0 of 5000. If every read asks all three replicas the share drops to 0%, but one unreachable replica then stops every read as well as every write with w = 3. Overlap in the steady state is not recency during a write; fixing it needs synchronous read repair at a performance cost (see [[Quorums, Version Vectors and Last-Write-Wins]]).

## CAP and the real cost
"Pick two of three" misleads because partitions are not a choice. Better: when partitioned, a system is *either consistent or available*. If cut-off replicas must stay linearizable some must refuse requests; if not, all can answer but may diverge. The formal result covers only linearizability and network partitions, not delays or dead nodes. More often systems give up linearizability for **performance**: RAM across CPU cores is not linearizable, with no partition involved, and linearizable reads and writes must have a response time at least proportional to the uncertainty in network delay.

## Ordering and causality
Leaders order writes, serializability orders transactions, timestamps try to order events; the underlying need is usually **causality** (a question before its answer, a row created before it is updated). A **total order** compares any two elements; causality gives a **partial order**, since concurrent events are incomparable, like branches in Git. Linearizability is a total order and implies causality; causal consistency is the strongest model that does not slow down for network delay and stays available during partitions. A consistent snapshot is exactly causal consistency. Full causality tracking needs version vectors, so practical systems use sequence numbers: free from a single leader's log, otherwise see [[Lamport Timestamps and Total Order Broadcast]].

## Pitfalls
- Treating `w + r > n` as strong consistency.
- Confusing linearizable (recency on one object) with serializable (isolation across many); neither implies the other.
- Running leader election over a table flag or a timestamp, which combines the clock and pause flaws in [[Unreliable Networks, Clocks and Process Pauses]]; use a coordination service, or a database row lock with fencing.

## See Also
- [[Transaction Isolation Levels and Anomalies]] — related (a different question: isolation, not recency)
- [[Replication Lag, Failover and Read Anomalies]] — prerequisite-for
- [[Lamport Timestamps and Total Order Broadcast]] — extends
- [[Fencing Tokens and Zombie Writers]] — related
