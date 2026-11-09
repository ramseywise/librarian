---
title: S-LoRA Multi-Adapter Serving
tags: [infra, concept]
summary: "S-LoRA serves thousands of LoRA adapters from one base model by batching the base computation, keeping adapters in host memory, and paging adapter weights and KV cache from one shared GPU pool; it held 7.61 req/s at 2,000 adapters on one A100 (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-sheng-2023-s-lora.md
---

# S-LoRA Multi-Adapter Serving

S-LoRA (Sheng et al., 2023, MLSys 2024) is a serving system for many fine-tuned LoRA adapters that share one base model. The extraction describes the design: the base model's matrix multiply is batched across all requests, and each adapter's low-rank addition is computed separately with custom kernels (a Triton kernel for prefill, a decode kernel modified from Punica). Adapters sit in host memory; the active batch's adapters are copied to the GPU, while adapters for the following batch are guessed from the waiting queue and loaded early. It is built on LightLLM with iteration-level scheduling from Orca.

## Unified Paging

One memory pool serves both KV cache and adapter weights, with a page holding one hidden-dimension vector. A sequence of S tokens occupies S pages; a rank-R adapter occupies R pages. Two ablations (no unified memory, and no custom kernels with padded batched matmul) were worse, but the extraction notes the numbers exist only in plots.

## Results (self-reported)

- Llama-7B, rank 8, one A100 80GB: 8.05 req/s at 5 adapters and 7.61 req/s at 2,000 adapters. Throughput stops falling beyond roughly 100 adapters, which the extraction attributes to a constant number of active adapters per batch.
- The paper reports up to 4x the throughput of vLLM-packed and up to 30x PEFT. The extraction's check: the 4x holds at 5 adapters (8.05 against 2.04 req/s), and the 30x holds at 100 adapters (7.99 against 0.25 req/s), where PEFT ran for a shorter duration.
- Tensor parallelism: adapter communication is small next to base-model communication, and going from 2 to 4 GPUs gave more than 2x throughput (Llama-30B on A100 40GB and Llama-70B on A100 80GB; exact values only in a plot).
- Merging an adapter into the base wins at one adapter (A10G, Llama-7B, mixed ranks), but the paper says it declines past 2 adapters because switching is slow.

## Limits

- The vLLM baseline merges LoRA weights into the base and runs separate processes, so it is not native LoRA serving; vLLM has since added LoRA support, which dates the 4x claim.
- Synthetic traces dominate; the one real trace (Chatbot Arena) has about 26 adapters. In the 2,000-adapter runs most adapters are cold (power-law rates).
- Adapters are applied to the attention Q, K, V and O projections only, excluding the feed-forward module.
- Table 3 combines different request rates and durations; the PEFT baseline was not run with 1,000 or more adapters.
- Systems only: no accuracy evaluation.

## See Also
- [[LLM Inference Economics]] — prerequisite-for (the serving cost model it works inside)
- [[Prefix Caching]] — related (another way of sharing GPU memory across requests)
- [[KV Cache Reduction Methods]] — related (KV memory pressure that shares the pool)
- [[Doc-to-LoRA]] — related (adapters generated per document)
