---
title: Native Sparse Attention
tags: [foundations, concept]
summary: "Native Sparse Attention (NSA) pretrains a model with three gated attention branches (compressed blocks, top-n selected blocks, sliding window) and Triton kernels, reporting 9.0x forward and 6.0x backward speedup over Triton FlashAttention-2 at 64k with quality at or above full attention on a 27B MoE (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-yuan-2025-native-sparse-attention.md
---

# Native Sparse Attention

Yuan et al. (preprint, 2025) argue that sparse attention is usually applied at inference to a model trained with full attention. NSA is trained sparse from the start. Per query it sums three branches with learned gates: attention over compressed blocks, over top-n selected blocks, and over a sliding window, each with its own keys and values. Block selection is shared across a GQA group, and the kernels are written for arithmetic intensity, how many compute operations are done per memory access.

## Results (self-reported)

- Speed, 8-GPU A100, GQA g=4, 16 heads, Triton kernels, 64k tokens: forward 9.0x and backward 6.0x faster than Triton FlashAttention-2.
- Decode speed at 64k is an expected figure from memory-access volume (5632 against 65536 tokens loaded), not a timed run. The paper estimates softmax attention at 70-80% of decode latency at 64k.
- Quality: a 27B-total, 3B-active GQA and MoE model pretrained on 270B tokens beat its full-attention twin on 7 of 9 general metrics and on the average LongBench score against the sparse baselines, and reached perfect 64k needle retrieval.
- Reasoning: after 10B tokens of SFT on 32k distilled R1 traces (temperature 0.7, nucleus 0.95, 16 samples per problem), NSA was compared with full attention on AIME 24 at 8k and 16k generation limits.
- In a 3B ablation, two other block-selection schemes (an auxiliary loss, and a heuristic with no extra parameters) reached worse loss than NSA.

## Limits

- Token count is printed as 260B in the introduction and 270B in Section 4.1.
- Pretraining corpus, optimiser, learning rate, batch size, training hardware and seeds are not stated; single run per model, no variance.
- Sparse baselines are inference-only on a full-attention model, so native training and method are confounded.
- Efficiency is measured only on A100 against Triton FlashAttention-2; reasoning evaluation is SFT distillation only and AIME 24 is small.

## See Also
- [[KV Cache Reduction Methods]] — related (the family this page belongs to)
- [[Self-Attention Mechanism]] — prerequisite-for
- [[MiniMax Sparse Attention]] — alternative-to
- [[FlashAttention and FlashAttention-2]] — related (the speed baseline)
