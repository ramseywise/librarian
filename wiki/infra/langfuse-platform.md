---
title: Langfuse Platform
tags: [infra, eval, concept]
summary: Langfuse is an open-source LLM engineering platform for tracing, prompt management, and evaluation — chosen by Shine's AI teams as the observability standard, with SSO and governance pending before production rollout.
updated: 2026-06-05
sources:
  - raw/gdrive/2026-05-15-ai-chapter-meeting-1.md
  - raw/gdrive/2026-05-28-ai-chapter-meeting-2.md
  - raw/notion/2026-05-13-compare-langgraph-adk-langfuse-langsmith.md
  - raw/notion/2026-06-01-chat-agent-rfc.md
---

# Langfuse Platform

Langfuse is an open-source LLM engineering platform for observability, tracing, evaluation, prompt management, and analytics. It is purpose-built for LLMs and agentic workflows — unlike general APM tools like Datadog, which are not designed for the trace-level visibility needed when agents call other agents, manage sessions, and run multi-step evaluations.

**Shine adoption status (as of 2026-06):** Legal review complete; contract being finalized. SSO is mandatory before production rollout. SaaS version adopted for testing; self-hosting preferred long-term for data sovereignty. Virtual Assistant and Advisor Production teams have both connected staging environments.

---

## Core Capabilities

### 1. Observability & Tracing
- Traces every request and tool call in an LLM system — inputs, outputs, inter-agent steps, guardrail decisions, execution time, cost
- Session-based tracing: groups all traces for a conversation into one view
- Non-LLM deterministic steps can also be tracked via the SDK (not just model calls)
- OpenTelemetry-native — integrates with frameworks via OTel without custom instrumentation

### 2. Prompt Management
- Prompts stored and versioned in Langfuse platform
- Non-engineers (PMs, domain experts) can update prompts without code changes
- **Langfuse-first approach**: prompts loaded from Langfuse at runtime; fallback to repo version if unavailable. CI check ensures repo stays in sync.
- Enables fast iteration on prompts without code redeploy

### 3. Evaluation & Experiments
- Upload golden datasets and run experiments against them
- Track custom metrics (F1 score, precision, recall, latency) per experiment
- Compare experiments side-by-side
- Does NOT support uploading/running custom Python code in the platform — evaluations must run in your code and push results to Langfuse
- Dashboards and score timelines for monitoring quality over time

### 4. Multi-Project Organization
- Separate work into distinct projects with independent access control
- Unlimited users on all tiers — charged per usage, not per seat

---

## Datadog / Langfuse Split

Langfuse is **not** a replacement for Datadog:
- **Datadog**: system monitoring, APM, infrastructure — uptime, endpoint health, latency at the service level
- **Langfuse**: LLM-agent-specific traces, prompt management, evaluation, quality metrics over time

The key architectural split: Datadog for ops, Langfuse for AI quality. Both are needed; they serve different audiences and answer different questions.

---

## Shine-Specific Decisions

### SaaS vs Self-Hosting
- **Current**: SaaS version chosen for the testing phase (avoids infrastructure management overhead)
- **Preferred long-term**: self-hosted, for PII/data sovereignty — traces may contain sensitive financial data
- Self-hosting requires infrastructure team involvement (upgrades, scaling, access control)

### Compliance & Governance
- PII reduction required before sending data to Langfuse (SaaS is external infrastructure)
- Governance framework being defined: process for onboarding teams to production not yet finalized
- Data deletion compliance pattern: use token-based references (IDs) in golden datasets to point to files in their authoritative storage — never copy raw documents into the observability platform

### SSO Requirement
- SSO is **mandatory** before production use (security team requirement)
- Will be enabled as part of the pro contract (Teams add-on tier)
- Currently using password/Google auth in staging — acceptable for testing only

### Legal Status
- Legal review complete as of May 2026
- Contract finalization in progress (aligning with Shine's requirements)
- Until contract signed, production data is not permitted

---

## Langfuse vs Patronus AI (Shine context)

| Dimension | Langfuse | Patronus AI |
|---|---|---|
| Deployment | SaaS + self-hosted | Self-hosted (on-premise, used by Advisor Production inside SHI) |
| LLM-as-judge | Available but not required | Pre-packaged LLM-as-judge evaluators |
| Framework fit | Framework-neutral, OTel-native | Similar feature set |
| Maturity | More mature, larger ecosystem | Startup (direct contact with team in San Francisco) |
| Shine decision | Adopted (legal cleared) | Being discontinued — doesn't fit current SHI context |

---

## Langfuse vs LangSmith

See [[Observability — LangFuse vs LangSmith Decision]] for the original RAG-focused decision.

The Shine VA team conducted a more comprehensive evaluation for an AWS-hosted, ADK-compatible, high-compliance accounting system:

| Platform | Weighted Score | Best when |
|---|---|---|
| **Langfuse** | **8.58 / 10** | AWS-hosted, ADK-compatible, Datadog-aligned, high-compliance |
| LangSmith | 7.92 / 10 | LangGraph-first architecture with deep HITL debugging needs |

Langfuse wins on: security/data sovereignty, AWS fit, Datadog integration, cost/scalability, framework agnosticism, prompt governance.  
LangSmith wins on: LangGraph-native HITL trace quality, evaluation workflow maturity.

Pricing: Langfuse = unlimited users + usage-based ($29–$199/mo). LangSmith = $39/user/month + per-trace overages (~6× more expensive at scale).

---

## Integration Patterns

### Chat Agent (Shine Banking)
- Traces sent to Langfuse after each turn
- Prompts loaded from Langfuse versioned registry (Langfuse-first approach)
- Banking Context Classifier prompt managed in Langfuse
- Redirection rate tracked as a Langfuse runtime metric

### Advisor Production / Agentic CPA
- Langfuse connected to staging for observability
- In-house evaluation solution being built for deterministic metrics (not using Langfuse evaluation layer)
- Patronus AI being discontinued in favor of Langfuse for observability

---

## See Also
- [[Observability — LangFuse vs LangSmith Decision]]
- [[AI Engineering Chapter @Shine]]
- [[Shine Chat Agent]]
- [[Input Guardrails Pipeline]]
- [[RAG Evaluation]]
