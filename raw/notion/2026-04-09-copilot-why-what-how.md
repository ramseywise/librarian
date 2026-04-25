# Copilot — Why, What, and How

**Source:** Notion (work)  
**Date:** 2026-04-09  
**URL:** https://www.notion.so/30df148b3ab780258383cb415b68b3ac

---

## State of Project (as of doc date)
- Initial discovery complete (competitor benchmarking, user survey, AI-driven workflow analysis)
- In progress: iterating on chat interface interaction patterns; prototyping foundational Copilot infrastructure (orchestration, context awareness, execution layer)
- Next: user feedback on prototype, collect new use cases

---

## Executive Summary

Copilot is the embedded guidance, orchestration, and execution layer across the platform. It reduces administrative burden, increases confidence in financial workflows, and progressively enables automation.

Copilot is NOT a standalone chatbot. It is a cross-domain capability spanning accounting, invoicing, and banking — integrated directly into workflows.

**Long-term ambition:** Zero minutes spent on administration for small businesses. Approached incrementally:
1. Assistance and explanation
2. Guided execution
3. Structured automation
4. Selective autonomy in well-defined areas

---

## Problems Copilot Addresses

### Bridging the Execution Gap
Most platforms are systems of record — store data, execute commands, rely on users to know what to do. Copilot reduces the distance between intent and execution.

### Domain Complexity and Confidence Gaps
Automation handles structured tasks but uncertainty remains in edge cases, regulatory nuances, VAT-related scenarios. Copilot coordinates existing intelligence + adds structured reasoning.

### Repetitive Manual Work
Many workflows are predictable but still require repeated confirmations. Copilot shifts users from performing predictable work to reviewing and approving it.

### Information Fragmentation
Guidance and execution are separated — users leave workflow to search for help, then return to execute. Copilot combines guidance and action in one surface.

### Monitoring Burden
Small businesses must actively monitor unpaid invoices, reconciliation gaps, VAT deadlines. Copilot introduces structured prompts and contextual nudges.

### Lack of Personalization and Context
Copilot adapts to user's context, behavior, and preferences — making guidance more relevant, timely, and actionable.

---

## Copilot System Model

Copilot is architected as a coordination layer between:

### Conversational Interface
Structured chat interface — universal entry point but not the system itself.
- Maintains session history
- Scoped per organization and user
- Supports clarifying follow-up questions
- Preserves context during escalation

### Multi-Modal Responses & Structured Elicitation
Copilot does not respond only with text. Can generate:
- Structured text explanations
- Data visualizations (charts, tables, financial summaries)
- Interactive UI components
- Contextual action prompts (Suggestion/Automation cards)
- Full task surfaces (invoice forms, draft previews, structured workflows)

**Structured elicitation:** system can dynamically generate UI elements — buttons, dropdowns, forms, pre-filled drafts — so users provide precise input without natural language descriptions.

Conversation is one interface. Generated UI is another. Copilot moves fluidly between reasoning, explanation, visualization, and execution.

### Context Awareness & Personalization
Copilot understands:
- Active organization
- Current page or object
- User permissions
- Historical interactions

Over time extends to personalization: recognizes recurring workflows, adapts based on past actions, surfaces suggestions proactively, tailors communication.

### Agent-Orchestrated Execution
Domain-specific agents perform tasks:
- Invoice creation
- Reconciliation
- Financial aggregation

Orchestrator interprets intent and invokes appropriate agent. ML services operate as specialized agents.

---

## Learning Loop

Copilot improves through structured feedback, analysis, and deliberate knowledge refinement — NOT automatically.

### Signal Capture
- Direct user feedback (corrections, ratings, overrides)
- Behavioral signals (ignored suggestions, manual reversals, escalation patterns)
- Unresolved or low-confidence conversations
- Automation acceptance and rejection patterns
- Cases requiring CS/Human escalation

### Internal Tooling & Analysis
- Exploration of failure cases and edge scenarios
- Identification of recurring knowledge gaps
- Detection of incorrect or misleading responses
- Validation of patterns before increasing autonomy

### Knowledge Refinement Workflows
- Support conversations and unresolved queries systematically processed
- Domain experts have workflows to correct, extend, or improve answers
- Knowledge updates versioned and reintegrated into retrieval systems
- Improvements must measurably reduce recurrence of same issue

### Controlled Autonomy Expansion
Autonomy expands ONLY where usage data demonstrates: stability, correctness, sustained user trust.

---

## Core Scenarios

### Knowledge-Based Assistance (→ linked to Support Knowledge Agent doc)
- Answers product usage questions and accounting scenarios
- Retrieves from: help articles, structured knowledge sources, processed support conversations, relevant public guidance, local market legislation
- Contextual, conversational, capable of clarification
- Escalation: preserves context, seamless handoff, gaps feed learning loop

### From Explanation to Execution
Interaction evolves across levels:
1. Instructional guidance (step-by-step explanation)
2. Guided navigation (take user to relevant page/object)
3. Embedded task surface (generate appropriate interface within interaction)
4. Execution through agents (collect inputs, execute via domain agent)

