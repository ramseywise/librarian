---
title: "Conformed Dimensions, the Bus Matrix and Drilling Across"
tags: [data-engineering, ingest-and-modelling, pattern]
summary: "Joining a finer-grain table or a second fact directly onto a fact multiplies rows and inflates sums with no error; share conformed dimensions, aggregate each fact to them first, then join."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--02-ingest-and-modelling--notes--02-dimensional-modelling.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch01-dimensional-modeling-primer.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch03-inventory.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch06-customer-relationship-management.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch07-accounting.md
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

## Kimball and Ross on conformance

From chapters 1, 3, 6 and 7 of *The Data Warehouse Toolkit*; the figures and rules are the authors' guidance.

- **Definition:** a conformed dimension is identical to, or a strict subset of, the most granular version, and agrees on keys, attribute names, definitions and values. A roll-up such as brand must be a strict subset of product with identically labelled shared attributes. Conformed facts share definitions, equations, context and units; facts that cannot be conformed exactly get different names.
- **Effort:** Kimball and Ross estimate that conformed dimensions take about 90 percent of the effort in the early data architecture work. A large enterprise presentation area ends up with 20 or more similar data marts.
- **Bus matrix:** each row is a business process rather than a department, and each column a shared dimension. They call it a design, project-management and communication tool.
- **Build order:** implement first-level (single-source) marts before consolidated ones such as profitability, since ETL effort grows with each source. Isolated independent marts, they say, give irreconcilable views.
- **Dimension authority:** one group builds a conformed dimension once in staging and publishes it to the marts together; the authors say use is a business policy mandated from the top, with a least-common-denominator attribute set if full conformity is unrealistic. A stovepipe mart is retrofitted by cross-reference mapping and re-keying its facts, or rebuilt if its grain is wrong.
- **Units:** store a quantity in both units (shipping cases and scanned units) rather than keeping a conversion factor on the product dimension.
- **Drilling across:** run one SQL pass per mart and outer-join on a common dimension attribute. Chapter 6 adds that two fact tables of different cardinality must not share one dimension join in a single query; the alternatives are separate passes or a consolidated fact table. Chapter 7 says a consolidated fact table sits at the least common denominator of its dimensions and should be built only when the facts share grain, not forced with artificial facts or dimensions.
- **Packaged applications:** conform dimensions even when buying a packaged analytic solution or CRM application, which otherwise becomes a stovepipe mart.

## Limits

- Opinionated practitioner guidance; the extractions note no measurements. The 90 percent figure carries no data.
- Early-2000s text (the extraction infers the 2nd edition, 2002; chapter 1 may be earlier than the 3rd). Examples such as 60,000 products and 100 stores are hypothetical, and modern warehouses are not covered.
- Chapter 3 defers multiple units of measure and heterogeneous products to later chapters, and consolidated marts to other chapters not in this batch.

## See Also
- [[Dimensional Model Grain and the Four Design Steps]] — prerequisite-for
- [[SQL Fan-Out and Source Reconciliation]] — related
- [[Pandas Merge Validation and Many-to-Many Blow-up]] — related
- [[One Big Table versus Star Schema]] — related (second grain has nowhere to go)
- [[Core and Custom Schemas for Heterogeneous Products]] — extends
- [[Transaction, Periodic and Accumulating Snapshot Fact Tables]] — related (the three types share conformed dimensions)
- [[Bridge Tables for Multivalued and Ragged Hierarchy Dimensions]] — related (the same overcounting hazard)
- [[Degenerate, Junk and Role-Playing Dimensions]] — related (role-playing views over the shared date dimension)
