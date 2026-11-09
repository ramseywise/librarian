---
title: "UniversalRAG Modality and Granularity Routing"
tags: [rag, pattern]
summary: "UniversalRAG routes each query to one of seven corpus routes (none, paragraph, document, table, image, clip, video) instead of using one shared embedding space; a trained Qwen3-VL-2B router reached 95.28 modality accuracy (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-yeo-2025-universalrag.md
---

# UniversalRAG Modality and Granularity Routing

UniversalRAG (2025 preprint) keeps a separate index per modality and granularity and trains a router to choose among seven routes: no retrieval, paragraph, document, table, image, clip and video. The alternative it argues against is embedding all modalities into one space. The generator is Qwen3-VL-8B-Instruct, evaluated on 10 benchmarks with a 3:7 train/test split. Routing labels were annotated automatically.

## Results (self-reported)

- Router modality accuracy: 95.28 for the trained Qwen3-VL-2B router against 68.22 for a training-free GPT-5 router.
- Average end-to-end score 42.40, against 42.45 for an oracle router, 37.26 for ParagraphRAG and 34.07 for MultiRAG.
- On out-of-domain data the trained router scored 71.29 against 77.38 for GPT-5.

## Limits

- Routing labels are auto-annotated and noisy. The extraction notes that each benchmark maps one-to-one onto a route, which inflates in-domain router accuracy.
- The theory is a toy model; latency appears as theory plus one plot.
- The main experiments use only two granularity levels per modality.
- The trained router drops below the training-free one out of domain.

## See Also
- [[RAG Retrieval Strategies]] — related
- [[RAG Architecture Selection]] — prerequisite-for
- [[Skill-RAG Failure-State-Aware Retrieval]] — related (both route queries to different retrieval behaviour)
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for
