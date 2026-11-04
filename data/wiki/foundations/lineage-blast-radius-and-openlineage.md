---
title: "Lineage for Blast Radius and Rebuild Lists"
tags: [foundations, concept]
summary: "Lineage is a graph of which job read and wrote which dataset; walking it downstream gives the blast radius of a bad table, upstream gives suspects, and joined to run history it gives the exact runs to redo."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--02-monitors-and-lineage.md
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--06-dataops.md
---

# Lineage for Blast Radius and Rebuild Lists

Once a table is known to be wrong, the next question is what else is. Code dependencies are found by compilers; data dependencies have no equivalent, so long chains build up unseen. Lineage is the missing tool. dbt's `ref()` gives it inside one project but stops at the tool's edge, and the model consuming the output is exactly what an incident needs.

## OpenLineage model

An open standard with three things: a **Dataset**, a **Job** and a **Run** (one execution). Jobs emit run events as they change state: `START`, then terminal `COMPLETE`, `FAIL` or `ABORT`. A backend weaves the events into one graph; extra information travels as facets. A `nominalTime` run facet records which day of data the run was for, separate from when it ran, the logical-date idea again. Integrations exist for Airflow, Spark and dbt.

## Three graph walks

On a six-job synthetic pipeline over eight days (96 events), once events are plain data the incident questions are short walks:

- **Blast radius:** five datasets sat downstream of the raw table, including a model's predictions the dashboard owner may not know exist.
- **Root-cause candidates:** walking up from a broken dashboard gives a short, finite suspect list; a reference table on it shows what can be ruled out.
- **Rebuild list:** joining the graph with run history gave 20 completed runs to redo from the onset date. That list feeds a backfill (see [[Idempotent Backfills and Dated Corrections]]). A failed run may have written partial output, so consider including it.

## Limits

Table-level lineage says a mart read a staging table, not whether it used the faulty column. Column lineage (an OpenLineage dataset facet) removes that from the rebuild list but is more work to collect. Declaring a dashboard as a dbt exposure with an owner extends lineage to the last hop: `state:modified+` then lists the dashboard as affected. Lineage inside one tool only is a pitfall.

## See Also
- [[Data Incident Playbook: Contain Before Diagnosing]] — prerequisite-for
- [[Expand, Migrate, Contract]] — related (lineage says who still reads the old column)
- [[Slim CI for dbt Models: state:modified and defer]] — related
