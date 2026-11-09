---
title: FAISS GPU Similarity Search
tags: [rag, concept]
summary: The Faiss GPU paper builds a register-resident k-selection (WarpSelect) fused with distance kernels and runs IVFADC product-quantised search across GPUs, reaching billion-scale search and k-NN graph building in hours or minutes.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-johnson-2019-billion-scale-similarity-search-gpus.md
---

# FAISS GPU Similarity Search

Johnson, Douze and Jegou ask how exact search, IVFADC product-quantisation search and k-NN graph construction can use GPUs near peak throughput. Their hypothesis is that earlier GPU work was held back by k-min selection and by weak use of the memory hierarchy.

## Mechanism

WarpSelect keeps the k-selection state in GPU registers by means of odd-size merge and sort networks, which allows fusing it with an L2 distance kernel based on cuBLAS GEMM for exact search. IVFADC is a coarse k-means quantiser plus a product quantiser on residuals, searched over tau inverted lists (the multi-probe parameter). Its implementation keeps PQ lookup tables in shared memory, selects k over several passes, and spreads work over GPUs by replication or sharding. A rule of thumb sets the coarse centroid count near the square root of the dataset size.

## Results

Self-reported unless the baseline row is another paper's figure.
- SIFT1B, 8-byte codes, one Maxwell Titan X, 10^4 queries: R@10 reaches 0.376, with each query taking 17.7 us, which is 8.5 times quicker than Wieschollek et al. and at a higher recall (their number as reported, matched on memory).
- Deep1B, 4 GPUs, PQ m=20: R@1 is 0.4517 at 0.0133 ms per vector, compared with a CPU result of 0.45 taking 20 ms (a 1-thread figure from the dataset paper on different hardware).
- At k=100 WarpSelect attains 55% of peak memory bandwidth, and at k=1000 16%. Against the best selection method compared it is 1.62x faster for k=100 and 2.01x faster for k=1000.
- On SIFT1M, exact search attains 85% of peak, and dropping the fused kernel makes it at least 25% slower.
- MNIST8m k-means (256 centroids, 20 iterations): 140 s on one GPU against 320 s for BIDMach.
- Building a k-NN graph (k=10) with accuracy over 0.8 for 95M YFCC100M images takes 35 minutes on 4 GPUs; Deep1B takes roughly 6 hours to half a day depending on quality.

## Limits

- Wieschollek and Deep1B CPU numbers are taken from those papers, on different hardware.
- No variance or seeds; only exact search and IVFADC are covered, not graph indexes, filtering, updates or deletes.
- Efficiency drops at large k; the authors call the k-means benchmark somewhat unrealistic.
- The text is the 2017 arXiv v1 (Maxwell GPUs, CUDA 8), not the 2021 journal version; Sift1B IVFADC parameters are unstated.

## See Also
- [[Vector Database Comparison]] — prerequisite-for
- [[HNSW Hierarchical Navigable Small World Index]] — alternative-to
- [[Cosmos DB DiskANN Integrated Vector Index]] — related
- [[Lucene HNSW and Pyserini Dense Retrieval]] — related (compared against Faiss)
