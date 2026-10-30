---
title: Deep Agents Framework
tags: [deep-agents, langgraph, pattern]
summary: Opinionated agent harness built on LangChain/LangGraph — create_deep_agent() wraps planning, file management, subagent delegation, and HITL into configurable middleware with no boilerplate.
updated: 2026-10-30
sources:
  - data/raw/agent-skills/deep-agents-core/SKILL.md
  - data/raw/agent-skills/deep-agents-orchestration/SKILL.md
  - data/raw/agent-skills/framework-selection/SKILL.md
  - data/raw/agent-skills/README.md
  - data/raw/agent-skills/deep-agents-core/references/middleware-patterns.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop--deep-agents.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--deep-agents.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--deep-agents.md
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

## Execution Environment, Permissions, and Context Layers

The upstream overview groups the harness into four components — execution environment,
context management, delegation, steering — and several of their rules are non-obvious:

- **Filesystem permissions are first-match-wins, default-allow.** `permissions=` takes rules of
  `operations` (read/write) × `paths` (globs) × `mode` (allow/deny), evaluated top to bottom; if
  no rule matches, the operation is **allowed**. A deny-list therefore needs an explicit trailing
  catch-all deny if you want an allowlist posture. Subagents can be given narrower rules than the parent.
- **Permissions do not cover sandbox backends.** Once a backend exposes `execute` (arbitrary
  shell), path rules no longer bound what the agent can touch — custom validation has to move
  into backend policy hooks. Choosing a sandbox backend is choosing to leave the permission model.
- **Two code-execution modes, different blast radius.** Sandbox backends (detected via the
  sandbox protocol) add an `execute` shell tool — dependency installs, tests, CLIs. Interpreters
  add an `eval` tool running JavaScript in a scoped QuickJS runtime — loops, batching,
  deterministic transforms, programmatic tool calling — with no shell, package install,
  filesystem, or network access. Prefer the interpreter when the need is computation, not an OS.
- **Restricting tools is an allowlist on the middleware, not removal of it.** Hide all file tools
  via a harness profile's `excluded_tools`, or pass `FilesystemMiddleware(tools=[...])` for a
  subset (a read-only agent = `read_file, ls, glob, grep`). `read_file` is mandatory (omitting it
  raises at construction), and excluding `FilesystemMiddleware` or `SubAgentMiddleware` outright
  is rejected — they are required scaffolding. Tools the backend cannot support (`execute`,
  `delete`) are hidden automatically. The restricted instance is inherited by the general-purpose subagent.
- **Memory vs skills is always-loaded vs progressive.** `memory=` takes `AGENTS.md` files that are
  loaded every run (and the agent may update them); skills load only frontmatter at startup and
  the body on demand.
- **Context flow has four parts:** input context (system prompt, memory, skills, tool prompts) →
  compression (automatic summarization and large-tool-result offloading) → isolation (subagents
  return only a final result) → long-term memory (virtual filesystem across threads).
- **Prompt caching is automatic** on Anthropic and Bedrock (Claude/Nova) models — the static
  system-prompt sections (base instructions, memory, skill content) are cache-marked with no
  configuration; other providers need provider-specific caching middleware.
- **Subagents are single-handoff.** Fresh context per call, run to completion, one final report,
  cannot send multiple messages back — the token-efficiency win and the statelessness constraint
  are the same property.

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
- [[Framework Selection — LangChain vs LangGraph vs Deep Agents]] — prerequisite-for
- [[SKILL.md Pattern]]
- [[LangGraph Advanced Patterns]]
- [[Harness Anatomy]] — instance-of (middleware, sandbox, and state backends as harness components)
- [[Harness Maturity and Failure Modes]] — instance-of (cited as a Stage 2→3 reference implementation)
- [[Loop Detection and the Two-Retry Rule]] — implements (loop-detection middleware)
- [[Deep Agent Pillars]] — instance-of (the framework implements the four pillars)
