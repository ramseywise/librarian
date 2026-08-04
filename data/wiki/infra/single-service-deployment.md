---
title: Single Service Deployment
tags: [infra, pattern]
summary: One container running the AI backend, reachable by a small internal team — the rung where deployment first exists but auth, frontends, and independent scaling deliberately do not.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/deployment-topology.md
---

# Single Service Deployment

Second rung of the [[Deployment Topology Ladder]]. *"One container running your AI backend
(FastAPI + agent). Accessible to anyone who can reach the host — your team on the same
network, or via a simple cloud host (Railway, Render, a VPS)."*

## When to Use

- A small team (2–6 people) needs access
- All users are internal (staff, volunteers) — no external/public access needed
- Simple deployment without frontend/backend split complexity
- The AI is an API or a simple web interface, not a full application

## When Not To

- External users (nonprofit clients, community members) need access — they need auth
- You need a polished frontend, not just API calls or a basic chat UI
- Multiple services need to scale independently

## Complexity Rating

**Multi-sprint** — needs a Dockerfile, environment variables managed, and a host.
*"Railway is the easiest for DSSG — free tier, auto-deploy from GitHub."*

## Example Scenario

> *"A DSSG volunteer team builds a meeting-transcript-to-action-items pipeline. The 4 team
> members and 2 nonprofit staff need to upload transcripts and see results. One Docker
> container on Railway, accessed via a shared URL, protected by a simple API key in a
> header."*

Note the auth model: **a shared API key in a header**, not per-user identity. That is the
defining limitation of this rung — access is binary and collective. The moment you need
"user A sees only their data", you are at [[Split Service Deployment]].

## Copier Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `deployment_target` | `docker` | Container-based deployment |
| `primary_backend_language` | `python` | Single Python service, no TS frontend needed |
| `frontend_backend_topology` | `single` | One deployable unit |
| `primary_users` | `internal` | Team/staff access only |
| `data_sensitivity` | `internal` | No external user data flowing through |

## What the Template Provides

- `infrastructure/containers/docker-compose.yml` — local multi-container dev
- `infrastructure/containers/lg_agent/Dockerfile` — production container image
- `.github/workflows/ci.yml` — CI that builds and tests the container
- `Makefile` targets: `make lg-up`, `make adk-up` (local dev), `make docker-build` (production)

## Trade-offs

- **Pro:** Simple mental model (one thing to deploy); cheap (Railway/Render free tier); team can share
- **Con:** No frontend (API only, or very basic); scaling is *"make the one container bigger"*; no user-level auth (shared API key at best)
- **Upgrade paths:** Add a frontend → [[Split Service Deployment]]. Add auth → Supabase integration.

Vertical-only scaling is acceptable at the 5–20-user scale this rung targets; it becomes
the binding constraint well before cost does.

## See Also
- [[Deployment Topology Ladder]] — part-of
- [[Local-Only Deployment]] — prerequisite-for
- [[Cloud Service Deployment]] — upgrade-path (same container, real hosting)
- [[Split Service Deployment]] — upgrade-path (when external users need auth)
- [[Cloud Run + Cloud SQL Pattern]] — instance-of (GCP realization of one-container hosting)
