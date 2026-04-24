# ADK Agent Samples — Pattern Analysis & Comparison

**Date:** 2026-04-17  
**Source:** `adk-agent-samples-main/` (added to workspace)  
**Purpose:** Inform the rag_poc upgrade decision — LangGraph modernization vs. Google ADK migration  
**Related plans:** [`rag-architecture-refactoring-plan.md`](../plans/rag-architecture-refactoring-plan.md), [`rag-system-development-plan.md`](../plans/rag-system-development-plan.md)

---

## 1. What the ADK Samples Repo Is

A production-grade reference implementation of the **Google Agent Development Kit (ADK)** demonstrating:

- 16 ADK agents + a LangGraph port of the key patterns
- Three skill-loading strategies (proxy, native, all-preloaded)
- Multi-agent orchestration (router, parallel, supervisor/subagent)
- Safety hardening (7-stage guardrail pipeline, multilingual routing)
- Voice/BIDI streaming, A2UI declarative UI rendering
- MCP integration via `billy` accounting server (13 tools)

The LangGraph port lives at `langgraph_agents/native_skill_mcp/` — a direct translation of ADK patterns for teams staying on LangGraph.

---

## 2. Context Engineering Patterns

### 2.1 How ADK handles agent instructions

| File | Role |
|------|------|
| `prompts/system.txt` | Static system instruction — never changes per turn (prefix cache) |
| `prompts/summarizer.txt` | History compaction prompt |
| `skills/SKILL.md` | YAML frontmatter (`adk_additional_tools`) + instruction body, loaded on demand |
| `CLAUDE.md` | Developer-facing spec (not runtime context) |
| `SPEC.md` | Architecture specification per agent |

**Core discipline:** `static_instruction=` is always a string literal or file read — no dynamic data allowed. Dynamic context goes into `instruction=callable` or is injected into conversation history as `function_response` events.

### 2.2 SKILL.md pattern (key innovation)

```yaml
---
name: invoice-skill
metadata:
  adk_additional_tools:
    - list_invoices
    - get_invoice
    - create_invoice
---
# Invoice Management Instructions

You can create, view, and edit invoices...
```

The frontmatter declares which MCP tools to activate. The body is the instruction text injected when the skill loads. This separates domain logic from agent orchestration code entirely.

### 2.3 Comparison to rag_poc / playground

| Layer | `rag_poc` | `playground` | ADK Samples |
|-------|-----------|--------------|-------------|
| System prompt | Embedded in LangChain PromptTemplates (code) | `prompts.py` dict (code) | `prompts/system.txt` (filesystem) |
| Per-domain context | N/A | N/A | `SKILL.md` injected at load time |
| Dev docs | `.claude/docs/` plans | `CLAUDE.md` | `CLAUDE.md` + `SPEC.md` per agent |
| Runtime injection | Chain rebuild | `get_system_prompt(intent)` | `instruction=callable` |

**Gap in both our projects:** No skill-file pattern. Prompts are code, not loadable artifacts.

---

## 3. Three Skill-Loading Strategies (ADK)

### Strategy A — Dynamic/Proxy (`dynamic_skill_mcp`)
- Tools list: `[load_skill, execute_mcp_action, _preloaded_toolset]` — static, never changes
- Skill instructions + tool schemas injected into conversation history as `function_response`
- **Prefix cache benefit:** tools list is stable across all turns
- **Trade-off:** Schemas in conversation history; incompatible with voice/BIDI (VAD interrupts the 2-step chain)

### Strategy B — Native SkillToolset (`native_skill_mcp`) ← most relevant
- Tools: `[_preloaded_toolset, _skill_toolset]`
- `load_skill` returns prose only; schemas live in the `tools` API field
- Tool registry expands dynamically as `activated_skills` state grows
- **Benefits:** Voice compatible (single-turn tool calls), smaller `load_skill` responses, clean separation
- **LangGraph mapping:** `activated_skills` state + `get_visible_tools()` + `MultiServerMCPClient`

### Strategy C — All Preloaded (`live_mcp`)
- All tool schemas + all skill instructions in system prompt from turn 1
- **Why:** Voice/BIDI agents can't tolerate multi-step `load_skill → domain_tool` chains
- **Trade-off:** Large initial context; no lazy loading

**Our rag_poc uses an implicit Strategy C** — one tool (`search_knowledge_base`) always bound, no lazy loading. Fine for single-domain RAG but doesn't scale to multi-domain.

---

## 4. LangGraph Port Analysis (`langgraph_agents/native_skill_mcp/`)

The ADK samples include a direct LangGraph translation of the native skill pattern:

### Graph shape
```
agent_node → (tool_calls?) → tools_node → (summarize?) → agent_node
```

### Key patterns translated from ADK → LangGraph

| ADK Concept | LangGraph Implementation |
|-------------|-------------------------|
| `SkillToolset` | `activated_skills` in `TypedDict` state + `get_visible_tools()` |
| `McpToolset` (filtered) | `MultiServerMCPClient` with tool allowlist |
| `load_skill` tool | Async function that appends to `activated_skills` |
| `_preloaded_toolset` | Tools always in tool node (support/faq skills) |
| History compaction callback | `before_node` callback in `history_pruning.py` |
| `static_instruction` | System message never rebuilt |
| `instruction=callable` | `SystemMessage` rebuilt each turn from state |

### Summarization node
- 8-message trigger, 4-message overlap
- Separate summarizer model call (Haiku, not Sonnet) for cost
- Preserves factual state across compaction

### History pruning
- `shared/tools/history_pruning.py` — removes prior tool responses before each LLM call
- Keeps: user messages + agent text + current turn tool calls
- **Neither rag_poc nor playground has this.** Long sessions accumulate full tool history.

---

## 5. Web Client Comparison

