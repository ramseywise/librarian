---
title: YOCO Decoder-Decoder Architecture
tags: [foundations, concept]
summary: "YOCO splits a language model into a self-decoder with a constant-size cache and a cross-decoder that reuses one global KV cache, so the cache is stored once; at 3B it cut 1M-token inference memory 9.38x and 512K prefill from 180 s to under 6 s (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-sun-2024-you-only-cache-once.md
---

# YOCO Decoder-Decoder Architecture

YOCO (You Only Cache Once; Sun et al., 2024) is a decoder-decoder design. The first half of the layers, the self-decoder, uses efficient attention (gated retention or sliding-window attention) and keeps a constant-size cache. Its output yields one set of global keys and values, K = LN(X)WK and V = LN(X)WV, taken after layer L/2. The cross-decoder in the second half only reads that shared cache. The KV cache therefore holds one global layer, not one per layer.

## Why prefill gets cheaper

The cross-decoder reads the cache without producing it, so prefill can stop after the self-decoder, which is at least half the layers. The paper gives attention prefill cost falling from quadratic to linear in token count N: O(L·N²·D) becomes O(L·N·D), with L layers and width D.

## Results (self-reported)

- Per-token KV memory is about 80x smaller at the 65B size against a Transformer with grouped-query attention (per-token ratio from Figure 8, not an end-to-end run). The same figure gives 128K tokens in 1GB for YOCO against 1.6K for the Transformer.
- 3B model on one H100-80GB, same-size GQA Transformer with Flash-Decoding and kernel fusion, last 1,024 tokens generated: total inference memory 9.38x lower at 1M tokens (12.4GB); prefill at 512K falls from 180 s to under 6 s; throughput at 512K is 43.1 against 4.5 tokens/s (9.6x).
- Quality: YOCO-3B trained on 1.6T tokens averages 0.636 on the LM Eval Harness zero-shot suite, against 0.619 for OpenLLaMA-3B-v2 and 0.612 for StableLM-base-alpha-3B-v2 at 1T tokens. Loss curves match those of a Llama-style Transformer at model sizes 160M through 13B, trained on 10B tokens.
- YOCO-3B-1M, multi-needle retrieval at 128K: scores of 0.98 (1 needle), 0.98 (2), 0.84 (4) and 0.56 (8).

## Limits

- The self-decoder still stores a constant-size cache (footnote 2), so "once" refers to the global KV only.
- Adopting it means training a new architecture from scratch; existing checkpoints cannot be converted.
- Memory and speed numbers are 3B on H100 only; no comparison with other KV-reduction methods (quantization, eviction, latent-attention caches) and no combined runs.
- Scaling comparisons use small token budgets; quality evidence is zero-shot harness scores, needle retrieval and loss curves, with no long-context downstream benchmarks.
- The extraction notes that the mapping of Figure 7-10 ratios to context lengths was inferred from axis order.

## See Also
- [[KV Cache Reduction Methods]] — prerequisite-for (the family it belongs to)
- [[Layer-Condensed KV Cache]] — alternative-to (another way to keep one layer's KV)
- [[Self-Attention Mechanism]] — prerequisite-for (the layer-wise cache it shrinks)
