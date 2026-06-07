# Chat Agent — RFC

**Source:** Notion — Virtual Assistant Team Documents Database
**URL:** https://app.notion.com/p/36ff148b3ab780fe8e4bfa0bb52c2bbb
**Status:** Shaping
**Type:** RFC
**Last updated:** 2026-06-01
**Teams:** Virtual Assistant

---

## Executive Summary

**Problem:** 40% of customer inquiries can be answered via static content from Shine's knowledge base. Today every inquiry is handled by the customer support team, leading to slower response times and inefficiencies.

In line with OKR Objective 2, the Virtual Assistant team is developing a customer support agent: **chat-agent**. It will use Shine's Intercom knowledge base to answer customer inquiries faster than the customer support team can today, while providing appropriate escalation paths, boundary adherence, and guardrails.

Target: initial launch by EoQ2 2026.

---

## Background

**Current situation:** Shine's customer support is fully human-driven. Customers reach out, customer support agents respond manually (assisted by macros/templates), referencing the Intercom knowledge base.

**Why now:** By shielding customer support agents from inquiries that can be handled automatically, we free them for complex cases and enable customer support to scale with Shine's growth.

---

## Proposal

Develop a chat-agent that answers static user inquiries using the Intercom knowledge base, with proper escalation paths. Future evolution: personalization, autonomous agent actions, Shine Banking MCP Server.

### How It Works

1. User asks a question
2. Service retrieves most relevant content from Intercom knowledge base
3. Agent generates a grounded, conversational response
4. Answers sourced exclusively from verified knowledge base content — no speculation beyond what is documented

### Technology

- **Retrieval**: Google Cloud Discovery Engine (Vertex AI Search), specifically the `ConversationalSearchService:answer` endpoint
- **Knowledge base indexing**: Vertex AI Search auto-indexes `help.shine.fr/*` — automatically updated as pages are added/changed
- **GCP handles**: retrieval, ranking, and answer generation (fully managed RAG service)

---

## Component Architecture

### Request Flow

User → REST or SSE → Dedicated UI in Shine Help Center (web + mobile) → Agentic RAG Chatbot → Guardrails layer (input validation before any generation) → GCP Answer Engine

### Answer Generation

Validated input → GCP Answer Engine → Vertex AI Conversational Search (retrieve articles + generate streaming response)

Conversation session and history stored in database so any Cloud Run instance can resume a conversation without sticky sessions.

### Guardrails (3-layer safety pipeline)

```
Layer 1 — UnicodeValidator          (character-level, cheapest)
Layer 2 — PromptInjectionDetector   (regex-based)
Layer 3 — BankingContextClassifier  (LLM, most expensive)
```

If an earlier (cheaper) layer rejects, remaining layers are skipped.

- **UnicodeValidator**: Explicit allowlist; everything outside is rejected. Eliminates Unicode-based attacks with a single regex check.
- **PromptInjectionDetector**: Detects prompt injection using compiled regex patterns from JSON files. Case-insensitive matching. Fails if any malicious pattern matches.
- **BankingContextClassifier**: LLM classifier using Google Gemini to classify whether sanitized input is within authorized scope of a banking support chatbot. Prompt managed within Langfuse.

### Observability & Prompt Management

- **Langfuse**: traces sent after each turn, prompts fetched from versioned registry
- **Langfuse-first prompt approach**: system prompts loaded from Langfuse, editable without code redeploy. Fallback to last repo version if needed. CI check ensures repo version stays in sync with Langfuse source of truth.
- **Datadog**: remains the system/infrastructure observability tool (NOT replaced by Langfuse)

---

## Risks & Mitigations

**Boundary adherence risk:** chat-agent must remain within its boundaries and refuse questions not grounded in static knowledge base.
- Mitigation: Banking Context Classifier prevents out-of-scope prompts
- Mitigation: Queries that are safe but unanswerable (require user-specific data or account-level actions) → redirect to customer support agent
- Mitigation: Evaluation framework at two levels:
  - **Offline**: curated test cases for redirect correctness (precision/recall of classifier output)
  - **Runtime**: Langfuse metric tracking redirection rate — spikes indicate over-escalation, drops indicate under-escalation

---

## Implementation Plan

Targeting phased rollout to start by EoQ2 2026.

**Already built:**
- Working agent in GCP trained on Intercom knowledge base
- Working backend capable of answering customer questions
- Backend instrumented with Langfuse observability and tracing
- Evaluation, performance metrics, and continuous improvement framework far along

**Next steps (by EoQ):**
- Backend deployment to shine-api-staging
- Frontend implementation (web or mobile first TBD)
- Start phased rollout to X% of users
- Selection of chat-agent database for chat history and session management

---

## Metrics for Success

Reducing inquiries reaching customer support team by providing faster, consistent, and safe responses.

---

## Tech Stack

**Backend:**
- Python (≥3.11)
- uv for dependency management
- Pydantic, Pytest, FastAPI (REST API + SSE streaming), Ruff, Lefthook

**GCP:**
- Google ADK for agent orchestration
- Deployed to GCP Cloud Run
- Vertex AI Discovery Engine (Conversational Search API)
- Database: TBD

**Observability:**
- Langfuse SDK

**Future capabilities:**
- FastMCP to support MCP server implementation
- Both Google ADK and FastMCP: Python is first-class (new versions + features released first, more comprehensive docs)
