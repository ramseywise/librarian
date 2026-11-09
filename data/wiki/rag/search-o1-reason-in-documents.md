---
title: Search-o1 Reason-in-Documents
tags: [rag, pattern]
summary: "Search-o1 wraps a large reasoning model with on-demand web search inside its chain of thought and condenses retrieved pages with a separate Reason-in-Documents pass before injection; gains are clearest on GPQA and multi-hop QA and absent on some code and math sets (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-li-2025-search-o1.md
---

# Search-o1 Reason-in-Documents

Li and colleagues (2025 preprint) ask whether a large reasoning model can search the web in the middle of a long chain of thought, with each batch of retrieved pages summarised before it re-enters the reasoning, so missing knowledge is supplied without derailing it. Their hypothesis is that one-shot, problem-oriented RAG does not fill step-wise knowledge gaps, while agentic search plus a condensing pass does.

## Mechanism

The framework is an inference-only wrapper around QwQ-32B-Preview.

1. The model emits a search query between special tokens, which pauses generation.
2. The top 10 Bing pages are fetched.
3. **Reason-in-Documents**, a separate generation pass by the same model, reads the pages against the earlier reasoning and the current query and returns refined knowledge.
4. The refined text is inserted between result tokens and the reasoning resumes.

The baselines are direct QwQ-32B, standard RAG (RAG-QwQ-32B) and agentic RAG without condensing (RAgent-QwQ-32B, inspired by ReAct).

## Results

Self-reported, QwQ-32B-Preview backbone, Pass@1, Bing top-10.

- GPQA diamond (198 questions, temperature 0.7): Search-o1 63.6 overall against RAgent 61.6, RAG 58.6 and direct 58.1. On the 546-question extended set it scores 57.9 against RAG 54.6 and direct 51.8; on extended chemistry it trails human chemists (40.7 against 72.6).
- Across five reasoning sets (GPQA, MATH500, AMC23, AIME24, LiveCodeBench) the average gain is 4.7 percent over RAgent and 3.1 percent over direct; the paper does not say absolute or relative. LiveCodeBench (112 problems) is 33.0, equal to direct and above RAG (24.1) and RAgent (26.8); AIME24 (30 questions) ties RAgent at 56.7.
- Multi-hop QA (HotpotQA, 2WIKI, MuSiQue, Bamboogle): agentic RAG improves average EM by 23.2 percent over standard RAG, and Search-o1 by 29.6 percent over RAG and 5.3 percent over RAgent (units not stated). HotpotQA EM is 45.2 against 43.0 for RAgent, so condensing adds 2.2; MuSiQue 16.6 against 13.6.
- Single-hop QA (NQ, TriviaQA): agentic and standard RAG come out level, 47.8 and 47.6 average EM. Across six QA sets without retrieval, QwQ-32B direct (30.7 average EM) does not beat Qwen2.5-32B (31.3).
- Read from Fig 3: retrieving one document with Search-o1 beats direct reasoning and ten-document standard RAG on GPQA overall. With direct reasoning the word "perhaps" averages over 30 occurrences per output on GPQA diamond.

## Limits

- A work-in-progress preprint. It reports no variance, seeds or significance tests, does not define Pass@1 and does not state samples per item.
- Search limits and Reason-in-Documents input truncation are not given. No cost or latency is reported despite the extra generation passes.
- There is no gain over direct QwQ on LiveCodeBench or AMC23, and a single backbone is used. Live web results mean reruns can differ.

## See Also
- [[Agentic RAG — Advanced Patterns]] — prerequisite-for
- [[WebThinker Deep Research Agent]] — alternative-to
- [[GPQA]] — related (main science benchmark)
- [[RL for Retrieval Policies]] — related
- [[RAG Retrieval Strategies]] — prerequisite-for
