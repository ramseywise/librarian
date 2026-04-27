# ADK Skill Loading and Context Engineering Patterns

**Source:** adk-agent-samples-main — 16 ADK agents + LangGraph port  
**Relevance:** Core patterns for building scalable VA agents on ADK or LangGraph

---

## Context Engineering Discipline

The key rule: `static_instruction` is always a fixed string (enables prefix caching). Dynamic context goes into `instruction=callable` or is injected as conversation history events — never into the static instruction.

| File | Role |
|------|------|
| `prompts/system.txt` | Static system instruction — never changes per turn |
| `prompts/summarizer.txt` | History compaction prompt |
| `skills/SKILL.md` | YAML frontmatter (`adk_additional_tools`) + instruction body, loaded on demand |

---

## SKILL.md Pattern

Separates domain logic from agent orchestration. The frontmatter declares which MCP tools to activate; the body is the instruction text injected when the skill loads.

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

The agent starts with no domain tools. Each `load_skill` call activates a domain's tools + instructions in one step. This keeps the initial context window small regardless of how many domains the agent covers.

---

## Three Skill-Loading Strategies

| Strategy | Tools at startup | Skill load returns | Voice compatible | Best for |
|----------|-----------------|-------------------|-----------------|---------|
| **A — Dynamic/Proxy** | `[load_skill, execute_mcp_action, preloaded]` | Prose + schemas in history | ✗ (2-step chain) | Text agents, max prefix cache benefit |
| **B — Native SkillToolset** | `[preloaded_toolset, skill_toolset]` | Prose only; schemas in tools API | ✓ | Most VA agents — best balance |
| **C — All Preloaded** | All tools + instructions from turn 1 | N/A | ✓ | Voice/BIDI agents only |

**Strategy B is the default recommendation.** `load_skill` returns prose only; tool schemas appear in the `tools` API field. `activated_skills` state grows as the agent navigates domains.

**LangGraph equivalent of Strategy B:**
```python
# activated_skills state + get_visible_tools() + MultiServerMCPClient
class AgentState(TypedDict):
    activated_skills: list[str]  # grows as load_skill is called

def get_visible_tools(activated_skills: list[str]) -> list[Tool]:
    base_tools = [load_skill]  # always available
    domain_tools = [TOOL_REGISTRY[t] for s in activated_skills for t in SKILL_TOOLS[s]]
    return base_tools + domain_tools
```

---

## History Pruning and Summarization

Two patterns missing from most agent implementations:

**History pruning** — remove prior tool call/response pairs before each LLM call. Keep: user messages, agent text, current turn tool calls. Without this, tool history grows unbounded and eventually fills the context window.

```python
def prune_tool_history(messages: list) -> list:
    # Keep system + user messages + last N tool calls only
    return [m for m in messages if m.role in ("system", "user", "assistant")
            or is_current_turn_tool(m)]
```

**Summarization node** — trigger at 8 messages, compress to 4-message summary using a cheap model (Haiku):
- Preserves factual state (decisions, confirmed values) across compaction
- Runs a separate LLM call — keeps summarizer prompt separate from main system prompt
- After compaction, full CRAG graph continues from compressed state

---

## Agent Gateway Pattern (Session Manager)

Cleaner than route-per-request for multi-agent VA systems:

```
POST /chat          → triggers background agent turn, returns task_id
GET  /chat/stream   → SSE stream for session (event-driven)
POST /agents/switch → hot-switch active agent without losing session state
```

Per-session: one `Runner` + one SSE queue. The gateway handles multiplexing. This enables multi-agent switching mid-conversation without the client managing agent state.

---

## ADK ↔ LangGraph Pattern Mapping

| ADK Concept | LangGraph Equivalent |
|-------------|---------------------|
| `SkillToolset` | `activated_skills` in TypedDict state + `get_visible_tools()` |
| `McpToolset` (filtered) | `MultiServerMCPClient` with tool allowlist |
| `load_skill` tool | Async function that appends to `activated_skills` |
| `_preloaded_toolset` | Tools always in tool node |
| History compaction callback | `before_node` callback |
| `static_instruction` | System message never rebuilt |
| `instruction=callable` | `SystemMessage` rebuilt each turn from state |

---

## See Also
- [orchestration-patterns.md](orchestration-patterns.md) — supervisor/handoff/swarm trade-offs
- [memory-architecture.md](memory-architecture.md) — context window management strategies
- [hitl-and-interrupts.md](hitl-and-interrupts.md) — HITL patterns compatible with Strategy B
