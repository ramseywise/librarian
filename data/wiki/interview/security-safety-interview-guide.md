---
title: Security and Safety Interview Study Guide
tags: [interview, infra, reference]
summary: Exam-prep reference for the "and how do you make it safe?" question — the agent threat model by name, source-to-sink containment instead of detection, the nine-layer defence stack in walk order, operational boundaries before shipping, compliance quick answers, and the recovery ladder as safety's twin.
updated: 2026-10-17
sources:
  - data/raw/repos/learn-ai-engineering/interviewing--guides--7-security-safety--interview-guide.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--7-security-safety--00-overview.md
  - data/raw/repos/learn-ai-engineering/interviewing--guides--security-safety.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--security.md
---

# Security and Safety Interview Study Guide

Every serious agent design question ends with "…and how do you make it safe?"; forward-deployed
loops add compliance framing. Citing the OWASP AI Agent Security and Prompt Injection
Prevention cheat sheets by name lands well.

## Threat model — name risks precisely

- **Prompt injection**, direct (user input) and indirect (retrieved docs, pages, emails, tool
  outputs). Named techniques: encoding/obfuscation, typoglycemia, Best-of-N jailbreaking,
  HTML/markdown injection, multi-turn persistence, system-prompt extraction, **RAG poisoning**,
  multimodal injection. Detail in [[Prompt Injection]].
- **Agent-specific risks:** tool abuse and privilege escalation, exfiltration via tool calls,
  **memory poisoning**, goal hijacking, excessive autonomy, approval manipulation (gaming risk
  thresholds), cascading multi-agent failure, **denial-of-wallet** (unbounded loops burning
  spend), supply-chain risk via third-party tools and MCP servers. Taxonomy in
  [[Agent Security Risk Taxonomy]].
- **Accidental private-data leakage** with no attacker at all — over-broad MCP access is the
  typical path.

## The mental model that scores: source → sink

Don't promise to detect every injection; you can't. Trace where untrusted content enters
(**source**) and which high-impact actions it could influence (**sink**). The goal is that
untrusted content never reaches a dangerous sink with enough authority to cause harm, so even
a successful manipulation has bounded impact. **"How do you prevent prompt injection?" is
answered by reframing to containment; detection-only answers are wrong answers.**

## Defence stack — walk it in order

1. **Input guardrails** — deterministic, LLM-free where possible: fast, cheap, auditable ([[Input Guardrails Pipeline]]).
2. **Separation of trust** — untrusted content in user-role messages only, wrapped in explicit markers so it reads as data.
3. **Structured outputs** — shrink the injection surface and make validation mechanical.
4. **Least privilege** — minimum tools per agent, read vs write scoping, resource allowlists, separate tool sets per trust level, scoped MCP configs ([[MCP Server Security Patterns]]).
5. **HITL for sensitive actions** — classify by impact; irreversible, financial, or externally visible actions need approval.
6. **Dual-LLM / independent verification** — the verifier sees only the proposed action, policy, and evidence, never the contaminated context. Strongest form: the model that reads untrusted content has no tools, and the model with tools never reads raw untrusted content.
7. **Memory hygiene** — validate before persisting, never store arbitrary user input long-term, isolate per tenant.
8. **Output validation** — moderation, PII redaction on the way out, grounding checks.
9. **Trace graders in production** — safety evals run continuously, not only pre-launch.

## Operational boundaries before shipping

Three questions: **who can trigger it** (allowlist), **where it can act** (workspace isolation;
shell tools path-check and error outside the workspace), **what it did** (append-only audit log
per execution). Add circuit breakers (fail-max plus reset timeout) and per-tenant token quotas
against denial-of-wallet. Skills combined with open network access is a high-risk exfiltration
pairing — use strict per-request allowlists. See [[Execution Boundaries and Guardrails]].

## Compliance quick answers

- **GDPR** — deletion, transparency, EU residency → self-hostable observability, logging with
  opt-out, PII masking before traces leave.
- **HIPAA / PCI-DSS** — isolate regulated data; no third-party model calls without the right
  agreements; private endpoints.
- **SOC 2 / ISO 27001** — audit logs, access control, an explainability surface.
- **PII masking** — regex (fast, misses context) vs NER vs LLM vs hybrid; contextual PII ("my
  neighbour from apartment 4B") is the hard case ([[PII Masking Approaches]]).

## Reliability is safety's twin

From a published pharma research-assistant case study: persist workflow state per node so
recovery resumes from the failed step; retry at both LLM-call and node level; fallback chains
across providers; feed error context back so the agent replans; user-initiated retry skips
completed steps. **Degradation ladder: retry → fallback model → simpler baseline → human.**
On a streaming failure, close with an error event — never hang.

## Question bank (answer sketches)

- *"Secure banking-support chatbot."* — lead with governance layers: trust separation, tenant-scoped data access, approved-corpus retrieval only, anonymised session memory, human fallback, output redaction, full audit trail.
- *"Your agent has shell access."* — workspace isolation, command allowlists, sandbox, audit log, HITL for destructive ops, quotas.
- *"RAG poisoning?"* — corpus admission control, source confidence tiers, grounding checks, anomaly monitoring on retrieval distributions.
- *"What's different about multi-agent security?"* — every handoff is an injection surface; authenticate inter-agent messages, verify provenance, isolate so one compromised agent cannot cascade.

## See Also
- [[Prompt Injection]] — prerequisite-for (the core attack in depth)
- [[Agent Security Risk Taxonomy]] — prerequisite-for
- [[Input Guardrails Pipeline]] — instance-of (layer 1 of the stack)
- [[Production Hardening Patterns]] — extends
- [[Agents Interview Study Guide]] — complements (HITL and harness boundaries)
