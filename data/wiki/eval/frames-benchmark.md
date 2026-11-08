---
title: FRAMES Benchmark
tags: [eval, rag, llm, reference]
summary: "FRAMES is an 824-question multi-hop Wikipedia benchmark that scores factuality, retrieval and reasoning together; the paper's multi-step BM25 loop with search-planning prompts took Gemini-1.5-Pro from 0.408 to 0.66."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-krishna-2024-fact-fetch-reason.md
---

# FRAMES Benchmark

FRAMES (arXiv 2409.12941) has 824 questions, each needing 2 to 15 Wikipedia articles. About 36% need two articles, 35% three and 16% four; about 36% carry multiple constraints and 20% need numerical reasoning. The authors had an LLM draft questions first, but over 30% were hallucinated, so humans wrote the final set. Yes/no questions were dropped because a guess succeeds half the time, and questions carry date anchors. Re-annotation after three months dropped 5.5% of samples whose answer had changed. Grading is by an LLM autorater, whose agreement with human grading was 0.96 accuracy and 0.889 kappa (self-reported, measured on Gemini-Pro-1.5-0514's own answers).

## Results (all self-reported)

Setup: Gemini-Pro-1.5-0514 unless stated, BM25 over a Wikipedia dump.

| Condition | Accuracy |
|---|---|
| No retrieval, Pro | 0.408 |
| No retrieval, Flash and Gemma2-27b | 0.263 and 0.308 |
| No retrieval, Llama3.2-3B and Qwen2.5-3B | 0.115 and 0.095 |
| Single-step BM25, 2 docs then 4 docs (Pro) | 0.452 then 0.474 |
| Oracle (all gold articles in the prompt, Pro / Flash) | 0.729 / 0.665 |
| Multi-step, vanilla, (k,n,n_docs) = (5,5,2) | about 0.45 rising to about 0.52 |
| Multi-step with search-planning prompt, (5,5,10) | 0.66 |

About 80% of the oracle errors fell in numerical, tabular and post-processing categories, so reasoning, not retrieval, limits the oracle run.

## The multi-step loop

The model writes k search queries per step for n steps; BM25 returns n_docs per query, and only documents not already in context are added; a final call answers. Vanilla multi-step improves slowly because the generated queries lack diversity (the authors observed the model going the wrong way and not correcting). A planning prompt (sample query sequences, a rule against repeating queries, and a step-by-step cue) brought 0.66 against the 0.73 oracle. It costs six non-parallelizable inference calls.

## Limits

- Possible pretraining contamination (Wikipedia), acknowledged by the authors; limited query diversity.
- BM25 over Wikipedia only, held fixed on purpose; no dense retriever, reranker or web search. Multi-step results are for Gemini-Pro-1.5-0514 only.
- The planning-prompt parts were changed together, so no ablation says which matters. The 0.66 comes from a plot; the text has no grid table.
- Single-step context recall was low (0.12 to 0.15). The models are 2024 vintage.

## See Also
- [[RAG Evaluation]] — prerequisite-for (where multi-hop retrieval benchmarks sit)
- [[FreshQA]] — related (also date-anchored; the FRAMES authors cite it for anchoring)
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for (multi-step retrieval with planning)
- [[Sufficient Context Autorater]] — related (separating retrieval from reasoning errors)
