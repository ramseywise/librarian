---
title: Artificial Hippocampus Networks
tags: [foundations, concept]
summary: Artificial Hippocampus Networks (AHN) keep a lossless 32K sliding-window KV cache and fold each token that leaves it into a fixed-size recurrent state, cutting FLOPs and cache at 128K while matching or beating full attention on average scores, but not on exact recall (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-fang-2025-artificial-hippocampus-networks-efficient-long.md
---

# Artificial Hippocampus Networks

Fang et al. (ByteDance Seed, 2025) keep recent tokens exactly (128 sink tokens plus a 32,640-token window) as short-term memory. A small RNN-like module (the AHN, built on GatedDeltaNet or DeltaNet or Mamba2-style layers) compresses each key-value pair leaving the window into a fixed-size state. Below 32K the module never activates, so the model equals the base model there by construction.

Training freezes the base model and trains only the AHN parameters (about 0.4%) by self-distillation: KL divergence to the full-attention teacher on ChatQA2 data, 1B tokens, about 10 hours on 32 A100s for the 7B model.

## Results (self-reported)

- LV-Eval at 128K, Qwen2.5-3B-Instruct, 11 datasets: average 4.41 for full attention against 5.88 for AHN-GDN, with 40.5% fewer FLOPs and 74.0% less cache memory. For 7B: 3.62 full, 5.34 sinks plus sliding window, 6.54 AHN-GDN. For 14B: 4.99, 5.69 and 6.51. InfiniteBench 7B: 13.50 full attention, 16.93 AHN-GDN.
- Gains over an equal-memory sliding window are about 1 point on LV-Eval at 7B and under 1 at 14B.
- Training ablation on Qwen2.5-7B, LongBench average over six tasks: KL loss with a random window 40.59, cross-entropy 39.59, KL with a fixed 1,024-token window 38.53.

## Limits

- Exact recall is lost: RULER-128K needle tasks for Qwen2.5-7B scored about 25 to 28 for AHN and sliding window against 85 to 99 for full attention. LV-Eval fact recall on 14B: 4.31 full, 0.15 AHN.
- Only Qwen2.5-Instruct 3B/7B/14B, mostly at 128K. Absolute LV-Eval scores are low (about 4 to 7), single run, no seeds or intervals, and full attention degrading at 128K helps the comparison (an attention-dilution hypothesis of the authors).
- Needs trained weights and a custom architecture, so it cannot be applied to hosted models. No agent, multi-turn, cross-session or retrieval comparison. The extraction notes some Table 2 and 6 cells are garbled.

## See Also
- [[Recurrent Memory Transformer (RMT)]] — alternative-to
- [[Self-Attention Mechanism]] — prerequisite-for
- [[MiniMax Sparse Attention]] — alternative-to (cut compute by selecting blocks instead of compressing the evicted past)
- [[Why Context Is Finite]] — related
