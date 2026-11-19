---
title: "Transaction, Periodic and Accumulating Snapshot Fact Tables"
tags: [data-engineering, ingest-and-modelling, concept]
summary: "Kimball and Ross sort every fact table grain into transaction, periodic snapshot or accumulating snapshot; the choice decides whether rows are inserted or updated, how dense the table is and which facts can be summed over time."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch01-dimensional-modeling-primer.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch02-retail-sales.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch03-inventory.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch05-order-management.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch07-accounting.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch09-financial-services.md
---

# Transaction, Periodic and Accumulating Snapshot Fact Tables

Kimball and Ross classify any fact table's grain as one of three kinds, and require every measurement in a table to share that grain. This page collects what their chapters on retail, inventory, orders, accounting and banking say about choosing among the three. The grain idea itself is on [[Dimensional Model Grain and the Four Design Steps]].

| | Transaction | Periodic snapshot | Accumulating snapshot |
|---|---|---|---|
| One row is | one event at an instant | one entity per period (day, week, month), snapshots stacked | one item at the lowest level of detail entering a pipeline |
| After loading | typically not revisited | insert-only | revisited and updated as activity happens |
| Date keys | not stated | the period end (month end in the banking chapter) | several, one per milestone |
| The authors say it suits | not stated | long-lived, continuously replenished things such as inventory or bank accounts | processes that start and finish within a short time |

## Semi-additive facts

A balance or inventory level adds up over products and over stores but not over dates; over dates the authors average it. Setup: a checking account with Monday to Friday balances of 50, 50, 100, 100, 100 averages 80, not the 400 a sum gives. Setup: a query over 3 products, 4 stores and 7 dates; SQL's average divides by 84 rows, so the chapter has the application divide the sum by the 7 dates in the constraint (the extraction notes this is stated for the standard SQL of the time). The retail market-basket count is also semi-additive, because summing it across more than one product counts a basket twice.

Kimball and Ross also advise against storing ratios and to-date columns. GMROI is not additive, so the additive components (quantity sold, plus values at cost and at the latest selling price) are stored and the ratio is computed after summing. Quarter-to-date and year-to-date columns are left out of the general ledger snapshot since they do not match the grain and inflate totals when added; the access application computes them instead.

## Density and volume

A sales fact table is sparse: the chapter says about 10 percent of products sell on a given day, and Kimball and Ross advise leaving out rows with no activity. An inventory snapshot is dense, with zero-quantity rows kept. Setup: 60,000 products in 100 stores at a 14-byte row gives about 6 million rows and 84 MB per daily load, over 30 GB a year. Holding the latest 60 days at daily detail and the older history as weekly rows in a second fact table gives 208 snapshots against 1,095 daily over three years, which the chapter puts at more than a factor of 5 smaller.

## Pairing the types

For inventory the authors say transactions alone are impractical for reading position, so a transaction table is paired with a snapshot, and the three types share conformed dimensions ([[Conformed Dimensions, the Bus Matrix and Drilling Across]]). For the order pipeline they advise an accumulating snapshot with one row per order line and its own surrogate key for every milestone date, so a date not yet known loads as 'Unknown' or 'To be determined'; lag measures are exposed as view columns computed from date differences.

Point-in-time balances can come from a transaction table instead of a snapshot. Setup: a bank with 10 million accounts and one snapshot row per account per day would add about 3.65 billion rows a year. The chapter's transaction table carries a sequence number, a final flag and an ending balance, is keyed on date, account and sequence number (not time of day), and for each account takes the latest date key falling at or before the date asked for.

Budgets show grain choice at work. Setup: a budget line of 200,000 raised by 40,000 in June and cut by 25,000 in October is stored as three rows, one per net change, rather than as a monthly status snapshot; adding the rows over time yields the current approved budget, and the one amount column is fully additive.

## Factless fact tables

A fact table with no measures records only a relationship between keys. The retail chapter uses a promotion-coverage table: 'on promotion but did not sell' is the coverage rows minus the sales rows. The order chapter uses one for sales-rep assignments to customers even when no order occurred.

## Limits

- The extraction describes the advice as opinionated practitioner guidance with no measurements; all sizes above are the chapters' hypothetical worked examples.
- The text is from the early 2000s (the extraction infers the 2nd edition, 2002; chapter 1 may be an earlier edition than the 3rd). The storage figures, the SQL average limitation and the index-based arguments reflect engines of that time, and the extraction says columnar and lakehouse engines are not covered.
- The point-in-time technique needs the transaction table to be complete and accurate; when a row arrives late, later balances and sequence numbers must be incremented in a sweep forward. It is invalid where a balance changes without transactions, such as brokerage valuations; the chapter says to use a snapshot there.
- The chapters on inventory and orders defer some detail (accumulating snapshot, multiple units of measure) to other chapters not in this batch.

## See Also
- [[Dimensional Model Grain and the Four Design Steps]] — prerequisite-for
- [[Conformed Dimensions, the Bus Matrix and Drilling Across]] — related (the three types share conformed dimensions)
- [[Degenerate, Junk and Role-Playing Dimensions]] — related (dimensions the order and ledger facts carry)
- [[Slowly Changing Dimensions Types 1, 2 and 3]] — related (a monthly snapshot can key to the dimension row in force at month end)
