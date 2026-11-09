---
title: KV Cache Reduction Methods
tags: [infra, concept]
summary: "The KV cache grows with batch, sequence length, hidden size and layers, so reduction methods cut it along different axes (tokens, precision, channels, layers, sparsity); this page maps the axes and records the survey's reported numbers and its caution that sparse attention does not by itself shrink KV memory."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-xu-2024-survey-resource-efficient-llm-multimodal.md
---

# KV Cache Reduction Methods

The survey of resource-efficient models (Xu et al., 2024) gives the single-precision KV cache size as the product of batch, sequence length, hidden size, layers, a factor of 2 for keys and values, and 4 bytes. Each term is an axis a method can attack. See [[LLM Inference Economics]] for why decode makes this cache the long-context bottleneck.

## Axes

- Tokens: evict entries judged unimportant. The survey reports H2O (attention-score eviction) cutting latency by up to 1.9x and raising throughput 29x against unnamed baselines, Scissorhands up to 5x KV memory reduction while maintaining quality, and Dynamic Context Pruning up to 2x throughput. [[LazyLLM Dynamic Token Pruning]] works on this axis.
- Memory management: vAttention reports up to 1.29x throughput over vLLM by using OS and CUDA paging instead of a custom kernel (survey figure). [[Prefix Caching]] shares entries across requests.
- Channels: [[ThinK Key Cache Channel Pruning]] prunes along the hidden dimension.
- Layers: [[YOCO Decoder-Decoder Architecture]] and [[Layer-Condensed KV Cache]] store keys and values for few layers rather than all.
- Sparsity of access: [[Native Sparse Attention]], [[Lookahead Sparse Attention]], [[Declarative Attention]] and [[MiniMax Sparse Attention]] restrict what each query reads; [[Lookahead Sparse Attention]] also moves the rest off the GPU.
- Compressed recurrent state: [[Artificial Hippocampus Networks]].
- Precision: quantised KV. The survey's quantisation numbers are for weights and activations (ATOM 7.73x throughput over FP16 at 4-bit, survey-reported), not KV specifically.

## Caution

The survey states that most sparse attention designs target computational complexity and do not necessarily reduce KV cache memory. A method that reads fewer entries still needs them resident unless it also offloads or never stores them.

## Limits

- Every number is quoted from the cited papers with hardware, models and baselines mostly unstated in the survey; they are not comparable across rows.
- The survey covers work to early 2024; its mapping of methods to these axes beyond the cases it names is this page's grouping, not the survey's.

## See Also
- [[LLM Inference Economics]] — prerequisite-for (the decode memory problem)
- [[YOCO Decoder-Decoder Architecture]] — instance-of
- [[Layer-Condensed KV Cache]] — instance-of
- [[ThinK Key Cache Channel Pruning]] — instance-of
- [[Native Sparse Attention]] — instance-of
- [[Lookahead Sparse Attention]] — instance-of
- [[Declarative Attention]] — instance-of
- [[Speculative Decoding]] — related (the survey's other decode-side lever)
