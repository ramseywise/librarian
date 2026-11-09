---
title: TurboTransformers Variable-Length Serving
tags: [infra, pattern]
summary: "TurboTransformers (PPoPP 2021) serves encoder transformers on GPUs with fused kernels, a sequence-length-aware memory allocator and a dynamic-programming batch scheduler; the paper reports gains on variable-length BERT but parity or losses against tuned fixed-length runtimes."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-fang-2021-turbotransformers.md
---

# TurboTransformers Variable-Length Serving

TurboTransformers targets one problem: transformer requests arrive with different lengths, and runtimes built for fixed lengths either pad or batch badly. The paper combines three pieces.

## Mechanisms

- Kernel fusion and batch reductions: non-GEMM kernels between matrix multiplies are fused, and Softmax and LayerNorm use a multi-element warp reduction. The motivating profile (Tesla V100, BERT) found PyTorch spending 38.2% of its time outside matrix multiplies at batch 20 and length 128, and leaving the GPU idle for 80.64% of a batch-1, length-40 run, which the paper attributes to kernel launch overhead.
- Sequence-length-aware allocator: once a request's length is known, tensor offsets are computed once from the computation graph and packed into chunks. Allocating on demand left 50% of compute idle on a Tesla M40 (batch 20, length 128). Offset scheduling cost 0.07% to 5.77% of inference latency (self-reported); the paper says PyTorch and onnxruntime caches grow after a length-460 request and do not shrink.
- Dynamic-programming batch scheduler: queued requests are sorted by length and batch boundaries come from dynamic programming over a table of measured costs, so that short requests are not padded to the length of long ones. In the paper's worked example (five requests of lengths 17, 18, 52, 63 and 77) three batches beat one batch of five, a 35% throughput gain (illustrative, 20.62 ms against 15.24 ms in the figure).

## Reported results (self-reported)

Setup: BERT on a consumer RTX 2060 unless stated.

- Fixed-length BERT, batch 1 and 20, lengths 10-500: average speedup over PyTorch 1.23x to 2.77x.
- Variable-length BERT, random lengths 5-500: 0.97x to 2.44x over PyTorch, with larger gains on short inputs; 0.88x to 1.05x over onnxruntime (about parity).
- Fixed-length BERT against TensorRT 5.1.5 (offline-tuned): 0.53x to 0.96x, so slower. Against FasterTransformer v1: 0.71x to 1.32x.
- Albert (GEMM-dominated): 1.04x to 1.45x over PyTorch. Seq2seq decoder, source length 28-137: 1.14x to 1.20x.
- At lengths 5-500, naive batching was worse than no batching; the extraction records the serving throughput numbers without values.
- Under DP batching with lengths 2-100, average latency was 24.74 ms at 402 requests per second (minimum 4.23, maximum 57.02), and the scheduler raised long-request latency relative to naive batching.

## Limits

- Everything runs on one consumer GPU, apart from the V100 and M40 motivating profiles; no data-center serving numbers.
- Workloads are synthetic with uniform length distributions; no p99 tail latency, real traffic or accuracy evaluation. No repeats or significance tests, and the compared runtimes (old releases of PyTorch, onnxruntime and TensorRT) have dated.
- Matrix multiplication itself is left unoptimised, so long sequences gain little. The scheduler reorders requests and delays long ones, and needs a warm-up cost table that takes tens of minutes.
- Only encoder models and a small decoder were tested; autoregressive LLM serving, KV caches and continuous batching are out of scope.
- Internal inconsistency noted by the extraction: Table 3 lists hidden_size 4096 for BERT, which does not fit base BERT.

## See Also
- [[Clipper Prediction Serving]] — related (adaptive batching and response cache)
- [[LLM Inference Economics]] — prerequisite-for
- [[Chunked Prefill and Adaptive Batching]] — related (batching under variable length, for LLM serving)
