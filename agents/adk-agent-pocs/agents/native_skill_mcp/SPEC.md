# DESIGN_SPEC.md — langgraph/native_skill_mcp

## Status: planned

## Overview

Port `agents/native_skill_mcp` — the Billy accounting assistant using the
native skill-loading pattern — from Google ADK to LangGraph. The result is a
functionally equivalent agent that:

- Maintains the **lazy skill-loading architecture**: a small tool registry at
  session start that grows only when the user touches a new domain.
- Replaces ADK's `SkillToolset` + `adk_additional_tools` mechanism with a
  **state-driven tool gating** pattern native to LangGraph.
- Replaces ADK's `McpToolset` with `langchain-mcp-adapters` for connecting to
  the Billy MCP server.
- Preserves the **same system prompt, skill definitions (SKILL.md files),
  summarizer prompt, and Billy MCP backend** — no domain logic changes.

---

## Scope

### In scope
- Single-agent ReAct graph (equivalent to ADK's single `root_agent`)
- Lazy skill loading via `load_skill` meta-tool + state-driven tool gating
- Preloaded support skill (always-visible `fetch_support_knowledge`)
- All 5 lazy skills: invoice, customer, product, email, invitation
- History pruning for `fetch_support_knowledge` (equivalent to ADK's
  `make_history_prune_callback`)
- Context compaction / summarization (equivalent to ADK's
  `EventsCompactionConfig`)
- Billy MCP server connection via SSE or stdio subprocess
- In-memory and SQLite checkpointing (equivalent to ADK's session store)

### Out of scope
- `ContextCacheConfig` (Gemini prefix caching) — no LangGraph/LangChain
  equivalent; omit for now
- `live_audio_patch` and BIDI/live voice mode — text-only port
- ADK `App` wrapper — the LangGraph `CompiledGraph` + checkpointer serves
  the same purpose
- `run_skill_script` meta-tool — implemented as a stub returning "not supported"

---

## Framework Selection Rationale

The project's skill suite maps naturally to the decision table in the
`framework-selection` skill:

> "Does the task require loading on-demand skills?" → **Deep Agents**

Deep Agents ships a built-in `SkillsMiddleware` that reads SKILL.md files from
a directory and loads them on demand — nearly identical to ADK's `SkillToolset`.
The SKILL.md frontmatter format is also compatible (YAML `name` + `description`).

**However, Deep Agents' `SkillsMiddleware` does not replicate the
`adk_additional_tools` tool-gating mechanism.** It loads skill *instructions*
into context but does not dynamically add or remove tools from the model's
registry based on which skills are active. All Billy MCP tools would be
permanently visible, bypassing the lazy-loading guarantee that keeps the tool
set small per turn.

**Verdict: LangGraph.** The tool-gating behaviour is the key architectural
requirement. LangGraph's `StateGraph` with dynamic `bind_tools()` is the only
layer that gives full control over which tools the model sees on each turn.

> Note: If tool-gating is not a hard requirement in future — e.g. if all 14
> Billy tools are acceptable to show at all times — Deep Agents would be a
> significantly simpler implementation path:
> `create_deep_agent(skills=["./skills/"], tools=all_billy_tools, ...)`.

---

## ADK → LangGraph Concept Mapping

| ADK concept | LangGraph equivalent |
|---|---|
| `Agent(model=..., tools=[...], instruction=...)` | `StateGraph` with an `agent` node that binds tools dynamically |
| `SkillToolset` (lazy tool gating via session state) | Custom state field `activated_skills: list[str]`; agent node filters tool list before `bind_tools()` |
| `adk_additional_tools` (SKILL.md frontmatter) | Same SKILL.md files parsed at startup into `SKILL_TOOL_MAP: dict[str, list[str]]` |
| `McpToolset` (ADK MCP adapter) | `langchain-mcp-adapters` `MultiServerMCPClient` or `MCPClient`; tools loaded as `BaseTool` instances |
| `after_tool_callback` (prefer_structured_tool_response) | Post-processing in the tools node before returning `ToolMessage` to graph |
| `before_model_callback` (history pruning) | Preprocessing step inside the agent node before calling `.bind_tools().invoke()` |
| `EventsCompactionConfig(interval=8, overlap=4)` | `maybe_summarize` conditional node: count messages, call LLM summarizer, replace history |
| `ContextCacheConfig` | Not ported (no equivalent) |
| Session state (`_adk_activated_skill_*`) | `AgentState.activated_skills: list[str]` — persisted by checkpointer |
| `App` + SQLite session store | `CompiledGraph` + `SqliteSaver` (or `MemorySaver` for dev) |
| `LlmEventSummarizer` | Custom summarizer node calling `ChatGoogleGenerativeAI` with `summarizer.txt` |

---

## Architecture

### Graph structure

```
                    ┌──────────────────────────┐
        user msg ──▶│        agent_node         │
                    │  1. prune history         │
                    │  2. filter tools by       │
                    │     activated_skills      │
                    │  3. bind_tools + invoke   │
                    └──────────┬───────────────┘
                               │
                   ┌───────────▼────────────────┐
                   │    should_continue?         │
                   │  has tool_calls → tools     │
                   │  no tool_calls  → END       │
                   └───────────┬────────────────┘
                               │ (tool_calls present)
                    ┌──────────▼───────────────┐
                    │       tools_node          │
                    │  - meta-tools handled     │
                    │    locally (no MCP):      │
                    │      load_skill           │
                    │        → update state     │
                    │        → return prose     │
                    │      list_skills          │
                    │      load_skill_resource  │
                    │      run_skill_script     │
                    │  - Billy MCP tools:       │
                    │    called via MCP client  │
                    └──────────┬───────────────┘
                               │
                    ┌──────────▼───────────────┐
                    │   maybe_summarize node    │
                    │  count non-pruned msgs    │
                    │  if ≥ compaction_interval │
                    │    call summarizer LLM    │
                    │    replace history        │
                    └──────────┬───────────────┘
                               │
                           back to agent_node
```

### Tool visibility at each state

```
Session start (activated_skills = []):
  Visible tools = [list_skills, load_skill, load_skill_resource,
                   run_skill_script, fetch_support_knowledge]
  Total: 5

After load_skill("invoice") → activated_skills = ["invoice"]:
  Visible tools += [list_invoices, get_invoice, get_invoice_summary,
                    create_invoice, edit_invoice]
  Total: 10

After load_skill("customer") → activated_skills = ["invoice", "customer"]:
  Visible tools += [list_customers, create_customer, edit_customer]
  Total: 13
```

### Turn flow for a lazy skill

```
Turn 1 — user: "create an invoice for Acme"
  agent_node:
    activated_skills = [] → bind 5 tools to model
    model calls: load_skill("invoice")

  tools_node:
    load_skill handles locally:
      → reads invoice-skill/SKILL.md, extracts instructions
      → returns Command(update={"activated_skills": ["invoice"]},
                        goto="agent_node")
      → appends ToolMessage with prose instructions

Turn 2 — model continues (same LangGraph "step")
  agent_node:
    activated_skills = ["invoice"] → bind 10 tools
    model calls: create_invoice(...)

  tools_node:
    Billy MCP client calls create_invoice
    returns ToolMessage with result
```

---

## State Schema

```python
# state.py
from typing import Annotated
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    activated_skills: list[str]    # tracks which lazy skills are loaded
    summary: str                   # compacted history summary (empty string = none)
```

**`activated_skills`** is the central state field. It replaces ADK's
`_adk_activated_skill_native_skill_mcp` session key. The checkpointer persists
it across turns, so:
- Tools added by a `load_skill` call remain visible for the rest of the session.
- After context compaction, the tools are still present in the registry (same
  guarantee as the ADK implementation).

---

## Tool Gating — Skill Manager

`skills.py` contains the skill management logic and is the LangGraph replacement
for `SkillToolset`.

### Startup: build the SKILL_TOOL_MAP

Parse YAML frontmatter from each SKILL.md at import time:

```python
# skills.py
import pathlib, yaml

SKILLS_DIR = pathlib.Path(__file__).parent / "skills"

# { skill_name: list[mcp_tool_name] }
SKILL_TOOL_MAP: dict[str, list[str]] = {}
SKILL_INSTRUCTIONS: dict[str, str] = {}

for skill_dir in SKILLS_DIR.iterdir():
    md = (skill_dir / "SKILL.md").read_text()
    frontmatter, body = _parse_frontmatter(md)
    name = frontmatter["name"]
    tools = frontmatter.get("metadata", {}).get("adk_additional_tools", [])
    SKILL_TOOL_MAP[name] = tools
    SKILL_INSTRUCTIONS[name] = body
```

### Preloaded vs. lazy split

```python
PRELOADED_SKILLS = ["support-skill"]   # tools always visible
LAZY_SKILLS = [
    "invoice-skill", "customer-skill", "product-skill",
    "email-skill", "invitation-skill",
]

PRELOADED_TOOL_NAMES: set[str] = {
    t for s in PRELOADED_SKILLS for t in SKILL_TOOL_MAP.get(s, [])
}
# = {"fetch_support_knowledge"}
```

### Agent node: filter visible tools

```python
# nodes/agent_node.py
def get_visible_tools(
    all_billy_tools: dict[str, BaseTool],
    activated_skills: list[str],
    meta_tools: list[BaseTool],
) -> list[BaseTool]:
    visible_names = set(PRELOADED_TOOL_NAMES)
    for skill_name in activated_skills:
        visible_names.update(SKILL_TOOL_MAP.get(skill_name, []))
    billy_visible = [t for name, t in all_billy_tools.items() if name in visible_names]
    return meta_tools + billy_visible
```

---

## Meta-Tools

Meta-tools are plain Python functions decorated with `@tool`. They do **not**
call Billy MCP. They are always in the visible tool list regardless of
`activated_skills`.

### `load_skill`

The most important meta-tool. In the ADK implementation, `SkillToolset` handles
`load_skill` internally and mutates session state. In LangGraph, `load_skill`
returns a `Command` to update graph state and route back to the agent node.

```python
# skills.py
from langgraph.types import Command
from langchain_core.tools import tool, InjectedToolCallId
from typing import Annotated

@tool
def load_skill(
    skill_name: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
    state: Annotated[AgentState, InjectedState],
) -> Command:
    """Load a skill to activate its tools and retrieve its instructions."""
    # Normalise: accept "invoice" or "invoice-skill"
    canonical = skill_name if skill_name.endswith("-skill") else f"{skill_name}-skill"
    if canonical not in SKILL_INSTRUCTIONS:
        return Command(
            update={
                "messages": [ToolMessage(
                    f"Unknown skill '{skill_name}'. "
                    f"Available: {list(SKILL_INSTRUCTIONS)}",
                    tool_call_id=tool_call_id,
                )]
            }
        )
    instructions = SKILL_INSTRUCTIONS[canonical]
    already_active = state.get("activated_skills", [])
    new_active = already_active if canonical in already_active else [*already_active, canonical]
    return Command(
        update={
            "activated_skills": new_active,
            "messages": [ToolMessage(instructions, tool_call_id=tool_call_id)],
        }
    )
```

**Note:** `InjectedState` requires `langgraph >= 0.2.x`. The `load_skill` tool
reads `state["activated_skills"]` to avoid re-adding already-loaded skills.
Using `Command` instead of a plain string return is what allows the state update
to propagate back into the graph.

### `list_skills`

```python
@tool
def list_skills() -> str:
    """List all available skills and their descriptions."""
    lines = []
    for skill_dir in SKILLS_DIR.iterdir():
        md = (skill_dir / "SKILL.md").read_text()
        fm, _ = _parse_frontmatter(md)
        lines.append(f"- {fm['name']}: {fm['description'].strip()}")
    return "\n".join(lines)
```

### `load_skill_resource`

```python
@tool
def load_skill_resource(skill_name: str, resource_name: str) -> str:
    """Load a resource file from a skill directory."""
    # Resolve path and return file contents; raise ToolException if not found
    ...
```

### `run_skill_script`

```python
@tool
def run_skill_script(skill_name: str, script_name: str) -> str:
    """Run a script from a skill directory. (Not supported in LangGraph port.)"""
    return "run_skill_script is not supported in this implementation."
```

---

## Billy MCP Tool Integration

Use `langchain-mcp-adapters` to load Billy MCP tools as LangChain `BaseTool`
instances. Connection logic mirrors the ADK `billy_toolset.py`:

```python
# tools.py
import os
from langchain_mcp_adapters.client import MultiServerMCPClient

def build_mcp_client() -> MultiServerMCPClient:
    billy_mcp_url = os.getenv("BILLY_MCP_URL")
    if billy_mcp_url:
        transport = {"url": billy_mcp_url, "transport": "sse"}
    else:
        transport = {
            "command": "uv",
            "args": ["run", "python", "-m", "app.main_noauth"],
            "cwd": str(BILLY_MCP_DIR),
            "transport": "stdio",
        }
    return MultiServerMCPClient({"billy": transport})
```

Load all Billy tools at graph construction time into a `dict[str, BaseTool]`
keyed by tool name:

```python
async def load_all_billy_tools(client: MultiServerMCPClient) -> dict[str, BaseTool]:
    tools = await client.get_tools()
    return {t.name: t for t in tools}
```

**MCP client lifecycle**: `MultiServerMCPClient` must be used as an async
context manager (`async with`). The graph entrypoint (e.g., `app.py`) must
manage this lifetime — open the client once per process, pass the loaded tools
dict into the graph at construction time.

---

## History Pruning

Equivalent to ADK's `make_history_prune_callback(["fetch_support_knowledge"])`.

In ADK, the callback runs before each model call and redacts `function_response`
events for `fetch_support_knowledge` from all turns **except** the current
invocation.

In LangGraph, implement this as a helper function called inside `agent_node`
before passing messages to the model:

```python
# nodes/agent_node.py
def prune_tool_responses(
    messages: list[BaseMessage],
    prune_tool_names: set[str],
    current_invocation_id: str | None,
) -> list[BaseMessage]:
    """
    Replace ToolMessage content with '[pruned]' for old fetch_support_knowledge
    calls. 'Old' means not in the current invocation batch (identified by
    matching the immediately preceding AIMessage's tool_call_ids).
    """
    # Find tool_call_ids in the most recent AIMessage (current invocation)
    current_call_ids: set[str] = set()
    for msg in reversed(messages):
        if isinstance(msg, AIMessage) and msg.tool_calls:
            current_call_ids = {tc["id"] for tc in msg.tool_calls}
            break

    pruned = []
    for msg in messages:
        if (
            isinstance(msg, ToolMessage)
            and msg.name in prune_tool_names
            and msg.tool_call_id not in current_call_ids
        ):
            pruned.append(msg.model_copy(update={"content": "[pruned]"}))
        else:
            pruned.append(msg)
    return pruned
```

Called at the top of `agent_node` before `bind_tools`:

```python
effective_messages = prune_tool_responses(
    state["messages"],
    prune_tool_names={"fetch_support_knowledge"},
    current_invocation_id=None,
)
```

---

## Context Compaction (Summarization)

Equivalent to ADK's `EventsCompactionConfig(compaction_interval=8, overlap_size=4)`.

### Trigger condition

After `tools_node` completes, the `maybe_summarize` node counts the number of
non-pruned messages. If the count exceeds `COMPACTION_INTERVAL = 8`:

```python
COMPACTION_INTERVAL = 8
OVERLAP_SIZE = 4

def should_summarize(state: AgentState) -> str:
    """Conditional edge: decide whether to summarize before next agent turn."""
    msg_count = len([m for m in state["messages"] if not _is_pruned(m)])
    if msg_count >= COMPACTION_INTERVAL:
        return "summarize"
    return "agent"
```

### Summarizer node

```python
from langgraph.types import Overwrite

async def summarize_node(state: AgentState) -> dict:
    messages = state["messages"]
    # Keep the last OVERLAP_SIZE messages verbatim
    to_summarize = messages[:-OVERLAP_SIZE]
    to_keep = messages[-OVERLAP_SIZE:]

    summary_prompt = SUMMARIZER_TEMPLATE.format(
        history=format_messages_for_summary(to_summarize)
    )
    summary_response = await summarizer_llm.ainvoke(summary_prompt)
    summary_text = summary_response.content

    # Replace history: SystemMessage with summary + overlap tail.
    # IMPORTANT: `messages` uses operator.add as its reducer, so a plain
    # list return would APPEND to existing messages, not replace them.
    # Use Overwrite to bypass the reducer and replace the field entirely.
    compacted = [SystemMessage(content=f"[Context summary]\n{summary_text}")]
    return {
        "messages": Overwrite(compacted + to_keep),
        "summary": summary_text,
    }
```

**`activated_skills` survives compaction** because it is a separate state field,
not stored in `messages`. After compaction, the tool registry still contains all
previously-loaded skill tools — the model only needs to re-call `load_skill` to
recover the HOW-TO instructions (same recovery path as the ADK implementation).

The summarizer LLM uses the same `prompts/summarizer.txt` template as the ADK
agent.

---

## Agent Node

```python
# nodes/agent_node.py
async def agent_node(state: AgentState, config: RunnableConfig) -> dict:
    # 1. Assemble visible tools based on activated_skills
    visible_tools = get_visible_tools(
        all_billy_tools=ALL_BILLY_TOOLS,  # injected at graph construction
        activated_skills=state.get("activated_skills", []),
        meta_tools=META_TOOLS,
    )

    # 2. Prune old fetch_support_knowledge responses
    messages = prune_tool_responses(
        state["messages"],
        prune_tool_names={"fetch_support_knowledge"},
    )

    # 3. Prepend summary as context if present
    if state.get("summary"):
        messages = [SystemMessage(f"[Context summary]\n{state['summary']}")] + messages

    # 4. Bind tools and call the model
    response = await llm.bind_tools(visible_tools).ainvoke(
        [SystemMessage(SYSTEM_PROMPT)] + messages,
        config=config,
    )
    return {"messages": [response]}
```

---

## Tools Node

```python
# nodes/tools_node.py
async def tools_node(state: AgentState) -> Command:
    last_ai = state["messages"][-1]
    tool_results = []
    state_updates: dict = {}

    for tool_call in last_ai.tool_calls:
        tool = ALL_TOOLS_BY_NAME[tool_call["name"]]
        result = await tool.ainvoke(tool_call)

        if isinstance(result, Command):
            # Meta-tools (load_skill) return Command with state updates
            state_updates.update(result.update)
            tool_results.extend(result.update.get("messages", []))
        else:
            tool_results.append(
                ToolMessage(content=str(result), tool_call_id=tool_call["id"])
            )

    updates = {**state_updates, "messages": tool_results}
    return Command(update=updates, goto="maybe_summarize")
```

---

## Graph Assembly

```python
# agent.py
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver     # dev only
# from langgraph.checkpoint.sqlite import SqliteSaver     # local persistence
# from langgraph.checkpoint.postgres import PostgresSaver # production

def build_graph(billy_tools: dict[str, BaseTool]) -> CompiledGraph:
    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)
    builder.add_node("tools", tools_node)
    builder.add_node("maybe_summarize", maybe_summarize_node)
    builder.add_node("summarize", summarize_node)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", END: END},
    )
    # NOTE: use add_conditional_edges (not add_edge) here.
    # If tools_node returns a Command(goto=...) AND a static add_edge exists,
    # both paths execute — the Command's goto runs in addition to the static
    # edge, not instead of it (LangGraph fundamentals warning).
    builder.add_conditional_edges(
        "tools",
        lambda state: "agent",   # always go back to agent after tools
        {"agent": "agent"},
    )
    builder.add_conditional_edges(
        "maybe_summarize",
        should_summarize,
        {"summarize": "summarize", "agent": "agent"},
    )
    builder.add_edge("summarize", "agent")

    checkpointer = InMemorySaver()  # swap for SqliteSaver / PostgresSaver in production
    return builder.compile(checkpointer=checkpointer)

# Invoke with thread_id — ALWAYS required for checkpointed graphs:
# graph.invoke({"messages": [HumanMessage(...)]},
#              {"configurable": {"thread_id": "session-abc"}})
```

---

## Model Configuration

```python
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-3-flash-preview",
    temperature=0,
    # Thinking config: pass via model_kwargs if supported by SDK version
    # model_kwargs={"thinking_config": {"thinking_budget": 512}},
)
```

The ADK agent uses `thinking_level="LOW"` with `include_thoughts=False`. In
`langchain-google-genai`, thinking config is available via `model_kwargs` with
`thinking_config`. Verify the installed SDK version supports this before
including it.

---

## System Prompt

Use the same `prompts/root_agent.txt` file as the ADK agent with one change:
replace the `{preloaded_skills_section}` placeholder at graph construction time.

The ADK `build_preloaded_section()` utility reads the preloaded SKILL.md bodies
and inlines them into the prompt. Replicate this in `skills.py`:

```python
def build_preloaded_section(preloaded_skill_names: list[str]) -> str:
    lines = ["## Preloaded Skills\n\nThe following skills are always active:\n"]
    for name in preloaded_skill_names:
        body = SKILL_INSTRUCTIONS.get(name, "")
        lines.append(f"### {name}\n{body}\n")
    return "\n".join(lines)

SYSTEM_PROMPT = (
    PROMPTS_DIR / "root_agent.txt"
).read_text().replace("{preloaded_skills_section}", build_preloaded_section(PRELOADED_SKILLS))
```

The ADK `SkillToolset.process_llm_request` appends an `<available_skills>` XML
block automatically on every request. In LangGraph, this must be done explicitly
in `agent_node` by appending a list of lazy skill names and descriptions to the
system prompt before calling the model:

```python
available_skills_xml = "<available_skills>\n" + "\n".join(
    f'  <skill name="{name}" description="{SKILL_DESCRIPTIONS[name]}" />'
    for name in LAZY_SKILLS
) + "\n</available_skills>"
# Append to SYSTEM_PROMPT when constructing messages
```

---

## File Structure

```
langgraph_agents/native_skill_mcp/
├── DESIGN_SPEC.md          ← this file
├── __init__.py             ← exports: graph, AgentState
├── agent.py                ← build_graph(), graph singleton, MCP client lifecycle
├── state.py                ← AgentState TypedDict
├── skills.py               ← SKILL_TOOL_MAP, SKILL_INSTRUCTIONS,
│                              load_skill, list_skills meta-tools,
│                              build_preloaded_section(), get_visible_tools()
├── tools.py                ← Billy MCP client factory, load_all_billy_tools()
├── nodes/
│   ├── __init__.py
│   ├── agent_node.py       ← agent_node(), prune_tool_responses()
│   ├── tools_node.py       ← tools_node()
│   └── summarizer_node.py  ← maybe_summarize_node(), summarize_node(),
│                              should_summarize(), COMPACTION_INTERVAL
├── prompts/
│   ├── root_agent.txt      ← identical to agents/native_skill_mcp/prompts/root_agent.txt
│   └── summarizer.txt      ← identical to agents/native_skill_mcp/prompts/summarizer.txt
└── skills/                 ← symlink or copy of agents/native_skill_mcp/skills/
    ├── support-skill/SKILL.md
    ├── invoice-skill/SKILL.md
    ├── customer-skill/SKILL.md
    ├── product-skill/SKILL.md
    ├── email-skill/SKILL.md
    └── invitation-skill/SKILL.md
```

**Preferred approach for `skills/` and `prompts/`**: symlink both directories to
their counterparts in `agents/native_skill_mcp/` so there is a single source of
truth for domain content:

```bash
ln -s ../../agents/native_skill_mcp/skills langgraph_agents/native_skill_mcp/skills
ln -s ../../agents/native_skill_mcp/prompts langgraph_agents/native_skill_mcp/prompts
```

---

## Dependencies

Per `langchain-dependencies` skill: `langchain`, `langchain-core`, and
`langsmith` are **always required** alongside any LangGraph project.

Verify these are present in `pyproject.toml`; add any that are missing:

```
langchain>=0.3.0                # always required
langchain-core>=0.3.0           # always required
langsmith                       # always required (tracing)
langchain-google-genai>=2.0.0   # ChatGoogleGenerativeAI
langgraph>=0.2.0                # StateGraph, Command, InjectedState, InMemorySaver
langchain-mcp-adapters          # MultiServerMCPClient — add if not present
python-dotenv>=1.2.1            # .env loading
```

Key import paths:

```python
from langgraph.checkpoint.memory import InMemorySaver        # dev checkpointer
from langgraph.checkpoint.sqlite import SqliteSaver          # local persistence
from langgraph.checkpoint.postgres import PostgresSaver      # production
from langgraph.types import Command, Overwrite, RetryPolicy
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import InjectedState, InjectedToolCallId
```

LangSmith env vars (add to `.env`):

```ini
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=<your-key>
```

---

## Environment Variables

Identical to the ADK agent:

| Variable | Purpose |
|---|---|
| `GOOGLE_API_KEY` | Gemini API key (AI Studio) |
| `GOOGLE_GENAI_USE_VERTEXAI` | `1` to use Vertex AI instead |
| `BILLY_MCP_URL` | SSE endpoint; if unset, spawns stdio subprocess |

---

## Key Implementation Gotchas

### 1. `load_skill` must return a `Command`, not a string

If `load_skill` is a plain `@tool` that returns a string, the `activated_skills`
state update will never reach the graph. The tool **must** return
`Command(update={...})` with both the `activated_skills` update and the
`ToolMessage`. This requires `langgraph >= 0.2.x` and `InjectedToolCallId`.

### 2. Custom `tools_node` is required — but not because of `Command`

LangGraph >= 0.2's `ToolNode` from `langgraph.prebuilt` does support tools that
return `Command` — state updates and routing are propagated correctly.

The reason a **custom** tools node is required here is **dynamic tool binding**:
the model is bound to a filtered tool list each turn (based on `activated_skills`).
`ToolNode(all_tools)` would execute tools that were never offered to the model,
bypassing the gating contract. The custom tools node must execute only the tools
that were in scope for the current `activated_skills`.

### 3. `thread_id` is always required

Invoking a checkpointed graph without `thread_id` in the config means state is
never persisted — `activated_skills` will reset to `[]` on every call:

```python
# WRONG — state not persisted
graph.invoke({"messages": [HumanMessage("list invoices")]})

# CORRECT
graph.invoke(
    {"messages": [HumanMessage("list invoices")]},
    {"configurable": {"thread_id": "session-abc"}},
)
```

### 5. MCP client async context manager

`MultiServerMCPClient` must be entered (`async with client`) before calling
`get_tools()`. The recommended pattern is to open it once at process start in
`agent.py` (e.g., in an `asyncio.run()` wrapper or a `lifespan` function) and
pass the resulting `dict[str, BaseTool]` into the graph. Do not open a new
client per turn.

### 6. Tool binding on every agent_node call

LangGraph calls `agent_node` on every turn. The `bind_tools()` call rebuilds the
tool list each time based on current `activated_skills`. This is correct — it is
the mechanism that gates tool visibility. It is also cheap (binding is
synchronous and just modifies the model invocation config).

### 7. `Overwrite` is required when replacing messages in summarize_node

`AgentState.messages` uses `operator.add` as its reducer. Returning a plain list
from `summarize_node` would **append** the compacted summary to the existing
history, not replace it. Use `Overwrite(...)` from `langgraph.types` to bypass
the reducer:

```python
# WRONG — appends to existing messages
return {"messages": compacted + to_keep}

# CORRECT — replaces messages entirely
from langgraph.types import Overwrite
return {"messages": Overwrite(compacted + to_keep)}
```

### 8. `summarizer.txt` expects structured history

The summarizer prompt (`prompts/summarizer.txt`) was written for ADK's
`function_call` / `function_response` event format. In LangGraph, history is
`HumanMessage` / `AIMessage` / `ToolMessage`. The `format_messages_for_summary()`
helper (in `nodes/summarizer_node.py`) must convert LangChain messages to a
readable text format before passing to the summarizer LLM.

### 9. History pruning and `activated_skills` across compaction

After `summarize_node` runs, `messages` is replaced with a `[SystemMessage +
overlap tail]`. The `activated_skills` field is **not** in `messages`; it is a
separate state field persisted by the checkpointer. The tool registry therefore
remains fully populated after compaction — same guarantee as ADK.

### 10. `should_continue` edge

```python
def should_continue(state: AgentState) -> str:
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return END
```

---

## Success Criteria

The LangGraph port is complete when it can reproduce the following ADK scenarios:

1. **Support query** (preloaded skill): User asks "how do I void an invoice?"
   → `fetch_support_knowledge` called directly, no `load_skill` needed.

2. **Lazy skill load**: User asks "list my invoices"
   → Turn 1: `load_skill("invoice-skill")` called, state updated.
   → Turn 2: `list_invoices` called directly via Billy MCP.

3. **Cross-domain task**: User asks "create an invoice for Acme with product X"
   → Both `invoice-skill` and `customer-skill` (and `product-skill`) are loaded.
   → Customer and product IDs resolved before invoice creation.

4. **History pruning**: After 3+ support queries, old `fetch_support_knowledge`
   responses are replaced with `[pruned]` in the messages passed to the model.

5. **Context compaction**: After 8+ messages, the summarizer fires and replaces
   history with a compact summary. On the next turn, `activated_skills` is
   unchanged and domain tools are still accessible.

6. **Cross-compaction continuity**: Load `invoice-skill`, trigger compaction,
   then ask another invoice question — `list_invoices` is still callable without
   re-loading the skill.