### ADK `web_client/server.py`
- FastAPI + Jinja2 templates (Python-rendered)
- Agent discovery: scans `agents/` dir automatically → populates dropdown
- Live agent detection: regex for `gemini-*live*` → enables WebSocket mode
- Text agents: SSE streaming
- Live agents: WebSocket bidirectional audio (16kHz PCM in → 24kHz out)
- Warmup: pre-loads specified agents + optional cache-warmup turn
- Tool call visibility: numbered steps, JSON hover tooltips
- Response timing: first token, LLM spans, tool spans

### A2UI client (`agents/a2ui_mcp/web_client/`) — React + Vite
- `@a2ui/react` renders declarative JSON from agent responses
- Delimiter: `---a2ui_JSON---` splits prose from UI JSON
- Enables agents to generate interactive dashboards, forms, panels

| Feature | `rag_poc` Streamlit | `playground` Next.js | ADK `web_client` |
|---------|--------------------|--------------------|-----------------|
| Stack | Python Streamlit | Next.js 16 + React 19 | FastAPI + Jinja2 / React+Vite |
| Streaming | Declared, not wired | Full SSE (`@ai-sdk/react`) | SSE + WebSocket (voice) |
| Agent switching | N/A | Client-side keyword triage | Server-side dropdown, hot-switch |
| Voice/BIDI | No | No | Yes |
| Tool visibility | LangSmith only | None | Built-in (steps + hover) |
| Response timing | LangSmith | None | Yes (first token, LLM, tool spans) |
| Agent discovery | Hardcoded | Hardcoded endpoints | Auto-scan |
| Dynamic UI | No | No | A2UI JSON rendering |

---

## 6. Safety & Guardrails

`shared/guardrails/` contains production-ready utilities:

| Module | What it does |
|--------|-------------|
| `pii_redaction.py` | 13 patterns: email, phone, card, SSN, PEM, API keys, Bearer tokens, env vars |
| `prompt_injection.py` | 10 injection categories: instruction overrides, goal hijacking, DAN mode, encoding obfuscation, template tokens |
| `domain_*.py` | Keyword classifiers (accent-normalized) for domain restriction |

**rag_poc has no guardrail layer.** Relevant for production deployment.

---

## 7. MCP Architecture (Billy Server)

`mcp_servers/billy/` is a clean reference for MCP server design:

- **Dual entry points:** REST API (FastAPI, port 8766) + MCP server (stdio/SSE, port 8765)
- **Shared database:** SQLite used by both
- **Tool count:** 13 tools, pure Python, no ADK dependency
- **Pre-aggregated analytics endpoints:** revenue summary, aging report — bypasses agent entirely

**Agent Gateway** (`agent_gateway/`) — session manager pattern:
- Per-session `Runner + SSE queue`
- `POST /chat` triggers background agent turn
- `GET /chat/stream` SSE stream for session
- `POST /agents/switch` hot-switches active agent

This is cleaner than playground's route-per-request pattern and handles multi-agent switching properly.

---

## 8. Dependencies Snapshot

| Package | ADK Samples | rag_poc | playground |
|---------|-------------|---------|------------|
| `google-adk` | `>=1.28.0` | ✗ | `>=1.0.0` (optional) |
| `langgraph` | `>=0.2.0` | `>=1.0.6` | `>=0.4.0` |
| `langchain-google-genai` | `>=2.0.0` | ✗ | ✗ |
| `langchain-mcp-adapters` | `>=0.1.0` | ✗ | via `mcp>=1.0.0` |
| `fastmcp` | `>=2.13.0` (dev) | ✗ | ✗ |
| `anthropic` | ✗ | `>=0.88.0` | `>=0.88.0` |

---

## 9. Key Gaps in `rag_poc` vs ADK Samples Patterns

Ranked by impact:

| Gap | Severity | ADK Pattern to adopt |
|-----|----------|---------------------|
| No history pruning — tool history grows unbounded | High | `shared/tools/history_pruning.py` callback |
| No summarization node — long sessions degrade | High | 8-msg compaction node with Haiku |
| No streaming chat endpoint — API stub only | High | SSE `format_sse()` pattern from agent_gateway |
| System prompts embedded in code | Medium | Filesystem `prompts/` dir; loadable at init |
| No tool call visibility in UI | Medium | `web_client` numbered steps pattern |
| No guardrail layer (PII, injection) | Medium | `shared/guardrails/` modules |
| No session/thread persistence | Medium | LangGraph checkpointer + `thread_id` |
| Single static tool (no lazy loading) | Low-Med | `activated_skills` pattern (only relevant if multi-domain) |
| No SKILL.md pattern | Low | Only needed for multi-domain skill routing |

---

## 10. Framework Decision Surface

The ADK samples repo contains **both** ADK and LangGraph implementations of the same patterns. The LangGraph port (`langgraph_agents/`) proves the patterns are framework-agnostic. Key decision factors:

| Factor | Favor LangGraph | Favor Google ADK |
|--------|-----------------|-----------------|
| Existing codebase | Already on LangGraph 1.0.6 | Migration cost |
| Anthropic models | First-class via `langchain-anthropic` | Requires adapters or swap to Gemini |
| HITL patterns | `interrupt()` + `Command(resume=)` already in use | ADK has own HITL primitives |
| Voice/multimodal | Add-on | Native (Gemini Live) |
| Skill loading | Manual via state | `SkillToolset` built-in |
| Observability | LangSmith + Langfuse | Cloud Trace + ADK eval tooling |
| Deployment | Any Python host | Agent Engine / Cloud Run (Google) |
| Guardrails | Must build | Reference impl in `shared/` |
| Community/docs | Larger ecosystem | Growing, Google-backed |

**Recommendation:** See upgrade plan for decision matrix and recommended path.
