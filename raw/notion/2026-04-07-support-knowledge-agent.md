# Support Knowledge Agent — Why, What, and How

**Source:** Notion (work)  
**Date:** 2026-04-07  
**URL:** https://www.notion.so/31ef148b3ab78088b1c8d80877b01784

---

## State of Project (as of doc date)
- Ready to start implementation of FE for the MVP
- Clear definition of the scope of the knowledge agent
- Next: define together

---

## Purpose

Defines the problem, scope, and design approach for the knowledge retrieval capability within the Copilot architecture. Aligns product, engineering, and design on how knowledge is structured, retrieved, evaluated, and continuously improved.

---

## Relationship to Copilot Initiative

The Copilot initiative document defines the overall Copilot vision, system model, and operating principles. This document focuses specifically on the **knowledge retrieval capability** that Copilot uses when answering product and accounting questions.

First user-facing implementation: Help Center chat (validates knowledge system before integrating into Copilot product workflows).

---

## 1. Context

Customer base growth → increased demand for guidance and support. Users frequently need assistance with:
- Product functionality
- Accounting questions
- Financial workflow navigation

Current path: searching help center articles or contacting support directly.

Platform is evolving toward a broader Copilot capability — embedded intelligence across accounting, invoicing, and banking.

For Copilot to operate reliably, it must be grounded in trustworthy knowledge. Static documentation is insufficient. Knowledge must be structured, retrievable, and continuously improved.

---

## 2. Problem Statement

Users struggle to find precise answers when navigating workflows or interpreting accounting behavior.

**Structural limitations of current support model:**
- Users must leave their workflow to search for help
- Help center content optimized for manual reading, not conversational retrieval
- Valuable knowledge from support conversations is not systematically reused
- Guidance and execution are disconnected

**Results:**
- Users open support tickets for resolvable self-service questions
- Users spend unnecessary time searching
- Knowledge remains fragmented across multiple systems

---

## 3. Vision

Knowledge system provides the foundation for Copilot's ability to explain, guide, and assist users across the platform.

Moves from static documentation and keyword search → conversational guidance. Instead of forcing users to leave workflow, retrieves relevant information, clarifies ambiguous questions, and provides contextual explanations within the product.

Over time expands beyond answering questions to: contextual explanations, guided task execution, financial reasoning, proactive recommendations.

First implementation in Help Center. Same knowledge capability later integrated into Copilot across product workflows.

---

## 4. Scope

**In scope:**
- Knowledge ingestion and preparation
- Retrieval and response generation
- Evaluation and quality measurement
- Learning mechanisms for continuous improvement
- User interface for the help center

**Explicitly out of scope:**
- Domain execution agents
- Workflow automation
- Transactional system actions

Users can ask about:
- Product functionality
- Regulatory or reporting questions for supported markets

---

## Success Definition

**Primary outcomes:**
- ≥60% self-service resolution rate (share of queries resolved without escalation)
- ↓15% support contacts from Help Center
- Maintain or improve user satisfaction

**Supporting signals:**
- Answer Grounding: high % of answers referencing correct knowledge sources, low hallucination rate
- Market Accuracy: near-zero rate of wrong regulatory market answers, correct language/market filtering
- Coverage: high coverage of most common support questions, reduction in unanswered queries
- User Resolution: users can resolve common questions without contacting support

**Benchmarking:** compare against existing Bookkeeping Hero chatbot being replaced.

---

## 5. Core Use Cases

**Product guidance** (step-by-step instructions):
- How do I create an invoice?
- How do I correct an invoice after sending it?
- How do I reconcile a bank transaction?

**Accounting interpretation** (higher risk — must be grounded):
- Why is this expense categorized in this account?
- What VAT rate should apply to this transaction?

**Troubleshooting** (often requires clarification):
- Why is my invoice marked as unpaid?
- Why can't I match this transaction?

---

## 6. Conversational Behavior

Must support conversational interaction, not simple Q&A retrieval. Questions often phrased ambiguously. System must be able to clarify intent when necessary.

Example: "Why can't I reconcile this?" — requires follow-up to determine relevant workflow.

Responses must support:
- Clarification questions
- Structured explanations
- References to supporting sources
- Conversational continuity across multiple turns

---

## 7. Knowledge Sources

**Primary:** existing help center articles.

**Future consideration:**
- Product documentation
- Intercom support macros
- Internal support playbooks
- Public accounting guidance
- Regulatory documentation

**Support conversations:** valuable signal but NOT ideal retrieval sources — frequently contain partial explanations, edge cases, corrections made later in conversation. Should primarily serve as input for **knowledge improvement workflows**, not direct retrieval.

---

## 8. Knowledge Preparation

Existing documentation optimized for human reading, not machine retrieval. Preparation work:
- Splitting long articles into smaller knowledge units
- Removing redundant or outdated content
- Rewriting sections so answers are self-contained
- Attaching structured metadata (product area, feature, market, language, object type)

Metadata is critical for retrieval accuracy — prevents technically correct but market-irrelevant answers.

Documentation consistency is a challenge: multiple articles describing same process differently → conflicting explanations.

---

## 9. Market and Language Requirements

Platform operates across multiple markets and languages. Accounting rules vary significantly:
- Chart of accounts
- VAT rules
- Regulatory reporting obligations

Every knowledge unit must include market and language metadata. At runtime, retrieval must include user's market context as part of the query.

**Incorrect regulatory guidance is the highest-risk failure mode.**

---

## 10. Evaluation Strategy

**Benchmark dataset** contains representative user questions derived from historical support conversations.

Each entry includes:
- Original user question
- Expected explanation or answer
- Relevant knowledge source

Dataset purposes:
- Establishing baseline for system performance
- Identifying gaps in existing documentation
- Validating improvements across iterations

**Without structured evaluation dataset, system cannot be improved reliably.**

---

## 11. Learning Loop

Signals indicating improvement required:
- Questions that cannot be answered
- Answers marked as incorrect
- Conversations that escalate to human support
- Recurring questions indicating missing documentation

Typical improvement actions:
- Updating existing articles
- Creating new documentation
- Refining metadata
- Improving retrieval logic

Internal tooling required to: review conversations, analyze failure cases, monitor improvements over time.

---

## 12. Copilot Compatibility

Knowledge system must remain compatible with broader Copilot architecture.

**Context-aware retrieval:** Copilot understands user's context (current page, object, workflow). Knowledge retrieval must accept contextual signals: active product area, object type, market context.

**Integration with Copilot learning loop:** Copilot captures behavioral signals (rejected suggestions, unresolved conversations, escalation patterns) → feed back into knowledge system.

Designing for these integrations ensures system can evolve alongside Copilot without architectural redesign.
