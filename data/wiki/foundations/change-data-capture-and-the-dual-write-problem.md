---
title: "Change Data Capture and the Dual-Write Problem"
tags: [foundations, concept]
summary: "Writing one change to two systems leaves them permanently different about half the time; CDC instead reads the database's own ordered change log, and a replay-safe consumer stores the log position per row and remembers deletes."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--02-ingest-and-modelling--notes--01-ingest.md
---

# Change Data Capture and the Dual-Write Problem

## Why not write to both

An application could write to its database and also to a warehouse, search index or cache. It goes wrong for two reasons: two clients can reach the two systems in different orders, and one of the two writes can fail while the other succeeds. A simulation of only the ordering problem (two clients, one key, 100,000 runs per strategy) gave:

| Strategy | Systems disagree |
|---|---|
| Dual write | 49.71% of runs |
| Follow one ordered log | 0.00% of runs |

Nothing failed, so nothing is logged. Making the two writes atomic is the expensive atomic-commit problem. The better shape is one leader that decides the order, with everything else following.

## Change data capture

Replication already needs a record of changes: the leader writes every change to a log and followers apply it in order. **CDC** exposes that log to other systems, making the warehouse one more follower. Debezium is a common open-source implementation: it reads the log of databases such as PostgreSQL and MySQL and publishes events through Kafka Connect. Versus polling, it captures all changes including deletes and needs no "last updated" column. Triggers writing a change table can imitate CDC, but are fragile and costly next to parsing the log.

Procedure: take a **snapshot at a known log position**, then apply everything after it. Starting without a snapshot tied to a position loses or double-applies changes around the start.

## Applying changes safely

Delivery is normally at least once: a consumer that crashes before saving its offset sees events again. So:

- Store with each row the log position of the change that last touched it, and ignore events not newer.
- Keep a record of deleted keys (a tombstone). Without it, replaying an old update for a deleted key brings the row back with its old value.

In the worked example the consumer replayed the whole log after a simulated crash: position stayed at 3, the corrected fare held, the deleted trip stayed gone, and row counts matched the source.

Costs: more moving parts than a nightly query; real logs are truncated, so a connector that falls too far behind must take a new snapshot; CDC is usually asynchronous, so replication lag still applies. A compacted topic (latest value per key) lets a new consumer rebuild from offset zero without a separate snapshot.

## Three kinds of record

- A CDC event says what a row became.
- An **event** (event sourcing) says what happened, keeping intent that a row update discards.
- A **command** is a request that can still be refused; once validated it becomes an event, a fact consumers may not reject.

A pipeline can trust an event log in a way it cannot trust a stream of commands, so ask which of the three a source emits.

## See Also
- [[High-Watermark Incremental Extraction and Its Blind Spots]] — alternative-to
- [[Idempotent Window-Replace Loads]] — related
- [[Kafka Ingest Model, Delivery Semantics and Stream Windows]] — related
- [[Slowly Changing Dimensions Types 1, 2 and 3]] — related (versioned rows in a stream)
- [[Data Engineering Foundations]] — related
