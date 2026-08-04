---
title: Local-Only Deployment
tags: [infra, pattern]
summary: The zero-infrastructure rung — the AI runs on a developer's machine with no hosting and no external access, chosen when the only user is the developer and iteration speed matters more than availability.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/deployment-topology.md
---

# Local-Only Deployment

The lowest rung of the [[Deployment Topology Ladder]]. *"The AI runs on a developer's
machine. No deployment, no hosting, no external access. Start the server, use it, stop it
when done."*

## When to Use

- Weekend sprint / prototype — proving the concept works
- The only user is the developer (or someone sitting next to them)
- Zero infrastructure cost and zero ops burden are requirements
- Rapid iteration without deploy cycles

## When Not To

- Anyone besides the developer needs to use it
- It must run when the developer's laptop is closed
- You're past the prototype phase

## Complexity Rating

**Weekend sprint** — `make lg-up` or `make adk-up` and you're running. This is the only
rung with no infrastructure setup at all, which is what makes it viable inside a
[[Complexity Floor]] weekend budget.

## Example Scenario

> *"A volunteer wants to prove that RAG over housing regulations works before committing
> the team to a multi-week build. They ingest 5 sample PDFs, run queries locally, show the
> results at the next team meeting. No deploy needed."*

The pattern here: local-only is used to buy **evidence for a scoping decision**, not to
serve users. The output of a local-only phase is a go/no-go, not a system.

## Copier Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `deployment_target` | `local` | Design record: this is local-only for now |
| `project_type` | `prototype` (or any) | Prototype skips some scaffolding overhead |
| `frontend_backend_topology` | `single` | No frontend/backend split needed |

Setting `deployment_target: local` is a **design record**, not a no-op — it documents
that hosting was consciously deferred rather than forgotten.

## Trade-offs

- **Pro:** Zero cost; zero ops; instant iteration; no security concerns (nothing exposed)
- **Con:** Only one user; dies when the laptop closes; can't demo remotely; no persistence beyond local disk
- **Upgrade path:** Containerize (Docker) → push to Railway/Render → [[Single Service Deployment]]

The "no security concerns" pro is real and underrated: nothing is exposed, so no auth,
no CORS, no secret rotation. Every rung above pays for its audience in security work.

## See Also
- [[Serverless Deployment]] <!-- auto-linked -->
- [[Deployment Topology Ladder]] — part-of
- [[Single Service Deployment]] — upgrade-path
- [[Complexity Floor]] — related (the weekend tier's only viable topology)
- [[Single Prompt Baseline]] — complements (the orchestration analogue of local-only)
