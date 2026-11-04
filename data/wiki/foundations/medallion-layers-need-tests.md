---
title: "Medallion Layers Need Tests"
tags: [foundations, pattern]
summary: "Bronze, silver and gold layers organise where problems get fixed but detect nothing; filters between layers drop rows silently unless a test counts them."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--03-lakehouse-vs-warehouse.md
---
# Medallion Layers Need Tests

Lakehouse teams usually organise tables in layers: **bronze** holds raw data as received (append-only), **silver** holds cleaned and conformed data, **gold** holds business-level aggregates for one question. The idea is older than the name: keep raw data so you can reprocess, and let each layer depend only on the previous one.

## What the layers hide

A five-row bronze table held a duplicate trip, a negative fare and a missing fare. The silver step selected distinct rows with `fare > 0` and a typed date, leaving 2 rows; gold held 1 aggregate row (2 trips, 20.5 revenue). The filter silently dropped the negative-fare trip and the null-fare trip, and nobody is told unless a test counts them. Layers say where a fix belongs; they do not notice anything. Silver can be wrong with perfect naming.

## What to add

- Count rows in and out of each stage, and assert that the dropped count is expected.
- Keep bronze untouched so any silver rule can be changed and replayed.
- State expectations as tests that fail loudly and early, the same principle as cost guards in [[Materialise or Query and Cost Tests]].

The layering is a convention with no enforcement; the lakehouse metadata layer is the natural place to attach quality and governance checks, but a schema check alone catches a type mismatch, not a wrong value.

## See Also
- [[Lakehouse vs Warehouse Decision]] — related
- [[Table Format as a Commit Log over Parquet]] — related
- [[Rerunnable Cleaning Loader with Assertions]] — related
