---
title: Data Pipeline Pattern Selection
tags: [infra, comparison]
summary: Four ways data reaches an AI system — batch ingest, event-driven, streaming, hybrid — chosen by one question about where the data comes from, with hybrid treated as a phase-2 evolution rather than a phase-1 option.
updated: 2026-08-04
sources:
  - data/raw/claude-docs/ai-project-template/skills/project-discovery/reference/data-pipeline-patterns.md
---

# Data Pipeline Pattern Selection

How data gets into and moves through an AI system. The choice fixes how fresh the AI's
knowledge is, how much infrastructure the team must operate, and which scaffold toggles get
set.

| Pattern | Freshness | Infrastructure | Best for |
|---|---|---|---|
| Batch ingest | Hours to days | Simple — run once, query many | Stable document corpora |
| Event-driven | Minutes | Medium — webhooks + queue | System integrations |
| Streaming | Seconds | Complex — persistent connections | Real-time monitoring |
| Hybrid | Varies by source | Medium–high | Multiple data sources |

## One question decides it

> **"Where does the data the AI needs come from?"**

| Answer | Pattern |
|---|---|
| Documents we already have (PDFs, reports) | Batch ingest |
| Things that happen (meetings, form submissions, events) | Event-driven |
| Live systems (databases, calendars, APIs) | Event-driven or hybrid |
| A conversation happening right now | Streaming |
| A mix | Start with the dominant one; plan hybrid for phase 2 |

Sourcing, not latency, is the discriminator. Asking users how fresh the data must be invites
"real-time" as a reflexive answer; asking where it comes from produces a checkable fact.

## Batch ingest: the default, and why

Documents are loaded, chunked, embedded, and stored once (or on a schedule); queries hit the
pre-built index. The ingest pipeline runs entirely off the query path, which is what makes it
the simplest architecture: no live infrastructure beyond the query endpoint.

It is correct when the corpus is documents, content changes weekly-to-monthly, and hours of
staleness are tolerable — a legal aid org's 200 housing-regulation PDFs updated quarterly.
It is wrong the moment the AI must know about something that happened five minutes ago, or
when the source is an API rather than a document set.

The trade is precisely staleness for debuggability: the index is inspectable and the ingest
is repeatable. Backend choice scales with size (an embedded store below ~10k chunks, Postgres
above it, or when Postgres is already the deployment target). See
[[RAG Knowledge Preparation]] and [[Vector Database Comparison]] for the internals.

## Event-driven: minutes, not seconds

External events — webhook callbacks, form submissions, scheduled triggers — start independent
extract → transform → act pipelines. There is **no persistent corpus**; data flows through
rather than being stored and searched. A Zoom session ends → transcribe → extract action items
→ create tasks → notify on Slack.

Two boundaries mark where it stops working: users needing to *search across historical*
events need retrieval instead, and volumes above roughly 1000/hour need real message-queue
infrastructure rather than direct handlers.

The named hazard is [[Webhook Handler Idempotency]] — *"events may be delivered more than
once. Every handler must be safe to run twice."* The complementary difficulty is failure
granularity: *"what if step 3 of 5 fails?"* — a multi-step pipeline has partial-completion
states a single request does not, and local testing requires simulating events that normally
arrive from outside.

Event-driven pipelines pair with `human_approval: sometimes`, because the actions at the end
of the chain (sending mail, creating records) are the irreversible ones.

## Streaming: usually not what "real-time" means

Persistent connections — WebSockets, SSE, polling — processing at sub-second latency with
live state. It fits a crisis hotline co-pilot surfacing resources *during* a call, not
after-the-fact summaries.

It is the only pattern rated a full semester of complexity: connection management, state
synchronization, graceful reconnection, no serverless deployment, and frontend expertise.
Hence the standing advice:

> *"Unless the use case genuinely requires sub-second latency, start with event-driven and
> add streaming later. Most 'real-time' needs are actually 'within a few minutes' needs."*

This is a vocabulary correction, not a capability judgment — users say "real-time" for a
latency class that event-driven already serves at a fraction of the operational cost.

## Hybrid is phase 2 by construction

A static batch-ingested corpus plus live sources queried at request time: policy lookups from
a procedures manual, case status from Salesforce, availability from Google Calendar, combined
to answer *"what should this client do next?"*

> *"This is almost always a phase-2 evolution, not a phase-1 choice."*

The blocking cost is evaluation, not implementation: *"harder to evaluate (which source
caused a wrong answer?)"*. Multiple data paths make an incorrect answer ambiguous between
retrieval failure and stale live data, so attributing regressions requires per-source
instrumentation the first version does not have.

The discipline is to **start with the dominant pattern and name the second path explicitly in
"Out of Scope"** for the POC — an application of the same not-a-blocker-but-recorded move as
[[Deferred Decision Status]]. Recording the deferred path is what makes adding it later a
plan rather than a surprise.

## See Also
- [[Integration Pattern Selection]] — alternative-to (the sibling card: how services connect, not how data arrives)
- [[Webhook Handler Idempotency]] — prerequisite-for (the event-driven pattern's core obligation)
- [[Project Discovery Conversation]] — prerequisite-for (the pipeline question is a discovery output)
- [[AI Project Archetypes]] — extends (archetype implies a default pipeline)
- [[Deferred Decision Status]] — extends (the deferred second data path stays recorded)
- [[AI Project Template Scaffold]] — instance-of (project_type / vector_backend toggles)
- [[Data Engineering Foundations]] — complements (the six pipeline stages, orthogonal to how data arrives)
