---
title: ADK Context Engineering
tags: [adk, context-management, pattern]
summary: How the ADK samples repo manages context — SKILL.md pattern, three skill-loading strategies, static vs dynamic instruction, and history compaction.
updated: 2026-04-24
sources:
  - raw/playground-docs/adk-samples-patterns-analysis.md
  - raw/playground-docs/rag-agent-template-research.md
---

# ADK Context Engineering

## Core Discipline

**`static_instruction=`** is always a string literal or file read — no dynamic data allowed. Dynamic context goes into `instruction=callable` or is injected into conversation history as `function_response` events.

**Why this matters:** static instructions are eligible for prefix caching — the model caches everything up to the first dynamic token. Mixing dynamic data into static instructions breaks caching and inflates costs.

## File Organization

| File | Role |
|---|---|
| `prompts/system.txt` | Static system instruction — never changes per turn (prefix cache) |
| `prompts/summarizer.txt` | History compaction prompt |
| `skills/SKILL.md` | YAML frontmatter (`adk_additional_tools`) + instruction body |
| `CLAUDE.md` | Developer-facing spec (not runtime context) |
| `SPEC.md` | Architecture specification per agent |

## SKILL.md Pattern

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

The frontmatter declares which MCP tools to activate. The body is the instruction text injected when the skill loads. **This separates domain logic from agent orchestration code entirely.**

**Gap in both rag_poc and playground:** no skill-file pattern. Prompts are code, not loadable artifacts.

## Three Skill-Loading Strategies

### Strategy A — Dynamic/Proxy (`dynamic_skill_mcp`)

- Tools list: `[load_skill, execute_mcp_action, _preloaded_toolset]` — static, never changes
- Skill instructions + tool schemas injected into conversation history as `function_response`
- **Prefix cache benefit:** tools list is stable across all turns
- **Trade-off:** schemas in conversation history; **incompatible with voice/BIDI** (VAD interrupts the 2-step chain)

### Strategy B — Native SkillToolset (`native_skill_mcp`) ← most relevant

- Tools: `[_preloaded_toolset, _skill_toolset]`
- `load_skill` returns prose only; schemas live in the `tools` API field
- Tool registry expands dynamically as `activated_skills` state grows
- **Benefits:** voice compatible (single-turn tool calls), smaller `load_skill` responses, clean separation
- **LangGraph mapping:** `activated_skills` state + `get_visible_tools()` + `MultiServerMCPClient`

### Strategy C — All Preloaded (`live_mcp`)

- All tool schemas + all skill instructions in system prompt from turn 1
- **Why:** voice/BIDI agents can't tolerate multi-step `load_skill → domain_tool` chains
- **Trade-off:** large initial context; no lazy loading

**Current state:** rag_poc uses an implicit Strategy C — one tool always bound, no lazy loading. Fine for single-domain RAG but doesn't scale to multi-domain.

## LangGraph Translation of Strategy B

| ADK Concept | LangGraph Implementation |
|---|---|
| `SkillToolset` | `activated_skills` in `TypedDict` state + `get_visible_tools()` |
| `McpToolset` (filtered) | `MultiServerMCPClient` with tool allowlist |
| `load_skill` tool | Async function that appends to `activated_skills` |
| `_preloaded_toolset` | Tools always in tool node (support/FAQ skills) |
| History compaction callback | `before_node` callback in `history_pruning.py` |
| `static_instruction` | System message never rebuilt |
| `instruction=callable` | `SystemMessage` rebuilt each turn from state |

## History Compaction Node

- **Trigger:** 8 messages
- **Overlap:** keep last 4 messages after compaction
- **Model:** Haiku (cost-efficient, not Sonnet)
- **Why:** preserves factual state across compaction; Sonnet is overkill for summarization

```python
# Summarization node pattern
if len(state["messages"]) >= 8:
    summary = await haiku.ainvoke(
        [SystemMessage(SUMMARIZER_PROMPT)] + state["messages"][-8:]
    )
    state["messages"] = [summary] + state["messages"][-4:]
```

## Context Management for Voice/BIDI

Voice agents require Strategy C (all-preloaded) because voice activity detection (VAD) can interrupt mid-sequence, making the 2-step `load_skill → domain_tool` chain unreliable.

**Voice-specific constraints:**
- Latency budget: <400ms for first response token
- No multi-step tool chains in the hot path
- All tool schemas in system prompt from turn 1
- Session state must handle text and voice turn structures (spike: verify compatibility)

## Output Schema Placement (Multi-Agent)

`output_schema` belongs on **leaf agents only**. The root router has no schema.

**Risk if set on root:** ADK enforces that the router's routing-decision text conforms to the output schema. It won't, and the call fails with a validation error that looks like a model output problem.

## ContextVar vs session.state (ADK Python)

In ADK Python multi-agent, `asyncio.create_task()` copies a context snapshot — `ContextVar` mutations after creation are invisible to child tasks. **Use `session.state` as the primary auth channel for multi-agent**, not `ContextVar`.

```python
# FastAPI endpoint — write auth into session before runner call
session = await session_service.create_session(
    app_name="copilot-py",
    state={
        "billy_api_token": body.api_token,
        "billy_org_id": body.org_id,
    },
)

# Tool functions — read via ToolContext (multi-agent safe)
async def list_bills(tool_context: ToolContext) -> list[dict]:
    token = tool_context.state["billy_api_token"]
    ...
```

## See Also
- [[ADK vs LangGraph Comparison]]
- [[Agent Memory Types]]
- [[LangGraph Advanced Patterns]]
- [[MCP Protocol]]
