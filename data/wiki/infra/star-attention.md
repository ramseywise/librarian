---
title: Star Attention
tags: [infra, concept]
summary: "Star Attention encodes a long context in two phases, local blocks each prefixed by an anchor block, then global attention for the query and generated tokens, and reports large speedups over Ring Attention on multi-host Llama inference with small accuracy loss."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-acharya-2024-star-attention.md
---

# Star Attention

Acharya, Jia and Ginsburg ask whether long-context inference can be sped up across several hosts, with no fine-tuning, by letting context tokens attend only locally and reserving global attention for the query and the generated tokens.

**Phase 1** divides the context into contiguous blocks, each b tokens long. Every block except the first is prefixed with the first block (the anchor block, with its original position ids). Each host attends over its own 2b tokens with no cross-host communication, keeps the key-value cache of its non-anchor block and discards the anchor's. **Phase 2** broadcasts the query to every host; each attends to its local cache, and one designated query host combines the local outputs and softmax denominators into global attention through an online softmax (log-sum-exp) merge. Only that host appends to its cache. Communication per token per host is one vector and one scalar, not cache movement. It is applied to pretrained Llama models with FlashAttention per host.

## Results (all self-reported)

- Llama-3-8B-Instruct-1048K, RULER, block 32K, above 128K tokens: up to 11x faster than Ring Attention with 97-100% of accuracy retained; at 1M tokens on 32 A100 GPUs the figures are 16.9x and a 5.32% accuracy loss.
- Llama-3.1-70B-Instruct, RULER: 4.7x at 64K with a 1.44% drop (block 16K, 16 GPUs); 8.7x at 128K with a 7.47% drop (block 16K, 32 GPUs).
- Llama-3.1-8B-Instruct, block one quarter of length: the gain over Ring Attention rises from 1.1x (16K) to 2.7x (128K), accuracy change between -1.90% and +1.17%.
- Averaged over 16K-128K on RULER: 84.44 for Star, 85.21 full attention, 45.07 StreamingLLM, 80.71 MInference. On InfiniteBench (10 tasks): 46.51, 48.06, 14.72 and 34.07 respectively.
- Per-sample time at 128K on 8 A100s in bf16: vanilla runs out of memory, Ring 53 s, Star 20 s.
- Ablations: removing the anchor drops RULER needle-in-a-haystack accuracy by 39.59% at 64K (global attention 99.50); first-block content with its position ids scores 97.61 while a constant-token anchor scores 0.00. Accuracy is best when the anchor equals the block size; one quarter of the sequence length is the recommended block size.
- By category at 32K with block 8K: +16.15% on aggregation, -6.52% on multi-hop tracing against global attention.

## Limits

- Multi-hop tracing degrades because blocks cannot see each other in Phase 1; cross-block communication is left to future work.
- Accuracy falls when blocks are small relative to sequence length (-6.73% at 512K).
- Why the anchor must match the block size is unexplained; the attention-sink account of anchors is a conjecture.
- Speedups are measured only against Ring Attention. Below about 32K tokens vanilla inference is as fast or faster (at 16K the times are 7 s vanilla, 10 s Ring, 9 s Star).
- No variance, seeds or decoding settings; the method assumes prompts of a long context with a brief query and answer after it. The Llama-3.1-8B base model, lacking instruction tuning, behaves anomalously on BABILong.

## See Also

- [[FlashAttention and FlashAttention-2]] — prerequisite-for
- [[Self-Attention Mechanism]] — prerequisite-for
- [[StreamingLLM Attention Sinks]] — related (anchor blocks borrow the sink idea)
- [[MiniMax Sparse Attention]] — related
