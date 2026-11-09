---
title: Partitioning Layouts for Transformer Inference
tags: [infra, concept]
summary: "Pope et al. (2022) pick how to shard a large Transformer across TPU chips with an analytical communication-cost model, choosing among 1D and 2D weight-stationary and weight-gathered layouts and sharding multiquery attention over batch; headline numbers are 29 ms per token decode, 76% MFU prefill and up to 32x longer context on PaLM 540B (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-pope-2022-efficiently-scaling-transformer-inference.md
---

# Partitioning Layouts for Transformer Inference

Pope et al. study how to split large Transformers over many chips so generation stays fast at tight latency targets and long contexts. They implement a JAX/XLA inference stack for TPU v4 and an analytical model of communication cost, then use it to select per workload (batch size, context, latency target) among feedforward layouts: 1D weight-stationary, 2D weight-stationary and weight-gathered, plus head-sharded or batch-sharded attention. A sample term in the model is Tcomm = 8BLE / (sqrt(nchips) x network bandwidth). Cost is reported in chip-seconds per token (nchips x time / BL). Models evaluated are PaLM 8B, 62B and 540B and a Megatron-Turing 530B variant, compared by MFU against FasterTransformer. The paper's definitions: prefill is the time to process the input tokens, decode is autoregressive generation, MFU is observed throughput over the theoretical peak with no memory or communication overhead.

## Contributions as stated (self-reported)

- A claim: with dff = 4 dmodel, 2D weight-stationary layouts win over 1D once there are more than 16 chips.
- Multiquery attention sharded over batch permits contexts up to 32 times longer than multihead attention, for PaLM 540B on 64 chips with 30% of memory set aside for the KV cache (the multihead variant uses d_head 128 to hold parameters constant).
- Looped CollectiveEinsum and int8 weights give a new latency-versus-MFU Pareto frontier over FasterTransformer.
- On PaLM 540B with 64 TPU v4 chips and a 2048-token context (2048 prefill tokens, 64 decoded): decode takes 29 ms per token and prefill reaches 76% MFU.
- Low-batch latency scales about as the square root of model size (read off Fig 1, a claim).

The extraction lists the per-configuration measurements without result values, so only the contribution figures above are available here.

## Limits

- Each Pareto point is a single measurement; there are no repeated runs or variance.
- Activation quantisation is not implemented and the int8 large-batch path lacks optimisation, so high-throughput configurations use bfloat16.
- Hardware is a TPU v4 3D torus; generalisation to GPUs is asserted, not measured, and the FasterTransformer comparison is made on different chips and judged by MFU alone.
- The paper concludes FLOPs and communication fundamentally limit dense models; no batch sizes below 4 are reported for batch-sharded multiquery attention.

## See Also
- [[LLM Inference Economics]] — prerequisite-for (prefill, decode and MFU framing)
- [[Multi-Query and Grouped-Query Attention]] — prerequisite-for (the attention variant sharded over batch)
- [[KV Cache Reduction Methods]] — related
