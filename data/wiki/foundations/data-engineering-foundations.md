---
title: Data Engineering Foundations
tags: [foundations, concept]
summary: "The six stages of data engineering as a pipeline discipline — ingest, transform, orchestrate, warehouse, monitor, feature-serve — where each stage's job is to prepare data for the next, plus the modern-stack tools (DuckDB, Polars, Iceberg, Dagster) missing from Zoomcamp-era material."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--CURRICULUM.md
  - data/raw/repos/learn-ai-engineering/data-engineering--README.md
  - data/raw/claude-docs/learn-ai-engineering/docs/research/2026-07-21_data-engineering_inventory.md
---

# Data Engineering Foundations

Data engineering is a **pipeline discipline**: the stages are not a menu of topics but a
sequence in which each stage's output is the next stage's input. That framing is the load
-bearing part — it means a weakness at stage *n* cannot be compensated for at stage *n+1*,
only inherited.

## The six foundations

| # | Foundation | What it covers |
|---|---|---|
| 1 | **Ingest** | Pull from APIs and streams; incremental loading; `dlt` pipelines; Kafka |
| 2 | **Transform** | Layered modelling (raw → staging → mart); dbt; SQL transformation patterns |
| 3 | **Orchestrate** | DAG authoring; scheduling; backfill; retry logic |
| 4 | **Warehouse / store** | Warehouse internals; partitioning and clustering; Spark batch; columnar storage |
| 5 | **Monitor** | Pipeline observability; data quality checks; drift monitoring |
| 6 | **Feature-serve** | Feature engineering for ML; experiment tracking; model registry; deployment |

Two structural observations worth carrying:

**The raw → staging → mart layering at stage 2 is the same idea as this wiki's
`data/raw/` → compiled `data/wiki/` split** — an immutable landing zone, a normalising
middle, and a consumer-facing output shaped for queries rather than for fidelity. The
reason both converge on three layers is that mixing ingestion fidelity with query
convenience makes it impossible to recompute the second when the first is discovered to
be wrong. See [[Karpathy LLM Wiki Pattern]].

**Stages 5 and 6 are where DE meets ML** and where the discipline stops being about moving
bytes. Monitoring at stage 5 covers *data* quality and *model* drift with the same
tooling, because from the pipeline's point of view a distribution shift and a broken
upstream feed are the same class of event: the data stopped looking like it used to. This
is the pipeline-side counterpart to agent observability — see
[[Observability and Runtime Patterns]].

### Per-stage practice and the question interviewers probe

| Stage | Practices that define it | What interviewers probe |
|---|---|---|
| Ingest | Idempotency (upserts, dedup keys), partitioning, freshness SLAs, CDC for operational sources | *"Idempotency is the word interviewers listen for"* |
| Transform | SQL-first, versioned, tested models; Kimball modelling; all transforms in source control with CI tests | Layering (staging → core → marts) |
| Orchestrate | Sensor triggers, backoff retries, task-state observability, scaling idle compute down | Backfill design, idempotent reruns |
| Warehouse | Star schema, slowly changing dimensions (SCD), partitioning, ACID via lakehouse table formats | Partitioning strategy, cost per query |
| Monitor | Expectations at ingest, lineage, PII classification, ML drift (input, concept, feedback-loop latency) | The monitoring hierarchy: SLO → alert → retrain trigger |
| Feature-serve | Offline + online store, feature-code lineage, train/serve consistency; embeddings as features | *When* to adopt a feature store: only when features are reused across teams **and** train/serve skew already exists |

The feature-store row works as an adoption test, not just a description. A feature store
pays for itself only when both conditions hold. Adopting one before that adds
infrastructure without a problem for it to solve. The source also notes that the toolset
grew from three core tools (Hadoop, Spark, Kafka) to roughly thirty. That growth is the
reason the stages are defined by responsibility and not by tool.

## Orchestration is a stage, not a tool

The material uses Mage in two places and Prefect in a third, and names this an artefact of
course versions rather than a design choice — the tools are equivalent in capability.
The generalisable point is that **stage 3 is defined by its responsibilities** (DAG
authoring, scheduling, backfill, retry logic), and orchestrators are interchangeable to
the extent they cover those four. Backfill and retry are the two that separate an
orchestrator from a cron job, and they are the two most often discovered to be missing
after the first production incident.

Retry logic here is the same design problem as agent retry, at a different layer — a retry
that re-runs a non-idempotent transform corrupts rather than recovers. See
[[Agent Retry Taxonomy]] and [[Webhook Handler Idempotency]].

## Modern-stack gaps

Zoomcamp-era material predates several tools now standard. Named in the source as future
additions rather than covered content:

| Tool | Displaces / adds |
|---|---|
| **DuckDB** | In-process OLAP; largely replaces Spark for single-node analytics |
| **Polars** | Rust-performance DataFrames; preferred over pandas at scale locally |
| **Delta Lake / Apache Iceberg** | Open table formats for lakehouse architecture |
| **dlt** | Python-native ingestion; present but under-covered |
| **Dagster** | Asset-first orchestration model |

The through-line in the first two is that **single-node capacity grew faster than the
average dataset**, so a distributed engine is now often overhead rather than leverage. The
Dagster entry is the substantive one: an asset-first model inverts the orchestrator's unit
of reasoning from *tasks that ran* to *data that should exist*, which changes what backfill
means — you rebuild an asset, not re-run a job.

## Prerequisites and what follows

Python fundamentals and SQL are assumed — concretely, Python modules 01–03 and SQL modules
01–09 of the curriculum's programming subject; Docker is taught from scratch in the source
material. The typical progressions after these foundations are MLOps depth (stages 5–6),
data science, or AI engineering — where **DE pipelines become the data layer** underneath
the application. That last progression is why this page sits in a wiki about agents: an
agent's retrieval corpus is a pipeline output, and corpus quality is the first eval gate.
See [[RAG Eval Gate Contract]].

## See Also
- [[AI Engineering Curriculum Structure]] — part-of (where this pillar sits in the two-wave corpus)
- [[Data Pipeline Pattern Selection]] — complements (how data *arrives* — batch, event-driven, streaming — orthogonal to these six stages)
- [[Data Science Curriculum Layers]] — alternative-to (the sibling branch after shared analytics foundations)
- [[Observability and Runtime Patterns]] — instance-of (stage 5 monitoring, applied to agent runtimes)
- [[RAG Eval Gate Contract]] — prerequisite-for (corpus quality as the first gate, fed by these pipelines)
- [[Agent Retry Taxonomy]] — complements (retry semantics as a cross-layer design problem)
- [[Data Clusters by Writer and Trust]] — extends (cluster tables by who writes them and how much you trust it)
- [[Change the Channel, Not the Count]] — extends (source portfolio and rights as pipeline inputs)
- [[learn-ai-engineering Project]] — extends (the curriculum repo this subject belongs to)
