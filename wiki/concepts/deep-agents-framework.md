---
title: Deep Agents Framework
tags: [deep-agents, langgraph, pattern]
summary: Opinionated agent harness built on LangChain/LangGraph — create_deep_agent() wraps planning, file management, subagent delegation, and HITL into configurable middleware with no boilerplate.
updated: 2026-04-25
sources:
  - raw/agent-skills/deep-agents-core/SKILL.md
  - raw/agent-skills/deep-agents-orchestration/SKILL.md
  - raw/agent-skills/framework-selection/SKILL.md
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

## See Also

- [[Deep Agents Memory Backends]]
- [[Framework Selection — LangChain vs LangGraph vs Deep Agents]]
- [[SKILL.md Pattern]]
- [[LangGraph Advanced Patterns]]
