---
title: Complexity Floor
tags: [pattern, planning]
summary: The minimum viable complexity of a project shape — a constraint that makes capacity a selection criterion rather than a schedule, forcing archetype reframing rather than scope-thinning when the team can't reach the floor.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/agent-orchestration.md
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/archetype-selection.md
---

# Complexity Floor

Each project shape has a **minimum** complexity below which it cannot work at all. This
is distinct from an estimate: an estimate can be trimmed, a floor cannot.

| Tier | Time | Team | Achievable |
|---|---|---|---|
| Weekend sprint | 1–2 focused days | 1–2 | Working prototype, one happy path. No auth, deploy, or eval suite. |
| Multi-sprint | 2–6 weeks | 2–4 | Production-ready core feature, basic eval, deployed. |
| Semester | 8–12 weeks | 3–6 | Auth, multi-tenancy, integrations, eval gates, monitoring, handoff docs. |

## Why it's a selection constraint

The floor turns capacity into an input to *what you build*, not just *how long it takes*.
A team with weekend capacity cannot choose Conversational Interface — that archetype
requires auth, per-user data scoping, conversation history, tool-calling, deployment, and
evaluation before it does anything useful at all. There is no 20% version.

The correct response is to **reframe the archetype**, not thin the scope: a weekend team
facing a conversational ask should deliver Document Generation instead, which has a
weekend floor.

## The governing rule

> *"Reduce scope, not quality. A weekend sprint that delivers one working feature well is
> more valuable than a semester plan that ships nothing because the team ran out of hours."*

A half-built system at a tier above your capacity is worth less than a complete system at
your tier — the failure mode isn't a late project, it's a project with no working path
through it.

## Interaction with orchestration

The floor applies to [[Agent Orchestration Patterns]] as well as archetypes. Multi-agent
systems are semester-scope by construction: agent-to-agent communication, shared state,
per-agent evaluation, and cross-agent failure handling are all prerequisites, not
refinements.

## See Also
- [[AI Project Archetypes]] — extends (each archetype has a floor)
- [[Agent Orchestration Patterns]] — constrains
- [[Scope-POC Design Interview]] — applies
- [[Deployment Topology Ladder]] — constrains (team-hours bound the reachable topology rung)
- [[Split Service Deployment]] — instance-of (semester-tier only; no reduced version exists)
- [[Capability Parity Audit]] — extends (an identified gap is not automatically work worth doing)
