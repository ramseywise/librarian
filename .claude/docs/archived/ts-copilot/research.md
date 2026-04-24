# Research: TypeScript Copilot Service

**Date:** 2026-04-14
**Scope:** `v2/ts_google_adk/` — the live, production TS copilot service embedded in Billy.dk

---

## What This Service Is

An AI accounting assistant ("Shine Assistant") embedded as an iframe chatbot inside the Billy.dk web app. It wraps a Google ADK `LlmAgent` (Gemini Flash) with 18 tools covering the core Billy.dk accounting surface. The UI is Next.js 16 with React 19 and Recharts for visualizations.

The service is deployed on AWS ECS (`billy-staging` cluster) and accessed via Docker Compose locally.

Entry point: `http://localhost:3000/va-agents/bot?BILLY_API_TOKEN=...&BILLY_ORGANIZATION_ID=...&theme=light`

---

## Product Design Intent

### Three interaction levels (from the Copilot product doc)

| Level | Mode | What the agent does |
|---|---|---|
| 1 | Knowledge | Answers "how do I…" questions using support documentation |
| 2 | Guided execution | Walks the user through completing a task, navigating to the right page |
| 3 | Autonomous execution | Creates, edits, sends documents directly via API tools |

The current agent covers all three levels in a single `LlmAgent`. The instruction distinguishes modes implicitly but does not separate them architecturally.

### Structured output contract

The agent produces a JSON object (enforced via `outputSchema`) that drives all UI behaviour — not just the message text. The frontend renders different components based on the fields present:

| Field | UI effect |
|---|---|
| `message` | Markdown content |
| `suggestions` | Clickable green suggestion chips |
| `navButtons` | Blue navigation buttons that drive the parent Billy app via `postMessage` |
| `tableType` | Enables click-to-select row behavior on markdown tables |
| `form` | Inline creation form (customer, product, invoice, quote) |
| `emailForm` | Editable email form for send-invoice/send-quote flows |
| `confirm` | Confirm/Discard buttons for edit operations |
| `contactSupport` | Contact Support button (shown on frustration or repeated failure) |
| `chart` | Inline Recharts visualization (bar, line, pie) |
| `sources` | Support article links (from Bedrock KB knowledge tool) |

### Page context awareness

`parentUrl` from the Billy parent app is passed via `postMessage` and threaded through `useChat`. The agent instruction reads: each user message may be prefixed with `[User is currently on page: <url>]`. This enables context-aware responses without asking "which invoice?".

### Escalation path

The agent sets `contactSupport: true` when:
- User expresses frustration
- Same question asked 3+ times
- Agent fails 2+ times on the same task
- User explicitly asks to reach a human

`navigation.ts` handles the escalation — generates an Intercom session summary and routes to support. The summary endpoint (`/va-agents/api/sessions/{sessionId}/summary`) is called but does not yet exist.

### Current feature surface (from README + test-chat.md)

**Invoices:** list, filter, view detail, create (with form), create from quote, edit draft, send by email, summary + chart
**Quotes:** list, filter, create (with form), send by email
**Customers:** list, create (with form), edit
**Products:** list, create (with form), edit
**Organization:** invite collaborator
**Knowledge fallback:** Bedrock KB for anything outside tool scope
**Navigation:** 30+ named routes in `navButtons`, covering all major Billy.dk pages
**Charts:** pie (status breakdown), bar (monthly revenue), line (period comparison)

### E2E acceptance test matrix (8 cases — from `.claude/commands/test-chat.md`)

1. Form rendering (create_customer)
2. Nav buttons + suggestions on list
3. Sources from Bedrock KB on support question
4. Form pre-filling from natural language
5. Session persistence across page reload
6. Full customer creation end-to-end
7. Contact Support fallback on out-of-scope query
8. Email form pre-filling (to field must be plain email only)

---

## Relationship to py-copilot-service

`py-copilot-service.md` (plan) describes an intentional **Python port** of this same service. The port's primary goal is:
1. Surface engineering friction between TS/Python + ADK
2. Enable swapping `fetchSupportKnowledge` from Bedrock KB to the playground LangGraph CRAG pipeline (possible only in Python)
3. Run a head-to-head quality/latency comparison

**Cross-cutting decisions logged in the Python plan that affect TS:**

| Decision | Python plan | TS implication |
|---|---|---|
| Model name | `gemini-2.5-flash-preview-04-17` | TS code uses `gemini-3-flash-preview` — `gemini-3` does not exist; this is likely a wrong string and needs verification |
| Session namespace | `app_name = "copilot-py"` | TS session service should use `app_name = "copilot-ts"` if both services share the same Postgres instance |
| Knowledge tool future | Phase 2 swaps Bedrock for RAG endpoint | Same swap applies to TS eventually — `fetchSupportKnowledge` should be replaceable without agent instruction changes |
| Structured output fragility | Pydantic `null` vs omit divergence is a known risk | Zod handles both cleanly; TS is not at risk here |
| Tool schema quality | Python docstring auto-schema is weaker than Zod | TS `FunctionTool` + Zod is the stronger pattern; preserve it when adding new tools |

---

## Architecture Observations

### What's working well

- **`FunctionTool` + Zod** is the right tool-definition pattern — explicit descriptions, type-safe execute, easy to test
- **`outputSchema`** is doing real work: the frontend is driven entirely by the structured output, not by parsing message text
- The `navButtons` + `suggestions` separation is clean — nav opens pages in Billy, suggestions send follow-up messages
- **`parentUrl` injection** is already partially wired; completing it is low-effort, high-value

### Known fragilities

- **Model string `gemini-3-flash-preview`** — this model name does not correspond to any known Gemini release. Should be verified against the deployed environment. If wrong, it may be falling back to a default model silently.
- **`fetchSupportKnowledge`** uses Bedrock KB (AWS) — when the playground RAG pipeline is ready, this should be the first tool to swap. The tool signature must stay identical so the agent instruction doesn't need to change.
- **No TS type check or ESLint in CI/hooks** — all code quality enforcement is Python-only (see hooks gap analysis in the upgrades plan).
- **No real test framework** — `quotes.test.ts` runs via `npx tsx`, manual invocation only. No coverage enforcement.
- **Session summary endpoint missing** — `navigation.ts` calls it for Intercom escalation, but the Next.js route doesn't exist yet.

### Tool count budget

| State | Count | Risk |
|---|---|---|
| Current | 18 | Safe |
| After Tranche A (bills) | 21 | Safe |
| After Tranche B (transactions + VAT + reports) | 28 | At limit for Gemini Flash |
| After agent split | ~12/8/1 per sub-agent | Safe |

---

## Open Questions

1. **Is `gemini-3-flash-preview` a valid model string in this deployment?** Check the ECS task definition or the deployed config. If it's wrong, the service may be degraded in production today.
2. **Does the Postgres session table need `app_name` namespacing?** Only matters if both TS and Python services are pointed at the same database during the comparison phase.
3. **Is the LangGraph CRAG endpoint ready to replace Bedrock KB?** The Python plan calls for a `POST /query` endpoint on the playground FastAPI. When that lands, the TS service should be updated in parallel.
4. **What is the Billy.dk rate limit for `GET /v2/reports/*`?** Financial reports can be expensive queries — the reports tools need a note on caching or debouncing if used frequently.
