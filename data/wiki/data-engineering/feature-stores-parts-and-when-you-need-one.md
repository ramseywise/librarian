---
title: "Feature Stores: Parts and When You Need One"
tags: [data-engineering, ml-platform, concept]
summary: "A feature store is a point-in-time join with a registry, an offline history store, an online latest-value store and a materialisation job around it; most teams with one model need only the join and a shared function."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--01-feature-stores.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch15-quality-acceptance-testing.md
  - data/raw/papers/2026-11-08-ml-engineering-in-action-ch16-production-infrastructure.md
---

# Feature Stores: Parts and When You Need One

A feature store is the [[Point-in-Time As-Of Join for Features]] plus a catalogue and a low-latency copy. Know which part you need before adopting one.

## Four parts

- **Registry:** definitions (name, entity, type, owner, time to live). Makes a feature findable and reusable.
- **Offline store:** full history, usually in the warehouse or lake; answers point-in-time joins for training.
- **Online store:** latest value per key (Redis, DynamoDB, SQLite); millisecond lookups for the prediction service.
- **Materialisation:** the job copying offline to online. It is a pipeline with lateness and failure modes of its own; when it dies, the service keeps serving yesterday's numbers.

An MLOps architecture guide describes the same pairing as an optional component at its level 1: a batch API for training and a low-latency API for serving, whose job includes avoiding [[Train-Serving Skew and the Shared Feature Function]]. Practitioners also value it for debugging: retrieving the historical version of a feature when a prediction went wrong makes it a versioning tool as much as a serving tool.

## Behaviour to verify on your own store

In a local run (Parquet offline, SQLite online, Feast 0.67), historical retrieval matched a hand-written DuckDB as-of join on every timestamp both returned, but dropped a pre-history row that DuckDB kept with nulls. Materialisation then served values dated February 2024 although the view had a three-hour TTL and the run clock read 2026: the TTL shaped history and did not stop stale online reads. Treat online freshness as something you monitor (freshness checks), not something the store guarantees.

## Do you need one?

| Situation | Use |
|---|---|
| One model, batch scoring | A dbt model and an as-of join; no online store |
| One model, online, features in the request | A shared feature function |
| One model, online, features computed elsewhere | A key-value cache filled by a pipeline; you own sync and skew checks |
| Several models or teams sharing definitions | A feature store; registry and reuse are the point |
| Stream features used online and in training | A store with stream ingestion; backfill and online consistency are hard to build |

Evaluation criteria: sync to the online store, accessibility, batch and streaming ingestion, access control (features often derive from personal data), merging just-in-time data with stored features, lineage. Adopting a store for one model means running a registry, an online database and a sync job to solve what one SQL query solves.

## Wilson on feature stores

Wilson (*Machine Learning Engineering in Action*, chapters 15 and 16) advises defining each feature once in a store with ACID storage and a low-latency serving layer, using a denormalised key-value layout that consumers can only read. He advises that a change to a key metric's definition goes through a change process with every producing and consuming group and then syncs to the store by ETL, and that teams avoid private data silos. In his Databricks example registering the model through the store's API bundles the feature engineering with the model artifact, and batch scoring then calls just `score_batch`. His evaluation list matches the criteria above. These are practitioner recommendations; his code is Databricks-, Spark- and MLflow-specific and he warns that feature store APIs may change significantly.

## See Also
- [[Point-in-Time As-Of Join for Features]] — prerequisite-for
- [[Train-Serving Skew and the Shared Feature Function]] — prerequisite-for
- [[Data Engineering Foundations]] — related
- [[ML Stage Layering with Typed Contracts]] — related
