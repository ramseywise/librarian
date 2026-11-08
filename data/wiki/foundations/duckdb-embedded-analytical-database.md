---
title: DuckDB Embedded Analytical Database
tags: [foundations, concept]
summary: DuckDB runs analytical SQL inside the host process using a vectorized interpreted engine, compressed column blocks and serializable MVCC, built from existing techniques rather than new ones.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-raasveldt-2019-duckdb.md
---

# DuckDB Embedded Analytical Database

Raasveldt and Muhleisen (CWI; SIGMOD 2019 demonstration paper, four pages) present DuckDB as an analytical SQL engine embedded in another process. The paper has no performance numbers: the comparison against SQLite, MonetDBLite and HyPer was a live demo. The statements below are the authors' own claims (self-reported).

## Motivation

The authors say SQLite is the most widely deployed SQL engine (more than a trillion databases, citing its website) but is built for transactional work, with row-oriented execution over a B-Tree layout, and the authors call its analytical performance very poor (no benchmark given). Their gap: no embeddable engine aimed at analytics. They name interactive analysis from R and Python data-frame workflows, and edge computing (analysing power-meter readings locally instead of shipping them to a central site, which raises bandwidth and privacy concerns) as uses. Lessons from their earlier MonetDBLite gave four requirements: efficient analytics without giving up all transactional ability, fast table transfer within one address space, stability (a crash must never take the host down), and portability with no external dependencies.

## Design

- **Components.** The authors say none is new: SQLite-style API, a Postgres parser library, a cost-based optimizer, a vectorized engine, serializable MVCC and the DataBlocks storage layout, combined from the state of the art.
- **Execution.** Vectorized and interpreted, chosen over JIT compilation for portability because JIT engines depend on large compiler libraries. Vectors hold at most 1024 values by default. A pull-based "Vector Volcano" model moves chunks (horizontal slices of a result) up from scans. Fixed-width values sit in plain arrays, strings are held as pointers into a separate heap, NULLs sit in a bit vector, and selection vectors avoid moving data after a filter.
- **Storage.** Tables are split into horizontal chunks of columns, compressed lightly into blocks that carry min/max indexes per column.
- **Concurrency.** HyPer's serializable MVCC: updates in place with prior versions in an undo buffer. The authors say they picked it because users often asked for concurrent table changes.
- **Interfaces.** C/C++ API, a SQLite compatibility layer, and R and Python APIs; MIT licence.
- **Status in 2019.** Every TPC-H query ran, as did all TPC-DS queries except two, and most of SQLite's logic test suite passed.

The extraction stresses what the paper does not say: it never uses "SQLite for analytics" as a phrase, never calls the engine columnar (only the storage), and has no mention of Parquet or CSV, so those claims need other sources.

## Limits

- Demo paper with no measurements; performance statements are predictions.
- Incomplete by the authors' account: DataBlocks, cardinality estimation and a buffer manager were still to come, and only inter-query parallelism existed. Checksums and self-checking are future ideas.
- Silent on larger-than-memory operation and on later DuckDB features. MonetDBLite is the authors' own earlier system.

## See Also

- [[Row Stores vs Column Stores]] — prerequisite-for
- [[Data Engineering Foundations]] — prerequisite-for
- [[Distributed Compute Cost and the Single-Machine Threshold]] — related
