---
title: Deployment Topology Ladder
tags: [infra, pattern]
summary: Five deployment topologies (local → single service → cloud service → split service → serverless) ordered by who can access the system, with cost and ops-complexity as the selection axes rather than technical capability.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/deployment-topology.md
---

# Deployment Topology Ladder

Deployment topology is *"where your AI system runs and how it's structured"* — and the
source frames it as determining four things at once: **cost, complexity, who can access
it, and how you operate it after the POC.** The fourth is the one that gets skipped in
scoping conversations and then dominates the six months after demo day.

The ladder mirrors [[Complexity Floor]]: each rung has a minimum team-hours cost that no
amount of scope reduction can shrink below.

## The Five Topologies

| Topology | Who can access | Infra cost | Ops complexity | Best for |
|----------|---------------|-----------|----------------|----------|
| [[Local-Only Deployment]] | Just the developer | $0 | None | Weekend sprints, prototypes |
| [[Single Service Deployment]] | Team on same network / VPN | $5–20/mo | Low | Internal tools, multi-sprint POCs |
| [[Cloud Service Deployment]] | Anyone with the URL | $20–100/mo | Medium | Production internal tools |
| [[Split Service Deployment]] | External users + internal backend | $40–150/mo | High | Client-facing applications |
| [[Serverless Deployment]] | Anyone with the URL | Pay-per-use | Medium | Low-traffic, bursty workloads |

## The Selection Axis Is Audience, Not Capability

Every rung can run the same agent. What changes across the ladder is **who is allowed to
reach it** — and each widening of the audience drags in a fixed infrastructure cost:

| Audience widening | What it forces |
|---|---|
| Developer → team | A host that stays up when the laptop closes |
| Team → distributed team | Monitoring, health checks, env management |
| Internal → external users | Authentication, data scoping, multi-tenancy |

This is why the source's decision shortcut leads with *"Who uses this?"* rather than
"what does it do?" — the capability question does not discriminate between rungs.

## Decision Shortcut

| Question | Answer → Topology |
|----------|-------------------|
| "Who uses this?" | Just me → Local. My team → Single/Docker. External users → Split service. |
| "What's the budget?" | $0 → Local or serverless free tier. $5–20/mo → Single service. $40+ → Split. |
| "Do external users log in?" | No → Single service. Yes → Split service (needs auth). |
| "How many hours does the team have?" | Weekend → Local. Multi-sprint → Single/Docker. Semester → Split service. |
| "Does it need to be up 24/7?" | No → Local. Business hours → Cloud. Always → Cloud or serverless. |

Note that two independent questions — budget and team-hours — both land on the same
rung for a well-scoped project. When they disagree (money for split service, hours for
local), the hours win: infrastructure you can pay for but cannot operate is worse than
none.

## The Anti-Over-Engineering Rule

The source repeats a cost-restraint theme at three separate rungs:

> *"Railway's free tier ($5/mo credit) handles most DSSG workloads. Don't over-engineer
> hosting for a system that serves 5-20 users."*

> *"This is the 'real product' topology. Only choose it if the nonprofit's
> clients/community will use it directly. Internal tools should use single-service."*

> *"Good fit for low-traffic tools (< 100 requests/day) that don't need streaming."*

The governing bias matches [[Agent Orchestration Patterns]]: start at the lowest rung
that serves the actual audience, and treat each upgrade as a decision requiring evidence
rather than a default.

## Upgrade Paths

The rungs are designed to compose rather than replace:

- Local → Single Service: containerize, push to Railway/Render
- Single Service → Split Service: add a frontend; add Supabase auth
- Single Service → Cloud Service: same container, proper hosting + monitoring

Serverless is the one rung that is *not* on the linear path — it is an alternative to
cloud service chosen on traffic shape (bursty, low-volume, stateless) rather than on
audience size.

## Copier Parameter Surface

Topology choice writes to five scaffold parameters — see
[[Asked vs Derived Scaffold Variables]] for which are asked vs derived:

| Parameter | Range |
|---|---|
| `deployment_target` | `local` / `docker` / `cloud` / `serverless` |
| `frontend_backend_topology` | `single` / `split_service` |
| `primary_backend_language` | `python` / `typescript` / `both` |
| `primary_users` | `internal` / `customers` |
| `data_sensitivity` | `internal` / `restricted` |

## See Also
- [[Local-Only Deployment]] — instance-of
- [[Single Service Deployment]] — instance-of
- [[Cloud Service Deployment]] — instance-of
- [[Split Service Deployment]] — instance-of
- [[Serverless Deployment]] — instance-of
- [[Complexity Floor]] — constrains (team-hours bound the reachable rung)
- [[Agent Orchestration Patterns]] — complements (orchestration ladder on the same start-low bias)
- [[Asked vs Derived Scaffold Variables]] — related (how topology answers reach copier)
- [[AI Project Archetypes]] — related (archetype and topology are chosen together)
- [[ADK Deployment Patterns]] — extends (GCP-specific target selection)
- [[Runtime Topology and Checkpointer Alignment]] — constrains (topology dictates checkpointer backend)
