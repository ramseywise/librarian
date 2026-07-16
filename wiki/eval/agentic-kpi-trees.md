---
title: Agentic KPI Trees
tags: [eval, pattern]
summary: KPI tree pattern for agentic products — goal completion rate, no-touch rate, and transaction match accuracy as the primary success metrics for VA, document processing, and reconciliation agents.
updated: 2026-06-05
sources:
  - raw/gdrive/2026-05-28-ai-chapter-meeting-2.md
---

# Agentic KPI Trees

A KPI tree for an agentic product measures the value the agent creates for the customer, not just its internal quality. The tree flows from a top-level customer value metric down through health metrics and leading indicators.

This pattern emerged from the [client] AI Engineering Chapter's cross-team KPI alignment effort (May 2026). Each team is building toward a centralized KPI register.

---

## KPI Tree by Agent Type

### Conversational / Support Agent (Virtual Assistant team)

**Top-level KPI:** % of customers with regular AI interaction × goal completion rate

- **Goal completion**: No escalation to customer support, OR successful completion of an agentic action (create invoice, write email, etc.)
- Completion definition varies by intent/context — different for chat vs. agentic actions
- Health metrics: usage volume, escalation rate, session length

**Key design challenge:** Defining "completion" for different intents. A completed support query looks different from a completed invoice creation.

### Document Processing / Accounting Agent (Advisor Production / Agentic CPA)

**Top-level KPI:** No-touch rate — % of documents processed automatically without human intervention

- Supporting metrics: cost per document, token consumption, accuracy (F1/precision/recall on extracted fields)
- Latency: end-to-end processing time
- Regression prevention: metric must be tracked per-PR to catch quality degradation early

**Key design challenge:** Evaluations must be deterministic (hard output fields like posting entries, not LLM-judged quality) and must run in CI on every pull request.

### Auto-Reconciliation Agent (Matching Service)

**Top-level KPI:** % of correctly matched transactions to invoices

- Health metric: % of auto-reconciled matches later reverted by users
- Target: ~90% match accuracy (validated empirically)
- Auto-reconciliation: system matches automatically without user action — revert rate is the quality signal

---

## Design Principles

1. **KPI trees belong to product teams, not just engineering** — business metric definition requires PM input and cross-functional alignment
2. **Evaluation conditions should be close to production** — same context, model versions, data distributions as what users see
3. **Make metrics public and accessible** — everyone on the team should see when quality changes (not just the ML team)
4. **Evaluation from the start, not the end** — quality metrics should be defined and running before the agent is in production, ideally on every PR
5. **Golden datasets require domain experts** — accountants build accounting datasets; customer support experts build support datasets. Technical teams alone cannot define ground truth.
6. **Goal completion ≠ no escalation** — for chat agents, escalation to a human is the right outcome for complex queries. The KPI measures completion rate for queries the agent *should* handle.

---

## Compliance / Health Metrics Common to All Agents

- Redirection/escalation rate (runtime) — spikes indicate over-escalation; drops indicate under-escalation
- Token consumption and cost per interaction
- Latency
- Human-in-the-loop trigger rate

---

## See Also
- [[RAG Evaluation]]
- [[HITL Annotation Pipeline]]
- [[VA Eval Harness]]
- [[AI Engineering Chapter @[client]]]
- [[Copilot Learning Loop]]
