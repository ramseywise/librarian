---
title: Shine Knowledge Agent
tags: [rag, eval, langgraph, project]
summary: Shine's Help Center RAG system — knowledge retrieval capability for the Copilot architecture, initially deployed as Help Center chat, targeting ≥60% self-service resolution.
updated: 2026-04-25
sources:
  - raw/notion/2026-04-13-rag-pipeline-requirements.md
  - raw/notion/2026-04-07-support-knowledge-agent.md
---

# Shine Knowledge Agent

## What It Is

The knowledge retrieval capability within the Shine Copilot architecture. First user-facing implementation: Help Center chat (validates knowledge system before integrating into Copilot product workflows).

Not a standalone feature — it is the knowledge foundation that Copilot uses across product and accounting questions. See [[Shine Copilot Architecture]].

**Replaces:** Bookkeeping Hero chatbot (existing system, used as benchmarking baseline).

---

## Problem Statement

Users struggle to find precise answers when navigating workflows or interpreting accounting behavior:
- Must leave workflow to search for help
- Help center content optimized for manual reading, not conversational retrieval
- Valuable knowledge from support conversations is not systematically reused
- Guidance and execution are disconnected

Result: users open support tickets for resolvable self-service questions; knowledge remains fragmented.

---

## MVP Scope

**Market:** Danish only (DK/EN languages, source written in Danish). System design must support future multi-language, multi-market, multi-product-area expansion.

**Knowledge sources:**
- Minimum: Help Center articles + blog content
- Preferred: include Intercom content if feasible

**Explicitly out of scope:**
- Domain execution agents
- Workflow automation
- Transactional system actions

---

## Success Targets

- **≥60% self-service resolution rate** (queries resolved without escalation)
- **↓15% support contacts from Help Center**
- **Maintain or improve user satisfaction**

**Supporting signals:**
- High % of answers referencing correct knowledge sources, low hallucination rate
- Near-zero rate of wrong regulatory market answers (correct language/market filtering)
- High coverage of most common support questions

**Benchmarking:** compare against Bookkeeping Hero (existing system) — evaluate answer quality, identify cases where existing system performs well, identify failure cases to avoid.

---

## Core Use Cases

### Product Guidance (step-by-step)
How do I create an invoice? / How do I reconcile a bank transaction?

### Accounting Interpretation (higher risk — must be grounded)
Why is this expense categorized in this account? / What VAT rate applies?

### Troubleshooting (often requires clarification)
Why is my invoice marked as unpaid? / Why can't I match this transaction?

Troubleshooting questions frequently require clarification before answering — see Conversational Behavior below.

---

## Conversational Behavior

Must support multi-turn clarification, not simple Q&A retrieval. Questions often phrased ambiguously.

Example: "Why can't I reconcile this?" → requires follow-up to determine relevant workflow or object.

Responses must support:
- Clarification questions
- Structured explanations
- References to supporting sources (link/title)
- Conversational continuity across multiple turns

---

## Knowledge Sources

**Primary:** existing Help Center articles.

**Future:** product documentation, Intercom support macros, internal support playbooks, public accounting guidance, regulatory documentation.

**Support conversations:** valuable signal but NOT direct retrieval sources — contain partial explanations, edge cases, corrections mid-conversation. Should feed **knowledge improvement workflows** instead.

---

## Knowledge Preparation

See [[RAG Knowledge Preparation]] for the full protocol. Key steps:
- Split long articles into smaller knowledge units
- Remove redundant or outdated content
- Rewrite sections so answers are self-contained
- Attach structured metadata: product area, feature, market, language, object type

Documentation consistency is a challenge — multiple articles describing the same process differently can produce conflicting answers.

---

## Market and Language Requirements

Platform operates across multiple markets. Accounting rules differ significantly:
- Chart of accounts
- VAT rules
- Regulatory reporting obligations

Every knowledge unit must include market and language metadata. Retrieval must include user's market context as part of the query at runtime.

**Incorrect regulatory guidance is the highest-risk failure mode.** Market boundary enforcement is a fundamental design requirement, not an optional filter.

---

## Evaluation Strategy

**Benchmark dataset** (derived from historical support conversations):
- Original user question
- Expected explanation or answer
- Relevant knowledge source

Serves three purposes:
1. Establishing baseline for system performance
2. Identifying gaps in existing documentation
3. Validating improvements across iterations

**"Without a structured evaluation dataset, the system cannot be improved reliably."**

Metrics target: align with [[RAG Evaluation]] three-tier architecture. Self-service resolution rate (≥60%) as the top-line business metric alongside retrieval hit_rate@k and hallucination rate.

---

## Escalation Path

Triggered when:
- System lacks sufficient information
- Request falls into predefined unsupported scenarios (subscription termination, account-specific cases)

Escalation paths:
- Contact support entry points (UI-level)
- Forward full context to Intercom
- Support email-based escalation when required

All escalated conversations must be logged (original question + final agent response) for later analysis and knowledge base improvement.

---

## [[Copilot Learning Loop]] Integration

Signals feeding the learning loop:
- Questions that cannot be answered
- Answers marked as incorrect
- Conversations escalating to human support
- Recurring questions indicating missing documentation

Improvement actions:
- Update existing articles
- Create new documentation
- Refine metadata
- Improve retrieval logic

Internal tooling required to review conversations, analyze failure cases, and monitor improvements.

---

## Copilot Compatibility

Designed for future context-aware retrieval — when a user is viewing a specific invoice or expense, knowledge retrieval should prioritize content relevant to that object type.

Retrieval system must accept contextual signals at runtime:
- Active product area
- Object type
- Market context

---

## Architecture Requirements

- Retrieval exposed via service/API layer (UI-independent)
- Designed as **reusable service**: Help Center (MVP) → Copilot (future)

---

## See Also
- [[Shine Copilot Architecture]]
- [[RAG Knowledge Preparation]]
- [[LangGraph CRAG Pipeline]]
- [[RAG Evaluation]]
- [[RAG Retrieval Strategies]]
- [[Copilot Learning Loop]]
- [[PII Masking Approaches]]
- [[HITL Annotation Pipeline]]
