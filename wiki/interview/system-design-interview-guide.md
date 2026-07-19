---
title: System Design Interview Study Guide
tags: [interview, reference]
summary: Method guide for the ML/LLM/agent system design round — 5-step process, trade-off narration formula, LLM reference architecture, bottleneck table, and failure mode reflexes.
updated: 2026-07-19
sources:
  - raw/repos/learn-ai-engineering/interviewing--guides--9-system-design--interview-guide.md
---

# System Design Interview Study Guide

The highest-weight technical round in 2026 AIE/MLE loops. This guide covers the method; domain content lives in [[RAG Interview Study Guide]], [[Agents Interview Study Guide]], and [[Evals and Observability Interview Study Guide]].

## The 5-Step Process (45–55 min, ~8 min/step)

1. **Clarify & scope** — never design against the raw prompt.
   - "Who are the primary users, and what's the top priority — latency, accuracy, cost, safety? That drives every trade-off downstream."
   - "Does the system touch personal/financial data — must it stay on-prem or can we call third-party model APIs?"

2. **Requirements split** — functional (multi-turn? autocomplete vs summarization?) vs non-functional (latency, consistency, scale, security). Write the non-functionals down — they're the trade-off axes.

3. **Design** — components, data flow, APIs; connect every choice back to a requirement, out loud.

4. **Identify shortcomings** — name your design's weaknesses before the interviewer does; propose what you'd do differently under different constraints.

5. **Iterate** — curveballs are deliberate adaptability tests.

## Trade-Off Narration Formula

**Consider 2–3 solutions → narrate pros/cons → ask which priority wins → justify the pick.**

("I'd compromise X for optimal Y — here's why that hurts least given the priority.")

Trade-offs live between non-functionals: latency↔accuracy, cost↔quality, consistency↔availability, full-automation↔safety, read↔write throughput, storage↔caching.

If told your trade-off was wrong: adapt visibly ("with that requirement, option B's consistency guarantee wins"). No points for stubbornness.

If you hit a knowledge gap: "my understanding there is superficial" — buys credibility and redirects time to areas you're strong in.

## LLM-System Reference Architecture

```
Client
  → API gateway (authn, rate limits, quotas)
  → orchestration (workflow/agent graph)
  → {retrieval: query rewrite → hybrid search → rerank}
  + {generation: prompt assembly → streaming LLM with fallback chain}
  → output validation/guardrails
  → response

Sidecars: caches (prefix + semantic), state store (session/checkpointer),
          trace/observability, eval pipeline, HITL queue
```

For each box: know its failure mode and its scaling story.

## Bottleneck Table

| Bottleneck | Cause | Mitigation |
|---|---|---|
| Token overload | prompt/response too large | truncate, summarize, stream, paginate |
| Queue congestion | slow embedding/model service | shard queues, priority tiers |
| Vector index bloat | stale docs | prune, compress, periodic rebuild |
| Model cold start | on-prem spin-up | warm pools, pre-warming |
| Rate-limited APIs | vendor throttling | backoff retries, caching, multi-provider |

## Failure Mode Reflexes

- Prompt crashes model → detect known patterns
- Irrelevant retrieval → thresholds, metadata filters
- Mid-stream failure → graceful fallback to full response
- Hallucination → grounding scores, double-pass validation

## See Also
- [[RAG Interview Study Guide]] — extends
- [[Agents Interview Study Guide]] — extends
- [[System Design — Shared Code-Index Service]] — instance-of
- [[System Design — Serverless Agent Backends]] — instance-of
- [[System Design — Unified Eval Harness]] — instance-of
