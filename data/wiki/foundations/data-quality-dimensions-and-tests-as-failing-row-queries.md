---
title: "Data Quality Dimensions and Tests as Failing-Row Queries"
tags: [foundations, concept]
summary: "Quality is six separate questions, each needing more context than the last; a test is a query that should return no rows, with a stated tolerance, and row-level tests are blind to anything that is only visible against time."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--05-quality-and-observability--notes--01-quality-dimensions-and-tests.md
---

# Data Quality Dimensions and Tests as Failing-Row Queries

A pipeline fails when code fails, and nothing in its code reads what the data says. A report can come out 18% too high while every job is green. Code dependencies are checked by compilers; data dependencies have no equivalent, so the checks have to be written.

## Six dimensions

The research literature names three as most used: completeness, consistency and accuracy. Practitioners split them further because each split needs a different check. Going down the table, each check needs more context than the last, so the cheap ones are the top rows and the most valuable (accuracy) is the least tested.

| Dimension | Question | Needs |
|---|---|---|
| Completeness | Is the value there (where the attribute applies)? | The table alone |
| Uniqueness | Is each thing recorded once? | The table alone |
| Validity | Is the value allowed? | A rule |
| Consistency | Do facts agree across columns or tables? | Another column or table |
| Timeliness | Did it arrive when promised? | Time of arrival |
| Accuracy | Is it true? | An outside source (see [[Reconciliation Against a Producer Control Total]]) |

Accuracy has a syntactic and a semantic form: a colour of "blue" is syntactically fine even if the product is red.

## A test is a query that returns bad rows

Each dimension becomes a test in one form: a `SELECT` that should return nothing. If it returns rows, the rows are the debugging evidence. dbt defines data tests this way; Deequ compiles constraints to aggregation queries so a check costs one scan. Generic dbt tests are `unique`, `not_null`, `accepted_values`, `relationships`; anything else is a singular test, a SQL file returning failing rows. A `store_failures` option keeps the rows, and a model contract enforces names and types at build time without looking at values.

## State the tolerance

A hard `not_null` on a column that is normally about 0.2% null failed on 86 of 87 normal days in a synthetic feed, and a test that fails daily gets muted. Fix the threshold from the metric's normal range with a margin (1% against 0.2% there), not from a round number. Great Expectations has `mostly=0.99`; dbt thresholds count rows rather than shares, so a share needs a singular test. Setting `mostly=0.75` let a 19.9% null day pass.

Two routes to thresholds: profile real data and adjust with domain knowledge, or write expectations first. Profiling first can encode an existing bug as the rule; writing first fires on harmless facts. Loose limits that encode physical truth outlast tight ones.

## What row-level tests cannot see

On a synthetic quarter with five planted faults, rule tests, a GX suite and dbt caught two (null spike, duplicate keys) and raised no false alarms on the other 87 days. They missed:

- a dropped day (no rows to test),
- a late partition,
- a unit change (kilometres for miles). A median-distance expectation of 1.5 to 4.0 passed because 2.4 miles becomes about 3.9 kilometres, just inside a generous limit.

A static limit wide enough to survive normal variation is often wide enough for a real shift. These three are questions about a batch against time, which is the job of monitors (see [[Freshness Alerts Need a Date Spine]], [[Same-Weekday Median and MAD Volume Monitor]], [[Distribution Monitors Need an Effect Size and a Fixed Reference]]).

## Pitfalls

- Testing what is easy rather than what matters; start from numbers people act on.
- Testing only the last table; test sources, staging and joins that change row counts.
- Green means only that no written rule failed.
- A check on zero rows usually passes; add an explicit row-count test per table written.
- Tests with no owner are an expensive log line.
- Writing one rule in three tools lets them drift; pick one home per rule (dbt tests if the model is in dbt, GX or plain SQL for files and frames).
- Block versus warn is a per-table decision: block where wrong data costs more than late data (finance, training sets).

## See Also
- [[Write-Audit-Publish and Atomic Visibility]] — extends
- [[Reconciliation Against a Producer Control Total]] — extends
- [[Rerunnable Cleaning Loader with Assertions]] — related (the analyst's by-hand version)
- [[Data Incident Playbook: Contain Before Diagnosing]] — extends
