---
title: Callable-By Integration Contract
tags: [infra, pattern]
summary: When a project needs to work with an external hosted service, the scaffoldable unit is not the service but the contract that makes your system reachable from it — a plain HTTP endpoint plus a signed-webhook receiver for the reverse direction.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/docs/research/multi-agent-tooling-parity.md
---

# Callable-By Integration Contract

A recurring category error in template and platform work: a downstream project names an
external service in its stack, and the template's owner reads that as "the template must
add support for the service." For a *hosted* service — one that runs outside your
deployment entirely — there is nothing to add. What can be added is the contract on your
side of the boundary.

The formulation from the source audit:

> *"The right shape isn't 'run n8n itself' (that's an external service, out of scope for a
> Copier template to install) but 'make the template's agents/services callable by n8n.'"*

## The two directions

The contract has exactly two halves, and they are asymmetric in cost:

| Direction | Mechanism | Cost |
|---|---|---|
| External → you | A plain HTTP endpoint the external tool's generic HTTP node can hit | Near zero if a service already exists |
| You → external, with a reply | A signed-webhook receiver | Real — endpoint, secret handling, dedup |

The first half is usually already satisfied and merely needs to be *stated*: any agent
already exposed over HTTP is callable by anything that can issue a POST. The audit's own
phrasing is telling — *"ensure every agent exposes a plain HTTP endpoint"* — an assurance,
not a build.

The second half is where the actual engineering lives, and it inherits the full obligation
set described in [[Webhook Handler Idempotency]]: HMAC verification with a timing-safe
comparison, and dedup on the receiver because the same event may arrive twice.

## Why this is documentation more than infrastructure

The audit classifies the work explicitly: *"closer to a documentation + thin-endpoint
pattern than new infrastructure."*

That classification is the practical payoff. A capability that looked like a shared,
high-leverage gap — one of three the audit surfaced across two projects — resolves to a
thin endpoint plus a written contract, rather than a new subsystem. Misclassifying it as
infrastructure would have inflated the roadmap with work that a paragraph of documentation
discharges. This is the [[Capability Parity Audit]]'s `partial` bucket doing its job.

## The boundary test

The discriminating question is not "is this service important?" but **"does this run inside
my deployment?"**

- **Runs inside** — a library, a database driver, an agent framework. A generator can
  install it, pin it, and wire it. It is a legitimate scaffold parameter.
- **Runs outside** — a hosted workflow engine, a managed connector platform, a SaaS API.
  A generator cannot install it. What it can scaffold is a client, an endpoint, or a
  receiver.

Both answers produce work; only the first produces a dependency. Conflating them is what
puts "add n8n" on a roadmap that can never contain it.

## Relation to the client-side patterns

Callable-by is the inbound complement to the outbound patterns in
[[Integration Pattern Selection]]. The same external service often needs both: your system
calls its API with a direct httpx client, and it calls back into your system through the
webhook receiver. Choosing the workflow tool for *turnover insurance* — because volunteers
rotate and a visual workflow survives team churn better than custom code — makes the
inbound half non-optional, since the whole point is that non-engineers wire the outer flow.

## See Also
- [[Webhook Handler Idempotency]] — prerequisite-for (the receiver's core obligation)
- [[Integration Pattern Selection]] — complements (the outbound half of the same boundary)
- [[Capability Parity Audit]] — part-of (the audit this contract resolved a gap for)
- [[MCP Protocol]] — alternative-to (callable-by, for agent consumers rather than workflow tools)
- [[AI Project Template Scaffold]] — instance-of (the template that ships the contract)
- [[NYC-DSSG Project]] — instance-of (the volunteer-turnover argument)
