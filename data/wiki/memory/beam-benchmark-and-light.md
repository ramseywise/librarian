---
title: "BEAM Benchmark and LIGHT Memory Framework"
tags: [memory, reference]
summary: "BEAM is a synthetic benchmark of 100 conversations and 2,000 questions from 100K to 10M tokens across ten memory abilities; LIGHT adds working memory and a scratchpad to retrieval and gained most over plain long context at 10M (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-tavakoli-2025-beyond-million-tokens.md
---

# BEAM Benchmark and LIGHT Memory Framework

## BEAM

100 synthetic conversations with 2,000 questions over 10 abilities, at lengths from 100K to 10M tokens (self-reported). Abilities include summarization, preference following, information extraction, temporal reasoning, instruction following, multi-hop reasoning, contradiction resolution and abstention.

## LIGHT

LIGHT combines three memories: an episodic retrieval index, a working memory and a scratchpad with noise filtering. The RAG baseline embeds each user-assistant turn pair (bge-small, FAISS, top-5); LIGHT uses the same retriever plus the other two.

## Results (self-reported)

Scores average 10 abilities over four backbones; the vanilla setting puts the full history in context, and at 10M, where nothing fits, each model gets the most recent segment it can hold.
- Vanilla long-context averages fell from 0.24-0.28 at 100K to 0.104-0.133 at 10M.
- LIGHT gains over vanilla were relative: +49.1% at 100K (one backbone) and +155.7% at 10M (another). Against RAG the margin is a few absolute points (Qwen at 100K, 0.269 against 0.311) and LIGHT lost to RAG on one backbone at 10M (0.216 against 0.192).
- Ablation on a 32B Qwen: at 10M, dropping any single component lost between 3.7 and 8.5 points, while at 100K to 1M dropping working memory gave a slight gain.
- Retrieval k=15 beat the default k=5 and k=20 did not improve; sparse retrieval helped slightly up to 1M and dense was better at 10M.
- Contradiction resolution was near zero for every method (about 0.01-0.05), and LIGHT often did worse than RAG on abstention (0.800 against 0.575 for one model at 100K).

## Limits

- Synthetic conversations, small or older models, single runs, and mixed relative and absolute units in the paper's prose. Table 10 contains a typo, and one ablation table does not name its model (the extraction infers Qwen).
- The headline gains are against vanilla long-context, not the strongest baseline.

## See Also
- [[Multi-Session Agent Benchmarks]] — related
- [[Memory-Augmented Conversational RAG]] — related
- [[Memory Lifecycle]] — related
- [[Context Window Budgeting]] — related
