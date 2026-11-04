---
title: "How Far Plain Postgres Stretches"
tags: [foundations, comparison]
summary: "A single relational server emulates key-value, document, search, time-series, graph and small-scale vector workloads at levels most applications never exceed; it stops being enough when writes exceed one primary, when scanning most of a huge table, for multi-region writes, search as a product, or blobs."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--01-storage-and-compute-foundations--notes--10-choosing-a-store.md
---

# How Far Plain Postgres Stretches

A survey of twenty years of attempts to replace the relational model concluded that SQL has been extended to capture the good ideas from others: a relational system easily emulates a key-value store, and vector databases are essentially document-oriented systems with specialised approximate-nearest-neighbour indexes, "a feature, not the foundation of a new system architecture". JSON support took years to reach relational systems and vector indexes under one. This is an argued position, not a neutral survey, but it can be checked. The runs below are on one private Postgres, one trial each; they are not benchmarks against specialised stores, only a test of whether the plain option clears the bar a workload sets.

| Pattern | What was tried | Result |
|---|---|---|
| Key-value | `text` key to `jsonb` value, 1,000,000 keys, one client over a Unix socket | 33,181 reads per second; 20,741 durable upserts per second (the sync used does not flush the drive, so honest flushes would be lower) |
| Document | 1,000,000 mixed-shape `jsonb` documents, containment query | 31.387 ms with a parallel scan; 0.017 ms with a GIN index (`jsonb_path_ops`) |
| Search | 300,000 short texts, `LIKE` vs `tsvector` with a GIN index | `LIKE '%satisfied%'` matched 138,026 rows; the stemmed query 257,679 (it also finds "satisfy" and "satisfies") |
| Time-series | range-partitioned table by month, 12 partitions | a one-week query read 1 partition; `DELETE` of 267,840 rows took 64 ms, `DROP` of a similar-size partition 5.4 ms (about 12 times faster, no dead rows to vacuum) |
| Graph | node and edge tables, recursive CTE, 100,000 nodes and 500,000 edges | 6 hops reached 17,297 nodes in 15 ms |
| Vector | brute-force exact search in memory, 384 dimensions | 0.1 ms per query at 10,000 vectors, 1.5 ms at 100,000, 16.7 ms at 1,000,000 |

**Notes by pattern.**
- Key-value: most applications do not need more than this; Redis earns its place as a cache in front of a database or for data structures like sorted sets, HyperLogLog and streams.
- Document: prefer `jsonb` (`json` keeps the text and reparses it); mix columns and documents in one table, real columns for what you filter and join on, `jsonb` for the variable part.
- Search: `LIKE` has no language support, ranking or index. One language and simple ranking on one table is often enough; move to a search engine for facets, typo tolerance, custom analysers and relevance tuning as a product feature.
- Time-series: range partitioning gives pruning and cheap expiry but not automatic chunk creation, retention policies or time-series compression, the case for an extension.
- Graph: this graph is sparse and random; a hub-heavy graph with higher fan-out grows much faster. With 3,000,000 edges fan-out rose from about 5 to about 30 per node and six hops took 4,440 ms instead of 15 ms, with later hops reaching almost nothing new while the query spends its work deduplicating. Path patterns as a first-class query language are the case for a graph store.
- Vector: exact search scales linearly, so about 6 million vectors reach 100 ms; many retrieval corpora are far smaller and need no approximate index. Before a new store, try reducing dimensions, filtering first, or an HNSW index in pgvector (approximate indexes trade recall for speed, alongside ACID and joins). Changing embedding models means rebuilding the store.

## When it is not enough
- **Writes exceed one primary.** Replicas scale reads, but one node takes every write ([[Partitioning Strategies and Hot Spots]]).
- **You scan most of a large table.** The roughly 200 times gap in [[Choosing a Store from the Access Pattern]] is architecture an index will not close; use a warehouse.
- **Multi-region writes with no single primary**, the goal that wide-column and Dynamo-style stores trade consistency for.
- **Search or retrieval is the product.**
- **Blobs**: large files belong in an object store, with paths in the database.

The opposite trap is adopting a specialised store for scale you do not have.

## See Also
- [[SQL Indexes and Query Plans]] — related
- [[Relational, Document and Graph Models and Schema on Read]] — related
- [[Row Stores vs Column Stores]] — related
