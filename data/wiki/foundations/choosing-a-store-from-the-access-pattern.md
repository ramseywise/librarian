---
title: "Choosing a Store from the Access Pattern"
tags: [foundations, decision]
summary: "Pick a data store by describing how records are found, how much one query touches, how data changes, its size and who operates it; row vs column is the first split, and each of ten store kinds is a bet that fits some patterns and hurts under others."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--10-choosing-a-store.md
---

# Choosing a Store from the Access Pattern

"Let's use a document database" or "we need a vector store" skips the question. A store is a set of bets about how data is read and written, so describe the access pattern first and match a store second. Confidence is medium: the choice depends on the workload, and the measurements below are one machine's, one trial each, on synthetic data; test your own queries on your own data.

## Questions that decide most of it
| Question | Answer | Points toward |
|---|---|---|
| How do you find a record? | by one key | key-value, or any database |
| | by several fields, ad hoc | relational, or document with indexes |
| | by words and relevance | search engine, or Postgres full-text search |
| | by meaning | vector index |
| | by following links many hops | graph store, or recursive SQL |
| How much does one query touch? | a few rows | row store, B-tree (OLTP) |
| | most rows, few columns | column store (OLAP) |
| How does it change? | updates in place, transactions | relational |
| | append-only by time, old data expires | time-series, partitioned table |
| | whole files written once | object store |
| How big and fast? | fits on one machine | stop here: one node is far simpler |
| | writes exceed one machine | partitioned store |
| Who runs it? | your process, no server | embedded |
| | a team with an on-call rota | whatever they already operate |

The last row is real: every new store brings its own backups, upgrades, monitoring and failure modes.

## Row or column first
Largest performance gap, independent of data model. On the same 2,000,000 rows, a point lookup by primary key took 0.0051 ms in a row-oriented embedded database and 0.2368 ms in a columnar one (nearly 50 times faster for the row store), while a group-by over every row took 436.2 ms against 2.1 ms (about 200 times faster for the columnar). Neither is better; see [[Row Stores vs Column Stores]]. A workload with both patterns is normally two stores with a pipeline between them. Selecting whole rows narrows the gap: in one run the row store took 46 ms without an index and 5.7 ms with one on the filter column, against 3.0 ms for the columnar store, because a column store must reassemble every column while a row store reads them directly.

## Ten kinds of store
| Kind | Bet | Reach for it when | It hurts when |
|---|---|---|---|
| Relational | you do not know all your queries yet | default for application state | writes outgrow one primary |
| Key-value | you read by key and that is all | sessions, caches, predictable high scale | a query arrives that is not by key |
| Document | data read together is stored together | varying shapes, whole-object reads | many-to-many joins; cross-document transactions |
| Wide-column | huge writes, known partition key | multi-region always-on writes | ad hoc queries; strong consistency |
| Search | relevance over text, slight staleness | ranking, facets, fuzzy text | as the only copy of your data |
| Time-series | append by time, expire old | metrics, sensors | frequent updates to old points |
| Graph | long chains of links dominate | deep variable-length traversal | mostly tabular reporting |
| Vector | nearest neighbours by embedding | semantic retrieval at scale | small corpora, where exact search is fine |
| Object | cheap durable whole files | lakes, backups, media | small mutable records; latency |
| Embedded | no server, one process | local apps, tools, analysis, tests | many concurrent writers |

**Details worth having.**
- A key-value store of the Dynamo kind inverts design order: relational lets you model first and query flexibly later; there you design the schema around your most important queries and must know access patterns up front. NoSQL does not mean no modelling.
- A document store now has multi-document transactions but advises against leaning on them: distributed transactions usually cost more than single-document writes and should not replace schema design.
- **Wide-column does not mean columnar.** It is a reduction of the document model with one level of nesting, partitioned with eventually consistent semantics, and not the choice for scanning one column across all rows.
- **Search is near real time on purpose.** New documents become searchable on a periodic refresh (every second by default) because opening a new segment is cheaper than a full commit. Keep the source of truth elsewhere and treat the index as derived data ([[Cache vs Source of Truth: Write-Through and Write-Behind]]).
- A metrics store keeps the current two-hour block in memory behind a write-ahead log; a Postgres extension instead keeps Postgres tables automatically split into time-based chunks. Purpose-built system vs extension of what you run.
- One embedded database's guidance says any site with fewer than 100K hits a day should work fine, noting one writer at a time as the real limit.

## Stores and what is not a store
Comparisons go wrong across layers. A warehouse stores and computes; an orchestrator stores no business data and schedules work that runs elsewhere, so they are not alternatives. A log (Kafka) against a store (Postgres), or a file format (Parquet) against an engine, is also a category error. Compare warehouses with warehouses, orchestrators with orchestrators; ask whether two tools would ever sit in the same box on a diagram.

## A worked decision, generalised
An application with transactional state, a varying-shape catalogue, text search, a session cache, nearest-neighbour recommendations over a small corpus, and large scan-and-aggregate dashboards: transactional state stays in Postgres as the system of record; the catalogue goes in `jsonb` columns; search starts with Postgres full-text and moves when relevance becomes a project; sessions are derived data that can be lost (a cache or a table); a small vector corpus can use exact search or pgvector; only the scan-heavy dashboards truly need a different store, a warehouse fed by a pipeline. Two stores, perhaps three, where the first instinct might name six.

## Pitfalls
- Choosing by data shape instead of access: JSON-shaped data does not require a document store.
- Adopting for future scale, paying operating cost now for load that may never arrive.
- Using a search index or cache as the only copy.
- Counting only licence and hardware; backups, upgrades, on-call and hiring are the real cost of each extra store.

## See Also
- [[How Far Plain Postgres Stretches]] — extends
- [[Row Stores vs Column Stores]] — prerequisite-for
- [[Distributed Compute Cost and the Single-Machine Threshold]] — related
- [[Write-Ahead Logs, fsync and the Durability Ladder]] — related
- [[SQL Schema Design and DDL]] — related
