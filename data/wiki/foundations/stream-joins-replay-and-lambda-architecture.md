---
title: "Stream Joins Replay and Lambda Architecture"
tags: [foundations, decision]
summary: "Stream joins depend on cross-stream event order, so a replay can silently change history unless the joined table is versioned; and a stream is worth its cost only if a faster number changes a decision, otherwise a micro-batch or one replayable stream path beats lambda."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--04-kafka-and-stream-semantics.md
---
# Stream Joins Replay and Lambda Architecture

## Join kinds

Windows handle one stream; joins add state, since something must remember one side while waiting for the other.

- **Stream-stream:** keep a window of recent events on both sides (a search matched to the click that followed).
- **Stream-table:** enrich each event from a table. Rather than a database call per record, keep a local copy of the table updated from a change stream.
- **Table-table:** consume two changelogs and maintain a materialised view.

All three share a difficulty: the answer depends on event order across streams, and nothing determines that order.

## Replay with a moving table

Rates changed from 0.08 to 0.10 at minute 50; sales of 100.0 occurred at minutes 10, 40 and 60.

| Join | Total |
|---|---|
| Live, each sale enriched with the table as it stood | 26.0 |
| Replay a month later using the latest rate | 30.0 |
| Replay with the rate version in force at event time | 26.0 |

The local table has moved on, so the same sales and rates give a different answer. Give each rate version an ID and store it on the sale: the join becomes deterministic, the same answer as a Type 2 dimension in a warehouse, at the cost of keeping every version. Stream state must also survive a crash: a remote store, a replicated local copy, periodic snapshots (Flink style), a changelog topic (Kafka Streams style) or replay of a short window.

## Do you need a stream at all

Streaming costs always-on compute and on-call attention, and a micro-batch every few minutes satisfies most dashboards. The test: what decision changes if the number is one second old rather than five minutes old?

## Lambda architecture

A batch path for correctness beside a stream path for speed. Its costs: the same logic maintained in two frameworks, two outputs to merge, and an incremental batch job that reacquires the streaming problems it was meant to avoid. Engines that replay history through the stream path with event-time windows and exactly-once remove the reason for it. Reprocessing is also how a pipeline changes shape safely: build the new view beside the old, move readers over gradually, keep the old until sure.

## Tools

| Tool | What it is | Pick when |
|---|---|---|
| Kafka or Redpanda | The durable log | Several consumers, replay, decoupling |
| Kafka Streams, ksqlDB | Processing as a library or SQL inside Kafka | Kafka-to-Kafka transformations |
| Flink | Stateful processor with event-time windows and checkpoints | Large state, low latency, complex joins |
| Spark Structured Streaming | Micro-batch on Spark | A Spark shop, seconds of latency acceptable |

## Pitfall

Stream-table joins without versions: a replay joins to today's table and silently changes history ([[Event Time, Watermarks and Late Data]]).

## See Also
- [[Event Time, Watermarks and Late Data]] — prerequisite-for
- [[Delivery Guarantees and Effectively-Once Processing]] — related
- [[Kafka Log, Partitions and Offsets]] — prerequisite-for
- [[Backfills, As-Of Dimensions and Past-Dependent Tables]] — related
- [[Slowly Changing Dimensions Types 1, 2 and 3]] — prerequisite-for
