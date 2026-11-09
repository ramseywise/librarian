---
title: Declarative Attention
tags: [infra, concept]
summary: "Declarative Attention prompts a model to declare, in its own output, whether each step attends globally, to chosen chunks, or only locally; a decode-time mask on block tables then cut attended tokens 45.8% on Gemma-4-31B at 1.40 points accuracy cost, with no training (self-reported)."
updated: 2026-11-09
sources:
  - data/raw/papers/2026-11-07-ho-2026-language-models-can-control-their.md
---

# Declarative Attention

Ho et al. (2026) have the model choose its own attention span. A prompt asks it to write tagged segments: a global tag, a focus tag naming chunks to attend to, or a local tag. A finite-state machine parses the output stream and edits vLLM block tables (no kernel change). The mask covers global-attention layers only. The first 16 tokens, the question and instruction, and the response so far are always visible. Context is cut into chunks of roughly 2K tokens, and nothing is evicted, so a later global step can read anything again.

## Results (self-reported)

- Zero-shot with thinking off, over 15 long-context sources (RULER, LongBench, LooGLE, ZeroSCROLLS) and averaging 3 runs: Gemma-4-31B attended 45.8% fewer tokens and Qwen-3.6-27B 19.6% fewer, at accuracy losses of 1.40 and 2.10 points respectively.
- The saving comes from the mask: on Gemma the prompt alone put attended tokens 50.2% above vanilla because generations ran longer, and the mask then cut them by 62.9% from that level.
- Measured decode-step time on one B200 (vLLM): about 3.5% overhead at low mask ratios and 55% saving above 90% masked on Gemma. The net full-response decode time is a roofline estimate, 0.76x on Gemma and 0.87x on Qwen, with prefill excluded.
- Accuracy as a share of vanilla grew with model size, from 29% for Gemma-4-E4B to 98% for the 31B model.
- The roofline analysis puts the global KV read at 94.11% to 99.37% of a decode step at 1M tokens for full-attention models.

## Limits

- Zero-shot only; thinking mode was disabled because models failed to follow the protocol inside thinking tags.
- The 15-source suite is the set where the method works; on six outside sources Gemma lost 30 and 21 points on two.
- With a sparse-attention indexer the per-step scan fell but the total rose to 1.28x of vanilla because decode steps were 2.78x vanilla (per-step scan 0.46 of vanilla). The extraction notes this clashes with the "about a third more" figure in the text.
- No matched-budget comparison with Quest, H2O or SnapKV; end-to-end speedup is estimated, not measured; most results are single runs, and the Qwen savings differed between runs (31.1%, 5.8% and 21.9%).
- The local mode can hallucinate masked content.

## See Also
- [[KV Cache Reduction Methods]] — related (the family this page belongs to)
- [[Lookahead Sparse Attention]] — alternative-to (a separate indexer chooses what stays on GPU)
- [[Native Sparse Attention]] — alternative-to (sparsity trained into the architecture)
