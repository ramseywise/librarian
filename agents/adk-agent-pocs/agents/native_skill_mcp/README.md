# native_skill_mcp (LangGraph)

A LangGraph port of [`agents/native_skill_mcp`](../../agents/native_skill_mcp/README.md) — the Billy accounting assistant using the native skill-loading pattern. Domain tools are called **directly** by the model (no proxy step), and the tool registry grows lazily as skills are activated.

---

## How it works

### Lazy skill loading via state-driven tool gating

The ADK implementation uses `SkillToolset` + `adk_additional_tools` to gate which MCP tools are visible each turn. This port replaces that mechanism with LangGraph's `StateGraph` and dynamic `bind_tools()`.

Each `SKILL.md` file declares `metadata.adk_additional_tools` — a list of MCP tool names to unlock when the skill is activated. At startup the agent only sees the 5 meta/support tools. As `load_skill` is called, `activated_skills` grows in graph state and more tools are bound on the next agent turn.

```text
Session start (activated_skills = []):
  Visible tools = [load_skill, list_skills, load_skill_resource,
                   run_skill_script, fetch_support_knowledge]
  Total: 5

After load_skill("invoice") → activated_skills = ["invoice-skill"]:
  Visible tools += [list_invoices, get_invoice, get_invoice_summary,
                    create_invoice, edit_invoice]
  Total: 10

After load_skill("customer") → activated_skills = ["invoice-skill", "customer-skill"]:
  Visible tools += [list_customers, create_customer, edit_customer]
  Total: 13
```

### Turn flow for a lazy skill

```text
Turn 1 — user: "create an invoice for Acme"
  agent_node: activated_skills=[] → bind 5 tools
  model calls: load_skill("invoice")

  tools_node: load_skill runs locally (no MCP)
    → reads invoice-skill/SKILL.md, returns prose instructions
    → Command(update={"activated_skills": ["invoice-skill"], messages: [ToolMessage]})
    → state updated

Turn 2 — model continues (same LangGraph step)
  agent_node: activated_skills=["invoice-skill"] → bind 10 tools
  model calls: create_invoice(...)

  tools_node: Billy MCP client calls create_invoice → returns result
```

### Graph structure

```
         START
           │
        agent_node
      (1. filter tools by activated_skills)
      (2. prune old fetch_support_knowledge responses)
      (3. bind_tools + invoke LLM)
           │
    ┌──────▼──────┐
    │ tool_calls? │
    └──────┬──────┘
     yes   │   no → END
           │
        tools_node
    (meta-tools handled locally;
     Billy MCP tools via MCP client)
           │ Command(goto="maybe_summarize")
           │
    maybe_summarize_node
           │
    ┌──────▼──────────────┐
    │ active msgs ≥ 8?    │
    └──────┬──────────────┘
     yes   │   no → agent_node
           │
      summarize_node
    (replace history with
     SystemMessage + 4-msg tail)
           │
        agent_node
```

### ADK → LangGraph concept mapping

| ADK concept | LangGraph equivalent |
|---|---|
| `SkillToolset` + `adk_additional_tools` | `activated_skills: list[str]` state field + `get_visible_tools()` |
| `McpToolset` | `langchain-mcp-adapters` `MultiServerMCPClient` |
| `before_model_callback` (history pruning) | `prune_tool_responses()` called at the top of `agent_node` |
| `EventsCompactionConfig(interval=8, overlap=4)` | `maybe_summarize_node` + `summarize_node` using `Overwrite()` |
| `ContextCacheConfig` | Not ported (no LangGraph equivalent) |
| ADK session state (`_adk_activated_skill_*`) | `AgentState.activated_skills` — persisted by checkpointer |
| `App` + SQLite session store | `CompiledGraph` + `InMemorySaver` (swap for `SqliteSaver` in production) |

---

## Running the agent

**Prerequisites:** Billy MCP server running, `GOOGLE_API_KEY` set.

```bash
# Terminal 1 — Billy MCP server
bash scripts/run_mcp_billy.sh

# Terminal 2 — interactive REPL
bash scripts/run_langgraph_billy.sh
```

```
Billy Assistant (LangGraph) — type 'quit' to exit

You: how do I void an invoice?
Billy: To void an invoice in Billy...

You: list my invoices
Billy: [loads invoice-skill, then calls list_invoices via MCP]
```

**Remote Billy MCP:** set `BILLY_MCP_URL` to the SSE endpoint. If unset, the agent spawns the MCP server as a subprocess automatically.

---

## Environment variables

| Variable | Purpose |
|---|---|
| `GOOGLE_API_KEY` | Gemini API key (AI Studio) |
| `GOOGLE_GENAI_USE_VERTEXAI` | Set to `1` to use Vertex AI instead |
| `BILLY_MCP_URL` | SSE endpoint for the Billy MCP server (unset = spawn subprocess) |
| `LANGSMITH_API_KEY` | Optional — enables LangSmith tracing |
| `LANGSMITH_TRACING` | Set to `true` to activate LangSmith tracing |

---

## Project structure

