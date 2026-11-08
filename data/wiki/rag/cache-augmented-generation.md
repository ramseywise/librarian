---
title: Cache-Augmented Generation
tags: [rag, llm, pattern]
summary: "Cache-augmented generation (CAG) preloads a whole small corpus into the model's KV cache once and answers with no retrieval step; one short paper reports it beating plain RAG on BERTScore at 21k-50k tokens, with the margin gone at 85k."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chan-2024-don-t-do-rag.md
---

# Cache-Augmented Generation

Cache-augmented generation (CAG) replaces the retrieval step with a precomputed attention cache. The paper (a short companion paper, arXiv 2412.15605) describes three phases.

1. **Preload.** The documents are encoded once into a KV cache. The one-time cost does not grow with the number of queries.
2. **Infer.** The cache is loaded together with the query, and generation runs with no retriever in the path.
3. **Reset.** The cache grows append-only as query tokens are added, so a reset is a truncation of those appended tokens.

The design premise is that a long-context model's usable window is smaller than its nominal one, and that a good share of knowledge bases fit inside it. The paper cites (not measures) an effective length of 32K for Llama 3.1 8B and 64K for the 70B, against a trained length of 128K.

## What the paper measured

All numbers are self-reported. Setup common to every row: all systems run on Llama 3.1 8B, the corpora span 21k to 85k tokens, and scoring is BERTScore against gold answers in a single run without variance. The RAG baselines are plain LlamaIndex pipelines, with BM25 as the sparse retriever and an OpenAI-index dense retriever, each tried at k = 1, 3, 5 and 10.

| Test set | CAG | Best sparse RAG |
|---|---|---|
| HotPotQA small (16 docs, 21k tokens) | 0.7951 | 0.7676 (top-5) |
| HotPotQA medium (32 docs, 43k tokens) | 0.7821 | 0.7633 (top-5) |
| HotPotQA large (64 docs, 85k tokens) | 0.7407 | 0.7535 (top-5) |
| SQuAD small (3 docs, 21k tokens) | 0.7695 | 0.7616 (top-3) |
| SQuAD large (7 docs, 50k tokens) | 0.7734 | 0.7658 (top-5) |

On HotPotQA large, CAG sits below both sparse top-3 (0.7463) and top-5. The authors describe the gap as narrowing "slightly", citing long-context degradation from the literature. The authors also read sparse RAG beating dense RAG on several cells as a sign that the datasets are easy.

Latency (self-reported; HotPotQA only, Tesla V100 32G x 8, seconds per query): CAG generation took 0.85 s on small and 2.26 s on large. The no-cache in-context baseline, which re-encodes the reference text each query, took 9.32 s and 92.08 s. Sparse RAG top-3 generation stayed near 0.67 to 0.74 s, so CAG is faster than dense RAG (retrieval alone about 0.41 to 0.48 s) but not faster than sparse RAG.

## When it fits

The authors suggest small, static internal knowledge bases such as FAQs and call centres. They propose, without an experiment, a hybrid that preloads a foundation context and retrieves only for edge cases or very specific queries.

## Limits

- The authors concede the approach is impractical for significantly larger datasets.
- One model, two QA sets and one metric. BERTScore is an embedding-similarity score; the extraction notes it is a weak judge of factual accuracy. The paper used no exact-match, F1 or judge-based scoring.
- The largest corpus (85k tokens) is above the 32K effective length the paper itself cites for the 8B model, and the paper does not discuss this.
- The extraction notes that the in-context baseline is a weak latency comparison because it recomputes the cache on every query, and that the paper says nothing about cache memory, disk size or corpus updates (a change means re-encoding).
- RAG baselines have no reranking, hybrid retrieval or query rewriting. The extraction judges the title stronger than the data, which backs CAG only for small, bounded corpora.
- Llama 3.1-era models; newer long-context models and provider prompt caches were not tested.

## See Also
- [[RAG Retrieval Strategies]] — alternative-to (retrieval at query time instead of a preloaded cache)
- [[Prefix Caching]] — prerequisite-for (the serving-side KV reuse that CAG depends on)
- [[Long-Context Prompting]] — prerequisite-for (using a long window well)
- [[RAG vs Long Context: Evaluation Evidence]] — related (other head-to-head comparisons, run on different setups)
- [[Semantic Cache for RAG Agents]] — related (a different kind of cache: answers, not attention state)
