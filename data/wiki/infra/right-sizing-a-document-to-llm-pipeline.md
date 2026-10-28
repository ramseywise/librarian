---
title: Right-Sizing a Document-to-LLM Pipeline
tags: [infra, pattern]
summary: For a stateless "documents in, one structured LLM output back" service, the defensible shape is three tiers (ingest → enrich → serve) on serverless compute with a queue, a dedup key and a dead-letter topic, a hand-rolled typed loop instead of a graph framework, plain HTTP with 202-and-poll instead of MCP — and an explicit omit list, because cost is dominated by input tokens, not infrastructure.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/sisyphus/docs/research/2026-08-08_ml6-prototyping_cloud-architecture.md
  - data/raw/claude-docs/sisyphus/docs/research/2026-08-08_ml6-prototyping_orchestration.md
---

# Right-Sizing a Document-to-LLM Pipeline

Synthesised from take-home research for a service that turns two source PDFs into a
templated document via one LLM generation with a repair loop. Medium-confidence web
research (vendor prices are point-in-time); the sizing reasoning is what transfers.

## The three tiers

1. **Ingest** — object storage with lifecycle deletion; OCR only for scanned input
   (born-digital PDFs skip it); a storage-arrival event onto a queue (at-least-once).
2. **Enrich** — stateless serverless worker consumes the queue and calls the model; use
   the provider's **batch API (~50% off)** when a multi-hour SLA is acceptable, sync only
   when the user is waiting.
3. **Serve** — a document store keyed by tenant path, or relational with row-level
   security when an audit trail is required; an HTTP endpoint that returns a job id.

**Idempotency is one line with outsized value:** dedup key = `sender + receiver +
hash(input text)` checked before invoking the model, because at-least-once delivery will
re-deliver; poison messages go to a dead-letter topic after N retries, alerted on depth.

## Where the money actually goes

Per-output cost was a fraction of a cent, with **LLM input tokens ≥75% of total** — OCR,
compute, storage and the database were rounding errors. Every optimisation therefore
targets context depth: fewer pages, convert PDF to markdown first (40–50% fewer tokens),
cache company research. Doubling page count doubles the bill; adding Kubernetes doesn't
change it. The hidden cost is the engineer maintaining the stack, not the API.

## Orchestration: a typed loop, not a framework

The pipeline is ~7 steps (ingest, extract, retrieve, draft, constrain, validate, fit) with
**one** repair loop — declarative enough to write down upfront. A graph framework's value
is persistent, resumable state for long-running agents; a 60-second generation that just
retries from the start doesn't need it.

- Pass one Pydantic state model through async functions; the repair loop is a `while`
  with an explicit `max_repairs` counter that **re-runs only the draft step**, and
  accumulates violations so traces show which constraint kept failing.
- Adopt the framework when restart-survival or parallel sub-agents become requirements —
  the state contract carries over unchanged ([[Loop-to-Graph Escalation]]).
- **"Orchestrator-agnostic" is a fiction.** An interface general enough for any
  orchestrator says nothing about retries, streaming or checkpoint config, and leaks the
  moment a real one is plugged in. The one cheap, high-value seam is a provider-agnostic
  LLM adapter injected as a dependency.

## Interface: HTTP, not MCP

MCP is for an agent discovering tools at runtime. A backend that runs a known DAG on a
fixed request is deterministic system-to-system integration — plain HTTP. LLM latency
(5–30 s) means **`202 Accepted` + job id + `GET /jobs/{id}` polling**, with a jobs table
(status, result, error, timestamps) as the only state. Row-locked status transitions and
per-step checkpoints are the production upgrade, not prototype scope.

Minimum observability that reads as senior: a span per step carrying job id, tokens,
`repair_attempt`, violation count and the loop's exit reason (`passed` /
`failed_max_retries`).

## The omit list

Name what is deliberately absent — it is part of the design:

| Omitted | Why |
|---|---|
| Kubernetes | Stateless, <100 req/s; serverless autoscaling covers it |
| Vector database | No repeated querying of a corpus; full context fits |
| ML pipeline orchestrator | No training, no multi-step DAG of models |
| Analytics warehouse | Thousands of rows/month; store-native aggregation suffices |
| Global DB / multi-region | Single-region data residency is simpler and compliant |
| Redis cache | In-process memory covers it; a cache adds failover and eviction ops |
| Multi-cloud codebase | 2× maintenance; abstract the inference call, not the orchestration |

Revisit each only at a named trigger (e.g. ~1M outputs/month, >10 tenants needing hard
isolation, a real-time analytics ask). Velocity is the argument: the lean stack ships in
weeks; the platform stack adds months of setup for an MVP whose success is unknown.

## See Also
- [[Deployment Topology Ladder]] — extends (picks the serverless rung for a stateless generation workload)
- [[LLM Inference Economics]] — extends (input-token depth as the dominant cost driver in practice)
- [[Loop-to-Graph Escalation]] — instance-of (a one-loop pipeline that does not earn a graph)
- [[Integration Pattern Selection]] — instance-of (HTTP over MCP for a deterministic backend)
- [[Canonical Document IR for Ingest]] — prerequisite-for (the ingest tier's output contract)
- [[Length Limits Are a Fit Layer, Not a Prompt]] — extends (the constrain/fit steps of the loop)
- [[AI-Assisted Take-Home Playbook]] — prerequisite-for (how this architecture is presented under a timebox)
