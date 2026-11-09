---
title: Lucene HNSW and Pyserini Dense Retrieval
tags: [rag, concept]
summary: Pyserini wraps Lucene BM25 and Faiss dense retrieval with hybrid interpolation for reproducible baselines, and a follow-up argues Lucene's own HNSW with OpenAI embeddings makes a separate vector store unnecessary for existing Lucene shops.
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-lin-2021-pyserini.md
  - data/raw/papers/2026-11-08-lin-2023-vector-search-openai-embeddings.md
---

# Lucene HNSW and Pyserini Dense Retrieval

Two papers frame retrieval tooling. Pyserini (SIGIR 2021 resource paper) is a pip-installable Python toolkit for sparse, dense and hybrid first-stage retrieval. "Lucene Is All You Need" (2023) asks whether a dedicated vector store is needed, or whether Lucene HNSW plus an embedding API is enough.

## Pyserini

BM25 runs through Lucene/Anserini; dense retrieval goes through Faiss (brute force or HNSW) using ready-made encoders such as TCT-ColBERT, DPR, ANCE and DistilBERT KD; hybrid retrieval interpolates sparse and dense scores with a weight. For roughly three dozen test collections (v0.12.0) it ships the queries, qrels, prebuilt indexes and evaluation scripts. The extraction's numbers were stripped, so only directions are recorded, on MS MARCO passage dev (6980 queries, 8.8M passages):
- Hybrid TCT-ColBERT + BM25 beats dense alone, and the best first stage reported is the hybrid that also uses doc2query-T5 expansion.
- Dense TCT-ColBERT with HNSW is far above default BM25 (k1=0.9, b=0.4) and loses little recall against exact brute force; tuned BM25 gains little; adding doc2query-T5 expansion to default BM25 gives a large jump yet remains a bag-of-words method.
- On the MS MARCO document dev set, per-passage hybrid indexing reaches MRR@100 0.378 against 0.332 for zero-shot dense (self-reported); on the passage test leaderboard, Pyserini's default BM25 beats the organisers' baseline (0.165) (self-reported).

## Lucene HNSW with OpenAI ada2

All MS MARCO v1 passages were embedded with ada2 (1536-d), indexed through Anserini into Lucene 9.5.0 HNSW, with a patch that lifts the 1024-dimension limit. Self-reported results on dev: R@1k 0.984, tied with ColBERT-v2; RR@10 0.343, which trails SPLADE++ ED at 0.383, ColBERT-v2 at 0.397 and TCT-ColBERTv2 at 0.358 and just above TAS-B (0.340); DL19 nDCG@10 0.704, DL20 0.676. Throughput is 9.8 QPS with 16 threads (efSearch=1000, two Xeon 8160, mean of four trials); indexing took about three hours (M=16, efC=100). The authors report Lucene reaches roughly half the query throughput of Faiss but scales better across threads. They argue the gap to dedicated stores is mainly performance, not features, and find pgvector compelling for Postgres shops; both are arguments, not measurements.

## Limits

- Pyserini: MS MARCO only; interpolation weight, HNSW settings, latency and hardware are unreported; BM25 was tuned on dev queries that also report scores; dense support is less mature than sparse.
- Lucene paper: no dedicated store (Pinecone, Weaviate, Milvus, Qdrant, Chroma) was benchmarked; Lucene is slower than Faiss in indexing and throughput; the 1024-dim patch is dated; one dataset, 8.8M passages, one dated server; possible MS MARCO leakage into ada2 is unknown.

## See Also
- [[Vector Database Comparison]] — prerequisite-for
- [[HNSW Hierarchical Navigable Small World Index]] — prerequisite-for
- [[FAISS GPU Similarity Search]] — related
- [[monoBERT duoBERT Multi-Stage Ranking]] — related
- [[Query2doc LLM Query Expansion]] — related
