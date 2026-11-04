---
title: "Kafka Ingest Model, Delivery Semantics and Stream Windows"
tags: [foundations, concept]
summary: "Topics, partitions, keys, offsets and consumer groups define what ordering and replay a stream gives you; auto-commit is at-most-once, a schema registry turns silent schema change into a failed deploy, and four window types cover most stream aggregation."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--02-ingest-and-modelling--notes--01-ingest.md
---

# Kafka Ingest Model, Delivery Semantics and Stream Windows

## The model

| Term | Meaning | Why it matters for ingest |
|---|---|---|
| Topic | Named, append-only log | Unit you produce to and subscribe to |
| Partition | Ordered shard of a topic | Ordering is per partition only; parallelism = partition count |
| Key | Hashed to choose the partition | Same key, same partition, ordered per key |
| Offset | Position in a partition | Consumers commit offsets; replay = reset the offset |
| Consumer group | Consumers sharing a subscription | Each partition goes to one consumer in the group |
| Retention | Time/size the log keeps messages | The window in which a consumer can fall behind and recover |

Most "cannot connect" errors in a container setup are the wrong one of two listeners: one address for containers on the broker's network, another for the host. A Kafka-API-compatible broker (Redpanda) runs the same client code without ZooKeeper or a JVM.

## Delivery semantics

- `enable_auto_commit=True` commits offsets on a timer whether or not processing finished: at-most-once on a crash. For at-least-once, commit manually after the write succeeds and make the write idempotent. Treat delivery as at least once, so the sink must be idempotent (see [[Change Data Capture and the Dual-Write Problem]]).
- JSON carries no contract. Avro with a schema registry rejects a producer whose schema breaks the subject's compatibility rule, so "an event schema changed and nobody told us" becomes a failed deploy upstream instead of a silent downstream break (see [[Breaking Schema Changes and Expand-Contract]]).
- A Spark streaming job's `checkpointLocation` makes a restart resume at the right offsets instead of reprocessing or skipping.

## Window vocabulary

| Window | Definition |
|---|---|
| Tumbling | Fixed size, no overlap (e.g. 1-minute counts) |
| Hopping / sliding | Fixed size, overlapping by a slide (e.g. 10 minutes every 5) |
| Session | Closed by a gap of inactivity (e.g. 60 seconds) |
| Grace | How late an event may arrive and still count |

Processing options span Kafka Streams (Java), Python stream libraries, Spark Structured Streaming and ksqlDB (SQL). A streaming database maintains a materialised view incrementally as events arrive, so a dashboard reads a precomputed answer with plain SQL.

## Batch or stream

| Question | Batch | Stream |
|---|---|---|
| Freshness needed | Hours or days | Seconds to minutes |
| Replay | Re-download file or re-run API window | Reset offsets within retention |
| Ordering | Sort after load | Per partition, by key |
| Failure unit | One file or day | One message; needs idempotent sinks |
| Operational cost | A scheduled container | Always-on brokers, registry, consumers |

Default to batch; move a source to streaming when a named consumer needs the freshness (real-time inference is the example).

## Ingesting documents instead of tables

For crawled documents feeding an LLM: normalise by content type (article, repository, post) with the source URL in metadata, so a new site means one new crawler; dispatch crawlers on the URL's domain with a generic fallback; a schemaless store suits hundreds of heterogeneous documents, with a warehouse at millions. Count successes and attempts per domain every run, since a crawler silently returning empty pages is the unstructured version of a source that stops sending. Prefer official APIs, exports or RSS to browser automation that violates a platform's terms.

## See Also
- [[Idempotent Batch Loads and Partition Overwrite]] — related
- [[Data Engineering Foundations]] — related
- [[Kafka Log, Partitions and Offsets]] — related (consumer lag, queue or log)
