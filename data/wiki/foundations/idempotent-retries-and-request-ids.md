---
title: "Idempotent Retries and Request IDs"
tags: [foundations, pattern]
summary: "Because a timeout hides whether a write applied, retries are needed and duplicate effects follow; a request ID stored in the same transaction as the write makes a retry harmless, which is what most 'exactly-once' means."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--06-when-distributed-systems-fail.md
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--04-transactions-and-isolation.md
---

# Idempotent Retries and Request IDs

A commit can succeed while its acknowledgement is lost, so the client cannot tell a failed write from an applied one (see [[Unreliable Networks, Clocks and Process Pauses]]). Retrying is therefore necessary and dangerous.

## The numbers
Simulating 100,000 charges over a lossy network:

| Strategy | Charges recorded | Duplicates | Never charged | Client gave up |
|---|---|---|---|---|
| No retry | 97,057 | 0 | 2,943 | 6,811 |
| Retry 3x | 104,129 | 4,131 | 2 | 26 |
| Retry 3x with request ID | 99,998 | 0 | 2 | 26 |

Without retries about 3% of customers were never charged while the client believed 7% had failed; with blind retries almost nobody was missed at the cost of over 4,000 double charges. The request ID fixes that without improving the network.

## Mechanism
Reuse **one request ID from the client to the store** across all retries, with a unique constraint, and record it in the same transaction as the effect:

```sql
insert into charge values (request_id, ...) on conflict (request_id) do nothing
```

With a fresh ID per retry a 2000-cent charge was recorded as 4000; with the same ID, 2000. Most of what the industry calls exactly-once is at-least-once delivery made harmless at the receiver. It is the same mechanism as an idempotent merge on a business key and as a producer-side idempotence setting in a log system. Retry has further edge cases: overload retries add load, permanent errors never succeed, and a side effect outside the database (an email) repeats.

## See Also
- [[Transaction Isolation Levels and Anomalies]] — related
- [[Fencing Tokens and Zombie Writers]] — related
