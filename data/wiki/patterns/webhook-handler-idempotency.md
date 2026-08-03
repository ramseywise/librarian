---
title: Webhook Handler Idempotency
tags: [infra, pattern]
summary: Every inbound webhook handler must tolerate the same event arriving more than once — at-least-once delivery is the sender's contract, so deduplication is unambiguously the receiver's responsibility.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/integration-patterns.md
---

# Webhook Handler Idempotency

The single non-negotiable rule for any inbound event endpoint:

> *"Every webhook handler must be idempotent — the same event may be delivered more than
> once."*

## Why duplicates are structural

Webhook senders retry. A sender that gets no `2xx` — because the receiver was slow, mid
deploy, or returned a `5xx` after already committing the side effect — has no way to
distinguish "not received" from "received but not acknowledged", so it redelivers. This is
at-least-once delivery, and it is the normal contract rather than a defect. The receiver
cannot negotiate it away, which is what makes dedup the receiver's obligation.

The failure mode is silent and duplicative rather than loud: a duplicate intake record, a
second Slack notification, a doubled charge. Nothing errors.

## What the receiver owes

A webhook endpoint carries four obligations, of which idempotency is the one that cannot be
delegated:

1. **HMAC signature verification** — a shared secret from an env var, compared
   timing-safely. An unauthenticated public endpoint is an open write path into the system.
2. **Event-type routing** — a pluggable handler registry dispatching per event type, rather
   than one branching function.
3. **Idempotent handlers** — the same event twice produces the same end state as once.
4. **Error recovery** — an async producer will not surface your handler's exception to
   anyone watching.

## Why it is harder than it looks

Webhook debugging *"is harder (events are async)"* — there is no request the developer
initiated to inspect, and failures surface downstream as bad data rather than at the call
site. Combined with duplicate delivery, an unhandled non-idempotent handler produces
corruption that is discovered long after the event that caused it, with no stack trace
pointing back.

This makes idempotency a design-time decision, not a hardening pass. The dedup key —
the sender's event ID, a content hash, or a natural business key — has to be chosen when
the handler is written, because retrofitting it means reconciling the duplicates already
written.

## The deployment consequence

An HMAC-verified receiver must be publicly reachable, which forces the deployment target to
`docker` or a cloud host rather than local. Air-gapped or security-restricted environments
cannot use webhooks at all and must fall back to polling — see
[[Integration Pattern Selection]].

## See Also
- [[Integration Pattern Selection]] — prerequisite-for (when a webhook is the right pattern)
- [[MCP Server Security Patterns]] — extends (the same authenticate-the-caller obligation)
- [[Observability and Runtime Patterns]] — extends (async failures need traces to be visible)
- [[Data Pipeline Pattern Selection]] — prerequisite-for (the event-driven pipeline depends on this)
