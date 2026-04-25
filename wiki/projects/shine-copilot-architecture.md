---
title: Shine Copilot Architecture
tags: [adk, langgraph, mcp, memory, eval, project]
summary: Shine's Copilot — embedded guidance, orchestration, and execution layer across accounting, invoicing, and banking. Centralized VA team owns orchestration; domain teams own execution agents.
updated: 2026-04-25
sources:
  - raw/notion/2026-04-09-copilot-why-what-how.md
  - raw/notion/2026-04-21-agt09-adk-vs-langgraph-spike.md
---

# Shine Copilot Architecture

## What It Is

Copilot is the embedded guidance, orchestration, and execution layer across the Shine accounting platform. It is NOT a standalone chatbot — it is a cross-domain capability spanning accounting, invoicing, and banking that integrates directly into workflows.

**Long-term ambition:** Zero minutes spent on administration for small businesses.

**Evolution stages:**
1. Assistance and explanation
2. Guided execution
3. Structured automation
4. Selective autonomy in well-defined areas

---

## System Model

### Conversational Interface
Structured chat interface — universal entry point but not the system itself. Maintains session history, scoped per organization and user, preserves context during escalation.

### Multi-Modal Responses & Structured Elicitation
Copilot responds beyond text — [[Multi-Modal Agent Response]] pattern. Can generate:
- Structured text explanations
- Data visualizations (charts, tables, financial summaries)
- Interactive UI components (buttons, dropdowns, constrained choices)
- Contextual action prompts (Suggestion/Automation cards)
- Full task surfaces (invoice forms, draft previews, structured workflows)

**Structured elicitation:** dynamically generates UI elements so users provide precise input without natural language descriptions. Reduces ambiguity, shortens path from intent to completion.

### Context Awareness & Personalization
Copilot understands: active organization, current page or object, user permissions, historical interactions.

Over time extends to personalization: recognizes recurring workflows, adapts based on past actions, surfaces suggestions proactively.

### Agent-Orchestrated Execution
Domain-specific agents perform tasks (invoice creation, reconciliation, financial aggregation). Orchestrator interprets intent and invokes the appropriate agent. ML services operate as specialized agents.

---

## Ownership Model

### Copilot Team (VA Team) — coordination layer
- Conversational infrastructure
- Orchestration layer
- Context handling and session management
- Long-term memory
- [[Copilot Learning Loop]] systems
- Cross-domain intelligence standards and governance model

### Domain / Stream-Aligned Teams — execution layer
- Domain-specific agents
- Business logic and execution flows
- Accuracy and regulatory correctness
- Data exposure and API contracts for orchestration

**Structural intent:** Domain expertise stays embedded in domain teams. Cross-domain intelligence remains centralized and consistent.

*Practical note: VA team expects to implement the first use cases and support domain teams for initial rollout.*

---

## Three-Level Interaction Hierarchy

| Level | Name | User Experience | Examples |
|---|---|---|---|
| 1 | Explicit AI Interaction | "I am talking to intelligence" — open-ended NL; reasoning visible | Chat agent, support chat |
| 2 | Guided Intelligence | "The product is thinking with me" — AI suggests/drafts; user reviews | Receipt reading, VAT suggestions, expense categorization |
| 3 | Invisible Intelligence | "The product just works" — background processing; no AI framing | Automated matching, email receipt fetching |

Copilot spans all three levels — unifying layer connecting explicit assistance, guided intelligence, and background automation.

---

## Core Scenarios

### Knowledge-Based Assistance
Powered by [[Shine Knowledge Agent]]. Answers product usage questions and accounting scenarios. Contextual, conversational, capable of clarification. Full escalation path preserves context.

### From Explanation to Execution
Interaction evolves across levels:
1. **Instructional guidance** — step-by-step explanation
2. **Guided navigation** — take user directly to relevant page/object
3. **Embedded task surface** — generate appropriate interface within interaction (forms, pre-filled drafts)
4. **Execution through agents** — collect inputs, execute via domain agent

Example: "How do I create an invoice?" → explanation → navigate to invoice page → pre-filled invoice draft → confirmation → execute.

### Context-Aware Object Interaction
When user is viewing a specific expense, invoice, or transaction — Copilot understands the exact object and explains it in context (like having an accountant by their side). Suggests alternative categorizations. Context flows both ways (UI → chat and chat → UI).

### Proactive Task Nudging
Surfaces contextual prompts based on system state: unpaid invoices, missing reconciliations, upcoming VAT deadlines. Reduces monitoring burden.

### Financial Insights
Natural language analysis across accounting, invoicing, and banking. Generates supporting visualizations. Over time: reactive answers → proactive recommendations.

---

## Architectural Principles

- **Scoped by Design:** All sessions, actions, and memory strictly scoped to active organization and user.
- **Centralized Orchestration:** Conversation state, intent interpretation, and policy guardrails managed by single coordination layer. Domain agents remain stateless.
- **Secure and Observable Execution:** All agent interactions auditable, structured, policy-governed. Risk, confidence, and ambiguity must be explicit.
- **Framework Independence:** Built around contracts and standardized schemas — underlying AI frameworks can evolve without redefining system architecture.
- **Human Compatibility:** Must support human escalation, advisor collaboration, and structured handoffs without loss of context.

---

## Success Metrics

| Dimension | Key Metric |
|---|---|
| Automation & Efficiency | % workflows via Copilot, time-to-completion reduction, automation acceptance rate |
| Self-Service Resolution | % intents resolved without escalation, escalation rate after multi-turn conversation |
| Financial Insight Utilization | insight → execution conversion, volume of insight queries |
| Trust & Reliability | correction rate, undo/override frequency, repeat usage after error events |
| Adoption & Activation | % active users weekly, depth of sessions (multi-step vs single-turn) |
| Learning Velocity | time from unresolved question → KB update, reduction in repeated unanswered intents |

---

## Risk Framing

- **Over-Automation Risk:** Premature autonomy in financial workflows erodes trust. Capability must expand only where predictability is high.
- **Trust Calibration:** Users must understand when system is assisting vs suggesting vs executing.
- **Knowledge Accuracy:** Must support clarification loops and escalation paths — not behave like static search.
- **Cross-Domain Governance:** Without orchestration standards, intelligence fragments across domains.

---

## Relationship to VA Agent Project

The [[VA Agent Project]] (Billy VA) is the active development vehicle for the Copilot execution layer. The ADK implementation maps to the Copilot orchestration shell; the LangGraph implementation maps to deterministic domain pipelines. AGT-09 (ADK vs LangGraph spike, ✅ Q2) validated both are viable with different strengths — see [[ADK vs LangGraph Decision]].

---

## See Also
- [[Shine Knowledge Agent]]
- [[VA Agent Project]]
- [[ADK vs LangGraph Comparison]]
- [[ADK Context Engineering]]
- [[Copilot Learning Loop]]
- [[Multi-Agent Orchestration Patterns]]
- [[Agent Memory Types]]
- [[Multi-Modal Agent Response]]
