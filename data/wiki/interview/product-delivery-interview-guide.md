---
title: Product and Delivery Interview Study Guide
tags: [interview, eval, reference]
summary: Exam-prep reference for business-sense rounds — the user → problem → metric → constraint opener, ROI arithmetic on both sides, where AI belongs in a workflow, metric trees, mission-driven-sector constraints, and pitching one system to three audiences.
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--guides--10-product-delivery--interview-guide.md
  - data/raw/repos/sisyphus/interviewing--guides--10-product-delivery--interview-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--10-product-delivery--00-overview.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--product-business.md
  - data/raw/repos/sisyphus/interviewing--guides--10-product-delivery--00-overview.md
---

# Product and Delivery Interview Study Guide

The differentiator round for forward-deployed and data-science roles, and the hidden rubric
everywhere else — published analyses of forward-deployed loops put business judgment and
customer empathy at roughly half the evaluation. The skill is connecting every technical choice
to an outcome, in the client's language.

## The framing habit

Every design answer opens **user → problem → success metric → constraint**. "Reduce support
cost 20% while holding CSAT" beats "build a RAG chatbot", which is a solution looking for a
problem. Process is graded over results: structuring the ambiguity, customising to *this* case,
and using the interviewer as a resource.

## ROI arithmetic

- **Cost:** spend per query × volume, infra, eval and annotation labour, maintenance; napkin
  token math (tokens/query × $/M × queries/day).
- **Value:** hours saved × loaded cost, deflection × cost-per-ticket, conversion lift, risk
  avoided.
- **ROI, not model maximalism.** "A small model gives 90% of the accuracy — why pick it?"
  Because the last 10% costs ~20× and the use case tolerates the error. Reverse the answer when
  errors are expensive.
- Build vs buy vs wait: how fast the capability gap is closing, lock-in, and the data leverage
  you uniquely hold.

## Product sense for AI

- **Where AI belongs:** high-volume, review-tolerant workflows first (drafting, triage,
  summarisation); irreversible actions last. Trust is earned by phase — search, then ask, then
  do.
- **Metric trees:** north star → drivers → guardrails. For agents: goal completion, no-touch
  rate, escalation rate, time-to-trust; guardrails on hallucination, complaints, cost per
  interaction ([[Agentic KPI Trees]]).
- **Feedback loops as product:** thumbs-down → eval set → fix → measured improvement ([[Copilot Learning Loop]]).
- **Failure UX is a product decision:** what the user sees on low confidence (abstain, cite,
  escalate).

## Mission-driven sector constraints

Grant-cycle budgets make API spend need caps and predictability; rotating maintainers favour
boring tech, documentation, and managed services; data is small. Success is impact, not
revenue — define reportable metrics with the organisation from day one. Beneficiary PII is
high-stakes, so consent and minimisation are trust, not checkboxes; run fairness checks on
anything that allocates services. Prefer **capacity building over dependency** — runbooks,
training, something the organisation can operate after you leave.

## One system, three pitches

Exec/funder: outcome, cost, risk, timeline — no architecture. Domain staff: workflow change,
what the tool does and doesn't do, escape hatches. Technical: the design and trade-offs.
Practise each at 60 seconds.

## Question bank (answer sketches)

- *"Client wants a chatbot."* — don't accept the solution; the answer may be search plus three macros.
- *"The model is 92% accurate — ship it?"* — 8% × volume × cost-per-error, then the error *distribution* (harmless vs catastrophic), mitigation UX, then a conditional yes/no.
- *"Prioritise the AI roadmap."* — impact × confidence ÷ effort with guardrail metrics as veto; earn trust with a reviewable-output use case first.

## See Also
- [[Agentic KPI Trees]] — prerequisite-for (metric trees)
- [[Copilot Learning Loop]] — instance-of (feedback loops as product)
- [[User Feedback Loops]] — extends
- [[AI Role Interview Loop Map]] — prerequisite-for (which roles weight this round)
- [[System Design Interview Study Guide]] — complements (the AI-product variant of the design round)
