---
title: "Relational, Document and Graph Models and Schema on Read"
tags: [foundations, comparison]
summary: "Choosing a data model by the relationships the data has: documents suit self-contained trees, relational suits shared and many-to-many facts, graphs suit variable-length paths; plus schema-on-read versus schema-on-write and why declarative queries free the engine."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--01-data-systems-and-data-models.md
---

# Relational, Document and Graph Models and Schema on Read

Every data model embodies assumptions that make some operations fast and others awkward. The deciding question is which relationships the data has and which will be queried. For SQL mechanics see [[SQL Schema Design and DDL]] and [[SQL Subqueries and CTEs]].

| Model | Natural fit | What goes wrong |
|---|---|---|
| Relational | Many-to-one and many-to-many, evolving questions | Object-relational impedance mismatch; large schema changes need planning |
| Document | Self-contained trees read and replaced as a unit | Shared facts duplicated; joins move to the application; large documents rewritten on each change |
| Graph | Connected data with variable-length paths | Few analytical engines; hard to partition |
| Columnar file or table | Scans over a few columns of many rows | Row-at-a-time updates (see [[Row Stores vs Column Stores]]) |

The models are converging (relational systems add JSON columns, document stores add joins), but emulating one in another is usually possible and usually awkward.

## Shared facts: relational vs document

The real difference is what happens to a fact many records share. In a test with 200,000 trips and 2,000 drivers, renaming a driver touched 1 row in the normalised design and 92 documents in the embedded one. An ID has the advantage that it means nothing to people so never has to change. The document form wins on reading a whole record without a join; both single-record reads took a few hundredths of a millisecond, so that test says little. Documents suit one-to-many trees, and suit many-to-one and many-to-many poorly because data grows more interconnected as features are added. Early hierarchical stores had the same many-to-many trouble, which the relational and network models were invented to solve; the relational model's lasting idea was to leave the access path to a query optimiser.

The warehouse version is the same trade: a dimension table normalises, a one-big-table denormalises, and an append-mostly analytical store can afford the second.

## Schema on read vs schema on write

"Schemaless" misleads: some code always assumes a structure. The real distinction is whether the schema is explicit and enforced on write or implicit and applied on read (roughly static vs dynamic typing).

- **On read:** old documents stay, but every consumer carries a function that remembers every shape ever written.
- **On write:** a change is an explicit event and bad rows are rejected on entry. An `ALTER TABLE` on 200,000 rows took 0.06 ms because only metadata changed; the backfill took 48.70 ms.

On read fits varied items or shapes controlled by someone else, which describes a raw landing zone. Most lakes read tolerantly at the raw layer and enforce a schema from the first transform. See [[Encoding Compatibility and Schema Evolution]].

## Declarative queries

A declarative query specifies the result and lets the engine choose steps, so it can reorder and parallelise without the query changing. Adding an index changed the plan from `SCAN` to a covering-index `SEARCH` and took a rare-value filter from 3.57 ms to 0.03 ms with the SQL untouched (see [[SQL Indexes and Query Plans]]). The same independence lets SQL move from a row store to a column store. MapReduce's requirement that map and reduce be pure functions is the same bargain: restricting what the programmer can say frees the system to rerun anywhere.

## Graphs and recursion

The number of joins in a graph query is not known in advance, since reachability may take two hops or twenty. SQL handles it with a recursive CTE (guard against cycles by tracking the path and capping hops). The equivalent of a 4-line graph-language query took 29 lines of SQL, so use a graph language if this is the main question and a CTE if it is occasional, as with lineage or a hierarchy in a dimension table.

## See Also
- [[SQL Subqueries and CTEs]] — related
- [[Faults, Load Parameters and Systems of Record]] — related
- [[Encoding Compatibility and Schema Evolution]] — prerequisite-for
- [[Data Systems Foundations Reading Map]] — related
