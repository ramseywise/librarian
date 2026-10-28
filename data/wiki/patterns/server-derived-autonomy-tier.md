---
title: Server-Derived Autonomy Tier
tags: [infra, pattern]
summary: "An agent's HITL tier (act on its own vs draft for approval) is computed server-side in one switch covering every agent, never taken from the model's output or the agent's own module, and drafts are written only through a database function that also creates the pending approval, so no agent can approve itself."
updated: 2026-10-17
sources:
  - data/raw/repos/nonprofit-success-ai/CLAUDE.md
  - data/raw/repos/nonprofit-success-ai/README.md
  - data/raw/repos/nonprofit-success-ai/.claude--skills--workflow-review--SKILL.md
---

# Server-Derived Autonomy Tier

From the nonprofit-success-ai repo, a portal with five agents (intake routing, assessment
and plan, partner messaging, impact stories, health signal) on a serverless API over
Postgres with row-level security.

## The contract

Two tiers carry the weight:

- **L2:** high confidence plus a readiness signal. The agent acts, and only on reversible
  effects.
- **L3:** everything else. The agent drafts and a human approves.

**The tier is never something the model outputs.** If the model's JSON included
`tier: "L2"`, or each agent's file computed its own tier, then a prompt change, a
hallucination or one sloppy agent could give itself autonomy. So:

1. **One switch for the whole roster.** `deriveHitlTier()` in a guardrails module holds
   every agent's tier rule in one place. A new agent cannot put a more permissive rule
   in its own directory, because the tier is not computed there.
2. **Fixed-tier agents are fixed in the write path, not in a flag.** The assessment,
   messaging and story agents are always L3. Their output reaches the database only
   through `SECURITY DEFINER` functions (`submit_*_draft()`). Each function writes the
   draft **next to a pending approval row** in the same transaction, so a draft without
   its approval cannot exist.
3. **State changes go through one door.** Lifecycle stage changes go only through a
   `transition_*()` function, and partners have no write permission on the underlying
   table. Converting an intake into a real record goes through one approval function,
   the only writer of the link column. The browser never writes the intake table either:
   the route files intakes through a function.

## Why the database, not just the API

An API-layer check covers one caller. A `SECURITY DEFINER` function plus RLS that denies
direct writes covers **every** caller: the SPA, a future script, and a model with a tool.
"Can this draft exist without an approval?" is answered by the schema, not by code review.

## Companion rules from the same repo

- **Every agent path has a deterministic fallback.** A pure local heuristic runs when the
  model call fails. With no model key configured at all, every path runs its fallback.
  This is the [[Dual Parser with Shared Shape]] posture applied to a whole roster.
- **Every agent has at least one eval metric.** A registry test fails the build when a
  roster agent has none. Thresholds come from a measured pass rate, and unmeasured
  metrics report `UNGATED` (see [[UNGATED Metric Convention]]).
- **The review checklist names this class.** The repo's pre-commit review has a `safety`
  dimension that looks specifically for "HITL tier granted client-side", next to
  secrets in the bundle and service-role keys on a client path.
- **The public-env prefix is the secrets boundary.** In a Vite SPA only `VITE_`-prefixed
  variables reach the browser, so adding the prefix to a model key publishes it. A build
  config that `define:`s an API key into the bundle did exactly that until it was
  removed. A pre-commit hook now guards against a server-only key behind the public
  prefix.

## See Also
- [[HITL Gradient]] — alternative-to (L1–L4 there is a measurement parameter; here the tier is an enforced runtime contract)
- [[Reversibility Cliff]] — extends (L2 is allowed only for reversible effects)
- [[Model Gateway Is Transport, Call Site Owns Meaning]] — extends (the gateway transports; tier and meaning are decided elsewhere)
- [[Stated Seams Drift, Enforced Seams Hold]] — instance-of (the tier boundary is enforced by schema and one switch, not stated in prose)
- [[Agent Management Layer]] — instance-of (HITL checkpoints plus a defined fallback per agent)
