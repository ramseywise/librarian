---
title: Disaggregated Prefill-Decode Serving
tags: [infra, pattern]
summary: "Disaggregated serving runs prompt prefill and token decode on separate GPU pools so long prefills stop delaying other requests' decode steps; the sources give routing, KV-transfer and sizing guidance, with figures mostly quoted from other work."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch15-multinode-inference-parallelism-decoding.md
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch17-scaling-disaggregated-prefill-decode-inf.md
  - data/raw/papers/2026-11-07-ai-systems-performance-engineering-ch18-advanced-prefill-decode-kv-cache-tuning.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch09-inference-optimization.md
  - data/raw/papers/2026-11-08-rostam-2024-achieving-peak-performance-large-language.md
---

# Disaggregated Prefill-Decode Serving

Prefill is compute-bound and decode is memory-bandwidth-bound. When both run on one GPU, a long prefill delays the decode steps of other requests (interference), and a long prompt at the front of a queue blocks shorter ones behind it (head-of-line blocking). Disaggregation gives each phase its own workers, hardware and parallelism, and ships the KV cache from prefill to decode.

## Design points from the sources

- Decode-centric ingress: the decode worker takes each request in and chooses between prefilling it locally and offloading the prefill. The chapter's guidance is to not offload short prompts or prompts with a large prefix-cache hit, and to compare against effective length, prompt length minus cached prefix length. Example thresholds (prompt length 256, queue depth 10) are illustrative, to be re-tuned when hardware changes.
- Per-phase settings: prefill on high-FLOPS GPUs with high tensor parallelism and low precision; decode with little or no tensor parallelism (often 1), fused kernels and bandwidth-rich GPUs. The parallelism tables are labelled illustrative.
- Prefill batching: latency-first means little batching; throughput-first means 8-32 prompts per batch with adaptive windows of 2-10 ms (claims, no measurement). Padding can reach half of all tokens in mixed-length batches (claim).
- Instance ratio: Huyen cites a prefill-to-decode instance ratio of 2:1 up to 4:1 when long inputs and TTFT dominate, and 1:2 up to 1:1 when short inputs and TPOT dominate (claim, no model or hardware).
- KV transfer: use GPUDirect RDMA or NIXL zero-copy transfer overlapped on a separate stream, and collate small KV pages into payloads of at least 128 tokens. LMCache reports that merging pages brought a 7,500-token transfer down from roughly 20 ms to roughly 8 ms (reported; 470 small transfers against merged pages, model not stated).
- Overload: early rejection, priority tiers and disabling remote prefill for low-priority requests; a minimum role dwell time to stop instances flipping roles.

## Sizing KV

KV bytes per token is 2 x layers x KV heads x head dimension x bytes per element. Worked examples: a 13B multi-head model at FP16 and 4,096 tokens needs about 3.36 GB, and with 8 KV heads about 0.671 GB. A 70B, 80-layer model needs about 1.31 MB per token, about 328 GB at 250,000 tokens, ignoring grouped-query attention. Huyen's figure for Llama 2 13B is 54 GB, with batch 32 and a 2,048-token sequence. A prefill-decode buffer of 1 GB holds roughly 4-8k tokens of FP16 KV for the 70B example (rule of thumb).

## Reported gains (none measured by the authors)

Setups are those of the cited work. DistServe: 7.4x more requests within latency SLOs against an unspecified state-of-the-art baseline, and up to 12.6x tighter SLOs (reported). In DistServe's example (P90 TTFT 0.4 s, P90 TPOT 0.04 s), a single colocated GPU sustained 1.6 requests per second, against 3.3 per GPU for two prefill GPUs and one decode GPU (reported). Splitwise: 4 H100 for prefill plus 4 A100 for decode gave 2.35x the throughput of 8 homogeneous GPUs at matched cost and power, and another configuration 1.4x throughput at 20% lower cost (reported). HexGen-2: up to 2x throughput at the same price, about 1.3x on average (reported). Arrow: up to 5.6x request rate under a shifting workload against a non-adaptive system (reported). The survey by Rostam summarises Splitwise but states no hardware or baselines for it.

## Limits

- No chapter here ran its own experiments; the numbers are quoted from DistServe, Splitwise, HexGen-2, Arrow, LMCache and MLPerf, or are worked examples.
- The extraction notes two slips in chapter 17: a memory subtraction printed with the wrong result, and TPOT named where prefill throughput was meant. Claims that named companies adopted disaggregation are uncited.
- The 70B KV example ignores grouped-query attention, which would shrink it.
- Chapter 15 attributes DistServe numbers without model, hardware or workload.
- Routing weights and autoscale values are illustrative; vLLM flags and Dynamo configs may have dated.

## See Also
- [[Prefix Caching]] — related
- [[Chunked Prefill and Adaptive Batching]] — alternative-to (keeps both phases on one pool)
- [[Goodput and Inference Metrics]] — prerequisite-for
- [[LLM Inference Economics]] — prerequisite-for
- [[Multi-Query and Grouped-Query Attention]] — related (shrinks KV size)
- [[DeepSpeed Inference and ZeRO-Inference]] — related
