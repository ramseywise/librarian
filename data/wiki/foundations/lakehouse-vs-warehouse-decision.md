---
title: "Lakehouse vs Warehouse Decision"
tags: [foundations, decision]
summary: "A lakehouse puts a transactional metadata layer over open files to avoid the two-tier lake-plus-warehouse copy; what you gain is one copy and many engines, what you give up is data independence, multi-table transactions and some native performance."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--04-warehouse-lakehouse-streaming--notes--03-lakehouse-vs-warehouse.md
---
# Lakehouse vs Warehouse Decision

## The problem it attacks

First-generation warehouses coupled compute and storage and enforced schema on write. A second generation put cheap lake storage (schema on read) beside a warehouse holding a copy for BI. Four problems with that two-tier design: **reliability** (two systems kept consistent through ETL), **staleness** (a vendor-sponsored survey, quoted by a lakehouse vendor, reported 86% of analysts on out-of-date data and 62% waiting on engineering numerous times a month), **advanced analytics** (ML wants files, not ODBC pulls) and **total cost** (data stored twice, proprietary format lock-in).

A lakehouse is low-cost, directly accessible storage that also provides DBMS features: ACID, versioning, auditing, indexing, caching, optimisation. It rests on a transactional metadata layer over open files ([[Table Format as a Commit Log over Parquet]]), SQL performance via caching, auxiliary statistics and layout, and declarative DataFrame APIs. The price: **some data independence**. A warehouse can change its layout silently because nobody sees it; an open format is a public interface.

## What can be tested

- **One copy, many engines.** A 2,000,000-row Delta table read the same through the log reader, plain pyarrow and DuckDB: 2,000,000 rows each.
- **The trap.** After a committed delete, a glob over the directory returned 2,500,000 rows against 1,500,000 through the log, with no error. Open formats let anyone read the files, wrongly too. Enforce that readers go through the log or catalog; direct file reads also bypass any row or column policy, so an open format is not an access boundary.
- **Schema enforcement is narrow.** The writer rejected a string-typed fare, and a hand-dropped file stayed invisible, but nothing stops a fare of a million dollars.

## What a warehouse still does better

- **Multi-table transactions.** After a simulated crash between two statements, the warehouse rolled back both (0 fact rows, 0 summary rows); the lakehouse left the fact table committed with no summary table. Handle with rebuildable idempotent derived tables, or store a watermark: commit the fact first, record its version in the summary's commit, and have readers read the fact at that version. Unsuitable for a ledger where two tables must agree at every instant. Some catalogs now offer multi-table commits; check yours.
- **Native format speed.** Same engine, same data: best of 5 was 6.2 ms on open Parquet against 1.7 ms on a native table (machine-dependent; read the ratio). Caching and auxiliary data can narrow the gap. A vendor TPC-DS run at scale factor 30,000 reported 3,302 s and $104 against 2,996, 7,143, 5,793 and 37,283 s and $153 to $570 for four unnamed warehouses. The system was tuned by its authors, the others are anonymous, and concurrency is not tested; it shows only that open formats are not inherently too slow for BI.
- Very many small concurrent updates: log writes to an object store bound transactions per second.

## Deciding

The industry outcome looks like convergence: warehouses read and write open formats, and lakehouse engines add BI features. The real question is where the system of record lives and who owns the format. A two-tier design is not wrong for holding two copies; it goes wrong when nobody can say which is the source and the copy cannot be rebuilt. Federation unifies reads, unbundling unifies writes with a log, and a lakehouse is one store with one commit protocol and many readers. Deploy as few moving parts as possible.

| Situation | Lean |
|---|---|
| SQL and BI only, one team, moderate scale | Warehouse |
| Heavy ML or Python alongside SQL on the same data | Lakehouse |
| Several engines share data, or lock-in must be avoided | Lakehouse |
| Multi-table transactions must always hold | Warehouse or OLTP |
| Very many small concurrent updates | Warehouse or OLTP |
| Existing warehouse and working lake | Keep both; federate |
| Fits on one machine | DuckDB and Parquet or a local table format |

Pitfalls: a lake of Parquet without a metadata layer is not a lakehouse; lower cost is not guaranteed (warehouse fees swap for engineering time on compaction, vacuum, catalog); migrating does not fix a people problem when nobody owns the data; quoting a vendor benchmark without saying who ran it. See [[Medallion Layers Need Tests]].

## See Also
- [[Separated Storage and Compute and Warehouse Billing Shapes]] — alternative-to
- [[Medallion Layers Need Tests]] — related
- [[Copy-on-Write vs Merge-on-Read]] — related
- [[Object Store Guarantees and the Partial-Write Problem]] — prerequisite-for
- [[Spark Shuffles and When One Machine Is Enough]] — related
