---
title: Chunked Prefill and Adaptive Batching
tags: [infra, pattern]
summary: "Chunked prefill splits a long prompt into pieces so decode steps can interleave, and adaptive batching tunes batch size and delay to load; the source rules of thumb are mostly unmeasured."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-ai-systems-performance-engineering-ch16-profiling-debugging-tuning-inference-sca.md
  - data/raw/papers/2026-11-08-ai-systems-performance-engineering-ch19-dynamic-adaptive-inference-engine-optimi.md
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch17-scaling-disaggregated-prefill-decode-inf.md
---

# Chunked Prefill and Adaptive Batching

## Chunked prefill

A long prefill can stall running decodes. Chapter 19 describes SARATHI-style chunked prefill with decode piggybacking, which it says raises throughput over naive scheduling (reported, no setup). Rule of thumb from the chapter: pick a chunk size so one chunk takes about 50-100 ms. Illustration: cutting one 10,000-token prefill into five chunks of 2,000 tokens leaves gaps where decode steps can run.

Chunking changes scheduling, not work. Chapter 16's worked example: a 20K-token prompt costs 200M QK operations at chunk sizes of 20K, 10K or 5K, and MLP tokens total 20K in all cases.

## Latency-aware scheduling

Chapter 16's example: with two GPUs and six prompts (two of 6K tokens and four of 2K) arriving together, cost-aware placement rather than first-in-first-out cut the critical-path self-attention work by about 42% (22,005,000 against 38,007,000 QK operations; assumes a variable-length fused kernel with no padding).

## Batching rules of thumb (claims, none measured)

- Dynamic batching delay of 2-10 ms; start at 1-2 ms, 0 ms at low load up to 5-10 ms at peak. A utilisation heuristic: above 80% allow larger batches, below 20% use batch size 1.
- On large models, moving from one or two requests per batch to four to eight can double or triple throughput. Target 90% of peak throughput as headroom, for example cutting the batch limit from 16 to 8.
- Concurrent decoding on multiple streams: an illustrative server went from 60% to 95% utilisation and doubled throughput.
- Chapter 17 sets continuous batching explicitly with the engine's maximum sequences and batched-token limits to bound KV memory.

## KV memory levers

Quantizing KV from INT8 to INT4 halves KV memory (arithmetic); quantized KV gives 2-4x reduction (claim). The chapter suggests an 80% GPU memory high-watermark that triggers 8-bit KV compression (no data). Without a good allocator fragmentation is put at 20-30%, which paging cuts to a few percent (claim). Offloading KV to CPU memory while prefetching a layer early carries a modest throughput cost (illustrative).

## Limits

- Chapter 16 says its metric tables are illustrative; chapter 19's tables 19-2 and 19-3 are approximate with no model, hardware or dataset. Chapter 19 code listings are truncated in the extraction.
- Cited speedups (SARATHI, FlashAttention-3) come without reference entries.

## See Also
- [[Disaggregated Prefill-Decode Serving]] — alternative-to
- [[Prefix Caching]] — related
- [[FlashAttention and FlashAttention-2]] — related
- [[TurboTransformers Variable-Length Serving]] — related
