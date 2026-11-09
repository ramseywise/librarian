---
title: LLM Inference Economics
tags: [infra, llm, concept]
summary: Why prompt tokens and output tokens have different unit costs — the prefill/decode split — and the four levers (quantization, distillation, speculative decoding, output-length discipline) that move serving cost and latency.
updated: 2026-11-08
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--guides--2-llm-fundamentals--interview-guide.md
  - data/raw/repos/sisyphus/interviewing--guides--2-llm-fundamentals--interview-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--llm-fundamentals.md
  - data/raw/papers/2026-11-06-xu-2024-survey-resource-efficient-llm-multimodal.md
  - data/raw/papers/2026-11-07-huyen-ai-engineering-ch09-inference-optimization.md
  - data/raw/papers/2026-11-08-rostam-2024-achieving-peak-performance-large-language.md
---

# LLM Inference Economics

Inference cost is not one number per token. It splits into two phases with different
computational shapes, and nearly every serving optimization is an attack on one of them.

## Prefill vs Decode

| Phase | What it does | Parallelism | Cost per token |
|---|---|---|---|
| **Prefill** | Processes the input prompt | Parallel — all prompt tokens at once | Cheap |
| **Decode** | Generates output tokens | Sequential — one token at a time, each conditioned on the last | Expensive |

Decode is sequential because token *n+1* cannot be computed before token *n* exists. This
asymmetry is the reason output-length discipline matters more than prompt-length
discipline, and why streaming improves *perceived* latency without reducing total cost —
the tokens still arrive one at a time, the user just sees them sooner.

The KV cache is what keeps decode from re-processing the whole sequence at every step;
[[Prefix Caching]] extends the same idea across requests that share a prompt prefix.

A survey of resource-efficient models (Xu et al., 2024) gives the KV cache size in single precision as
the product of batch, sequence length, hidden size, layer count, a factor of two for keys and values, and four bytes per element; see
[[KV Cache Reduction Methods]]. It also states that sparse attention designs aimed at computation do not necessarily
shrink that memory.

## Serving Metrics

- **TTFT** (time to first token) — dominated by prefill; what the user experiences as
  "did it hang?"
- **Tokens/sec** — decode throughput; what the user experiences as reading speed.
- **p95 latency** — the tail that determines whether the system feels reliable. Mean
  latency hides the requests that lose users.

TTFT and tokens/sec are separately optimizable, and they trade against each other under
batching: larger batches raise throughput and hurt TTFT.

## The Four Levers

**Quantization** — serve weights at 8-bit or 4-bit instead of 16-bit. Trades some output
quality for memory footprint and latency. The quality cost is task-dependent and must be
measured, not assumed. Huyen recommends starting with weight-only quantization, which she describes as
simple and effective, and the Rostam survey quotes GPTQ at 3-4 bits per weight for models of
hundreds of billions of parameters in about 4 GPU hours (reported from the original paper).
Quality should be checked after any such optimization, since providers' optimizations can
change model behaviour.

**Distillation** — train a small model on a large model's outputs (the sequence-level variant
is in [[Sequence-Level Knowledge Distillation]]), then route the ~80% of
traffic that doesn't need frontier capability to the small model. The routing decision is
the hard part; see [[RAG Architecture Selection]] for the analogous retrieval-side router.

**Speculative decoding** ([[Speculative Decoding]]) — a small draft model proposes several tokens ahead; the large
model verifies them in a single parallel forward pass. Accepted drafts are free; rejected
ones cost a normal decode step. Net latency win when the draft model agrees often, which
depends on how predictable the output distribution is. Variants and their reported speedups are
in [[Speculative Decoding Variants]].

**Output-length discipline** — the cheapest lever, since decode dominates. Cap
`max_tokens`, ask for structured output rather than prose, and avoid prompting patterns
that invite preamble.

## Why This Shows Up in Design Rounds

A system design answer that says "we'll cache" without distinguishing prefill from decode
is not yet a cost argument. The distinction is what makes the [[LLM System Bottleneck Table]]
mitigations follow from mechanism rather than from a list.

## See Also
- [[Prefix Caching]] — instance-of
- [[LLM System Bottleneck Table]] — extends
- [[Transformer Architecture]] — prerequisite-for
- [[LLM Fundamentals Interview Study Guide]] — instance-of (where this is examined)
- [[Two AI Cost Economies: Durable Once, Contextual On Demand]] — extends (splitting spend by durability of the output)
- [[Right-Sizing a Document-to-LLM Pipeline]] — instance-of (input-token depth dominating a real pipeline's bill)
- [[LazyLLM Dynamic Token Pruning]] — instance-of
- [[LLM in a Flash]] — instance-of (paging weights from flash when DRAM is short)
- [[MoE Expert Offloading]] — instance-of (expert caching and hard quantization on a small GPU)
- [[BitNet b1.58 Ternary Weights]] — instance-of (quantization applied during training)
- [[Scaling Laws for Precision]] — extends (loss as a function of precision)
- [[Speculative Decoding Variants]] — instance-of
- [[Sequence-Level Knowledge Distillation]] — instance-of (distillation lever)
- [[Disaggregated Prefill-Decode Serving]] — instance-of (phase split for serving cost)
- [[Chunked Prefill and Adaptive Batching]] — instance-of
- [[RouteLLM Preference-Trained Routers]] — instance-of (routing between a strong and a weak model)
- [[Goodput and Inference Metrics]] — related
- [[TurboTransformers Variable-Length Serving]] — related
- [[GPU Kernel Tuning Workflow]] — related
- [[Torch Compile and Triton Stack]] — related
- [[GPU Cluster Host, Network and Storage Tuning]] — related
- [[Intelligence per Watt]] — related (efficiency per watt and joule)
- [[Partitioning Layouts for Transformer Inference]] — related (MFU and chip partitioning)
- [[S-LoRA Multi-Adapter Serving]] — related
- [[Clipper Prediction Serving]] — related
- [[Medusa Decoding Heads]] — related (decode-time speedup without a draft model)
- [[DeepSpeed Inference and ZeRO-Inference]] — related
- [[Model Compression Landscape]] — related
- [[ZeRO-Offload]] — related (training-side offload to CPU)
