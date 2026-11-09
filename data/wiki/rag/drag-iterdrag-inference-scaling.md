---
title: DRAG and IterDRAG Inference Scaling
tags: [rag, pattern]
summary: "DRAG packs retrieved documents and RAG demonstrations into one long prompt and IterDRAG interleaves sub-query retrieval and answers; with Gemini 1.5 Flash the best configuration's accuracy rises almost linearly with each order of magnitude of input-token budget up to 5M, and a fitted allocation model predicts good settings (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-08-yue-2024-inference-scaling-long-context-retrieval.md
---

# DRAG and IterDRAG Inference Scaling

Yue and colleagues (2024 preprint) ask how RAG performance grows with inference computation that is divided among retrieved documents, demonstrations in the prompt and generation steps, and whether the best allocation for a budget can be predicted. They expect test-time scaling to be modellable from the maximum effective context length.

## Mechanism

- **Effective context length** is the sum of input tokens over every iteration up to the LLM's final answer. This is the compute measure (output tokens and retrieval cost are excluded).
- **DRAG** (demonstration-based RAG): one prompt holds k retrieved documents plus m in-context RAG demonstrations, and a single call produces the answer.
- **IterDRAG**: the query is decomposed into sub-queries in the Self-Ask format, retrieval and intermediate answers are interleaved, with up to 5 iterations.
- A grid over documents, shots and iterations yields the best configuration per budget. The **computation allocation model** regresses the inverse sigmoid of performance on (a + b times i) transposed times log of the parameters, plus c, where i holds dataset-specific terms.

## Results

Self-reported. Setup: Gemini 1.5 Flash, Gecko-1B retriever over Wikipedia passages, about 1.2k sampled examples per dataset, single run; budgets run from 16k to 5M tokens.

- With optimal configurations, performance rises almost linearly with each order of magnitude of inference compute (the paper names this inference scaling laws for RAG). Standard RAG levels off near 128k, DRAG keeps improving to 1M and IterDRAG improves further at 5M. DRAG is best at 16k and 32k tokens, IterDRAG from 128k up; gains shrink past 1M, possibly from long-context modelling limits.
- IterDRAG at 5M tokens on MuSiQue and 2WikiMultiHopQA is well above standard RAG at 128k, and on Bamboogle at 128k it is much higher too (the extraction gives no scores). IterDRAG beats chain-of-thought on 2WikiMultiHopQA at 5 documents and 4 shots. On StrategyQA, accuracy is 61.1 zero-shot, 74.7 many-shot, 74.7 with RAG and 79.0 with DRAG; IterDRAG is highest.
- For a fixed configuration, documents help more than shots. One-hop sets saturate early: TriviaQA peaks at 50 documents, and Natural Questions at 20 with one shot. Recall nears perfect at about 1k documents, yet NDCG and MRR flatten around 100, so extra documents add noise. By merging the sub-query retrievals, IterDRAG raises recall, NDCG and MRR above DRAG.
- In ablation the allocation model with sigmoidal scaling fits best, reaches 96.6 percent of the oracle on unseen datasets at 1M tokens (leave-one-dataset-out), and extrapolates from 128k to 1M with a small gap; 5M is less predictable.

## Limits

- One generator only, so model parameters are model-specific. Single run, no seeds or significance tests; the retriever check uses just 100 MuSiQue examples.
- The compute measure counts input tokens only. Whether adding a re-ranking or refining component changes the scaling is unknown.
- Errors persist in retrieval, reasoning and hallucination; EM, F1 and accuracy mis-score abbreviations and date formats; abstention is not handled. Optimal parameters depend on method, metric and dataset.

## See Also
- [[RAG vs Long Context: Evaluation Evidence]] — related
- [[Self-Ask Prompting]] — prerequisite-for
- [[LongRAG Long Retrieval Units]] — related
- [[Long-Context Prompting]] — related
- [[LongICLBench and Many-Shot ICL Scaling]] — related
- [[RAG Retrieval Strategies]] — prerequisite-for
- [[2WikiMultiHopQA]] — related
