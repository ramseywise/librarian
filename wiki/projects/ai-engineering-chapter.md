---
title: AI Engineering Chapter @Shine
tags: [project, infra, eval, decision]
summary: Cross-company AI Engineering Chapter at Shine — bi-weekly forum for sharing agent framework decisions, observability tooling, and KPI alignment across VA, Banking, Advisor Production, and Matching teams.
updated: 2026-06-05
sources:
  - raw/gdrive/2026-05-15-ai-chapter-meeting-1.md
  - raw/gdrive/2026-05-28-ai-chapter-meeting-2.md
---

# AI Engineering Chapter @Shine

The AI Engineering Chapter is a cross-company technical forum spanning all AI engineering teams at Shine (ageras.com). Led by Sebastian Rose. Bi-weekly, 1-hour sessions on Thursday afternoons.

---

## Teams / Chapter Members

| Team | Focus | Framework |
|---|---|---|
| Virtual Assistant | Billy.dk chatbot (va-agents, va-hypernova, chat-agent) | Google ADK → LangGraph transition |
| Banking / Advisor Production | Agentic CPA — invoice processing with multi-agent pipelines | Custom pipelines (moved away from AG2) |
| Banking — Shai | Customer banking assistant | ADK; evaluating Langfuse |
| Matching Service | Transaction-invoice auto-reconciliation | Custom (90% match accuracy) |

---

## Key Decisions (Chapter-level)

### Observability
- **Langfuse adopted** for LLM observability across all teams (May 15, 2026)
- Patronus AI discontinued (not fitting current context)
- SaaS Langfuse for testing; self-hosted preferred long-term for data sovereignty
- Datadog remains system/APM observability — not replaced by Langfuse
- SSO mandatory before production data use (security team requirement, aligned May 28)

### Evaluation Methodology
- Deterministic/static metrics preferred over LLM-as-judge for the current project phase
- Accounting/document processing requires hard-output metrics (F1, precision, recall) — LLM judge is overkill
- Golden datasets must be built by domain experts (accountants), not just engineers
- Evaluation should run on every PR (CI integration)

### Agent Frameworks (Chapter survey, May 28, 2026)
- **Banking/ADK team**: continuing with Google ADK
- **Advisor Production**: abandoned AG2, now building direct custom pipelines
- **Virtual Assistant**: transitioning to LangGraph for next VA iteration
- AI Agent Framework Selector tool (Alex Makssoud) shared across chapter — Excel-based decision support for AG2, LangChain, CrewAI, Pyante

### Next Meeting Topic
- MCP Server — teams including VA (Hypernova), Daniel Tadros's team (MCP on staging), and Banking chapter hackathon participants will present

---

## KPI Trees by Team

| Team | Primary KPI |
|---|---|
| Virtual Assistant | % customers with regular AI interaction × goal completion rate |
| Advisor Production | Cost, token consumption, no-touch rate (automated validation %) |
| Banking | Eval metrics for synthetic datasets; product-level KPIs not yet defined |
| Matching Service | % correctly matched transactions; auto-reconciliation revert rate |

Sebastian Rose to create a centralized KPI register across all teams.

---

## Compliance Context

- Auditability is a hard requirement for AI systems — compliance teams require the ability to demonstrate what AI systems are doing during regulatory inspections
- Pattern: "glass box" LLM systems (full transparency into inputs/outputs/steps) vs "black box"
- PII reduction required before sending data to external SaaS platforms
- Customer data deletion compliance: use token-based IDs in golden datasets, not copies of raw documents

---

## See Also
- [[Langfuse Platform]]
- [[VA Agent Project]]
- [[Shine Chat Agent]]
- [[VA Hypernova MCP]]
- [[ADK vs LangGraph Comparison]]
- [[Agentic KPI Trees]]
