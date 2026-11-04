---
title: "Orchestrator Design Rules and Tool Choice"
tags: [foundations, decision]
summary: "Keep domain logic in a plain package with orchestrator code as thin glue, hand off between tasks through storage, adopt an orchestrator on day 0, and pick the tool the organisation already runs unless starting fresh."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--03-transform-and-orchestrate--notes--02-orchestrate.md
  - data/raw/repos/learn-ai-engineering/data-engineering--03-transform-and-orchestrate--notes--05-dagster-and-airflow.md
---

# Orchestrator Design Rules and Tool Choice

## Design rules that hold across tools
- **Adopt on day 0**, even running locally. An orchestrator forces each pipeline to be a separate unit that hands off only through storage (warehouse, feature store, artifact store), so schedule, API and monitoring-alert triggers later become configuration, not a refactor.
- **Thin glue.** Most tools turn a function into a task under one decorator and a pipeline into a function calling tasks under another. Put domain code in its own package and keep task and pipeline folders as glue; the payoff is that the tool can be swapped or the same logic called from a REST API.
- **Pass paths, not data.** Hand off through storage and pass the path or key; task results and cross-task messages are for small values.
- **Granularity is a design decision**, because each deployed task runs as its own unit, often on its own machine, and what it returns must be serialisable by the tool.
- **Parameters from a file** loaded at run time, so a change of input needs no code change and every run's inputs are on record.
- **Do not run heavy work in the scheduler's process**; start it in the warehouse or on a worker, or one task stalls every pipeline.
- **A second orchestrator is a cost**: two views of what ran, with dependencies between them invisible to both.

## Parameterised, backfillable job shape
A batch scorer from the sources shows four ideas in one flow: the run date defaults to the run's scheduled start, so a late or re-run job scores the period it was scheduled for; output goes to a deterministic partitioned path (type, year, month, run id), so a rerun overwrites the same file and engines can prune by month; the model version is in the path and a column, so every prediction traces to a run; and the task is the retry unit. A backfill is then just the flow called over a date range. A pipeline that reads "today" from the clock cannot be backfilled.

## Choosing
| If | Use |
|---|---|
| Mostly dbt plus Python and lineage matters | Dagster ([[Dagster Assets vs Airflow Tasks]]) |
| The organisation already runs Airflow | Airflow; do not add a second |
| A Python team wants least ceremony for scheduled functions | Prefect |
| Non-Python teams scheduling across many systems | Airflow or a YAML-driven tool |

The tools are equivalent in capability for ordinary pipelines. Course cohorts used different ones (Airflow, Prefect, Mage, Kestra) because each re-recorded the module with a new tool; the concepts carry over and any one API is about a week's work. One team that tried Airflow, Prefect, Metaflow and Dagster chose a stack-based tool for keeping orchestrator, artifact store and container registry configuration outside the code; it gave no benchmark, so treat it as a preference. Prefect 3 dropped the Prefect 2 deployment API, though the flow and task decorators carried over.

## Pitfalls
- Reading the clock in a task; retrying non-idempotent work; a sensor with no timeout.
- Business logic inside decorated functions, which ties it to one tool.
- Treating a green run as correct data.

## See Also
- [[Orchestrator Core Loop, Logical Dates and Retries]] — prerequisite-for
- [[Dagster Assets vs Airflow Tasks]] — extends
- [[Idempotent Batch Loads and Partition Overwrite]] — related
