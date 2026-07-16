# Copilot Chat and Help Centre Integration PRD

**Source:** https://app.notion.com/p/2cdf148b3ab78042842fd2be27d37be6
**Last edited:** 2026-04-09

## Problem

product-a users face fragmented support across multiple touchpoints: "Bookkeeping Hero" chatbot, Help Centre article database, and direct support channels. Fragmentation creates confusion, duplicates effort, and prevents proactive intelligent guidance.

**Core problem:** Developing Copilot as a central assistant risks adding yet another fragmented touchpoint unless the experiences are deliberately unified.

## Goal

Create a unified Copilot experience that merges Help Centre content, support access, and AI-powered assistance into **two strategic entry points**, positioning Copilot as the primary interface for user guidance with intelligent escalation paths.

## Success Metrics (draft)
- 30% decrease in basic "how-to" support requests within 3 months
- 60% of user queries resolved without human intervention
- NPS 40+ for Copilot interactions
- 50% of active users interact with Copilot within first month

---

## Proposed Solution

**Vision:** Copilot functions as a digital accountant / CFO — always-available assistant that proactively guides users through accounting workflows, answers questions, surfaces insights, and connects to human expertise when needed.

Copilot must support:
- **Context awareness** (knows where user is, what they're doing; can attach context via current page/task/invoice/bill)
- **Instant Answers** (contained to the support page)
- **Interactive UI elements** (buttons, flows, task handling)

POST MVP LAUNCH:
- Visualizations (financial insights, charts, data tables)
- Multiple interaction modes (proactive support, task execution)
- Task suggestions (proactive user tasks)
- Onboarding (new user task progression cards)

---

## Two Entry Points

### Entry Point 1: Global Copilot (Side Panel)
- **Location:** Top-right corner of application (global navigation)
- **Trigger:** Click icon to open side panel
- **Purpose:** Work with Copilot within context — assistance without leaving current page
- **Capabilities:** Full conversational interface, context-aware of current page + user activity, can reference/act on objects user is viewing, session history and continuity, rich interactive components
- **Visual Behavior:** Opens as side panel (slides in from right), overlays current page, persists across page navigation, minimizes/expands as needed

### Entry Point 2: Help Centre Dialogue Input
- **Location:** Within Help Centre or as contextual help trigger
- **Trigger:** User types question into Help Centre search/input field
- **Purpose:** Instant answers — either through guided assistance or escalation to human support
- **Capabilities:** Quick focused responses, direct access to article content, clear escalation path, can expand to full conversation if needed

---

## Core Use Cases (Q1 MVP Scope)

### Use Case 1: Simple Support Question
- User asks "How do I create a recurring invoice?"
- Copilot searches Help Centre articles via RAG
- Provides step-by-step answer synthesized from articles with screenshots/UI references
- Offers to guide user through the process interactively

### Use Case 2: Complex Support Question (Escalation)
- User asks "My VAT report shows incorrect totals"
- Copilot attempts to resolve through articles/known solutions
- After 1–2 exchanges if unresolved: recognizes limitation, explains why human support is recommended, provides estimated wait time
- User confirms escalation; conversation context transferred to support agent with full history

### Use Case 3: Business Question with Context
- User asks "What were my top expenses last month?"
- Copilot accesses financial data with appropriate context
- Analyzes and presents insights with visualizations (table, chart)
- Offers follow-up analysis

---

## Guiding Principles

1. **AI first, but not AI-only** — Copilot speeds up resolution; human support remains a visible and trusted fallback
2. **Escalation must feel smooth and continuous** — handoff with context, never starting over
3. **Clarity beats intelligence** — interface should feel simple, not "smart"
4. **Context passes forward** — users should never repeat themselves when escalating
5. **Two entry points, one unified flow** — regardless of where users start, they end up in Copilot
6. **Transparency over intelligence** — proactively signal what Copilot can and cannot do
7. **Visible reasoning, visible feedback, visible limits** — show users why it answered, how to correct it, where its boundaries are

---

## Technical Notes

### Chat Structure & Sessions
- Chat history maintained; sessions grouped (not one continuous thread)
- Users can start new sessions (fresh chat) or continue old ones
- Suggested queries relevant to current context

### Context Awareness
- Chat can be shown within context (e.g., on a bill page)
- Agent can take action on current object (e.g., create invoice)

### Interactive UI Components
- Buttons (Yes/No confirmations)
- Input fields, dropdowns, tables/previews, graphs

### Mobile Support
- Chat must work on mobile; voice input in future scope
