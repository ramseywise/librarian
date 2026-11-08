---
title: AgentIR Reasoning-Aware Retrieval
tags: [rag, pattern]
summary: Embed the deep-research agent's current reasoning trace together with its search query, and train a retriever on that pairing; reported to raise end-to-end accuracy on BrowseComp-Plus without any reranking call.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-chen-2026-agentir.md
---

# AgentIR Reasoning-Aware Retrieval

A deep-research agent writes a reasoning trace before each search call. AgentIR feeds that trace plus the query to the retriever as one input, on the argument that the trace costs nothing extra (unlike a separate query-expansion call). The retriever, AgentIR-4B, is a LoRA fine-tune of Qwen3-Embedding-4B trained on DR-Synth: 5,238 instances taken from 250 correctly answered rollouts of the Tongyi-DR agent over 500 WebShaper questions. Labels come from an oracle listwise reranker run over 50 candidates and the gold passage; its first pick is the positive and its last 7 are hard negatives. All numbers are the paper's (self-reported); setup is BrowseComp-Plus with five returned snippets of 512 tokens each, accuracy judged by an LLM, one run per cell.

## Reported results

- **Main result.** With Tongyi-DR, accuracy 66.27% against 48.67% for the Qwen3-Embedding-4B backbone, 50.72% for the 8B model, 51.03% for ReasonIR-8B and 33.98% for BM25. On gpt-oss-120B (high) 66.99 against 47.59, and on GLM-4.7 64.66 against 50.48, although training used Tongyi-DR rollouts only.
- **Versus reranking.** About 10 points above the backbone plus a Qwen3-8B listwise rerank of the top 20 (55.66).
- **Fewer searches.** Search calls per run fall from 32.92 (BM25) to 25.91; recall of evidence rises from 59.90 to 78.86 (Tongyi-DR).
- **Ablation on the 4B backbone, Tongyi-DR.** Reasoning concatenated without training 55.54; training without reasoning 59.40; both 66.27. On GLM-4.7 the untrained reasoning variant is flat (50.90 against 50.48).
- **What not to add.** HyDE-style query expansion without agent state scored 31.08 (below BM25). Adding prior queries and reasonings gave 63.13, and also adding retrieved documents gave 60.00. In the docs variant, 11.45% of runs had zero recall and averaged 37.46 search turns against 27.18 overall.

## Limits

- One benchmark with a fixed corpus, no seeds or confidence intervals; gaps of 1 to 3 points between history variants are weak evidence.
- Training used one agent and one corpus; transfer was tested on two other agents. It needs an agent that exposes reasoning traces, plus fine-tuning.
- Because the oracle reranker sees the gold answer, it can only produce training labels. The Agentic-R comparison differs in backbone and data.
- Internal inconsistency: the abstract's 68% and 52% figures are the with-visit variants (68.07 and 51.93); without the visit tool the figures are 66.27 and 50.72.
- That variant combining prior queries and documents was cut to fit context, which may understate its score.

## See Also
- [[RAG Reranking]] — prerequisite-for
- [[RL for Retrieval Policies]] — related
- [[Deep Research Agent Systems]] — related
