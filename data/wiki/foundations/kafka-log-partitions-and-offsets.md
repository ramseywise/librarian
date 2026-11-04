---
title: "Kafka Log, Partitions and Offsets"
tags: [foundations, concept]
summary: "A log keeps every record and lets each reader remember its own offset, which gives replay, multiple independent consumers, per-partition ordering and a lag metric that tells you whether a consumer is healthy."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--04-kafka-and-stream-semantics.md
---
# Kafka Log, Partitions and Offsets

A queue hands out a message and forgets it. A log keeps everything and each reader remembers its own position. That one difference gives most of Kafka's properties; its design is described as closer to a database log than a traditional messaging system.

## Mechanism

- A topic is a set of partitions, each an append-only list. A record's position in its partition is its **offset**.
- The producer hashes the key to pick the partition, so equal keys land in one partition and stay in order. Order holds within a partition and not across them. In a toy topic of 3 partitions and 8 records with only 3 distinct keys, partition sizes came out [4, 4, 0]: with few keys, partitions sit empty.
- Reading removes nothing. Two consumer groups read the same partition from different offsets (one from 0, one from 2) without disturbing each other. A new consumer can replay history, a broken consumer can be fixed and rewound, and pointing a new consumer at production only moves its own offset.
- An offset is a log sequence number, so a consumer behaves like a follower of the broker and is cheap: the broker remembers one number per group.
- **Partitions are the unit of scaling.** Within a group each partition has one consumer at a time, so partition count caps parallelism. Changing the count later moves keys to other partitions and breaks per-key ordering across the change.
- Retention is by time or size; a compacted topic keeps at least the last value per key, which suits a changelog. At 150 MB/s a 6 TB disk fills in 11 hours when written flat out, and in practice far longer, so a slow consumer has days or weeks to catch up.

## Queue or log

A log suffers head-of-line blocking: a slow message holds up everything behind it in the partition. Where messages are expensive and order does not matter (a list of jobs) use a queue. Where throughput is high, each message is fast and order matters, use a log. A queue hides its own trap: combining load balancing with redelivery reorders messages.

## Consumer lag

Lag is the distance between the latest offset and the group's committed offset; it is the one number saying whether a consumer is healthy. Recovery depends on headroom:

- Producing 60,000 a minute for a ten-minute consumer outage then consuming 72,000 a minute: peak lag 600,000, drained 49 minutes after restart.
- Consuming only 61,000 (1.7% headroom): lag is still 550,000 an hour later.

Size consumers for catch-up rate, and alert on lag that is growing, not on lag that is merely high (it may be draining).

## Pitfalls

- **Too few partitions, or changing them later.**
- **Auto-commit in a pipeline that matters**: offsets are committed on a timer regardless of finished work ([[Delivery Guarantees and Effectively-Once Processing]]).
- **One idle partition holding a watermark back** ([[Event Time, Watermarks and Late Data]]).

## See Also
- [[Delivery Guarantees and Effectively-Once Processing]] — related
- [[Event Time, Watermarks and Late Data]] — related
- [[Stream Joins Replay and Lambda Architecture]] — related
- [[Data Engineering Foundations]] — related
- [[Kafka Ingest Model, Delivery Semantics and Stream Windows]] — related (ingest settings, windows, batch or stream)
