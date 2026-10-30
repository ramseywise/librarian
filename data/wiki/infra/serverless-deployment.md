---
title: Serverless Deployment
tags: [infra, pattern]
summary: Functions that spin up on demand and shut down after execution — an off-ladder alternative chosen on traffic shape (bursty, stateless, sub-30s) rather than audience size, paying cold starts and timeout limits for zero idle cost.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/deployment-topology.md
  - data/raw/claude-docs/playground/docs/archived/terraform-restructure-research.md
  - data/raw/claude-docs/ai-project-template/docs/plans/vercel-native-ts-agent-scaffold.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--vercel-native-ts-agent-scaffold.md
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
- **Volunteer-team consideration:** *"Good fit for low-traffic tools (< 100 requests/day) that don't need streaming. Not ideal for chat applications that need persistent connections."*

The chat-application exclusion is significant given how many AI POCs default to a chat
interface — serverless and conversational UX are frequently incompatible defaults.

## Model-in-Image RAG Serving: Fargate, Not Lambda

The 1–3 s cold start above assumes a slim function. A RAG API that bakes its models into the container image is a different workload (playground infra research, 2026-04):

| Step | Warm | Lambda cold start |
|---|---|---|
| 560M multilingual embedding | ~100–200 ms | +3–8 s model load |
| Cross-encoder rerank | ~100–300 ms | +1–2 s model load |
| LLM generation | 0.5–2 s | — |
| **Total** | **~0.7–2.5 s** | **+4–10 s** |

A sub-2-second target is impossible on cold Lambda. Provisioned concurrency fixes that, but at that point it costs about the same as Fargate. **Decision:** Fargate for serving, and Lambda only for async ingestion, where cold starts don't matter.

## Vercel AI SDK agent on Vercel: check the docs, not memory

Building a TS-native agent scaffold (`ts_agent_framework=vercel_ai_sdk`) corrected three
assumptions by reading current docs and the installed package before writing anything:

- **The streaming helper had been renamed.** The plan named the v4 response helper; the
  installed SDK (v5) uses `streamText().toUIMessageStreamResponse()`.
- **Express deploys with zero config** when the entry file sits at a conventional path
  (which included the scaffold's existing `src/index.ts`); both `app.listen()` and
  `export default app` work. A planned `vercel.json` rewrite was dropped as unnecessary.
- **Streaming works on the default Node runtime** — Edge is not required. The only lever
  is the function max-duration limit, documented as an if-needed pointer, not
  pre-configured.
- Env vars on the platform are a separate step from local `.env`; they do not sync.

The handler was kept framework-agnostic — a plain `(req: Request) => Response` mounted
into Express through one adapter route — so it drops unchanged into a Next.js route
handler later. Evaluating that agent surfaced [[In-Band Stream Errors Read as Bad Answers]].

## See Also
- [[Single Service Deployment]] <!-- auto-linked -->
- [[Deployment Topology Ladder]] — related (part of)
- [[Cloud Service Deployment]] — alternative-to (same audience, opposite traffic shape)
- [[Runtime Topology and Checkpointer Alignment]] — related (constrains; checkpointer must be external)
- [[System Design — Serverless Agent Backends]] — extends (streaming and session state within platform limits)
- [[ADK Deployment Patterns]] — related (Cloud Run as a managed-scaling middle ground)
