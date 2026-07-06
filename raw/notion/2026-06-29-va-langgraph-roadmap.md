# VA LangGraph Roadmap

**Source:** https://app.notion.com/p/374f148b3ab780649696c957e84a93b5
**Last edited:** 2026-06-29
**Project:** Virtual Assistant

## Goals

HC subgraph + router → multi-agent system (Python & LangGraph)

## Roadmap: Virtual Assistant v1 — TypeScript ADK → Python LangGraph

### Overview

**Objective:** Migrate two existing TypeScript ADK agents into a unified Python LangGraph multi-agent system.

**Source agents:**
- **PoC VA Agent** (TypeScript ADK) — proof-of-concept virtual assistant
- **MVP HC Agent** (TypeScript ADK) — Help Center RAG agent

**Target architecture:** Router (Python LangGraph) orchestrating two parallel subgraphs:
- **Receptionist Agent** (general conversation, triage, fallback)
- **HC Agent** (support/RAG)

Future agents (e.g., Invoicing Agent) are explicitly **out of scope for v1**.

### Why the Receptionist Agent is Needed

Not a "nice to have" — closes three concrete gaps:

1. **Router needs somewhere to send non-support traffic.** Without it, all greetings, chit-chat, and OOS questions force into the RAG pipeline — needless retrieval, hallucinated answers.
2. **Makes the router a real classifier.** With a single agent the router is just an on/off gate. A second destination turns intent classification into an actual decision that can be evaluated and de-risked in v1.
3. **Natural fallback and triage layer.** Low-confidence or no-match defaults to Receptionist, which can clarify and re-route.

**Scope guardrail:** Receptionist v1 mandate is thin — greet, clarify, handle conversational turns, triage, route. No business logic.

---

## Phase 0 — Golden Path: LangGraph "Hello World" (1 week)

**Purpose:** Prove the deployment + observability platform before porting any business logic.

**Deliverables:**
- Minimal LangGraph graph running end-to-end in Python
- Repeatable Golden Path project template the team can clone for every future agent
- **Deployment target: AWS Fargate** — containerize LangGraph service, validate CI/CD path
- CI/CD pipeline validated (build → deploy → invoke → observe)
- Bare-runtime latency baseline (Python + LangGraph overhead before RAG/LLM)

**Platform ingestion (established here):**
- LangGraph runtime + scaffolding
- Langfuse — LLM tracing, prompt management, step-level debugging
- DataDog — application monitoring, logging, error tracking, alerting
- Context/memory management baseline

**Exit criteria:** Trivial graph deploys to Fargate, emits traces to Langfuse and metrics to DataDog.

---

## Phase 1 — v1 HC Agent: 1:1 Port (1 week)

**Purpose:** Faithfully reproduce MVP HC RAG agent in Python/LangGraph with no behavioral changes.

**Deliverables:**
- RAG tool ported to Python (vector search, embedding, retrieval)
- State schema design (RAG-only, TypedDict) — minimal state for HC Agent in isolation
- Context/memory management scoped to HC Agent
- HC Agent runs standalone as a LangGraph graph (the future subgraph)

**Prerequisite:** Evaluation dataset of historical user queries + ideal answers from TS agents. Must exist or be built as an explicit Phase 1 task.

**Validation:** Evaluate Python HC Agent against frozen dataset using Ragas or TruLens. Named metrics with explicit thresholds: Context Precision, Context Recall, Answer Relevancy, Faithfulness.

**Exit criteria:** Python HC Agent matches or exceeds TypeScript MVP on parity set.

---

## Phase 2 — v1 VA Router: Design Document (2–3 weeks)

**Purpose:** Design-first — produce a LangGraph design document before writing the full system.

**Deliverables:**
- LangGraph architecture design doc — multi-way routing (Receptionist / HC / future agents)
- Routing & fallback policy — intent taxonomy, classification between Receptionist and HC, low-confidence defaults to Receptionist
- Receptionist Agent design — thin mandate (greet, clarify, triage, re-route)
- **Global state schema (TypedDict with explicit reducer functions)** — shared contract spanning router ↔ subgraphs; superset of Phase 1 RAG-only schema
- **Checkpoint & data-privacy strategy:** PostgreSQL checkpointer (LangGraph's PostgreSQL checkpointer). Fargate stays stateless. Define thread_id, retention/cleanup, S3 offload for large artifacts. **PII masking required inside the graph** (Microsoft Presidio or targeted regex) before checkpointer commits.
- Context/memory management strategy at system level
- HITL design — interrupt/resume workflows, escalate trigger when RAG confidence is low
- Evalsets for routing classification

**Key open item:** Does TypeScript ADK already implement HITL? Audit the source. Scopes Phase 3.

**Exit criteria:** Approved design document.

---

## Phase 3 — v1 VA: Full System Implementation (3 weeks)

**Workstreams:**
1. Router creation — Supervisor pattern with strict structured output (Pydantic/JSON)
2. HC subgraph integration — mount Phase 1 agent as subgraph, implement state-passing
3. Receptionist Agent build — thin triage/general-conversation/fallback subgraph
4. Context/memory management — promote to unified system-level design
5. State schema — implement shared schema between RAG, Receptionist, and router
6. Checkpointing — DynamoDBSaver with TTL, gzip compression, S3 offload; verify recovery and HITL resume
7. HITL — implement per Phase 2 decision

**Exit criteria:** Router + Receptionist + HC subgraphs operate as one system, pass evalsets, meet observability and HITL requirements. Virtual Assistant v1 feature-complete.

---

## Phase 4 — Validation & Cutover (3 weeks)

**Deliverables:**
- End-to-end SLA load test against assembled system (router + RAG + Receptionist)
- System evaluation — Phase 3 evalsets at scale, Langfuse trace review
- Shadow testing with semantic parity — LLM-as-a-judge (not string diffing)
- Canary cutover — 10% → 50% → 100% ramp with DataDog monitoring
- Soak period — 7–14 days at 100% traffic with TS agents kept idle (rollback ready)
- Decommissioning — only after soak period

**Exit criteria:** Live traffic served by v1, semantic parity confirmed, SLAs met, soak period elapsed — then TypeScript PoC VA and MVP HC ADK agents decommissioned.

---

## Cross-Cutting Concerns

- **Context/memory management:** narrows in Phase 1 (RAG-only) → widens in Phases 2–3 (router-aware)
- **Observability:** Langfuse + DataDog extended as each component lands
- **Evaluation:** Phase 1 = offline metric-based parity (Ragas/TruLens); Phase 4 = semantic parity (LLM-as-judge on shadow traffic)
- **State schema continuity:** RAG-only schema (Phase 1) must be forward-compatible subset of shared schema

---

## Phase Dependencies

| Phase | Depends on | Estimate |
|---|---|---|
| 0 — Golden Path | — | 1 week |
| 1 — HC Agent | Phase 0 | 1 week |
| 2 — Router Design | — (can parallel Phase 1) | 2–3 weeks |
| 3 — Full System | Phases 1 & 2 | 3 weeks |
| 4 — Validation & Cutover | Phase 3 | 3 weeks |
