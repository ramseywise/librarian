---
title: Context Graph Is Not an Execution Graph
tags: [langgraph, adk, infra, decision]
summary: Decision to keep a recommendation product's intelligence layer as plain TypeScript in one repo — a relationship graph is a data asset, not an orchestration runtime, and LangGraph/ADK are adopted only for the specific workflow that needs stateful orchestration, behind a named trigger.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-03-intelligence-runtime.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-intelligence-runtime.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-intelligence-runtime.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-intelligence-runtime.md
---

# Context Graph Is Not an Execution Graph

**Date:** 2026-09-03
**Status:** Decided with a named trigger (akira)
**Question:** should the intelligence domain of a TypeScript/Next.js recommendation
product stay in the application repo, become a separate system, or adopt an orchestration
framework (LangGraph or Google ADK)?

## Decision

Keep the product a TypeScript system. Keep the intelligence domain inside the application
repository. Introduce an agent/workflow runtime only for the parts that genuinely require
stateful orchestration. Do not turn the context graph or the bandit into an agent
framework.

## The distinction that settles it

The product's **context graph** is a representation of relationships — person ↔ venue ↔
scene, vibe adjacency, "good before/after this pick". It is queried for retrieval and
adjacency. A LangGraph or ADK graph is an **execution graph**: nodes are steps, edges are
control flow. Using an execution runtime as the database for a relationship graph confuses
the two; the context graph stays a data product (tables + TypeScript) regardless of
whether an agent runtime is ever adopted. Today it is a small hand-curated adjacency map;
the future graph *learns* the relationships currently encoded by hand, which is still a
data problem.

Most of the pipeline is deterministic: time fit, location fit, category match, hard
eligibility, weighted ranking. **TypeScript is not a temporary implementation waiting to
be replaced; it is the correct runtime for deterministic intelligence.**

## When a runtime is justified

| Dimension | Plain TypeScript | LangGraph | Google ADK |
|---|---|---|---|
| Best reason to adopt | Simplicity | Stateful, custom multi-step workflows | Agent ecosystem / Google stack |

Adopt LangGraph (functional API, TypeScript SDK) for *one* workflow when that workflow has
multi-step state that must survive interruption — not for scoring, not for the graph. A
separate learning/experimentation runtime (possibly Python, if ML tooling makes it worth
it) is justified only when the experimentation loop outgrows the product process.

**Separate deployment before separate repository.** If a Python service becomes necessary,
it is deployed as its own service from the same repo first; a second repo is a later,
separately-justified step.

## See Also
- [[ADK vs LangGraph Decision]] — extends (same conclusion for a different product: the gap was vocabulary, not architecture)
- [[ADK vs LangGraph Comparison]] — prerequisite-for
- [[Deployment Topology Ladder]] — instance-of (start low; separate deployment is a rung, separate repo is a later one)
- [[Named-Trigger Deferral]] — instance-of (runtime adoption parked behind a measurable condition)
- [[Knowledge Graph as Shared Agent Memory]] — related (a graph as memory substrate, not as control flow)
