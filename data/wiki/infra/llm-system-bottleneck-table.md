---
title: LLM System Bottleneck Table
tags: [infra, llm, reference]
summary: The five recurring bottlenecks in a production LLM system — token overload, queue congestion, vector index bloat, model cold start, rate-limited APIs — each with its cause and the mitigation that follows from the cause.
updated: 2026-08-04
sources:
  - raw/repos/learn-ai-engineering/interviewing--guides--9-system-design--interview-guide.md
---

# LLM System Bottleneck Table

Production LLM systems fail at a small number of recurring places. The value of the table
is not the list but the middle column: each mitigation follows from a mechanism, so
naming the cause tells you which mitigation applies rather than requiring recall.

| Bottleneck | Cause | Mitigation |
|---|---|---|
| **Token overload** | Prompt or response exceeds what the window or budget allows | Truncate, summarize, stream, paginate |
| **Queue congestion** | A slow embedding or model service backs up upstream requests | Shard queues, priority tiers |
| **Vector index bloat** | Stale documents accumulate; index grows without pruning | Prune, compress, periodic rebuild |
| **Model cold start** | On-prem or scale-to-zero deployments spin up on demand | Warm pools, pre-warming |
| **Rate-limited APIs** | Vendor throttling under burst load | Backoff retries, caching, multi-provider fallback |

## Reading the Table by Layer

The five map onto distinct layers of a production LLM system, which is why a design answer
that addresses only one of them reads as incomplete:

- Token overload is a **context** problem — see [[Why Context Is Finite]].
- Queue congestion and cold start are **serving** problems, governed by the prefill/decode
  economics in [[LLM Inference Economics]].
- Vector index bloat is a **retrieval** problem — the index is a mutable store with its own
  lifecycle, not a build artifact.
- Rate limiting is an **integration** problem, and the only one whose mitigation is
  primarily architectural (multi-provider) rather than operational.

## The Non-Obvious One

Vector index bloat is the bottleneck most often missed, because it degrades quality before
it degrades latency. A stale index returns confident, well-formed, wrong answers — the
failure surfaces as a hallucination complaint rather than a performance alert, so it gets
routed to prompt engineering instead of to the ingestion pipeline where it belongs.

## See Also
- [[LLM Inference Economics]] — prerequisite-for
- [[Why Context Is Finite]] — prerequisite-for (the mechanism under token overload)
- [[Safeguards Architecture — Five Protection Layers]] — alternative-to (failure prevention vs failure capacity)
- [[System Design Interview Study Guide]] — instance-of (where this is examined)
