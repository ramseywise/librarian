---
title: "Slowly Changing Dimensions Types 1, 2 and 3"
tags: [data-engineering, ingest-and-modelling, pattern]
summary: "Overwriting a dimension label rewrites published history; type 2 closes the old row and opens a new surrogate key so facts keep the label in force at event time, and a hash compare makes the load safe to re-run."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--02-ingest-and-modelling--notes--02-dimensional-modelling.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch04-procurement.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch06-customer-relationship-management.md
  - data/raw/papers/2026-11-08-data-warehouse-toolkit-ch08-human-resources-management.md
---

# Slowly Changing Dimensions Types 1, 2 and 3

A dimension attribute changes (a category is redrawn). What happens to last quarter's numbers is a business question; the modeller's job is to make the answer a deliberate per-attribute choice.

## Type 1: overwrite

One `UPDATE`, no history. Setup: one zone moves borough on January 15th. January's reported revenue for the destination borough went from 2,382,840 to 2,710,631 (about 328,000 dollars) for days already reported, with no record anything happened, and any aggregate built on top needs rebuilding. Right for corrections (a misspelled name); wrong for anything compared over time.

## Type 2: add a row

Keep the old row, close it, open a new one with a new surrogate key. Columns: row hash, `valid_from`, `valid_to`, `is_current`.

```sql
UPDATE dim d SET valid_to = :load_date, is_current = false
FROM incoming i
WHERE d.zone_id = i.zone_id AND d.is_current AND d.row_hash <> i.row_hash;
-- then insert a new current row for any key with no current row
```

Properties of the result: 250 zones became 251 rows (unchanged attributes create no history); a retry changes nothing, because a re-run finds a matching hash and no missing row; validity ranges form an unbroken chain with no overlap.

Facts take the key of the dimension row current at event time (range join on the event date). Then:
- Grouping through the fact's own key gives history as it was: 13,251 trips in the old borough up to the 14th, 15,998 in the new one from the 15th.
- Joining via the natural key to the `is_current` row restates history to today: all 29,249.
- Do not constrain facts by effective dates in ordinary queries; the dates serve load logic and as-of lookups of the dimension.

**Late-arriving facts** need no special case: the event date selects the right version; the remaining work is writing to the right partition. If a closed period would change, keep two date keys (event and booking). **Late-arriving dimension rows** are harder: insert a new key, fix the dates, repoint fact rows in the interval. Fact surrogate keys are not time-ordered.

Row growth: a rapidly changing attribute on a dimension of millions of rows can outgrow being a dimension, so split volatile columns into their own dimension. In dbt a snapshot generates this (`dbt_valid_from`, `dbt_valid_to`), but writing it once by hand shows what it does.

## Type 3: add a column

`prior_borough` beside `borough`: one before-and-after view, dimension does not grow, but it cannot say which value a trip had on its date and a second change loses the first. Use for one planned reorganisation.

| Type | Mechanism | History | Use for |
|---|---|---|---|
| 1 | Overwrite | Gone; past reports change | Corrections |
| 2 | New row, new key | Full | Anything compared over time |
| 3 | New column | One step | A single planned before/after |

## Same problem in streams

Joining a sale to a tax rate as it is now makes a rerun non-deterministic. The type 2 fix: give each rate version an identifier and reference it from the sale. The cost is that log compaction cannot discard any version.

## Variants in Kimball and Ross

From chapters 4, 6 and 8 of *The Data Warehouse Toolkit*; advice is the authors'.

- Kimball and Ross call type 2 the workhorse for attributes that must stay historically accurate, and say never to build the key from the natural key plus version digits or an effective date. Once type 2 rows exist, products are counted by natural key rather than surrogate key. A point-in-time count constrains the effective date to on or before the day and the expiration date to on or after it.
- They advise asking the business about change tracking up front, and using type 1 for corrections or values with no historical interest. They add that type 3 is seldom used, is no improvement on 1 or 2, and fits only when two views must be true at once.
- For a change that recurs on schedule they use a type 3 with a column for each year plus a current one. Setup: a sales-rep dimension whose district map is redrawn every year, five times in five years.
- **Type 6 (2+3+1):** one new row per change (type 2), a column holding the current value that is overwritten on all rows, and a column holding the value at the time. Setup: a product moved from Education to Strategy to Critical Thinking, keys 12345, 25984, 31726. They say to adopt it only once the business accepts the added complexity.
- To detect changed rows in staging, compare a per-row CRC checksum instead of every field.
- Chapter 4 says type 2 growth may be inappropriate for dimensions over a million rows; chapter 6 calls it predominant below 100,000. Larger dimensions split the volatile columns into [[Minidimensions for Rapidly Changing Monster Dimensions]].
- **Time-stamped type 2 (HR):** each row carries effective and expiration timestamps and a transaction description, which lets the dimension be sliced by time without a fact table. The current row gets a far-future expiration rather than null, a most-recent indicator is updated when a new transaction arrives, and source microtransactions are collapsed into one supertransaction. The authors prefer this to a factless transaction table with as many rows as the dimension. A monthly snapshot then keys to the row in force on the last day of the month ([[Transaction, Periodic and Accumulating Snapshot Fact Tables]]).

## Limits

- Design advice from case studies, with no measurements; the two size thresholds above differ and are not reconciled in the extractions.
- Early-2000s text (the extraction infers the 2nd edition, 2002); no MERGE or columnar engines, and the far-future expiration date and SQL tricks reflect that era. Rapidly changing dimensions and the surrogate-key workflow are deferred to chapters not in this batch.

## See Also
- [[Dimensional Model Grain and the Four Design Steps]] — prerequisite-for
- [[Data Vault Hubs, Links and Satellites]] — alternative-to (insert-only history)
- [[Idempotent Batch Loads and Partition Overwrite]] — related
- [[Change Data Capture and the Dual-Write Problem]] — related
- [[Minidimensions for Rapidly Changing Monster Dimensions]] — extends
- [[Transaction, Periodic and Accumulating Snapshot Fact Tables]] — related (a monthly snapshot keys to the row in force at month end)
- [[Bridge Tables for Multivalued and Ragged Hierarchy Dimensions]] — related (bridge rows carry effective and expiration dates)
