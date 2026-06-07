---
title: Shine Chat Agent
tags: [adk, rag, infra, eval, project]
summary: Shine Banking's customer support chatbot — grounded on the Intercom knowledge base via Vertex AI Search, with a 3-layer guardrails pipeline, Langfuse observability, and a phased EoQ2 2026 launch target.
updated: 2026-06-05
sources:
  - raw/notion/2026-06-01-chat-agent-rfc.md
---

# Shine Chat Agent

**Status:** Shaping / RFC  
**Target:** Initial launch EoQ2 2026 (phased rollout)  
**Team:** Virtual Assistant (Shine Banking)  
**Problem:** 40% of customer inquiries can be answered from Shine's static knowledge base; today all are handled manually by customer support.

---

## What It Does

A customer support chatbot embedded in the Shine Banking Help Center (web + mobile). Answers static user inquiries grounded in the Intercom knowledge base. Provides appropriate escalation paths when queries require human judgment or account-level actions.

Future evolution: personalization, autonomous agent actions, Shine Banking MCP Server.

---

## Architecture

### Request Flow

```
User
  → REST or SSE (Help Center UI)
  → Agentic RAG Chatbot
  → Guardrails (Layer 1 → Layer 2 → Layer 3)
  → GCP Answer Engine (Vertex AI Conversational Search)
  → Streaming response
```

### Retrieval

- **Google Cloud Discovery Engine** (Vertex AI Search) — `ConversationalSearchService:answer` endpoint
- Auto-indexes `help.shine.fr/*` — updates automatically as knowledge base pages change
- GCP handles retrieval, ranking, and answer generation (fully managed RAG)
- **Answers sourced exclusively from verified knowledge base content** — no speculation

### Guardrails Pipeline (3 layers)

```
Layer 1 — UnicodeValidator          (character-level; explicit allowlist; cheapest)
Layer 2 — PromptInjectionDetector   (regex patterns from JSON; case-insensitive)
Layer 3 — BankingContextClassifier  (Gemini LLM; scope enforcement; most expensive)
```

If any earlier layer rejects, remaining layers are skipped (cost-efficient safety cascade).

- **UnicodeValidator**: Eliminates Unicode-based attacks with a single allowlist regex check
- **PromptInjectionDetector**: Compiled regex patterns; fails if any malicious pattern matches
- **BankingContextClassifier**: LLM classifier using Gemini; prompt managed in Langfuse. Classifies whether input is within authorized scope of a banking support chatbot.

See [[Input Guardrails Pipeline]] for the broader pattern.

### Observability

- **Langfuse**: traces sent after each turn; prompts fetched from versioned registry (Langfuse-first approach)
- Banking Context Classifier prompt managed in Langfuse — editable without code redeploy
- CI check ensures repo prompt version stays in sync with Langfuse source of truth
- **Datadog**: system/infrastructure observability (not replaced by Langfuse)

See [[Langfuse Platform]] for full Langfuse integration details.

### Session / State

- Conversation session and history stored in database (type TBD)
- Any Cloud Run instance can resume a conversation — no sticky sessions needed

---

## Evaluation Strategy

**Boundary adherence** is the primary risk: the agent must stay grounded and escalate rather than speculate.

Two-level evaluation framework:
- **Offline**: Curated test cases for redirect correctness — precision/recall of Banking Context Classifier output against known-safe and known-escalation queries
- **Runtime**: Langfuse metric tracking redirection rate over time — spike = over-escalation (after prompt update), drop = under-escalation (after scope change)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent orchestration | Google ADK |
| Retrieval | Vertex AI Discovery Engine (ConversationalSearchService) |
| Deployment | GCP Cloud Run |
| Database | TBD |
| Backend language | Python ≥3.11 |
| Package management | uv |
| API | FastAPI (REST + SSE streaming) |
| Observability | Langfuse SDK |
| Future: MCP | FastMCP |

---

## Implementation Status

**Already built:**
- Working agent in GCP trained on Intercom knowledge base
- Backend capable of answering customer questions
- Langfuse observability and tracing wired
- Evaluation + performance metrics framework in progress

**Next steps (by EoQ2 2026):**
- Backend deployment to shine-api-staging
- Frontend implementation (web or mobile first — TBD)
- Phased rollout to X% of users
- Select chat history / session management database

---

## See Also
- [[VA Agent Project]]
- [[VA Hypernova MCP]]
- [[AI Engineering Chapter @Shine]]
- [[Langfuse Platform]]
- [[Input Guardrails Pipeline]]
- [[RAG Knowledge Preparation]]
- [[Agentic Workflow Patterns]]
