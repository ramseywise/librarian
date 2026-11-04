---
title: "dbt Layers, Materialisations and the ref Graph"
tags: [foundations, concept]
summary: "dbt compiles templated SELECTs into warehouse SQL and runs them in dependency order; staging, core and mart layers each read only the one before, so a wrong number traces to one line in one file."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--03-transform-and-orchestrate--notes--01-transform.md
---

# dbt Layers, Materialisations and the ref Graph

## ELT is why a transform tool exists
In ETL the transform runs before load in a separate engine and raw data is often discarded. In ELT the transform runs inside the warehouse after load and the raw layer stays as the replay point. A bug in a transform is then cheap: the input still exists and the output can be rebuilt. dbt is the "T": it moves no data, it compiles Jinja-templated `SELECT` statements into DDL and DML and runs them in the warehouse. Only the adapter changes between warehouses, and the SQL mostly does not.

## Layers
| Layer | Job | Usual materialisation |
|---|---|---|
| Source | Declared, not built; points at raw tables and starts lineage | n/a |
| Staging | One model per source table: rename, cast, dedupe, nothing else | view |
| Core | Facts and dimensions; joins across sources | table |
| Mart | Aggregates for one consumer | table |

The rule that pays for the ceremony: each layer reads only the one before it, so business logic has one home and a disputed number has one place to look. An intermediate layer for logic shared by several marts can wait until the same CTE appears twice. Materialisation is set per folder in the project file, which keeps model files free of boilerplate.

## Materialisations
| Kind | Becomes | Build cost | Read cost | Use for |
|---|---|---|---|---|
| view | stored query | almost none | whole query on every read | staging, small or rarely read |
| table | rebuilt table | full rebuild each run | cheap | core and marts until the rebuild hurts |
| incremental | table with rows merged or appended | new rows only | cheap | large facts (see [[dbt Incremental Models: Watermarks, Lookback and Strategies]]) |
| ephemeral | inlined CTE, no object | none | paid by the selector | shared logic kept out of the catalogue |

## ref() builds the graph
Nobody writes the build order. dbt parses every `ref` and `source` call into a graph (the manifest's parent map is plain JSON, which orchestrator integrations read) and walks it topologically. The model says what to compute; the wiring decides where input comes from and output goes, so one model runs unchanged against dev and prod. Compiled output is ordinary SQL that can be pasted into a console when debugging.

Selectors use the graph: `+fact` is the model and everything upstream, `stg+` is the model and everything downstream. `dbt build` runs seed, run, test and snapshot in DAG order and is the command to schedule, because a failing test skips its downstream models (see [[dbt Build Test Semantics, Severity and Source Freshness]]).

## Macros and packages
A macro is a Jinja function returning SQL. Write one when the same expression appears in two models or must differ by adapter, not to shorten SQL: the reader must then open a second file to know what the model does. Packages supply surrogate-key and generic-test macros; pin their versions, since an unpinned package can change a compiled query with no commit in the repo.

## Practical rules
- A union of staging models needs identical column lists; write the models to the same column order.
- Dashboards read marts, never staging or core; otherwise the metric definition moves into the BI tool and two dashboards disagree.
- First reconciliation on any new model: output counts equal raw counts minus what was deliberately removed. In a synthetic setup with 100,500 green and 200,500 yellow raw rows, 500 of each duplicated by a retried load, 300,000 distinct trips survived.
- Business logic in staging hides it from reviewers who assume staging is mechanical.

## See Also
- [[Staging Dedupe Keys and Fact Join Row Loss]] — extends
- [[dbt Build Test Semantics, Severity and Source Freshness]] — extends
- [[Orchestrator Core Loop, Logical Dates and Retries]] — related (the orchestrator runs `dbt build` as one task)
- [[Dagster Assets vs Airflow Tasks]] — related (expands the dbt graph into the orchestrator)
- [[SQL Join Patterns]] — prerequisite-for
