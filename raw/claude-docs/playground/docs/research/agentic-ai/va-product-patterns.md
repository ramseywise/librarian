# VA Product Patterns

**Source:** ts_google_adk (Billy Shine Assistant) — production VA embedded in Billy.dk  
**Relevance:** Product design patterns for VA agents: interaction model, structured output, escalation

---

## Three Interaction Levels

The right framing for a VA product. Don't build all three at once — ship level 1, validate, then expand.

| Level | Mode | What the agent does |
|-------|------|---------------------|
| **1** | Knowledge | Answers "how do I…" using support documentation |
| **2** | Guided execution | Walks user through a task, navigates to the right page |
| **3** | Autonomous execution | Creates, edits, sends documents directly via API tools |

A single `LlmAgent` can cover all three implicitly via instruction. Separate architecturally only when tool count grows past ~20 (see tool budget below).

---

## Structured Output as the UI Contract

The agent produces a typed JSON object that drives all frontend behaviour. The LLM never outputs free-form text that the UI tries to parse — it fills a schema.

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

---

## Page Context Awareness

Pass the user's current page URL from the parent app into every agent turn. Enables "which invoice?" to be resolved from context rather than asking.

```typescript
// Parent app → iframe via postMessage
window.postMessage({ type: "pageContext", url: window.location.pathname }, "*");

// Agent instruction reads:
// Each user message may be prefixed with [User is currently on page: <url>]
// Use this to pre-fill context and skip navigation questions.
```

This collapses 2-turn exchanges ("which customer?" / "Acme Corp") into 1-turn exchanges where the agent already knows the context from the URL.

---

## Escalation Path Design

Define escalation triggers in the agent instruction — don't rely on the LLM to decide ad hoc.

Trigger `contactSupport: true` when:
- User expresses frustration (explicit signal words)
- Same question asked 3+ times in the session
- Agent fails 2+ times on the same task  
- User explicitly asks for a human

On escalation: generate an Intercom session summary and hand off. The summary should include: what the user was trying to do, what the agent tried, why it failed.

---

## Tool Count Budget

Tool count directly affects routing quality. Gemini Flash degrades past ~20-25 tools.

| State | Tools | Risk |
|-------|-------|------|
| MVP (core accounting) | ~18 | Safe |
| + bills/expenses | ~21 | Safe |
| + transactions + VAT + reports | ~28 | At limit |
| After domain split | ~12 / ~8 / ~1 per sub-agent | Safe |

**Split signal:** when you hit 20+ tools, split into domain sub-agents (accounting, analytics, support). Each stays under 12 tools; the supervisor routes between them.

---

## E2E Acceptance Test Matrix

Minimum test coverage for a VA agent before shipping level 3 (autonomous execution):

1. Form rendering — agent generates inline creation form
2. Nav buttons + suggestions — correct page navigation and follow-up chips
3. Knowledge fallback — support docs retrieved and cited
4. Form pre-filling — natural language → pre-filled form fields
5. Session persistence — state survives page reload
6. Full flow end-to-end — create entity, confirm, verify in app
7. Out-of-scope fallback — graceful decline + redirect
8. Email pre-filling — to field is plain email only (no display names)

---

## See Also
- [orchestration-patterns.md](orchestration-patterns.md) — supervisor split when tool count exceeds budget
- [guardrails-pipeline.md](guardrails-pipeline.md) — safety pipeline before agent reaches level 3
- [eval-harness.md](../evaluation-and-learning/eval-harness.md) — eval harness for routing + tool accuracy