```text
langgraph_agents/native_skill_mcp/
├── README.md
├── SPEC.md                    # Full design specification and ADK→LangGraph mapping
├── __init__.py                # Package exports: build_graph, init_graph, run_turn, AgentState
├── agent.py                   # Graph assembly, build_graph(), should_continue(),
│                              # init_graph(), run_turn(), CLI entry point
├── state.py                   # AgentState TypedDict (_merge_skills reducer)
├── skills.py                  # SKILL_TOOL_MAP, SKILL_INSTRUCTIONS, meta-tools
│                              # (load_skill, list_skills, load_skill_resource,
│                              #  run_skill_script), get_visible_tools()
├── tools.py                   # Billy MCP client factory (MultiServerMCPClient)
├── nodes/
│   ├── agent_node.py          # make_agent_node(): tool gating, history pruning,
│   │                          # system prompt assembly, LLM invocation
│   ├── tools_node.py          # make_tools_node(): executes tool calls, merges
│   │                          # Command state updates from meta-tools
│   └── summarizer_node.py     # maybe_summarize_node(), summarize_node(),
│                              # should_summarize(), format_messages_for_summary()
├── prompts/ → ../../agents/native_skill_mcp/prompts/  (symlink)
│   ├── root_agent.txt
│   └── summarizer.txt
├── skills/  → ../../agents/native_skill_mcp/skills/   (symlink)
│   ├── support-skill/SKILL.md     # Preloaded
│   ├── invoice-skill/SKILL.md     # Lazy
│   ├── customer-skill/SKILL.md    # Lazy
│   ├── product-skill/SKILL.md     # Lazy
│   ├── email-skill/SKILL.md       # Lazy
│   └── invitation-skill/SKILL.md  # Lazy
└── tests/
    ├── test_state.py          # _merge_skills reducer
    ├── test_skills.py         # SKILL_TOOL_MAP, meta-tools, get_visible_tools
    ├── test_agent_node.py     # prune_tool_responses
    ├── test_summarizer.py     # _is_pruned, should_summarize, format_messages_for_summary
    └── test_graph.py          # Graph compilation, should_continue, tools_node
```

`prompts/` and `skills/` are symlinked to their counterparts in `agents/native_skill_mcp/` — single source of truth for domain content.

---

## SKILL.md format

Lazy skills declare `metadata.adk_additional_tools` — the MCP tool names to unlock:

```markdown
---
name: invoice-skill
description: >-
  Create, view, list, edit, approve, and summarize invoices.
metadata:
  adk_additional_tools:
    - list_invoices
    - get_invoice
    - get_invoice_summary
    - create_invoice
    - edit_invoice
---

# Invoice Operations
...instructions...
```

The preloaded `support-skill` uses `metadata.tools` instead (always visible, no lazy loading).

| Skill | Tier | Tools unlocked |
|---|---|---|
| `support-skill` | Preloaded | `fetch_support_knowledge` |
| `invoice-skill` | Lazy | `list_invoices`, `get_invoice`, `get_invoice_summary`, `create_invoice`, `edit_invoice` |
| `customer-skill` | Lazy | `list_customers`, `create_customer`, `edit_customer` |
| `product-skill` | Lazy | `list_products`, `create_product`, `edit_product` |
| `email-skill` | Lazy | `send_invoice_by_email` |
| `invitation-skill` | Lazy | `invite_user` |

---

## Adding a new skill

1. Create `skills/<name>/SKILL.md` with `name`, `description`, and `metadata.adk_additional_tools`.
2. Add the directory name to `LAZY_SKILLS` in `skills.py`.

No other changes required — `get_visible_tools()` and `load_skill` pick up the new skill automatically.

---

## Running tests

All tests are offline — no API key or Billy MCP server required.

```bash
uv run pytest langgraph_agents/native_skill_mcp/tests/ -v
```

---

## Key implementation notes

### `activated_skills` uses a merge reducer

`AgentState.activated_skills` has a custom `_merge_skills` reducer instead of plain list replacement. This means `load_skill` can return `Command(update={"activated_skills": ["invoice-skill"]})` without knowing the current state — the reducer appends and deduplicates automatically.

### `load_skill` returns a `Command`

Unlike plain `@tool` functions that return strings, `load_skill` returns a `Command` with a state update. The custom `tools_node` checks for `Command` returns and merges the updates before issuing its own `Command(goto="maybe_summarize")`.

### `Overwrite` is required in `summarize_node`

`AgentState.messages` uses the `add_messages` reducer. Returning a plain list from `summarize_node` would **append** to history. `Overwrite(compacted + tail)` bypasses the reducer and replaces the field entirely.

### `activated_skills` survives compaction

After `summarize_node` replaces `messages`, the `activated_skills` field is unchanged — it's a separate state field persisted by the checkpointer. Domain tools remain accessible without re-calling `load_skill`.

### History pruning

`fetch_support_knowledge` responses can be large. `prune_tool_responses()` in `agent_node` replaces old responses with `"[pruned]"` before each LLM call. "Old" means the tool call ID is not in the most recent `AIMessage`'s `tool_calls` — i.e., it was called in an earlier agent turn, not the current one.
