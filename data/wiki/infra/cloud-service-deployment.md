---
title: Cloud Service Deployment
tags: [infra, pattern]
summary: A long-running 24/7 hosted service — the same container as single-service plus monitoring, health checks, and env management, chosen when the system must be available without anyone starting it.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/deployment-topology.md
---

# Cloud Service Deployment

Third rung of the [[Deployment Topology Ladder]]. *"A deployed service running 24/7 on a
cloud platform (Railway, Render, AWS ECS, GCP Cloud Run). Same as Docker but with proper
hosting, monitoring, and optionally a custom domain."*

The distinction from [[Single Service Deployment]] is not architectural — it is the same
container. What changes is the **operational commitment**: uptime becomes a property
someone is responsible for.

## When to Use

- The system needs to be available when nobody's actively running it
- Multiple users access it throughout the day
- You need reliability (auto-restart, health checks, logging)
- Still internal users — but distributed (remote team, multiple offices)

## When Not To

- Traffic is very bursty with long idle periods — [[Serverless Deployment]] is cheaper
- You need sub-100ms cold starts (long-running has none; serverless does — this is the
  one axis where long-running *wins* over serverless)
- Budget is $0 — Railway's free tier has limits; Render's free tier sleeps on inactivity

## Complexity Rating

**Multi-sprint** — same as Docker plus environment variable management, health checks,
logging, and maybe a CI/CD pipeline for auto-deploy on merge.

## Example Scenario

> *"A workforce development nonprofit uses the AI daily for job-matching. Five case
> managers across 3 boroughs access it throughout the day. Needs to be up during business
> hours without anyone 'starting' it. Railway with a custom domain, auto-deploy from the
> main branch."*

Five users across three locations — the trigger is **geographic distribution**, not user
count. No one is sitting next to the machine, so no one can start it.

## Copier Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `deployment_target` | `cloud` | Long-running cloud service |
| `primary_backend_language` | `python` | Python backend (add TS if frontend needed) |
| `frontend_backend_topology` | `single` | One backend service (add frontend later if needed) |
| `primary_users` | `internal` | Distributed internal team |
| `data_sensitivity` | `internal` or `restricted` | Depending on client data flowing through |

## Trade-offs

- **Pro:** Always available; professional-grade reliability; the team doesn't need to "start" anything
- **Con:** Monthly cost even when idle; needs monitoring (*"what if it crashes at 2am?"*); environment management
- **DSSG consideration:** *"Railway's free tier ($5/mo credit) handles most DSSG workloads. Don't over-engineer hosting for a system that serves 5-20 users."*

The 2am question is the real cost of this rung. Adopting it means adopting an on-call
expectation, however informal — which is a volunteer-team liability that the dollar cost
understates.

## See Also
- [[Deployment Topology Ladder]] — part-of
- [[Single Service Deployment]] — prerequisite-for (same container, added ops)
- [[Serverless Deployment]] — alternative-to (chosen on traffic shape, not audience)
- [[Split Service Deployment]] — upgrade-path (when external users need auth)
- [[Production Hardening Patterns]] — extends (what 24/7 availability actually requires)
- [[Observability and Runtime Patterns]] — complements (the monitoring this rung introduces)
