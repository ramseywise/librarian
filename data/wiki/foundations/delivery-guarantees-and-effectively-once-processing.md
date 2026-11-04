---
title: "Delivery Guarantees and Effectively-Once Processing"
tags: [foundations, concept]
summary: "At-most-once, at-least-once and exactly-once differ only in whether position or output is saved first; effectively-once comes from idempotent keyed sinks, offsets stored atomically with the data, and idempotent producers, and it holds only within a boundary."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--04-kafka-and-stream-semantics.md
---
# Delivery Guarantees and Effectively-Once Processing

A consumer's guarantee reduces to one ordering question: when you process a batch, do you save your position first or save the output first? Vendors' exactly-once claims need the fine print read.

## The three, seen failing

One consumer over 9 rides of $10 each (truth $90), crashing once at the second batch of 3:

| Mode | Order | Result |
|---|---|---|
| at-most-once | commit offset, then write | 6 rows, $60: three rides lost, no error |
| at-least-once | write, then commit offset | 12 rows, $120: three rides counted twice, no error |
| atomic | output and offset in one transaction | 9 rows, $90 |

An auto-commit setting commits offsets on a timer independent of processing, so either failure can occur depending on timing: fine for a demo, poor for billing.

## Ways to get a correct result

1. **Keyed upsert (reach for it first).** At-least-once delivery plus an overwrite keyed on a stable business ID yields the right final state (9 rows, $90 in the toy), because a repeat overwrites itself. It fails on a sum computed by adding to a running total, since repeats add again.
2. **Offset stored with the data.** For running totals, commit the output and the consumer position in one transaction. In a toy sink with totals and offset in one database transaction, a crash rolled back both, the retry reprocessed the same batch from the same offset, and totals matched (zone totals 16.5, 6.0 and 7.0) though the sum is not idempotent. A lake writer does the same with an application ID and version recorded atomically with the data files ([[Table Format as a Commit Log over Parquet]]). Assumptions: replay sees the same messages in the same order, processing is deterministic, no one else writes the same value concurrently. A failed-over task's predecessor may not be dead, so fencing is needed: a new producer with the same `transactional.id` fences the old one.
3. **Idempotent producer.** Every producer gets an ID and each message a per-partition sequence number; the broker rejects a resend whose sequence was already seen. This fixes the lost acknowledgement (the log held `ride-1` twice without dedupe, once with it).
4. **Transactions.** A producer writes to several partitions atomically and, because consumer offsets live in an internal topic, can include its offsets in the same transaction. A consumer with `isolation.level=read_committed` sees only committed transactional messages; the default `read_uncommitted` sees everything. Streams-style read-process-write inside Kafka wires these together.

## What exactly-once means

The final effect is the same as if no fault occurred; "effectively-once" is the better name, since records may be processed more than once along the way. The limit is the boundary: guarantees hold inside Kafka. Once the consumer calls a payment API or writes to a store outside the transaction, the effect can still happen twice, so output leaving the framework needs idempotence or a distributed transaction. Ask: from where to where? Staying within one system avoids a heterogeneous two-phase commit holding locks while a coordinator is down. To extend past the boundary, carry one client-generated request ID to the final store so every hop can drop duplicates; a two-account transfer then needs no atomic commit: log the request once, derive a debit and a credit, and deduplicate each on the ID.

## Timeliness versus integrity

Timeliness is seeing up-to-date state and heals by waiting; integrity is no corruption, loss or contradiction and never heals (eventual consistency against perpetual inconsistency). A stream pipeline can give up timeliness to protect integrity. It needs: a write stated as a single message, everything else derived by deterministic functions, a client request ID passed throughout, and immutable messages so derived data can be reprocessed.

## See Also
- [[Kafka Log, Partitions and Offsets]] — prerequisite-for
- [[Event Time, Watermarks and Late Data]] — related
- [[Table Format as a Commit Log over Parquet]] — related
- [[Stream Joins Replay and Lambda Architecture]] — related
