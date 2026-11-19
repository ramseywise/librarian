---
title: "Minidimensions for Rapidly Changing Monster Dimensions"
tags: [data-engineering, ingest-and-modelling, pattern]
summary: "Kimball and Ross split the volatile or browsed attributes of a huge customer, account or service-line dimension into banded minidimensions keyed in the fact table, so the big dimension is not duplicated by every change."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch06-customer-relationship-management.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch09-financial-services.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch10-telecommunications-utilities.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch04-procurement.md
---

# Minidimensions for Rapidly Changing Monster Dimensions

Type 2 history ([[Slowly Changing Dimensions Types 1, 2 and 3]]) adds a row per change. Chapter 6 of Kimball and Ross says type 2 is still the usual technique for customer dimensions under 100,000 rows. Beyond that it describes the rapidly changing monster dimension, a customer table of millions of rows with frequent attribute changes. It reports (unnamed sources) monster customer dimensions over 100 million rows and one direct marketer keeping over 3,000 attributes per customer. For these the authors advise avoiding type 2 on the big table and building a **minidimension**.

## Mechanism

- Move the frequently analysed or frequently changing attributes into a separate dimension holding one row for each distinct combination of banded values. Continuous attributes (income, purchases) become ranges; raw values stay in the fact table when users need them.
- Put both the customer key and the minidimension key in the fact table. The fact row then records which profile applied, and the customer row is not duplicated. Setup: a monthly periodic snapshot where one customer moves from minidimension key 2 to 18 on a birthday.
- If the latest minidimension key is also stored on the customer row, treat that column as type 1 and label it as current.
- Size cap: 5 attributes of 10 values each gives 100,000 rows, a figure the authors give as a sensible ceiling. Split correlated clumps into several minidimensions (demographics apart from purchase and credit scores), never one per attribute.

## Where the book applies it

- **Bank accounts:** the master account dimension of a large bank may approach 10 million members, which the authors say makes type 2 unworkable; product, branch, household and volatile attributes move out, and credit-bureau, demographic and score minidimensions are keyed in the monthly snapshot. Value bands can be reported through a band definition table (a group, a sort order, a range name and lower and upper bounds) that the fact joins to with range conditions. Setup: five balance bands; one sample report lists 45,678 accounts in the lowest band (0 to 1,000) worth $10,222,543 in total, and reads over 90,000 balances. Discrete values are also stored as facts for mining and band checks.
- **Variable-width customers:** setup: 10 million contacts (9 million of them prospects) at 1,000 bytes a row make a 10 GB dimension, 90 percent of it empty trailing columns. A base dimension plus a 1-million-row extended-customer minidimension is the remedy for fixed-width databases.
- **Telecom service lines:** for a service line (a phone number) that has one customer, sales rep and rate plan yet millions of dimension rows, those three are modelled as minidimensions of the service line.

An outrigger is the contrast case. Setup: a 150-attribute county-demographics table attached to the customer dimension is allowed as a snowflake because its grain (county) differs, it loads at different times and it saves space; the authors call outriggers an exception, and many of them a sign of over-normalisation. The procurement chapter makes the same split for rapidly changing attributes in one line.

## Limits

- No benchmark numbers for performance gains; all examples are illustrative, and the 100,000-row cap and the 100 million figure are the authors' guidance or reports without data.
- The authors concede that changing the bands later is hard.
- The two type 2 size thresholds in this batch differ: chapter 4 says type 2 may be inappropriate above a million rows, chapter 6 calls it predominant below 100,000.
- Chapters 4, 6, 9 and 10 are early-2000s texts (the extraction infers the 2nd edition, 2002); the bank chapter notes its schemas are not complete industry solutions.

## See Also
- [[Slowly Changing Dimensions Types 1, 2 and 3]] — prerequisite-for
- [[Dimensional Model Grain and the Four Design Steps]] — prerequisite-for
- [[Bridge Tables for Multivalued and Ragged Hierarchy Dimensions]] — related
- [[Degenerate, Junk and Role-Playing Dimensions]] — related
