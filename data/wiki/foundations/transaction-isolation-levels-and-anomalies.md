---
title: "Transaction Isolation Levels and Anomalies"
tags: [foundations, concept]
summary: "What ACID letters actually promise and which anomaly each isolation level still allows: read skew, lost updates, write skew and phantoms, with the fixes (atomic update, row locks, constraints, serializable) and why level names differ across engines."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--04-transactions-and-isolation.md
---

# Transaction Isolation Levels and Anomalies

A transaction lets you pretend a group of reads and writes is one step that either happened or did not, with nobody else running. The first half is cheap; the second has a price, so isolation comes in grades, named so badly that people run on a weaker one than they think. Tested on a real Postgres 16 with two interleaved connections.

## ACID decoded
- **Atomicity** is abortability, not concurrency: if writes cannot finish, all are discarded. Without it, a crash between a driver credit and a platform credit lost 400 cents (total 4600 instead of 5000); with it the state returns to one you can retry from.
- **Consistency** means application invariants (credits equal debits); the database checks only some, through constraints. It belongs to the application.
- **Isolation** in the textbook sense is serializability: results as if run one at a time.
- **Durability** is a write-ahead log on one node and replicas on several; never absolute (bad blocks, `fsync` that lies).

Retrying an aborted transaction has edge cases: the commit may have succeeded with only the acknowledgement lost, overload retries add load, permanent errors never succeed, and external side effects (an email) repeat. See [[Idempotent Retries and Request IDs]].

## What each level lets through

Postgres defaults to read committed (as do Oracle 11g and SQL Server 2012). It accepts `READ UNCOMMITTED` and behaves as read committed.

| Anomaly | What happens | Read committed | Repeatable read (Postgres) | Serializable |
|---|---|---|---|---|
| Dirty read / write | See or overwrite uncommitted data | Prevented | Prevented | Prevented |
| Read skew | Different parts of the database seen at different times | Happens | Prevented | Prevented |
| Lost update | Read-modify-write overwrites a concurrent write | Happens | Aborted on Postgres | Prevented |
| Write skew | Decide from a read a concurrent write invalidates | Happens | Happens | Aborted |
| Phantom write skew | Same, about rows not yet existing | Happens | Happens | Aborted |

Level names do not translate: Oracle 11g's "serializable" is snapshot isolation, and MySQL InnoDB's repeatable read does not detect lost updates. Test the anomaly you care about, not the name.

**Read skew.** A reader summing two accounts while 10,000 cents moved between them saw 110000 under read committed and 100000 under repeatable read. Backups, analytic queries touching much of the database and integrity checks cannot tolerate it, and a data-quality test comparing two tables under read committed can fail or wrongly pass. Fix: snapshot isolation (see [[MVCC Row Versions and Snapshots]]).

**Lost update.** Two increments from 100 gave 101 under read committed with both transactions reporting success. Under repeatable read Postgres aborted the second writer. Eight threads of 150 increments each (expected 1200):

| Technique | Final | Retries | Time |
|---|---|---|---|
| Read-then-write, read committed | 172 | 0 | 0.10 s |
| Atomic update (`set trips = trips + 1`) | 1200 | 0 | 0.08 s |
| `SELECT ... FOR UPDATE` | 1200 | 0 | 0.10 s |
| Compare-and-set | 1200 | 0 | 0.58 s |
| Read-then-write, repeatable read | 1200 | 4240 | 1.02 s |

Use one atomic statement when the change fits; `FOR UPDATE` when logic sits between read and write. These assume a single up-to-date copy, so they do not apply to multi-leader or leaderless replication. An Iceberg-style commit is compare-and-set on a catalog pointer, with retry on conflict.

**Write skew.** Rule: sign off only if at least two drivers are on duty. Two drivers did it at once: read committed and repeatable read both left 0 on duty (the transactions wrote different rows, so nothing conflicted); serializable left 1 and aborted the second. The shape is always select-a-condition, decide, write something that changes the condition (bookings, usernames, double spending). Without serializable, lock the rows the decision depends on: `FOR UPDATE` made the second driver wait, re-evaluate and be refused.

**Phantoms.** When the decision depends on a row not existing, there is nothing to lock: `FOR UPDATE` on an empty result locked nothing and two bookings of one slot committed at both lower levels. Serializable aborted the second. Often better: a unique constraint turns absence into something enforceable, and an exclusion constraint does it for overlapping ranges. Materialising conflicts (pre-creating a row per slot to lock) is a last resort.

## What this means for a pipeline
- **Readers see your load.** Deleting and inserting a partition in two commits left a reader seeing 0 rows; in one transaction it saw old rows until commit and then all new ones. Multi-statement atomicity is what makes a replace safe, which is why incremental strategies and `INSERT OVERWRITE` are written as they are.
- **Concurrent writers are the warehouse's lost update.** Overlapping backfills or a compaction beside an ingest race; table formats resolve them optimistically, so a failed commit is normal and needs a retry.
- `TRUNCATE` is not `DELETE`: it takes a strong lock and is not MVCC-safe.

## See Also
- [[MVCC Row Versions and Snapshots]] — related
- [[Three Ways to Be Serializable]] — extends
- [[Idempotent Retries and Request IDs]] — related
- [[SQL Schema Design and DDL]] — related (constraints that enforce invariants)
