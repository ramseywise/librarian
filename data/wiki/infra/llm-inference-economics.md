---
title: LLM Inference Economics
tags: [infra, llm, concept]
summary: Why prompt tokens and output tokens have different unit costs — the prefill/decode split — and the four levers (quantization, distillation, speculative decoding, output-length discipline) that move serving cost and latency.
updated: 2026-08-04
sources:
  - raw/repos/learn-ai-engineering/interviewing--guides--2-llm-fundamentals--interview-guide.md
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
measured, not assumed.

**Distillation** — train a small model on a large model's outputs, then route the ~80% of
traffic that doesn't need frontier capability to the small model. The routing decision is
the hard part; see [[RAG Architecture Selection]] for the analogous retrieval-side router.

**Speculative decoding** — a small draft model proposes several tokens ahead; the large
model verifies them in a single parallel forward pass. Accepted drafts are free; rejected
ones cost a normal decode step. Net latency win when the draft model agrees often, which
depends on how predictable the output distribution is.

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