Example: "How do I create an invoice?" → explanation → navigate to invoice page → pre-filled invoice draft for confirmation

### Context-Aware Object Interaction
When user is viewing a specific expense, invoice, or transaction:
- Identify the relevant object and its state
- Explain why a specific account, VAT treatment, or status is applied
- Clarify system behavior and underlying logic
- Suggest alternative categorizations or interpretations

Context flows both ways — from UI to chat and from chat to UI.

### Assisted Correction & Error Resolution
When error/inconsistency identified:
- Explain what is wrong and why
- Identify and highlight affected object/fields
- Suggest corrected values or actions
- Generate structured interfaces for making changes
- Execute updates after user confirmation

### Proactive Task Nudging
Surfaces contextual prompts based on system state:
- Unpaid invoices
- Missing reconciliations
- Upcoming VAT deadlines

### Financial Insights
Natural language analysis across accounting, invoicing, banking data.
Examples: "Why did my expenses increase?" / "How many unpaid bills?" / "What is my profit margin?"
Over time: reactive answers → proactive recommendations.

### Personal Assistant Layer
Acts as personalized assistant over time — user-initiated requests AND proactive support.
- Recurring reminders ("add expenses every Friday")
- Weekly financial summaries
- Proactive notifications when something needs attention
- Requires clear user control and transparent expectation setting

---

## Ownership & Cross-Domain Operating Model

### Copilot Team (VA Team)
Owns coordination layer:
- Conversational infrastructure
- Orchestration layer
- Context handling and session management
- Long-term memory
- Learning loop systems
- Cross-domain intelligence standards and governance model

### Domain / Stream-Aligned Teams
Own execution layer within their area:
- Domain-specific agents
- Business logic and execution flows
- Accuracy and regulatory correctness
- Data exposure and API contracts for orchestration

### Structural Intent
- Domain expertise embedded in domain teams
- Cross-domain intelligence centralized and consistent
- Copilot evolves as structural capability, not siloed feature

*Note: VA team expects to implement first use cases and likely support domain teams going forward.*

---

## Architectural Principles

- **Scoped by Design:** All sessions, actions, and memory strictly scoped to active organization and user. Context isolation is foundational.
- **Centralized Orchestration:** Conversation state, intent interpretation, and policy guardrails managed by single coordination layer. Domain agents remain stateless and domain-specific.
- **Clear Separation of Responsibility:** Copilot layer owns orchestration, context management, interaction logic. Stream-aligned teams own domain logic and execution capabilities.
- **Secure and Observable Execution:** All agent interactions must be auditable, structured, and policy-governed. Risk, confidence, and ambiguity must be explicit.
- **Framework Independence:** Built around clear contracts and standardized schemas — underlying AI frameworks can evolve without redefining system architecture.
- **Cross-Domain Integration:** Must operate consistently across accounting, invoicing, and banking.
- **Human Compatibility:** Must support human escalation, advisor collaboration, and structured handoffs without loss of context.

---

## Success Metrics

1. **Automation & Efficiency:** % workflows via Copilot, time-to-completion reduction, automation acceptance rate
2. **Self-Service Resolution:** % intents resolved without escalation, clarification-to-resolution completion rate, escalation rate after multi-turn conversation
3. **Financial Insight Utilization:** volume of insight queries, follow-up actions triggered by insights, insight → execution conversion
4. **Trust & Reliability:** correction rate, undo/override frequency, rejection rate of suggested actions, repeat usage after error events
5. **Adoption & Activation:** % active users engaging weekly, % new users during onboarding, depth of sessions (multi-step vs single-turn)
6. **Learning Velocity:** time from unresolved question → KB update, reduction in repeated unanswered intents, KB coverage growth

---

## Risk & Constraints

- **Over-Automation Risk:** Premature autonomy in sensitive financial workflows erodes trust quickly. Capability must expand only where predictability is high.
- **Trust Calibration:** Users must understand when system is assisting vs suggesting vs executing.
- **Knowledge Accuracy:** Must not behave like static search — clarification loops and escalation paths required.
- **Latency & Performance:** Conversational systems introduce infrastructure complexity.
- **Cross-Domain Governance:** Without orchestration standards, intelligence can fragment.

---

## Interaction Model — Three-Level Hierarchy

| Level | Name | Characteristics | Examples |
|---|---|---|---|
| 1 | Explicit AI Interaction | User initiates; open-ended NL; reasoning visible; errors tolerated | Chat agent, support chat |
| 2 | Guided Intelligence | AI suggests/drafts; user reviews/approves; intelligence visible but constrained | Receipt reading, VAT suggestions, expense categorization |
| 3 | Invisible Intelligence | No user prompt; background processing; deterministic expectations | Automated matching, email receipt fetching |

Copilot spans all three levels — unifying layer connecting explicit assistance, guided intelligence, and background automation.
