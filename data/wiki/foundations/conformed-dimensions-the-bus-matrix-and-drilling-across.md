---
title: "Conformed Dimensions, the Bus Matrix and Drilling Across"
tags: [foundations, pattern]
summary: "Joining a finer-grain table or a second fact directly onto a fact multiplies rows and inflates sums with no error; share conformed dimensions, aggregate each fact to them first, then join."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--02-ingest-and-modelling--notes--02-dimensional-modelling.md
---

# Conformed Dimensions, the Bus Matrix and Drilling Across

One star is a report; a warehouse is many stars that can be compared. **Conformed dimensions** are built once and shared, so a zone dimension means the same in trips, driver shifts and vehicle inspections. Plan on a **bus matrix**: business processes down the side, dimensions across the top, a mark where a process uses a dimension. One page shows the integration plan before any pipeline is written.

## Grain violation: joining a finer table

Setup: 1,000,000 trips; 80,000 tolled trips with two toll rows each.

| Query | Fares |
|---|---|
| True total | 11,257,895 |
| Fact left-joined to toll rows | 12,157,075 |
| Tolls rolled up to trip grain first | 11,257,895 (tolls 879,936) |

Revenue rose by 899,180 (8%) because 80,000 trips appear twice. The SQL is valid and reads naturally; the finer table silently multiplied the fact. Fix: roll the finer table up to the fact's grain before joining, or model tolls as a separate fact. A uniqueness test on the primary key after each join is the cheapest protection (see [[SQL Fan-Out and Source Reconciliation]]).

## Fact-to-fact joins

Add a shifts fact (one row per zone, day, shift; two shifts per day) and ask for fares and drivers by zone. Joining the facts directly gave fares 22,466,405 (double the true 11,233,203) and drivers 42,499,888 against a true 314,322, over a hundred times too many, because each shift row repeated once per trip: fan-out in both directions at once.

**Drilling across** means aggregating each fact to the shared dimension keys separately, then joining the results: it returned the true totals exactly. A BI semantic layer does this if the model says which facts and dimensions conform.

## Pitfalls

Fact-to-fact joins; non-conformed "same" dimensions per mart; mixing grains in one table.

## See Also
- [[Dimensional Model Grain and the Four Design Steps]] — prerequisite-for
- [[SQL Fan-Out and Source Reconciliation]] — related
- [[Pandas Merge Validation and Many-to-Many Blow-up]] — related
- [[One Big Table versus Star Schema]] — related (second grain has nowhere to go)
