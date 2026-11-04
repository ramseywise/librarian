---
title: "Three Ways to Be Serializable"
tags: [foundations, comparison]
summary: "Serial execution, two-phase locking and serializable snapshot isolation each buy serializability at a different price: a throughput ceiling, blocking and deadlocks, or aborts under contention."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--04-transactions-and-isolation.md
---

# Three Ways to Be Serializable

Weak isolation is treacherous (see [[Transaction Isolation Levels and Anomalies]]), so why not always use serializable? There are three implementations, each with a cost.

**Actual serial execution.** Run transactions one at a time. It became viable around 2007 with cheap RAM and short transactions, as in in-memory stores. It requires short transactions, usually stored procedures that never wait on a client. SQLite does this with `BEGIN IMMEDIATE`, a single write lock; a SQLite or DuckDB file is a fine answer for a single-writer pipeline step. Two deferred transactions on a stale snapshot saw the second writer refused with "database is locked".

**Two-phase locking (2PL).** The only widely used algorithm for around 30 years. Readers block writers and writers block readers, unlike snapshot isolation. Latency becomes unstable and is worst at high percentiles since one slow transaction makes others wait. Locks cause deadlocks: two transactions each holding one row and wanting the other were resolved by Postgres killing one after about a second, its default `deadlock_timeout`; code must retry and the wait shows up as tail latency. Two-phase locking has nothing to do with two-phase commit (see [[Atomic Commit and Why Two-Phase Commit Blocks]]).

**Serializable snapshot isolation (SSI).** Optimistic: transactions run on a snapshot without blocking while the database tracks which reads a concurrent write invalidated; at commit, a transaction whose premise became false aborts. Postgres has used it since version 9.1. Cost is aborts under contention. Eight workers, 100 read-then-write attempts each:

| Hot rows | Commits | Aborts | Share of attempts aborted | Commits/s |
|---|---|---|---|---|
| 1 | 800 | 2800 | 78% | 1270 |
| 10 | 800 | 316 | 28% | 3528 |
| 1000 | 800 | 47 | 6% | 4911 |

Aborts do not reach zero even on 1000 rows because predicate-lock tracking is coarser than a row (tuple, page or relation level; a sequential scan needs a relation-level lock and raises failures). Pair serializable with short transactions and indexes. Any code using it must have a retry loop: a serialization failure is a normal outcome, not an error to report. On one hot row serializable and repeatable read cost about the same; serializable costs more when transactions read and write different rows.

## See Also
- [[Transaction Isolation Levels and Anomalies]] — prerequisite-for
- [[MVCC Row Versions and Snapshots]] — prerequisite-for
- [[B-Trees vs LSM-Trees]] — related (B-tree range locks against phantoms)
- [[Idempotent Retries and Request IDs]] — related
