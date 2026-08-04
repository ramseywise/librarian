---
title: Serverless Deployment
tags: [infra, pattern]
summary: Functions that spin up on demand and shut down after execution — an off-ladder alternative chosen on traffic shape (bursty, stateless, sub-30s) rather than audience size, paying cold starts and timeout limits for zero idle cost.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/deployment-topology.md
---

# Serverless Deployment

*"Functions that spin up on demand and shut down after execution. No persistent server. You
pay per invocation, not per hour."*

Serverless sits **beside** rather than on the [[Deployment Topology Ladder]]: it serves the
same audience as [[Cloud Service Deployment]] (anyone with the URL) but is selected on
**traffic shape**, not on who needs access.

## When to Use

- Traffic is unpredictable — mostly quiet, occasional bursts
- Budget is tight (pay only for actual usage)
- The AI tasks are stateless and complete quickly (< 30 seconds per call)
- You're already using Vercel for a frontend — serverless functions are native

## When Not To

- Responses take > 30 seconds (function timeouts)
- You need persistent connections (WebSockets, streaming)
- High sustained traffic — serverless gets expensive at scale
- You need in-memory state between requests

## The Three Disqualifiers

Three of the four exclusions are the same underlying constraint: **the function does not
outlive the request.** Long responses hit the timeout, streaming needs a connection that
survives, and in-memory state has nowhere to live. Any agent design that assumes a
long-lived process fails here — see
[[Runtime Topology and Checkpointer Alignment]], where `MemorySaver` in a serverless
deployment *silently* loses state between invocations rather than erroring.

The fourth exclusion (sustained traffic) is purely economic and inverts the pricing
advantage.

## Complexity Rating

**Multi-sprint** — *"simpler deployment than long-running (no container management), but
cold starts and timeouts require careful design."* Deployment complexity goes down; design
complexity goes up. Net effort is comparable to a container, spent in a different place.

## Copier Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `deployment_target` | `serverless` | Functions-as-a-service model |
| `ts_agent_framework` | `vercel_ai_sdk` | Vercel AI SDK designed for serverless |
| `primary_backend_language` | `typescript` | Most serverless platforms prefer TS/Node |

Note the language coupling: choosing serverless effectively chooses TypeScript, which
makes it a stack decision rather than a hosting decision.

## Trade-offs

- **Pro:** Zero cost when idle; auto-scales; no server management; deploys instantly via Vercel/AWS
- **Con:** Cold starts (1–3s on first request); timeout limits; no persistent state; debugging is harder
- **DSSG consideration:** *"Good fit for low-traffic tools (< 100 requests/day) that don't need streaming. Not ideal for chat applications that need persistent connections."*

The chat-application exclusion is significant given how many AI POCs default to a chat
interface — serverless and conversational UX are frequently incompatible defaults.

## See Also
- [[Single Service Deployment]] <!-- auto-linked -->
- [[Deployment Topology Ladder]] — part-of
- [[Cloud Service Deployment]] — alternative-to (same audience, opposite traffic shape)
- [[Runtime Topology and Checkpointer Alignment]] — constrains (checkpointer must be external)
- [[System Design — Serverless Agent Backends]] — extends (streaming and session state within platform limits)
- [[ADK Deployment Patterns]] — related (Cloud Run as a managed-scaling middle ground)
