---
title: Framework Selection — LangChain vs LangGraph vs Deep Agents
tags: [langgraph, deep-agents, concept, comparison]
summary: Decision guide for choosing between LangChain, LangGraph, and Deep Agents — layered frameworks where higher layers add planning, memory, and middleware on top of lower ones.
updated: 2026-04-25
sources:
  - raw/agent-skills/framework-selection/SKILL.md
  - raw/agent-skills/deep-agents-core/SKILL.md
---

# Framework Selection — LangChain vs LangGraph vs Deep Agents

## The Layer Model

The three frameworks are **layered**, not competing:

```
┌─────────────────────────────────────────┐
│              Deep Agents                │  ← highest: batteries included
│   (planning, memory, skills, files)     │
├─────────────────────────────────────────┤
│               LangGraph                 │  ← orchestration: graphs, state, HITL
│    (nodes, edges, state, persistence)   │
├─────────────────────────────────────────┤
│               LangChain                 │  ← foundation: models, tools, chains
│      (models, tools, prompts, RAG)      │
└─────────────────────────────────────────┘
```

Choosing a higher layer does not cut you off from lower layers — LangGraph graphs can be used inside Deep Agents; LangChain primitives work inside both.

## Decision Questions (in order)

| Question | Yes → | No → |
|---|---|---|
| Need planning across sub-tasks, file management across a session, persistent memory, or on-demand skills? | **Deep Agents** | ↓ |
| Need complex control flow — loops, dynamic branching, parallel workers, HITL, or custom state? | **LangGraph** | ↓ |
| Single-purpose agent: takes input, runs tools, returns result? | **LangChain** (`create_agent`) | ↓ |
| Pure model call, chain, or retrieval pipeline with no agent loop? | **LangChain** (chain) | — |

## Framework Profiles

### LangChain — focused, self-contained tasks

Best for: single-purpose agents, RAG pipelines, document Q&A, quick prototypes.
Not ideal when: state needs to persist, control flow is conditional or iterative.

### LangGraph — own the control flow

Best for: branching/loops (CRAG retry), HITL approval steps, parallel fan-out, persistent state within a session.
Not ideal when: you want planning + file management handled for you (use Deep Agents).

Middleware note: **LangGraph has no middleware** — you wire behavior directly into nodes and edges.

### Deep Agents — open-ended, multi-dimensional tasks

Best for: long-running tasks requiring a todo list, file management across a session, subagent delegation, on-demand skills, cross-session memory.

**Built-in middleware (always on):**

| Middleware | Provides |
|---|---|
| `TodoListMiddleware` | `write_todos` — plan and track multi-step tasks |
| `FilesystemMiddleware` | `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep` |
| `SubAgentMiddleware` | `task` — delegate to named subagents |

**Opt-in middleware:**

| Middleware | Provides |
|---|---|
| `SkillsMiddleware` | Load SKILL.md files on demand |
| `MemoryMiddleware` | Long-term memory via `Store` |
| `HumanInTheLoopMiddleware` | Interrupt before sensitive tool calls |

## Quick Comparison

| | LangChain | LangGraph | Deep Agents |
|---|---|---|---|
| **Control flow** | Fixed (tool loop) | Custom (graph) | Managed (middleware) |
| **Middleware** | Callbacks only | None | Explicit, configurable |
| **Planning** | No | Manual | TodoListMiddleware |
| **File management** | No | Manual | FilesystemMiddleware |
| **Persistent memory** | No | With checkpointer | MemoryMiddleware |
| **Subagent delegation** | No | Manual | SubAgentMiddleware |
| **On-demand skills** | No | No | SkillsMiddleware |
| **HITL** | No | Manual interrupt | HumanInTheLoopMiddleware |
| **Custom graph edges** | No | Full control | Limited |

## Mixing Layers

A LangGraph compiled graph can be registered as a subagent inside Deep Agents via the `task` tool. Common pattern: Deep Agents as outer orchestrator → LangGraph subgraph for tightly-controlled pipeline (e.g. CRAG retrieval loop).

LangChain tools and retrievers work as building blocks inside both LangGraph nodes and Deep Agents tools.

## See Also
- [[LangGraph CRAG Pipeline]]
- [[LangGraph Advanced Patterns]]
- [[ADK vs LangGraph Comparison]]
- [[Deep Agents Framework]]
- [[SKILL.md Pattern]]
