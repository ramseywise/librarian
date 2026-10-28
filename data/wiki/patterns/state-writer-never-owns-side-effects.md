---
title: State Writer Never Owns Its Side Effects
tags: [infra, pattern]
summary: Give each lifecycle field exactly one writer and let a database trigger fan the committed change out to notification consumers — the writer never sends the email, so every write produces identical comms whoever makes it, and a new consumer touches zero producers.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/dssg/docs/overview/design.md
  - data/raw/claude-docs/dssg/docs/overview/roadmap.md
  - data/raw/claude-docs/dssg/docs/milestones/project-mgmt-ai.md
  - data/raw/claude-docs/dssg/docs/milestones/kb-platform-api.md
---

# State Writer Never Owns Its Side Effects

From a 2026-07 multi-product platform design: a client portal, a lifecycle/coordination
service, and a thin platform API, all on one Postgres. Clients were supposed to get an email
every time their engagement changed stage. Nothing sent it, because no one owned it.

## The rule

1. **One accountable writer per lifecycle field.** The coordination service is the *sole*
   writer of `engagements.stage`. Staff act through it rather than editing the column; the
   portal renders the stage and never writes it. The ownership is enforced in RLS policy, not
   by a cross-service API call.
2. **The writer does not deliver the consequence.** A DB webhook on `UPDATE` of that column
   calls a comms route inside the platform API, which loads the contact, renders a template,
   and sends. The comms route accepts only the database's webhook signature. It is an
   internal trigger, not a public endpoint.
3. **Consumers subscribe to the write, not the writer.** The portal refreshes by reading the
   same rows, the dashboard reads them, and a future Slack digest would be one more consumer.

> One write, one webhook, one email. The app that owns the state change doesn't also own
> notification delivery — so every stage write, whoever makes it, produces identical comms,
> for free.

## Why it pays

- **Uniformity for free.** A manual test write, an automated transition, and a future second
  writer all produce the same email. Nothing can forget to notify.
- **Additive consumers.** A new channel (Slack, SMS) is one consumer-side change, not N
  producer changes.
- **Coupling lives in the schema.** The shared schema is the cheapest place to manage
  coupling. The coordination service knows nothing about email, and the portal never polls it.
- **No broker.** At this scale *Postgres is the event bus*: state changes are table writes and
  DB webhooks fan them out. If volume ever demands more, the upgrade is an `events` outbox
  table plus a worker. That is still Postgres, and still no broker.

## Preconditions

- The receiver must be idempotent. DB webhooks are at-least-once (see
  [[Webhook Handler Idempotency]]).
- The writer's credential must be attributable: its own service key, not the shared
  service-role key. Then every transition is traceable to the system that made it.
- Agent-drafted comms stay draft-only. The deterministic, human-authored templated email is
  the one exception to "a person sends".

## See Also
- [[Realtime Is UI Sync, Not the Event Bus]] — extends (the domain event is the committed row; realtime and webhooks only fan it out)
- [[Webhook Handler Idempotency]] — prerequisite-for (the comms consumer receives at-least-once)
- [[Principal Write-Surface Matrix]] — related (sole-writer ownership is one row of the write-surface audit)
- [[Agent Credential Ceiling]] — related (the writer uses its own attributable service credential)
- [[Advance-Only Machine Writes on a Shared Lifecycle]] — instance-of (a machine writer bounded to its own states)
- [[Deadline Transition Computed on Read]] — related (a state transition with no writer at all: derived on read)
