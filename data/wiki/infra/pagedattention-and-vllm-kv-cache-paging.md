---
title: PagedAttention and vLLM KV Cache Paging
tags: [infra, concept]
summary: "PagedAttention stores each sequence's KV cache in fixed-size blocks mapped through a block table, so memory is allocated on demand and shared across samples; vLLM, built on it, reports 2-4x higher serving throughput than FasterTransformer and Orca at the same latency (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-kwon-2023-efficient-memory-management-large-language.md
---

# PagedAttention and vLLM KV Cache Paging

Kwon et al. (SOSP '23) target the waste and duplication in LLM serving memory that cap batch size and throughput. Their answer borrows from operating-system virtual memory: cut every sequence's cache into equal blocks, hand out physical GPU blocks only when needed, and look them up through a per-request block table. Attention then reads from scattered memory.

## Mechanism

- **Blocks and block table.** Keys and values are grouped into equal KV blocks, and the attention computation (Eq 4 of the paper) sums block by block instead of over one contiguous tensor.
- **Sharing.** Reference counts and copy-on-write let parallel samples, beams and prefixes share physical blocks.
- **vLLM.** The engine built on this adds first-come-first-served scheduling, preemption of a whole request at a time (either swapped to CPU or recomputed later), Megatron-style tensor parallelism sharing a single KV manager, and fused CUDA kernels.
- **Why memory matters.** In FP16, OPT-13B needs 800 KB of cache for each token, so a 2048-token request can reach 1.6 GB (the paper's arithmetic multiplies 2, 5120, 40 and 2 bytes). Serving a 13B model on a 40GB A100, about 26GB (65%) goes to weights and more than 30% to the cache.

## Reported results (self-reported)

Setups: OPT 13B/66B/175B and LLaMA-13B on A100 GPUs, ShareGPT, Alpaca and WMT16 traces; Orca baselines are the authors' own re-implementations.

| Measure | Result |
|---|---|
| Throughput versus FasterTransformer and Orca at equal latency | 2-4x |
| KV memory holding token states, Orca variants versus vLLM (OPT-13B) | 20.4-38.2% versus 96.3% |
| Request rate on ShareGPT versus Orca (Oracle) | 1.7-2.7x higher |
| Requests batched on OPT-13B, ShareGPT, 2 reqs/s | 2.2x more than Orca (Oracle), 4.3x more than Orca (Max) |
| Memory saved by sharing, OPT-13B on Alpaca | 6.1-9.8% (parallel sampling, 2-6 samples), 37.6-55.2% (beam search, widths 2-6) |
| Shared prefix, LLaMA-13B on WMT16 | 1.67x (1-shot, 80 tokens), 3.58x (5-shot, 341 tokens) over Orca (Oracle) |

Block size 16 is the default. ShareGPT does best at 16-128 and Alpaca degrades above 32. Recomputing after preemption costs at most 20% of what swapping's latency does.

## Limits

- Orca is not public, so the three Orca baselines (Max, Pow2, Oracle) were rebuilt by the authors around an assumed buddy allocator; the 20-38% memory figure describes those versions, not deployed systems.
- Runs were not repeated, no seeds or intervals are given, and sampling settings such as temperature are missing.
- The advantage narrows when serving is compute-bound (OPT-175B on Alpaca).
- The PagedAttention kernel is 20-26% slower than FasterTransformer's attention kernel (batch sizes 8 and 32).
- The authors say the paging idea is not generally suited to DNN training (shapes are static) or to compute-bound serving of non-LLM models, where the extra indirection may cost performance.
- Nothing keeps the cache between rounds of a chatbot conversation.
- Only OPT and LLaMA-13B on A100 GPUs were evaluated.

## See Also
- [[KV Cache Reduction Methods]] — prerequisite-for
- [[Chunked Prefill and Adaptive Batching]] — related
- [[FlashAttention and FlashAttention-2]] — related (used for the prefill step)
