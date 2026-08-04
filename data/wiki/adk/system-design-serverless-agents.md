---
title: System Design — Serverless Agent Backends
tags: [adk, infra, reference]
summary: Interview-format system design writeup of running agent systems on serverless (Vercel Functions / Next.js API routes) — stateless invocations, session state in Postgres, streaming within platform timeouts, and the designed handoff to a stateful phase 2.
updated: 2026-07-17
sources:
  - raw/repos/atlas/CLAUDE.md
---

# System Design — Serverless Agent Backends

Interview-format writeup of the constraints governing the atlas/DSSG-portal TypeScript agent stack (Vercel AI SDK / ADK TS on Vercel Functions). Format: requirements → constraints → architecture → tradeoffs → scaling.

## Requirements

- Chat agents served from a serverless platform (Vercel Functions / Next.js API routes) — no long-running process to own state.
- Multi-tenant nonprofit clients: strict tenant isolation, API keys never client-side.
- Responses must feel live (streaming), within platform execution limits.

## Constraints

- **Every invocation is independent.** No in-memory session manager survives a cold start — an in-memory ADK session service in production is a designed outage.
- **Timeout budgets are hard:** Hobby 10s / Pro 60s / Enterprise 300s. An agent loop that buffers its full response before responding will hit the wall; streaming is not an optimization, it's the fit-inside-the-budget mechanism.
- Secrets: server-side env only — anything prefixed `NEXT_PUBLIC_`/`VITE_` ships to the browser. The one deliberately client-safe key is the Supabase anon key, because RLS governs it.

## Architecture

- **State lives in Postgres (Supabase), not the process.** Load session at request start, write at end. Session rows store a compressed summary + last N turns, not unbounded history — the context window is loaded per turn, not accumulated.
- **Agent objects are constructed per-request** from DB state; framework session managers are treated as request-scoped conveniences.
- **Streaming end-to-end:** ReadableStream out of the function; mid-stream failures close the stream with an error event rather than hanging the client.
- **Tenant isolation at the data layer:** every query scoped by RLS to the authenticated org; the service-role key never appears in a user-facing route.
- **Tools with schemas:** explicit input/output schemas (Zod / FunctionDeclaration); DB-writing tools return structured results and irreversible writes require a confirmation step in the loop.

## Tradeoffs

- Per-request state hydration costs a DB round-trip every turn — the price of surviving cold starts. Mitigated by summary-compression keeping rows small.
- Serverless caps agent-loop duration; long multi-step plans need background jobs, not longer requests.
- **The phase-2 handoff is designed now:** when stateful sessions become necessary, a persistent session manager runs as a long-lived service and the serverless functions become the API layer proxying to it — the Supabase session schema is written to be readable by either side, so the migration is a topology change, not a data migration.

## Scaling path

1. Now: stateless functions + Supabase sessions + streaming.
2. Heavier agents: background jobs for long loops; edge runtime only for truly stateless routes.
3. Phase 2: dedicated stateful agent service behind the same session schema.

## See Also
- [[ADK Deployment Patterns]] — extends
- [[ADK Context Engineering]]
- [[System Design — Unified Eval Harness]]
- [[System Design — Shared Code-Index Service]]
- [[Serverless Deployment]] — instance-of (the topology this design realizes)
- [[Split Service Deployment]] — related (Vercel frontend + external backend as the same stack)
