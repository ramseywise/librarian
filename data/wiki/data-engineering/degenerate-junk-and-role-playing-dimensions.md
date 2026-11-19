---
title: "Degenerate, Junk and Role-Playing Dimensions"
tags: [data-engineering, ingest-and-modelling, concept]
summary: "Three housekeeping dimensions in Kimball and Ross: a transaction number kept in the fact with no table, a junk table for low-cardinality flags, and one physical date table shown as several labelled views."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch02-retail-sales.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch04-procurement.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch05-order-management.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch07-accounting.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch08-human-resources-management.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch09-financial-services.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch10-telecommunications-utilities.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch11-transportation.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch13-health-care.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch14-electronic-commerce.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch15-insurance.md
---

# Degenerate, Junk and Role-Playing Dimensions

Kimball and Ross list these among the candidates to check when a draft schema has too few dimensions (their dimension triage, alongside causal, multiple dates, status and audit). Each can be added later without changing the grain.

## Degenerate dimension

An operational identifier kept as a column of the fact and given no table of its own: the point-of-sale transaction number, order number, purchase-order or check number, journal entry number, invoice or bill number. The authors advise this over building a header dimension (order number rather than an order-header table). They treat a dimension that nearly matches the fact table in row count as a warning sign. Where numbers repeat or collide between stores, a surrogate key replaces them.

## Junk dimension

A grouping of low-cardinality flags and indicators, so the fact table does not carry a column for each. The chapter's sizing arithmetic:

- 10 two-value indicators: at most 1,024 rows (2^10).
- 5 indicators of 3 values: 243 rows, which the chapter says favours a single junk dimension.
- 5 uncorrelated indicators of 100 values each: 100 million possible combinations; for these the chapter proposes separate dimensions.

When the theoretical combinations are too many, rows are built at extract time from the combinations that occur.

## Role-playing dimension

The same dimension appears several times in one fact table (order date, requested ship date). One physical table is kept, and each role is shown to the access tools as a separately labelled view with relabelled columns, for example `ORDER_DATE` and `REQ_SHIP_DATE` over the date table. The retail chapter does the same for a store's first-open date. The telecom chapter clones a shared location outrigger per role with distinguishable column names, and the HR chapter's survey schema plays an employee as both responder and reviewed.

## Audit dimension

One audit foreign key on the fact can point to a dimension of lineage and quality metadata: the source system, the extract software and allocation logic versions, why a value is null, whether it was altered after load, and outlier flags, all as readable text.

## Further cases in chapters 11 to 15

- **Role-playing as views (ch11, ch13, ch15):** date, time and airport roles are separate logical views on one physical table. Setup: the billing snapshot has seven date keys, so one view per role with relabelled columns, not seven joins to one date table. Insurance does the same for transaction date and effective date, with unique column names.
- **Superdimension (ch11):** a dimension that merges the attributes of several small ones, as a junk dimension does. Setup: class purchased, class flown and an upgrade indicator have three rows each and are merged into one class-of-service dimension, every pairing of purchased and flown class (9 rows). The authors say to combine only when row counts are tiny or attributes depend on the combination.
- **Cargo (ch11):** the bill-of-lading number is a degenerate dimension, and consignor, shipper, transporters and consolidators are roles of one business-entity dimension.
- **Degenerate keys (ch14, ch15):** the session ID on the clickstream page-event fact ([[Clickstream Session and Page-Event Fact Tables]]), and the policy number when the header attributes live in other dimensions.
- **Audit key (ch15):** each fact row carries a key pointing to when it was extracted, its source table and the software version.

## Limits

- Guidance from case studies; the extraction notes no measurements, and the sizing figures are worked arithmetic, not data.
- The text is early-2000s (the extraction infers the 2nd edition, 2002) and does not cover modern warehouse engines.
- Detail on junk-dimension loading and the multi-currency and unit-of-measure handling that shares chapter 5 is not covered here.
- Chapter 11's text says the class-of-service dimension has three purchased plus three flown rows, while its figure and the 3 by 3 product give 9; this page uses 9. Chapters 11 to 15 are illustrative case guidance with no measurements.

## See Also
- [[Dimensional Model Grain and the Four Design Steps]] — prerequisite-for
- [[Conformed Dimensions, the Bus Matrix and Drilling Across]] — related (the date dimension shared by every role)
- [[Transaction, Periodic and Accumulating Snapshot Fact Tables]] — related
- [[Clickstream Session and Page-Event Fact Tables]] — instance-of
