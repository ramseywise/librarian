---
title: Integration Pattern Selection
tags: [infra, comparison]
summary: Five ways an AI system connects to external services — MCP tools, Composio connectors, direct httpx clients, webhook receivers, n8n glue — and the single discriminating question that picks each one.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/integration-patterns.md
---

# Integration Pattern Selection

How an AI system connects to Slack, email, calendars, databases, and other APIs. The
choice determines which pre-built connectors you inherit, how much you write yourself, and
who can maintain it later.

| Pattern | Setup effort | Maintenance | Best for |
|---|---|---|---|
| MCP tools | Low (standard protocol) | Low (protocol-based) | AI-to-AI tool sharing, Claude Code integration |
| Composio connectors | Low (pre-built, config-driven) | Low (managed externally) | Slack, Gmail, GitHub, 100+ SaaS apps |
| Direct API clients | Medium (an httpx client per service) | Medium (APIs change) | Custom/niche services, fine-grained control |
| Webhook receivers | Medium (endpoint + HMAC) | Low (event-driven) | Receiving events from external systems |
| n8n workflow glue | Low–medium (config + HTTP) | Low (visual editor) | Non-engineers wiring several services |

## The discriminating questions

Each pattern is selected by one question, not by a general assessment:

| Question | Answer → pattern |
|---|---|
| Will other AI agents call this function? | Yes → MCP tools |
| Connecting to Slack/Gmail/GitHub/common SaaS? | Yes → Composio (fast) or direct API (control) |
| Is the service custom or niche? | Yes → direct API client |
| Do external services need to push events to you? | Yes → webhook receiver |
| Do non-engineers need to modify the integration logic? | Yes → n8n glue |

The patterns are not mutually exclusive; the common combined setup is MCP for AI consumers
+ Composio for SaaS + webhooks for inbound events.

## MCP vs. a REST endpoint

The boundary is the consumer, not the capability:

> *"If other AI agents will call your function, use MCP. If only humans or one specific
> system calls it, a REST endpoint is simpler."*

MCP buys typed, self-describing schemas and cross-project composability at the cost of
protocol overhead and stdio-transport debugging. Exposing a capability over
[[MCP Protocol]] is the right call when the capability should be discoverable — a
knowledge-base query tool that any session in any sibling project can add to its config
without reimplementing retrieval.

## Composio vs. direct client

Composio is a managed layer over 100+ SaaS APIs: it owns OAuth, API drift, and rate
limits, and the actions are configured rather than coded. The trade is control — its
actions are deliberately generic.

The split rule: **Composio for standard actions, a direct client for custom needs.** A
nonprofit that needs Slack notifications, Google Calendar events, and GitHub issue updates
gets three configured actions instead of three OAuth flows. The same nonprofit's Eventbrite
integration — custom fields, a draft→live two-step publish, attendee sync — falls outside
what the connector supports and gets a hand-written client.

They coexist for the same service; adopting Composio does not exclude a direct client
alongside it.

## The direct-client conventions

Where a client is hand-written, the shape is fixed: one client class per service, Pydantic
models at the boundaries for request and response types, an async httpx client, and a
`RuntimeError` with a clear message on missing credentials — **never a silent failure**.
Credential config is centralized rather than read ad hoc per client.

## Webhooks and the operational cost

A webhook receiver inverts the direction: the external service pushes to an endpoint you
expose, verified by HMAC signature with a timing-safe comparison against a shared secret.
That requires a *deployed, publicly reachable* service, which makes the deployment target a
dependent decision rather than a free one.

The load-bearing constraint is [[Webhook Handler Idempotency]] — the same event may arrive
more than once, and dedup is the receiver's responsibility, not the sender's.

## n8n as turnover insurance

n8n is a visual workflow tool where the AI system is one node — either a callable HTTP
endpoint or the trigger for downstream actions. It is chosen for *who maintains it* rather
than what it can do:

> *"Excellent fit for cohort projects where volunteers rotate. The n8n workflow survives
> team turnover better than custom code. AI does the hard part (extraction, matching,
> generation); n8n handles the plumbing."*

The cost is a second system to operate, extra HTTP hops of latency, and debugging that
spans two systems. It is the wrong choice when the whole team is engineers — the
indirection buys nothing.

## Common combinations

- **Internal team tool** — Composio for Slack/email + direct API for org-specific systems +
  MCP for cross-project sharing
- **Client-facing application** — direct clients for the org's data systems + webhook
  receivers for real-time events + **no MCP**, since end users aren't agents
- **Workflow-heavy project** — n8n for orchestration + a webhook receiver for its callbacks
  + Composio for what n8n misses + direct clients for custom logic

Each pattern maps onto concrete scaffold parameters (`include_mcp_server`,
`external_systems`, `optional_features`), so the integration answer given during discovery
becomes render-time configuration — see [[Asked vs Derived Scaffold Variables]].

## See Also
- [[Webhook Handler Idempotency]] — prerequisite-for (the receiver's core obligation)
- [[MCP Protocol]] — extends (when to expose a capability over MCP at all)
- [[Project Discovery Conversation]] — prerequisite-for (integration choice is a discovery output)
- [[AI Project Template Scaffold]] — instance-of (the scaffold that renders these choices)
- [[AI Project Archetypes]] — extends (archetype constrains the plausible integrations)
- [[NYC-DSSG Project]] — instance-of (the n8n turnover argument)
- [[Data Pipeline Pattern Selection]] — alternative-to (the sibling card: how data arrives, not how services connect)
- [[Callable-By Integration Contract]] — complements (the inbound half: being reachable from a hosted tool)
- [[Capability Parity Audit]] — extends (how a long tail of named tools collapses into these five)
