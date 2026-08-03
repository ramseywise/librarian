---
title: Split Service Deployment
tags: [infra, pattern]
summary: Separately deployed frontend and backend sharing identity through a common auth provider — the only rung that supports external users and multi-tenancy, at roughly double the operational burden.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/deployment-topology.md
---

# Split Service Deployment

Top rung of the [[Deployment Topology Ladder]]. *"Two separately deployed services: a
frontend (typically Next.js on Vercel) and a backend (typically FastAPI on Railway). They
share identity via a common auth provider (Supabase Auth) and communicate over HTTPS. Each
scales independently."*

The source calls this *"the 'real product' topology."*

## When to Use

- External users (nonprofit clients, community members) need a polished web interface
- Multi-tenancy required — each org sees only their own data
- Frontend and backend have different deployment/scaling needs
- The team has both frontend and backend expertise

## When Not To

- All users are internal — a single-service API with a simple UI suffices
- The team is 1–2 people — *"split-service doubles operational burden"*
- Weekend sprint — too much infrastructure for a prototype
- No frontend expertise on the team

The team-composition constraints are as binding as the technical ones. Two of the four
"when NOT to" conditions are about **who is on the team**, not what the system does.

## Complexity Rating

**Semester** — needs two deployments, shared auth (Supabase), CORS configuration,
environment management for both services, JWT validation, and frontend routing +
middleware. Per [[Complexity Floor]], this rung is simply unreachable on a weekend or
multi-sprint budget; there is no reduced version of it.

## Example Scenario

> *"A legal aid org wants tenants to check their case status. Tenants (external users) log
> in via a web app, see their own cases, chat with an AI about their rights. The Next.js
> frontend runs on Vercel (fast, global CDN). The FastAPI backend runs on Railway (handles
> the LLM calls, database queries). Supabase Auth provides login + RLS for tenant data
> isolation."*

Row-level security is doing the multi-tenancy work here — data isolation is enforced at
the database, not in application code.

## Copier Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `primary_backend_language` | `both` | Python backend + TypeScript frontend |
| `frontend_backend_topology` | `split_service` | The whole point of this topology |
| `primary_users` | `customers` | External users need auth + data scoping |
| `deployment_target` | `cloud` or `serverless` | Vercel (frontend) + Railway (backend) |
| `data_sensitivity` | `restricted` | External user data requires protection |
| `agent_memory` | `long_term` | Users expect continuity across sessions |
| `vector_backend` | `postgres` | Supabase Postgres for both vectors + app data |
| `ts_agent_framework` | `vercel_ai_sdk` | TS-native agent for frontend API routes (optional) |

Eight parameters move together — the largest coupled set of any topology. Choosing split
service is effectively choosing the whole stack, which is why it belongs in the scoping
conversation rather than in a later infrastructure decision.

## What the Template Provides

- Next.js 15 frontend with App Router + Supabase Auth
- `src/middleware/auth.py` — FastAPI middleware validating Supabase JWTs
- `vercel.json` — Vercel deployment config
- `railway.toml` — Railway deployment config
- Edge middleware for protected routes on the frontend
- Supabase client initialization (`src/lib/supabase.ts`)

## Trade-offs

- **Pro:** Professional-grade UX; proper security; each piece scales independently; Vercel's global CDN for frontend
- **Con:** Highest complexity; two deployments to manage; CORS + auth configuration; more expensive; needs full-stack team
- **DSSG consideration:** *"Only choose it if the nonprofit's clients/community will use it directly. Internal tools should use single-service."*

## See Also
- [[Deployment Topology Ladder]] — part-of
- [[Single Service Deployment]] — prerequisite-for
- [[Cloud Service Deployment]] — prerequisite-for
- [[Complexity Floor]] — constrains (semester-tier only; no reduced version exists)
- [[System Design — Serverless Agent Backends]] — instance-of (Vercel-hosted split stack in practice)
- [[PGVector Migration Pattern]] — related (Supabase Postgres as shared vector + app store)
