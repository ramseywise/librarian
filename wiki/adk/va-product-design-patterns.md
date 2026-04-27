---
title: VA Product Design Patterns
tags: [adk, langgraph, concept, pattern]
summary: Product design patterns for embedded VA agents — three interaction levels, structured output as UI contract, page context awareness, escalation triggers, and tool count budget for routing quality.
updated: 2026-04-26
sources:
  - raw/claude-docs/playground/docs/research/agentic-ai/va-product-patterns.md
---

# VA Product Design Patterns

Patterns from the Billy Shine VA (production, embedded in Billy.dk). Applicable to any product-embedded VA agent.

## Three Interaction Levels

Don't build all three at once — ship level 1, validate, then expand.

| Level | Mode | What the agent does |
|-------|------|---------------------|
| **1** | Knowledge | Answers "how do I…" using support documentation |
| **2** | Guided execution | Walks user through a task, navigates to the right page |
| **3** | Autonomous execution | Creates, edits, sends documents directly via API tools |

A single `LlmAgent` can cover all three implicitly via instruction. Separate architecturally only when tool count exceeds ~20.

## Structured Output as the UI Contract

The agent produces a typed JSON object that drives all frontend behaviour. The LLM never outputs free-form text that the UI must parse.

| Field | UI effect |
|-------|-----------|
| `message` | Markdown content |
| `suggestions` | Clickable suggestion chips (follow-up actions) |
| `navButtons` | Buttons that navigate the parent app via postMessage |
| `tableType` | Enables click-to-select on markdown tables |
| `form` | Inline creation form (customer, product, invoice) |
| `emailForm` | Editable email form for send flows |
| `confirm` | Confirm/Discard buttons for edit operations |
| `contactSupport` | Escalation trigger (shows support button) |
| `chart` | Inline visualization (bar, line, pie) |
| `sources` | Knowledge article links |

**Why this matters:** the frontend is completely decoupled from the agent's reasoning. Adding a new UI surface means adding a field to the schema and a renderer — no prompt parsing, no regex, no fragile text matching.

## Page Context Awareness

Pass the user's current page URL from the parent app into every agent turn. Enables "which invoice?" to be resolved from context rather than asking.

```typescript
// Parent app → iframe via postMessage
window.postMessage({ type: "pageContext", url: window.location.pathname }, "*");

// Agent instruction:
// Each message may be prefixed with [User is currently on page: <url>]
// Use this to pre-fill context and skip navigation questions.
```

This collapses 2-turn exchanges into 1-turn exchanges where the agent already knows context from the URL.

## Escalation Path Design

Define escalation triggers in the agent instruction — don't rely on the LLM to decide ad hoc.

Trigger `contactSupport: true` when:
- User expresses frustration (explicit signal words)
- Same question asked 3+ times in the session
- Agent fails 2+ times on the same task
- User explicitly asks for a human

On escalation: generate an Intercom session summary (what the user was trying to do, what the agent tried, why it failed) and hand off.

## Tool Count Budget

Tool count directly affects routing quality. Gemini Flash degrades past ~20–25 tools.

| State | Tools | Risk |
|-------|-------|------|
| MVP (core accounting) | ~18 | Safe |
| + bills/expenses | ~21 | Safe |
| + transactions + VAT + reports | ~28 | At limit |
| After domain split | ~12 / ~8 / ~1 per sub-agent | Safe |

**Split signal:** at 20+ tools, split into domain sub-agents (accounting, analytics, support). The supervisor routes between them; each sub-agent stays under 12 tools. See [[Multi-Agent Orchestration Patterns]].

## E2E Acceptance Test Matrix

Minimum coverage before shipping level 3 (autonomous execution):

1. Form rendering — agent generates inline creation form
2. Nav buttons + suggestions — correct page navigation and follow-up chips
3. Knowledge fallback — support docs retrieved and cited
4. Form pre-filling — natural language → pre-filled form fields
5. Session persistence — state survives page reload
6. Full flow end-to-end — create entity, confirm, verify in app
7. Out-of-scope fallback — graceful decline + redirect
8. Email pre-filling — to field is plain email only (no display names)

## See Also
- [[Multi-Agent Orchestration Patterns]]
- [[Input Guardrails Pipeline]]
- [[SKILL.md Pattern]]
- [[A2A Agent Protocol]]
- [[VA Eval Harness]]
