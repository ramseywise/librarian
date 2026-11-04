---
title: "Consensus and Coordination Services"
tags: [foundations, concept]
summary: "Consensus accepts a decision from a majority so it terminates while a majority is up; terms stop stale leaders, and most applications outsource it to a small coordination service or to a database row lock."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--07-consistency-and-consensus.md
---

# Consensus and Coordination Services

Many problems reduce to consensus: linearizable compare-and-set, atomic commit, total order broadcast, locks and leases, membership, uniqueness constraints. With a single leader all are easy until the leader fails; then you wait for recovery (blocks), have a human fail over, or use an algorithm to elect a new leader. The third is consensus. Leaderless and multi-leader systems avoid global consensus and accept conflicts instead of linearizability.

## What it provides
Uniform agreement, integrity, validity (safety) and termination (liveness, which two-phase commit lacks; see [[Atomic Commit and Why Two-Phase Commit Blocks]]). The trick is to accept a decision from a **majority**, so any majority carries on when others fail. If a majority fails, safety still holds and the system simply stops (see [[Fencing Tokens and Zombie Writers]]). Viewstamped Replication, Paxos, Raft and Zab each decide a sequence of values, so each implements [[Lamport Timestamps and Total Order Broadcast]].

## Terms stop old leaders
Electing a leader needs consensus, and consensus needs a leader. The way out is an **epoch number** (Raft's term) and two rounds of voting. A leader is unique only within its term; a new election uses a higher term and a node that has seen a higher term refuses the older leader. Before acting, a leader needs quorum approval; the vote for a leader and the vote on a value both need majorities, so the sets overlap and a new leader must hear of anything committed. This is the fencing token built into the protocol.

In a toy Raft-shaped simulation, a leader cut off with a minority wrote entries that reached only 2 of 5 nodes, so clients were never told they succeeded; the majority side elected a higher-term leader; after healing, the old leader's writes were refused and its uncommitted entries discarded. Over 3000 random runs with partitions, no term had two leaders and no acknowledged write was lost. Lowering the quorum from 3 of 5 to 2 of 5 broke an invariant in 688 of 1000 runs, because two disjoint "majorities" could each progress. A larger-than-majority quorum (4 of 5) is also safe but tolerates one failure instead of two, so there is no gain. A random test passing does not prove an algorithm correct.

## Costs
Voting before commit is effectively synchronous replication, which costs throughput; a strict majority is required, so a partition can stop the minority side; the member set is usually fixed; failure detection rests on timeouts, so on a flaky network elections can repeat and little work gets done. The FLP result says no deterministic algorithm guarantees consensus on a purely asynchronous network; timeouts are how real systems escape it. A two-node cluster tolerates no failures; use 3 or 5.

## Where it lives in a data stack
Few applications run consensus directly; they use a small service (ZooKeeper, etcd): small in-memory databases offering linearizable atomic operations, total ordering, failure detection through sessions and change notifications, typically on 3 or 5 nodes coordinating many others. They are for small, slowly changing metadata, not high-rate data.

| Tool | Decision to agree on | Mechanism |
|---|---|---|
| Kafka | who leads each partition | a Raft-based controller quorum, replacing ZooKeeper |
| Iceberg | which metadata file is current | the catalog's atomic swap; a database or service provides compare-and-set |
| Delta Lake on object storage | who owns version N of the log | put-if-absent on the store, or a coordinator |
| Airflow | which scheduler launches a task | row locks in the metadata database, no consensus among schedulers |
| Kubernetes | cluster state | etcd |

Airflow deliberately avoids a consensus algorithm between schedulers and uses `SELECT ... FOR UPDATE` row locks, to keep its operational surface small. The `FOR UPDATE` that fixes write skew ([[Transaction Isolation Levels and Anomalies]]) stops two schedulers launching one task, handing agreement to the database. With a single primary the problem reduces to "who is the primary": having a leader moves the need for consensus somewhere it is needed less often. The orchestrator's metadata database should be treated as a system of record.

## See Also
- [[Linearizability, Ordering and Quorum Reads]] — prerequisite-for
- [[Atomic Commit and Why Two-Phase Commit Blocks]] — alternative-to
- [[Unreliable Networks, Clocks and Process Pauses]] — prerequisite-for
