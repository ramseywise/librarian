---
title: Agent Credential Ceiling
tags: [infra, pattern]
summary: An agent serving a human never holds a credential broader than that human. It reads the user's own data under the user's JWT and RLS, reads cross-system data under a hashed, tenant-scoped service key, and never gets the service-role key. Tenant scoping is enforced server-side, never in the prompt.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/dssg/docs/overview/design.md
  - data/raw/claude-docs/dssg/docs/overview/tooling.md
  - data/raw/claude-docs/dssg/docs/milestones/portal-assistant.md
  - data/raw/claude-docs/dssg/docs/scoping/portal-assistant.md
  - data/raw/claude-docs/dssg/docs/scoping/kb-platform-api.md
---

# Agent Credential Ceiling

A design rule from a 2026-07 platform design for a client-facing status assistant. The
assistant is a thin in-repo TypeScript agent on one Supabase Postgres, sitting next to a
platform API.

## Two credential classes, nothing in between

| Class | Who holds it | Scope mechanism |
|---|---|---|
| Human JWT | a signed-in user, or an agent acting *as* that user | RLS restricts every query to the caller's rows |
| Hashed service key | machine callers: other products, cohort projects, the agent's cross-system tools | a `service_credentials` table: key hash → tenant scope, revocable per product |

Only the platform API itself holds the database's service-role key. Every other product or
agent that needs cross-product data gets its own key. That gives least privilege, per-caller
revocation and attributable writes, instead of one all-or-nothing shared secret.

## The ceiling, applied to an agent

The assistant's tools split along the credential line:

- `getEngagementStatus`: the client's own row, read **under the client's own JWT**. RLS is the
  authorization layer.
- `getPortfolioStatus`: cross-system data, read through the platform API **under a
  tenant-scoped service key**. The API resolves key hash → tenant before any query runs.

> Property to preserve: it never holds a credential broader than the person it serves.

This also answers prompt injection structurally. Tenant scoping happens server-side from the
credential, never from text in the prompt. A "show me another org's data" injection then has
nothing to exploit, because cross-tenant retrieval is *structurally impossible*, not
policy-discouraged. Adversarial tests (injection, other-tenant requests, PII probes) are still
part of launch acceptance.

## Same door as everyone else

The first-party assistant uses the **identical API and auth path** as any external project,
so there is no privileged back door. A key that does not appear in `service_credentials` is a
back door by definition. The milestone check is literal: the key the agent used is in the
table, and another tenant's data is unreachable with it. User JWTs are rejected by the
service-key endpoints, and missing, revoked or wrong-tenant keys get 401/403.

## See Also
- [[Principal Write-Surface Matrix]] — extends (the agent is a principal whose read column must not exceed its human's)
- [[Written-but-Inert RLS Policies]] — prerequisite-for (the JWT half only holds if the policies are actually in force)
- [[Split Service Deployment]] — instance-of (the topology where both credential classes exist)
- [[State Writer Never Owns Its Side Effects]] — related (attributable writes via a per-service key)
- [[Paired Allow Test for Deny Rules]] — related (how the isolation claim is proven)
