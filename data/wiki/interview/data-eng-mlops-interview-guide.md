---
title: Data Engineering and MLOps Interview Study Guide
tags: [interview, foundations, reference]
summary: Exam-prep reference for pipeline and model-to-production questions — idempotency and backfills as the words interviewers listen for, warehouse/batch/streaming trade-offs, the MLOps maturity ladder, deployment and drift monitoring, and the LLM-era mapping (embedding pipelines are ETL, prompt versioning is a model registry, eval-in-CI is monitoring).
updated: 2026-10-17
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--guides--8-data-eng-mlops--interview-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--8-data-eng-mlops--00-overview.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--data-engineering-mlops.md
---

# Data Engineering and MLOps Interview Study Guide

Tested directly in ML-engineer loops and as the substrate of every system-design answer. This
is the most "just do the course" pillar — the checklist below maps one-to-one onto a standard
module sequence (containers → orchestration → warehouse → analytics engineering → batch →
streaming; then tracking → pipelines → deployment → monitoring → practices). Background in
[[Data Engineering Foundations]].

## Data engineering checklist

- **Containers and IaC** — reproducible environments; infra as reviewable code.
- **Orchestration** — DAGs, **backfills**, retries with backoff, sensor vs schedule triggers.
  **Idempotency is the word interviewers listen for:** reruns must not double-write (upserts,
  partition overwrites, dedup keys).
- **Warehouse** — columnar storage, partitioning and clustering, star schema vs wide tables,
  slowly changing dimensions; OLTP vs OLAP in one breath.
- **Analytics engineering** — SQL transforms as versioned, tested, documented models;
  staging → marts layering; unique/not-null/referential tests in CI.
- **Batch** — partitions, shuffles (the expensive part), skew; **single-box DuckDB/Polars beats
  a cluster at most interview-scale data.**
- **Streaming** — topics, partitions, consumer groups, at-least-once vs exactly-once,
  watermarks and late data. Ask "do we actually need streaming?" before designing it.
- Parquet over CSV for anything processed; lakehouse table formats give ACID over object
  storage; contracts at ingest, lineage, PII classification.

## MLOps checklist

- **Maturity ladder** — notebook → scripted and tracked → automated pipeline → CI/CD-gated →
  monitored/self-healing. Place every system you describe on it.
- **Tracking and registry** — params, metrics, artifacts; stage transitions with rollback.
- **Training as a DAG** — validate corpus → featurise → train → evaluate against baseline →
  register on pass.
- **Deployment** — batch scoring vs online REST vs streaming consumer; warm the model at
  startup ([[Embedder Warmup]] is the same pattern); shadow → canary → full rollout.
- **Monitoring** — service metrics + data drift + concept drift + quality against delayed
  labels, with thresholds tied to retrain triggers.
- **Practices** — tests for data code, pre-commit, CI running the eval suite as a merge gate.

## LLM-era bridges — say the mapping out loud

Embedding pipelines are ETL (incremental refresh, fingerprint dedup, index rebuild plans).
Vector DB operations are snapshotting, reindexing, memory. **Prompt and config versioning is
model-registry thinking applied to prompts. Eval suites in CI/CD are the MLOps monitoring story
in new clothes.** Stating this mapping is the advantage of an AI engineer with MLOps roots.

## Question bank (answer sketches)

- *"Design a daily pipeline."* — idempotent, late-data-tolerant ingest → contract validation →
  layered, tested transforms → mart or feature store → monitoring and a backfill story; name the
  failure handling at each hop.
- *"Batch or streaming?"* — freshness need, cost, exactly-once complexity; batch until a product
  need forces streaming.
- *"Dashboard number is wrong."* — lineage walk, cheapest layer first: source freshness → ingest
  dedup → join fan-out → metric-definition drift.
- *"Feature store — when?"* — only for online/offline consistency (train/serve skew) or
  cross-team feature reuse; otherwise a well-tested mart suffices.

## See Also
- [[Data Engineering Foundations]] — prerequisite-for
- [[ML Foundations Interview Study Guide]] — prerequisite-for (hygiene before production)
- [[Experiment Tracking Schemas]] — instance-of (tracking applied to an LLM system)
- [[Evals and Observability Interview Study Guide]] — complements (eval-as-merge-gate)
- [[System Design Interview Study Guide]] — complements (pipelines are the substrate)
