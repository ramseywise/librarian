---
title: Framework Selection — LangChain vs LangGraph vs Deep Agents
tags: [langgraph, deep-agents, concept, comparison, conflict]
summary: Decision guide for choosing between LangChain, LangGraph, and Deep Agents — layered frameworks where higher layers add planning, memory, and middleware on top of lower ones.
updated: 2026-10-30
sources:
  - data/raw/articles/2026-07-19-autogen-agentic-design-patterns.md
  - data/raw/articles/2026-07-19-agentic-ai-frameworks-exploration.md
  - data/raw/agent-skills/framework-selection/SKILL.md
  - data/raw/agent-skills/deep-agents-core/SKILL.md
  - data/raw/claude-docs/galactus/skills/new-agent/references/framework-selection.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/new-agent/references/framework-selection.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--04-loop--deep-agents.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness-engineering--deep-agents.md
  - data/raw/repos/learn-ai-engineering/interviewing--notes--deep-agents.md
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

### A second cut: framework vs runtime vs harness

The upstream product docs classify the same three packages by *what they add*, which
generalizes beyond the LangChain ecosystem:

| | Framework | Runtime | Harness |
|---|---|---|---|
| Adds | abstractions, integrations, the agent loop, middleware | durable execution, streaming, HITL, thread + cross-thread persistence, low-level control | predefined tools, prompts, subagents, planning, filesystem, token management (summarization, large-result eviction) |
| Use when | getting started fast; standardizing how a team builds | long-running stateful work; mixing deterministic and agentic steps | autonomous agents on complex, non-deterministic, multi-step tasks |
| Examples | LangChain, Vercel AI SDK, CrewAI, OpenAI Agents SDK, Google ADK, LlamaIndex | LangGraph, Temporal, Inngest | Deep Agents SDK, Claude Agent SDK, Manus, coding CLIs |

In this framing **frameworks run on runtimes**: LangChain 1.0's agent loop is built on top of
LangGraph, and Deep Agents builds on LangGraph too. That conflicts with the layer diagram above,
which puts LangChain at the bottom (see `_conflicts.md`). Both can hold if "LangChain" means two
things — the model/tool integration packages (a dependency of everything) versus the
`create_agent` loop (which executes on the LangGraph runtime). Same capability, three integration
levels: short-term memory is LangChain short-term memory / LangGraph checkpointer / Deep Agents
`StateBackend`; subagents are LangChain multi-agent subagents / LangGraph subgraphs / Deep Agents
`task`; HITL is HITL middleware / `interrupt()` / the `interrupt_on` parameter.

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

For LangChain's own mechanics — `create_agent()`, tools, structured output, middleware, dependency/package management, and RAG-specific implementation classes — see [[LangChain Fundamentals — create_agent, Tools, Structured Output]], [[LangChain Agent Middleware]], [[LangChain Dependency Management]], and [[LangChain RAG Implementation Patterns]].

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

## A different axis: ADK vs LangGraph vs a TypeScript-native agent

The galactus `framework-selection` reference answers a different question from the layer
model above. It picks between Google ADK, LangGraph and the Vercel AI SDK, in this order
(stop at the first yes):

1. Duplex audio? See [[Duplex Voice Breaks Discrete-Turn Assumptions]].
2. Must the agent loop run in a TypeScript/Node process (e.g. inside a frontend's API
   routes)? Use the Vercel AI SDK. A TS frontend that merely calls a separate Python agent
   service does not need it.
3. GCP / Vertex with a managed session service and a maintained scaffolder? ADK.
4. Fine-grained control flow (branching, loops, fan-out/fan-in, HITL at arbitrary points),
   reusable LangChain assets, or multi-provider LLMs? LangGraph.
5. A plain single agent (plus sub-agents) on Gemini? ADK.

Default when nothing clearly applies: ADK on GCP, LangGraph anywhere else. Runtime choice is
asked before control-flow complexity because it is the one branch that has nothing to do
with complexity.

## Graph Topology vs Conversation Topology

A wider axis than the LangChain layer model: **graph-topology** frameworks (LangGraph —
explicit state, fine-grained control) vs **conversation-topology** frameworks (AutoGen —
every agent is a `ConversableAgent`, coordination happens in the message stream).

AutoGen's composition primitives, for comparison:

- **Sequential chats** — a pipeline of two-agent conversations.
- **Nested chats** — a sub-conversation that appears as one turn to the outer agent; this
  is how reflection is built (one writer + N reviewer agents) without a reflection node type.
- **Tool results as messages** — the executor agent posts tool output back into the
  conversation, so the full trace lives in history (debuggable, but contexts grow long).
- **GroupChat speaker selection** (auto, round-robin, or a custom function) is the main
  routing lever; a custom selector can do domain routing without an orchestrator agent.
- **HITL is an agent flag** (`human_input_mode`), where in LangGraph it is a graph primitive
  (`interrupt_before` / `interrupt_after`, see [[HITL and Interrupt Patterns]]).

A team POC found a deterministic LangGraph workflow faster than the non-deterministic
AutoGen equivalent, with no difference in end-user experience versus vanilla RAG.

**Process rules that transfer:**

- **Spike one framework per work item, with the decision criterion set up front, and end
  in an ADR.** A POC without a recorded decision is a research artifact, not a decision.
- **Hybrid stacks are normal** (a LangGraph orchestrator over ADK subagents, AutoGen groups
  inside a graph) — but the inter-framework protocol must be explicit (MCP tools, typed
  messages, or a shared store). Implicit coupling through shared global state is the
  failure mode.

## See Also
- [[LangGraph CRAG Pipeline]]
- [[LangGraph Advanced Patterns]]
- [[ADK vs LangGraph Comparison]]
- [[Deep Agents Framework]]
- [[SKILL.md Pattern]]
- [[LangChain Fundamentals — create_agent, Tools, Structured Output]]
- [[LangChain Agent Middleware]]
- [[LangChain Dependency Management]]
- [[LangChain RAG Implementation Patterns]]
- [[Duplex Voice Breaks Discrete-Turn Assumptions]] — extends (the duplex row asked first)
- [[HITL and Interrupt Patterns]] — complements (graph-level interrupt vs AutoGen's agent-level human flag)
