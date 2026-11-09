---
title: "RAG+ Application-Aware Retrieval"
tags: [rag, pattern]
summary: "RAG+ attaches pre-aligned worked application examples to each retrieved knowledge item, with no retriever change or fine-tuning; gains were large on a legal task and small or negative on several medical cells (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-wang-2025-rag.md
---

# RAG+ Application-Aware Retrieval

RAG+ (2025 preprint) builds, offline, a second corpus of application examples (worked uses of a knowledge item) and links each knowledge item to its examples, either by generating examples or by matching existing ones. At query time the retriever returns knowledge items as usual and the linked examples are appended to the prompt. The retriever and the generator are unchanged. Setup: a Dify pipeline, BGE-M3, top 3, results averaged over 3 runs.

## Results (self-reported)

- Legal, CAIL2018 Article 234, 200 samples: Qwen2.5-72B with reranked RAG went from 77.5 to 87.5.
- MedQA, 500 samples: LLaMA3.3-70B with reranked RAG went from 81.0 to 85.6. Qwen2.5-7B on MedQA went from 59.20 to 57.60, a drop.
- Math (self-built Numerical Analysis set, 430 questions): 70.47 to 73.72.
- GraphRAG often scored below the plain baseline in the same tables.

## Limits

- Internal inconsistencies: the abstract's peak gain of 13.5% was not located in the tables by the extraction. The text calls the LLaMA3.3-70B legal gains marginal while its own Table 2 shows 70.5 to 76.0.
- The application corpus is costly to build and LLM-generated. Evaluations are small and partly self-built, with possible contamination; most cells show ±0.0 variance.
- No comparison against retrieved few-shot examples or against more chunks at the same token budget.

## See Also
- [[RAG Retrieval Strategies]] — related
- [[Few-Shot Prompting]] — related
- [[Contextual Retrieval]] — alternative-to
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for
