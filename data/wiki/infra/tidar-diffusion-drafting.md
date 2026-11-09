---
title: TiDAR Diffusion Drafting
tags: [infra, concept]
summary: "TiDAR drafts tokens with one-step diffusion and verifies them autoregressively in the same forward pass using a structured attention mask, filling the idle token slots of memory-bound decoding; 4.71x (1.5B) and 5.91x (8B) decode speedup at batch size 1 on one H100 (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-liu-2025-tidar.md
---

# TiDAR Diffusion Drafting

Liu et al. (NVIDIA, 2025) build on an observation about decoding at small batch: latency stays about flat as more token slots are sent through one forward pass, until the model becomes compute-bound (profiled on Qwen3-32B, H100, batch size 1, in the paper's Figure 1). TiDAR uses those slots.

## Mechanism

Each forward pass has three sections. The prefix reuses its KV cache. The draft tokens from the previous step are verified by autoregressive rejection sampling under causal attention. Mask tokens pre-draft the next step with one-step diffusion, bidirectional inside the block and conditioned on every possible accept length. The base model is also the drafter, rejected tokens' KV entries are evicted, and no KV is recomputed. Training doubles the sequence length by appending an all-mask copy, with loss (alpha·L_AR + L_Diff)/(1+alpha).

## Results (self-reported)

- Single H100, batch size 1, BF16, native PyTorch with Flex Attention, exact KV cache: 4.71x decode throughput for the 1.5B model over Qwen2.5 1.5B and 5.91x for the 8B model over Qwen3 8B, averaged over generative tasks.
- Tokens per forward (T/NFE): 7.45 on average for 1.5B and about 8.2 for 8B.
- Generative average: TiDAR 1.5B 44.03% against 41.64% for its Qwen2.5 initialisation (50B continual-pretraining tokens); TiDAR 8B 65.31% (trust diffusion) or 63.90% (trust AR) against 68.09% for Qwen3 8B (150B tokens, block size 16). The extraction notes the 8B gap is about 2.8 to 4.2 points.
- It beat the authors' block-diffusion baseline and the Dream and LLaDA models on generative quality, and the paper reports higher T/NFE than EAGLE-3 open weights.
- Full-mask training beat random-mask training (average 48.42% against 45.45% at 4 drafts, 1.5B).

## Limits

- All speeds are batch size 1 on one H100; large-batch behaviour is untested and the free-slot premise weakens once decoding is compute-bound.
- Unlike classic speculative decoding, outputs are not guaranteed identical to the base model; it needs continual pretraining, so it cannot be dropped onto an existing model.
- The EAGLE-3 comparison uses an Instruct model with third-party weights against a Base-derived TiDAR, so it is unmatched. Speedups appear only in a figure; no variance anywhere.
- Evaluation covers code, math and multiple choice with 256-512 generated tokens; no long-context or reasoning-model tests.

## See Also
- [[Speculative Decoding]] — prerequisite-for (the draft-and-verify scheme it generalises)
- [[PaSS Parallel Speculative Sampling]] — alternative-to (another single-model drafter)
- [[LLM Inference Economics]] — prerequisite-for (decode is memory-bound at small batch)
