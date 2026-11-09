---
title: "MASS-RAG"
tags: [rag, pattern]
summary: "MASS-RAG is a training-free multi-agent filter for retrieved passages: three agents (summarizer, extractor, reasoner) feed a synthesis agent; it led on several QA columns but its headline gains are relative percentages (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-06-xiao-2026-mass-rag.md
---

# MASS-RAG

MASS-RAG (2026 preprint) places three role-specific agents between retrieval and answering: a Summarizer, an Extractor and a Reasoner each process the retrieved passages, an optional Answer Agent drafts a response, and a Synthesis Agent produces the final output. No training is used. Retrievals are the Contriever results released with Self-RAG.

## Results (self-reported)

Scores below are given in the order TriviaQA, PopQA, ARC-C (accuracy), then ASQA EM, rg and mau.

- MASS-RAG on Llama3 8B: TriviaQA 76.7, PopQA 64.2, ARC-C 78.7; ASQA 47, 35.2, 55.2.
- MAIN-RAG on Llama3 8B: TriviaQA 74.1, PopQA 64.0, ARC-C 61.9; ASQA 39.2, 42.0, 70.6.
- Self-RAG 7B: TriviaQA 66.4, PopQA 54.9, ARC-C 67.3; ASQA 30.0, 35.7, 74.3.
- Plain RAG on Qwen3 8B: 72, 62.1, 86.4; ASQA 46.1, 35.7, 16.1.
- Cost is estimated at 7x calls with the Answer Agent and 4x without, an analytic figure at 100 tokens per call.

## Limits

- The paper labels its gains absolute, but the extraction notes they are relative percentages; raw gaps over MAIN-RAG are +2.6, +0.2, +16.8 and +7.8.
- Internal inconsistency: Table 3 shows TriviaQA Mistral at 77.5 against 73.7 in Table 1.
- Baselines marked with an asterisk are copied, not rerun. One retriever, 7B to 8B models, no multi-hop set. No equal-compute comparison.
- Prompts are not given verbatim.

## See Also
- [[Multi-Agent Context]] — related
- [[RAG Retrieval Strategies]] — related
- [[Astute RAG]] — alternative-to
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for
