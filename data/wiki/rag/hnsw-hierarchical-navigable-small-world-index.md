---
title: HNSW Hierarchical Navigable Small World Index
tags: [rag, concept]
summary: HNSW is a multilayer proximity graph for approximate nearest-neighbour search, where links are separated by length scale across random layers and neighbours are chosen by a diversity heuristic; it is fast and accurate but memory-hungry and weak on updates.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-malkov-2018-efficient-robust-approximate-nearest-neighbor.md
---

# HNSW Hierarchical Navigable Small World Index

HNSW (Malkov and Yashunin) asks whether a fully graph-based multilayer index can offer approximate k-NN search with logarithmic complexity while remaining dependable for low-dimensional and clustered data, which is where the earlier single-layer NSW degrades.

## Mechanism

Elements are inserted incrementally. Each element is assigned a random top layer l, drawn as floor(-ln(unif(0,1)) * mL), and, on every layer it belongs to, is connected to M neighbours picked with a diversity heuristic. A search goes greedily down from the top layer using ef=1 and finishes with a beam search of width ef on layer 0. The authors liken it to a skip list with proximity graphs in place of linked lists. The diversity heuristic fixes failure on clustered data, where linking only to the closest neighbours sticks at cluster boundaries.

## Results

Self-reported.
- Complexity of O(log N) is proved only under an exact Delaunay graph with bounded degree; simulations are on low-dimensional (d=4) data. With 200M SIFT vectors, measured query time departs from a purely logarithmic curve.
- Parameter guidance: mL = 1/ln(M); Mmax0 = 2*M (Mmax0 = M penalises high recall strongly); M is the main construction parameter, range 5 to 48; efConstruction near 0.95 construction-time recall suffices for most uses.
- Memory use is roughly 60 to 450 bytes per object, not counting the data itself, for M between 6 and 48.
- In ann-benchmarks runs (10-NN, 1000 queries, single thread), HNSW beats rivals by a wide margin on SIFT, GloVe, DEEP and CoPhIR; for d=4 it is only a little faster than Annoy at high recall. On 2M Wiki-8 (JS divergence) HNSW needs nearly three orders of magnitude fewer distance computations than NSW.
- 10M SIFT builds in 3 minutes (M=16, efConstruction=100, 40 cores). On 200M SIFT (1-NN) it builds in 5.6 hours at efConstruction=500 (64 Gb peak) against 11-12 hours and 23.5-30 Gb for Faiss OPQ/IMI/PQ configurations (May 2017 CPU build); HNSW needs notably more RAM but is reported more accurate and faster to search.

## Limits

- The complexity proof assumes exact Delaunay graphs; the authors concede high-dimensional resilience lacks analytical support.
- The baselines are 2016-2017 builds, and since 2018 Faiss has offered an HNSW of its own.
- No element updates or removals; full 1B SIFT/DEEP untested; loses NSW's distributed-search property because search starts at the top layer.
- There are no repeats or error bars, and each algorithm's best result was picked per recall range. The 200M SIFT build ran through a special small-footprint code path without vectorization.

## See Also
- [[Vector Database Comparison]] — prerequisite-for
- [[FAISS GPU Similarity Search]] — alternative-to
- [[Cosmos DB DiskANN Integrated Vector Index]] — alternative-to
- [[Lucene HNSW and Pyserini Dense Retrieval]] — extends (Lucene's dense index is HNSW)
