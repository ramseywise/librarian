---
title: MiniMax Sparse Attention
tags: [foundations, concept]
summary: MiniMax Sparse Attention (MSA) adds a light index branch that picks 16 blocks of 128 key-value tokens per query group, cutting attention FLOPs 28.4x at 1M tokens versus dense GQA while staying close to full-attention quality at 109B scale; it reduces bytes read, not bytes stored (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-lai-2026-minimax-sparse-attention.md
---

# MiniMax Sparse Attention

Lai et al. (MiniMax, 2026) add an Index Branch to grouped-query attention: one index query head per KV group and one shared index key head. Token scores are max-pooled into block scores and the top-k blocks are chosen per GQA group, with the local block always kept. Each query then attends to a fixed 16 blocks of 128 tokens (2,048 tokens), so per-query attention cost does not grow with context. The indexer is trained with a KL loss to the group-averaged main attention, with stop-gradient and a short full-attention warmup. A specialised top-k kernel and KV-outer iteration are part of the system.

## Results (self-reported)

- At 1M tokens, 64 query heads and 4 KV heads: 28.4x lower attention FLOPs (analytic), 14.2x prefill and 7.6x decode attention-kernel speedup on H800. These are kernel latencies, not end-to-end serving.
- A 109B-parameter MoE with about 6B active parameters was trained from scratch (MSA-PT) or converted from a GQA checkpoint with 400B tokens of continued pre-training (MSA-CPT). Scores for full attention, MSA-PT and MSA-CPT in that order: MMLU 67.0, 67.2, 66.8; on GSM8K 76.2, 77.7, 73.7; on HumanEval 61.0, 64.0, 57.9; and RULER at 32K 75.0, 77.5, 75.7.
- Following long-context extension (about 140B tokens), the converted model stayed close to full attention at 128K: HELMET 46.53 against 45.93, RULER 72.00 against 72.12.
- A FLOP-matched sliding window had higher perplexity on agent-task text in a 10B pilot.

## Limits

- No KV-memory or cache-size figure and no serving throughput. The extraction notes that the selector reads from a full stored cache, so contrasting this with cache-size reduction is the extractor's reading.
- Gaps are benchmark-dependent (MSA-CPT is below full attention on GSM8K, HumanEval and ChartQA) and there are no error bars. The authors name a remaining long-context retrieval gap (Rerank/RAG about 2 points lower at 128K).
- Compared only with the authors' own GQA baseline; no head-to-head against other sparse methods. One configuration at 109B.

## See Also
- [[Self-Attention Mechanism]] — prerequisite-for
- [[Artificial Hippocampus Networks]] — alternative-to
- [[LazyLLM Dynamic Token Pruning]] — alternative-to
- [[LLM Inference Economics]] — related
