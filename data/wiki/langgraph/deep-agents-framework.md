---
title: Deep Agents Framework
tags: [deep-agents, langgraph, pattern]
summary: Opinionated agent harness built on LangChain/LangGraph — create_deep_agent() wraps planning, file management, subagent delegation, and HITL into configurable middleware with no boilerplate.
updated: 2026-07-14
sources:
  - raw/agent-skills/deep-agents-core/SKILL.md
  - raw/agent-skills/deep-agents-orchestration/SKILL.md
  - raw/agent-skills/framework-selection/SKILL.md
  - raw/agent-skills/README.md
  - raw/agent-skills/deep-agents-core/references/middleware-patterns.md
---

# Deep Agents Framework

## What It Is

Deep Agents is an opinionated framework built on LangChain/LangGraph. A single `create_deep_agent()` call wires planning, filesystem, subagent delegation, and optionally HITL and memory — you configure, you don't implement.

```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    model="claude-sonnet-4-6",
    tools=[my_tool],
    system_prompt="You are a helpful assistant",
)
config = {"configurable": {"thread_id": "user-123"}}
result = agent.invoke({"messages": [{"role": "user", "content": "..."}]}, config=config)
```

## Built-in Tools (always present)

Every agent gets these without configuration:
- `write_todos` — plan multi-step tasks as a tracked list
- `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep` — filesystem tools
- `task` — delegate to a named subagent

## Full Configuration

```python
agent = create_deep_agent(
    name="my-assistant",
    model="claude-sonnet-4-6",
    tools=[custom_tool],
    system_prompt="Custom instructions",
    subagents=[research_agent, code_agent],
    backend=FilesystemBackend(root_dir=".", virtual_mode=True),
    interrupt_on={"write_file": True},
    skills=["./skills/"],
    checkpointer=MemorySaver(),
    store=InMemoryStore()
)
```

## SKILL.md Format

Skills use progressive disclosure — only loaded when the agent reads the file:

```markdown
---
name: my-skill
description: Specific description of what this skill handles
---

# Skill Name

## Overview
## When to Use
## Instructions
```

Two loading backends:
- `FilesystemBackend` — reads SKILL.md from disk; use for local dev
- `StoreBackend` — reads from `InMemoryStore` / `PostgresStore`; required in serverless environments

Skills are **not** inherited by custom subagents — provide them explicitly per subagent.

## Subagents

The default `general-purpose` subagent is automatically available. Custom subagents get fresh context per call (stateless):

```python
agent = create_deep_agent(
    subagents=[{
        "name": "researcher",
        "description": "Conduct research and compile findings",
        "system_prompt": "Search thoroughly, return concise summary",
        "tools": [search_papers],
    }]
)
```

**Critical:** subagents are stateless — each `task()` call starts fresh. Provide complete instructions in a single call, not across multiple.

## HITL (Human-in-the-Loop)

```python
agent = create_deep_agent(
    interrupt_on={
        "write_file": True,
        "execute_sql": {"allowed_decisions": ["approve", "reject"]},
        "read_file": False,
    },
    checkpointer=MemorySaver()  # required for interrupts
)

# Resume
result = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config=config)
# Reject with feedback
result = agent.invoke(Command(resume={"decisions": [{"type": "reject", "message": "Run tests first"}]}), config=config)
# Edit before execution
result = agent.invoke(Command(resume={"decisions": [{"type": "edit", "edited_action": {...}}]}), config=config)
```

Interrupts happen between `invoke()` calls. Check `state.next` or `__interrupt__` in result after each call.

## What Cannot Be Changed

- Core middleware names (`write_todos`, `task`, filesystem tool names)
- HITL protocol structure (approve/edit/reject)
- Custom subagents cannot be made stateful

## Key Rules

- Always provide `thread_id` — without it, state is not persisted
- `checkpointer` is required for any `interrupt_on` configuration
- `store` is required when using `StoreBackend` or `MemoryMiddleware`
- Skills need a backend to load from — `FilesystemBackend` for local, `StoreBackend` for cloud

## Skill Directory Organization (`.agents/skills/`)

The on-disk skill catalog loaded by the harness is organized into five groups, each loaded on demand (not slash commands — the agent reads them at runtime):

| Group | Skills |
|---|---|
| Entry point | `framework-selection` — decides LangChain vs LangGraph vs Deep Agents for a given task; read first |
| Cross-domain | `voice-agents`, `observability`, `advanced-rag-patterns` |
| Google ADK | `adk-cheatsheet`, `adk-dev-guide`, `adk-scaffold`, `adk-deploy-guide`, `adk-eval-guide`, `adk-observability-guide` |
| Deep Agents | `deep-agents-core`, `deep-agents-memory`, `deep-agents-orchestration` |
| LangChain / LangGraph | `langchain-dependencies`, `langchain-fundamentals`, `langchain-middleware`, `langchain-rag`, `langgraph-fundamentals`, `langgraph-persistence`, `langgraph-human-in-the-loop` |

Reference files marked with `*` in the catalog are stubs pending wiki ingest — the pattern is to promote a research doc into a `references/` file once the wiki page grounding it exists. These skill files are also read directly by Claude Code coding sessions (not just by agents at runtime) as framework reference before writing agent code.

## See Also

- [[Deep Agents Memory Backends]]
- [[Framework Selection — LangChain vs LangGraph vs Deep Agents]]
- [[SKILL.md Pattern]]
- [[LangGraph Advanced Patterns]]
- [[Harness Anatomy]] — instance-of (middleware, sandbox, and state backends as harness components)
- [[Harness Maturity and Failure Modes]] — instance-of (cited as a Stage 2→3 reference implementation)
- [[Loop Detection and the Two-Retry Rule]] — implements (loop-detection middleware)
