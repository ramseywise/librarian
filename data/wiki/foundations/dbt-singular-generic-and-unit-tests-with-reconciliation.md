---
title: "dbt Singular, Generic and Unit Tests with Reconciliation"
tags: [foundations, pattern]
summary: "Column tests cannot see a join that fans out; a reconciliation test of fact against source plus a unique test on every joined model's grain catches it, and unit tests with mocked rows guard logic that today's data does not exercise."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--03-transform-and-orchestrate--notes--03-dbt-tests-snapshots-incremental.md
---

# dbt Singular, Generic and Unit Tests with Reconciliation

The built-in tests look at one column at a time; most real bugs are relationships between tables. A test is any `select` returning failing records, so any SQL assertion can be one.

## Test kinds
- **Singular**: a SQL file under the tests folder, one assertion.
- **Generic**: the same query with parameters, defined once as a test macro and attached to columns in YAML (for example a positivity test, or a range test taking low and high).
- **Unit** (dbt 1.8 and later): mock a model's inputs with a few rows and compare output with the expected rows; `dbt build` runs them before building the model.

## Reconciliation: the most useful test
Assert that the fact still adds up to its source on row count and sum. Setup: a source of 1,000 trips and 8 zones; the source then sent a second, perfectly valid row for one zone. Every trip in that zone appeared twice, the fact went from 1,000 to 1,125 rows and revenue from 24,870 to 27,980, a 12.5 percent overstatement small enough to be believed, and no value-level column test noticed.

The reconciliation says the numbers are wrong; a `unique` test on the dimension key points at the cause. Counts differ by what each query counts: the fact's unique test reported 125 failing (one per duplicated trip) and the dimension's reported 1 (the one repeated zone). Test the grain of every model that joins, on its key, at error severity; it is the cheapest test relative to what it catches. A composite key uses a unique-combination test from the utility package.

The same reconciliation catches a watermark that lost a late row ([[dbt Incremental Models: Watermarks, Lookback and Strategies]]) and an inner join that dropped orphans ([[Staging Dedupe Keys and Fact Join Row Loss]]).

## Unit tests are for logic
Data tests check the data you have; they cannot say whether logic is right for data you do not have yet. A fare-band model with a boundary at exactly 10 dollars may never see that value. A unit test mocking rows at 9.99, 10.00 and 30.00 caught a change from `<` to `<=` before the model built, naming the row and column, and the model was skipped.
| | Data test | Unit test |
|---|---|---|
| Checks | today's data | logic on rows you wrote |
| Runs | after the model builds | before, against mocks |
| Catches | bad sources, broken joins, drift | wrong boundaries, wrong CASE arms, regressions |
| Write for | every model | models with real logic, not renames |
| Run in | every environment | CI and dev |

A range test encodes an assumption about the data and goes stale when the data legitimately changes.

## See Also
- [[dbt Build Test Semantics, Severity and Source Freshness]] — prerequisite-for
- [[SQL Fan-Out and Source Reconciliation]] — related
- [[Staging Dedupe Keys and Fact Join Row Loss]] — related
- [[dbt Snapshots: History as Samples]] — related
