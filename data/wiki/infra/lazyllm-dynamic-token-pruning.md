---
title: LazyLLM Dynamic Token Pruning
tags: [infra, concept]
summary: LazyLLM prunes prompt tokens layer by layer during prefill using the last token's attention, lets pruned tokens return later, and cut time to first token 2.34x on multi-document QA with under 1% score loss on Llama 2 7B, without training (self-reported).
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-fu-2024-lazyllm.md
---

# LazyLLM Dynamic Token Pruning

Fu et al. (2024) note that prefill is a large share of long-prompt latency: for Llama 2 7B on LongBench (average prompt 3,376 tokens, 68 generated), time to first token is 21 decode steps and about 23% of total time (self-reported).

## Mechanism

- Each layer scores prompt token i by the head-averaged attention it receives from the last token. Tokens under a per-layer percentile cut are pruned, and stay pruned in all later layers.
- Pruning is progressive: more tokens kept in early layers, fewer in later ones, because later layers tolerate pruning better.
- Pruned tokens may return at later generation steps. An auxiliary cache keeps their hidden states, so no token is computed more than once per layer and the worst case is never slower than the unpruned baseline.
- No training or model change.

## Results (self-reported)

Llama 2 7B and XGen 7B on LongBench, run on an A100 and timed by wall-clock after five warm-up runs.
- Multi-document QA: 2.34x faster first token (Llama 2, score 22.31 against 22.43) and 2.65x (XGen). Up to about 3.0x with up to 10% accuracy loss.
- Other tasks (Llama 2 / XGen speedup): single-document QA 1.36x / 1.96x, summarisation 1.46x / 1.91x, few-shot 2.19x / 3.42x, synthetic 2.89x / 4.77x, code 1.94x / 3.47x. The largest accuracy drop is code on Llama 2 (55.18 to 53.30).
- Random token drop and one-shot static pruning lost far more accuracy at similar speed. Prompt compression made first-token time slower than baseline (0.10x to 0.49x) because of its own overhead.
- Overall generation sped up 1.01x to 1.79x (Llama 2); summarisation barely gained since it computes 99.59% of tokens.

## Limits

- Only 7B models on LongBench, HuggingFace transformers on A100, batch size not stated, no serving-system results.
- The exact pruning schedule is not given. Revival's value rests on the comparison with static pruning, not a dedicated ablation. Interaction with FlashAttention and speculative decoding is not examined. There is no limitations section.

## See Also
- [[LLM Inference Economics]] — prerequisite-for
- [[Prefix Caching]] — related
- [[MiniMax Sparse Attention]] — alternative-to
- [[Context Window Budgeting]] — related
- [[StreamingLLM Attention Sinks]] — related
