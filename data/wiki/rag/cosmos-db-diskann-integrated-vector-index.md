---
title: Cosmos DB DiskANN Integrated Vector Index
tags: [rag, concept]
summary: Azure Cosmos DB keeps one DiskANN graph index per partition inside its existing Bw-Tree index, so vector inserts, deletes and filters live in the operational database; the paper reports low query cost and sub-linear latency scaling, as a vendor study.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-upreti-2025-cost-effective-low-latency-vector.md
---

# Cosmos DB DiskANN Integrated Vector Index

Upreti and colleagues (Microsoft, PVLDB 2025) describe a vector index built into an operational database rather than a separate store. This is a vendor paper about the authors' own product.

## Mechanism

Each partition (limit 50 GB) holds one DiskANN index, rewritten in Rust. It is kept as Bw-Tree index terms that contain the quantized vectors and the adjacency lists. Every insert updates the terms immediately and durably, with no segment merge or rebuild. Quantization lets the graph be navigated in cache: the authors estimate (self-reported) that a top-10 query at degree 32 and L=100 reads roughly 3500 quantized vectors but only around 50 at full precision. Product quantization is built from about 1000 samples and re-quantized at 25,000 without a graph rebuild (self-reported). Filter-aware search scales distances by beta<1 when a label matches (beta=0.3 tested, self-reported), with filters matching fewer than 5000 documents (self-reported threshold) sent to a flat or quantized scan. A sharded per-tenant index is an alternative to one global index with a filter.

## Results

Self-reported; competitor figures use public prices dated 14 Jul 2025 and Cosmos cost from the authors' tests.
- 10M Wiki-Cohere 768-d vectors, recall@10 94.64%: 70 RU per query, $17.50 per 1M queries against Pinecone $768, Zilliz $220, DataStax $30.72.
- p50 under 20 ms with recall@10 91.83% at LSearch=50 (the figure legend says 91.43); 5000 sequential queries, warm cache. From 100K to 10M vectors, p50-p99 latency rises less than 2x, with barely any change across 100 and 768 dimensions.
- Updates on WikiCohere-10M and MSTuring runbooks: in-place delete recall is up to 20 points above a drop baseline.
- YFCC 1M: filter-aware search at L=200 gives 10x better p99 latency and 5x lower p99 cost than post-filtering (recall 98.60 vs 99.92). With a year-sharded index, recall@10 is 98.09% and p99 is 13.43 ms; a non-sharded L=100 index gets 66.17% at 38.59 ms.
- MSTuring 1B across 50 partitions: recall@10 is about 83.8, 89.6 and 93.9 for L=50, 100 and 200 (the extraction cannot tell which line is 1B and which 100M).
- Insert: 65 RU, $162.5 per 10M vectors, about 40 vectors/s per thread; 5.4x higher insertion charge than Zilliz.

## Limits

- Cost rests on public price lists in non-comparable units (RU against Read Units and vCUs) and on serverless pricing; no head-to-head latency or recall against Pinecone, Zilliz or DataStax, and pgvector was not benchmarked.
- At 1B vectors recall stays under 94% even at L=200, and the best latency requires few, densely packed partitions.
- One vector per path; the 50 GB cap and 5 s request limit force client-side continuations; insert throughput was measured with Resource Governance off.
- The extraction notes a Fig 6 recall mismatch (91.83 text, 91.43 legend) and an ambiguous Fig 10 recall assignment.

## See Also
- [[Vector Database Comparison]] — prerequisite-for
- [[HNSW Hierarchical Navigable Small World Index]] — alternative-to
- [[PGVector Migration Pattern]] — related
- [[FAISS GPU Similarity Search]] — related
