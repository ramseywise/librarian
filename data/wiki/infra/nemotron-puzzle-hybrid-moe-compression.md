---
title: Nemotron Puzzle Hybrid MoE Compression
tags: [infra, concept]
summary: "Static, hardware-aware pruning of a hybrid Mamba/MoE/attention model by Puzzle search plus distillation, then quantization and MTP drafting; the 75B-A9B result reaches 2.03x server throughput at matched user speed on 8xB200 for about 1.2 points lower average accuracy (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-bercovich-2026-nemotron-labs-3-puzzle-75b.md
---

# Nemotron Puzzle Hybrid MoE Compression

Bercovich et al. (NVIDIA, 2026) compress a 120.7B-total, 12.8B-active hybrid model (Nemotron 3 Super) into a 75.3B-total, 9.3B-active one. The extraction stresses that this is static structural pruning, rather than early exit or layer skipping, so the architecture stays fixed once training ends. Stages: Puzzle search with healing by distillation, iterated three times (MoE weights to 75%, then 60%, then activated routed experts to 50%), then FP8 or NVFP4 quantization, then a shared MTP head for speculative drafting. The final model has 88 blocks, split 40 Mamba, 40 MoE and 8 attention, with attention untouched and routed-expert capacity highly uneven across depth. For Mamba layers, pruning the SSM state from 128 to 96 channels gave a 1.2-1.3x decode kernel speedup at batch 8-512.

## Results (self-reported)

- Server throughput at matched per-user speed, 8xB200, NVFP4 weights, FP8 KV, single-step decoding: 2.03x (8K input/64K output, 100 tokens/s per user) and 1.60x on the prefill-heavy 50K/2K shape.
- With MTP at draft length 3 (8K/64K, 100 tokens/s per user): speed relative to Super single-step was 3.04x for Super with MTP, 2.03x for Puzzle single-step and 4.63x for Puzzle with MTP. Average accuracy 70.74 against 71.93.
- Throughput should be adjusted for verbosity: the 30B Nano has 5.84x raw tokens/s but 3.87x requests per minute.
- One H100 at 1M-token context: weights about 44.5GB against about 70GB, allowing 8 concurrent requests where the parent manages 1 (NVFP4, KV about 4GB per request).
- Iterative Puzzle scored 0.57 average points above one-shot pruning to the same size (69.05 against 68.48, single runs).

## Limits

- Needs over 120B distillation tokens across stages plus long-context distillation and RL; RL helped little; ablations have no variance.
- The accuracy cost is non-trivial: roughly 1.2 points lower on average, with SWE-Bench 2.6 lower and Arena-Hard 4 lower.
- Vendor hardware, kernels and models only; no independent replication.
- Internal inconsistencies in the paper: the prose gives 2.18x, 4.85x, 3.57x and 5.14x where Table 4 gives 2.03x, 4.63x and 3.04x, so this page uses the table. The body names 1.6x as the design target while the introduction says 2x, and a visible TODO remains in the MTP section.
- The 4x figure for the H100 1M-context comparison sets different batch sizes against each other (8 against 1).

## See Also
- [[LLM Inference Economics]] — prerequisite-for (throughput at a latency target and the prefill/decode split)
- [[Speculative Decoding]] — related (the MTP stage)
- [[MoE Expert Offloading]] — related (another way to fit a large MoE on less memory)
- [[BitNet b1.58 Ternary Weights]] — related (quantization during training versus after)
- [[Deep Compression Pipeline]] — related
- [[Model Compression Landscape]] — related
