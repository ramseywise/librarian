---
title: Multi-Agent Topology Patterns
tags: [graph, langgraph, agents, comparison]
summary: "The five recurring graph shapes (generate-then-verify, supervisor, fan-out/fan-in, subgraph, handoff), what each costs and how each fails, plus the two design questions underneath them: is context shared, and who decides what runs next."
updated: 2026-10-30
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--05-topology-patterns.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--03-state-and-reducers.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--OUTLINE.md
---

# Multi-Agent Topology Patterns

A handful of shapes recur in [[Graph Engineering]]. Each has a cost and a typical way of
failing. Patterns compose (a supervisor can dispatch to a fan-out subgraph whose workers each
run generate-then-verify), but add each layer only when one of the five signals in
[[Loop-to-Graph Escalation]] forces it.

## The catalogue

| Pattern | Shape | Use when | Costs | Fails by |
|---|---|---|---|---|
| **Generate-then-verify** | produce → check → bounded back-edge | The job splits into a produce step and an independent check | One extra node per cycle | The checker sees the producer's reasoning and agrees with it |
| **Supervisor** | router → specialists → router | Work arrives in several kinds needing different handling | A routing call per turn | Mis-routing; the supervisor becomes a bottleneck |
| **Fan-out / fan-in** | split → N parallel workers → merge | Many independent items, one combined result | Tokens scale with N | Missing reducer; redundant findings; correlated errors |
| **Hierarchical (subgraph)** | a compiled graph used as one node of a parent | A sub-topology is reused or owned by another team | State mapping at the boundary | Hidden cost; failures inside are hard to see from outside |
| **Handoff** | agent writes a status key → conditional edge reads it | Agents pass control without knowing each other | A status key in the schema | Status values drift; nobody handles an unexpected one |

**Choosing:** a produce step plus an independent check → generate-then-verify (start here).
Tasks of different kinds → supervisor. Many independent items → fan-out with a reducer
([[Send API Fan-out]], [[LangGraph State Reducers]]). A reused or separately owned
sub-topology → subgraph behind a wrapper node.

### Notes per pattern

- **Generate-then-verify.** The separation creates the value; parallelism is a bonus. Put
  deterministic checks before the LLM checker and bound the back-edge — the topology-level
  form of [[Verification Loops]].
- **Supervisor.** The settled baseline for multi-agent work: the orchestrator holds the plan,
  workers run in isolated contexts. **Specialise by system prompt first**; a separate model
  per node is an optimisation you justify with measurements ([[n8n AI Workflow Builder]] runs
  every specialist on one model at temperature 0).
- **Fan-out.** The canonical instance is the *parallel review graph*: planner → worker →
  security, logic and style reviewers in parallel → synthesiser → pass/fail gate that routes
  feedback back to the worker. A vendor reports ~3× faster than sequential on code review;
  treat that as a number to measure, not quote.
- **Subgraphs.** When parent and child schemas share keys, add the compiled subgraph
  directly. When they differ, call it inside a **wrapper node** that maps parent state →
  child input and child output → parent update. The wrapper is more code and usually worth
  it: it makes the contract explicit and stops a child writing parent keys it should not touch.
- **Handoff.** Coupling lives in the state schema, not in agent code, so agents can be
  swapped without touching neighbours. **Route unknown status values to an explicit error
  node** rather than letting the router throw.

## The same patterns in Claude Code

| Graph concept | Claude Code |
|---|---|
| Node | A subagent: own context window, system prompt, scoped tools |
| Edge | The main session's decision about which subagent to spawn, when, with what brief |
| State | Return values passed on by the orchestrator |
| Deterministic edge | A hook that guarantees a transition |
| Programmatic topology | The Agent SDK |

What is lost compared with LangGraph: **no typed shared state, no reducers, no
checkpoints.** State is whatever the orchestrator passes along — a context firewall when you
want one ([[Harness Orchestration]]), a liability when you need resume.

## Two design questions underneath the catalogue

A multi-agent textbook (*AI Agents in Depth*, ch. 10) separates two questions the catalogue
blurs.

### Shared vs. isolated context

Shared context is like threads sharing memory: nothing is lost in transfer, but everything
accumulates. Isolated agents are like processes: each has its own window and communicates
only through what is explicitly passed.

| Criterion | Share | Isolate |
|---|---|---|
| Subtasks | Tightly coupled; each needs earlier reasoning | Separable; each needs only a brief |
| Window | Cumulative trajectory fits | It would blow the window |
| Parallelism | Sequential is fine | Workers must run at once |
| Isolation | Roles may see each other's work | A role (e.g. a verifier) must not |
| Cost | One cache-friendly trajectory | N contexts, each paying its prefix |

Rule of thumb: **if the cumulative context would exceed about half the window, don't share;
if the task demands zero information loss, share.** Hybrids share early (requirements and
design) and switch to explicit handoff once the work splits. Two shared-context mechanisms:
**staged system prompts** (one trajectory whose prompt and tool set change by stage, with tool
calls as explicit, reversible transitions) and **role transfer** (`transfer_to_agent` swaps the
active role over the same history; guard circular handoffs with a counter).

### Who decides what runs next

| Topology | Who decides | Maps to |
|---|---|---|
| **Peer** | Equals, usually proposer + reviewer | Generate-then-verify |
| **Manager** | One agent plans and calls the others as tools | Supervisor; fan-out |
| **Decentralised** | Each agent picks its successor | Handoff |

- **Peer** collaboration exists mainly to stop *premature termination* (the lazy fake "done",
  the early give-up, the false success claim).
- **Manager**: the weak point is the planner — a bad plan sinks every worker — so the
  strongest model goes on planning. Sub-agents return structured summaries, like exit codes.
- **Decentralised** splits into orchestration (a conductor) vs. choreography (each agent knows
  its next step): no bottleneck, but the whole flow is harder to see. Frameworks sit at
  different points: a fixed SOP pipeline with a shared message pool is decentralised in
  communication but not control; group chat with a central speaker selector risks livelock;
  handoff SDKs are truly decentralised and need a max-handoff guard. A2A is a protocol, not a
  topology — **MCP connects an agent to tools; A2A connects an agent to other agents.**

> **A handoff package carries the task and its acceptance criteria, the confirmed facts and
> constraints, and paths to artifacts. Never the full trajectory.**

## When multi-agent beats single-agent: the new-information test

The one question: **does the collaboration introduce information the single agent didn't
have?**

| Collaboration | New information? | Evidence |
|---|---|---|
| Self-review (same model, no tools) | No | Often neutral or harmful in the self-correction literature; tool-grounded critique loses its gains when the tools are removed |
| Debate among copies of one model | No | Matches a single agent given the same compute — recombining the same information cannot add any |
| Execution, tool or visual feedback | Yes | Large gains (execution-feedback training; screenshot feedback roughly doubled a web-generation score) |

So **a reviewer earns its node when it can run something**: tests, a browser, a search, a type
checker. More steps alone also plateau — agents spend steps poorly unless told their budget,
so a manager should **allocate step budgets per worker**.

## The runtime as an operating system

| OS | Agent runtime |
|---|---|
| Program | Static prefix: system prompt + tool definitions |
| Process memory | The trajectory |
| Kernel | The agent runtime |
| System call | Tool call |
| `fork` / `kill` / `ps` | spawn / cancel / list sub-agents |
| Exit code | The structured summary a sub-agent returns |

The analogy (and its Actor-model precedent) breaks in one place: **agents pass meaning, not
bytes**, so every interface needs a contract the receiver can check.

- **Four file-system areas:** private scratchpad (one agent), shared workspace (optimistic
  lock or one worktree per agent), mounted external (mostly read-only, eventually consistent),
  built-in read-only (e.g. skills). **Pass file paths, not file contents** — a manager can hold
  only a file index.
- **Control plane:** a message envelope (sender, target, type, payload); status written by
  agents as an append-only JSONL trajectory (a write-ahead log that gives resume, audit and
  handoff for free) rather than polled — a status file whose mtime stops moving flags a stuck
  agent; graceful vs forced termination with cascading cancellation; token/step budgets,
  model tiering (strong planner, cheaper workers) and concurrency caps.
- When parallel workers race to success, settle it with a lock or idempotent writes. A message
  bus without persistence drops messages for a worker that is down.

## See Also
- [[Graph Engineering]] — extends
- [[Graph Topology Primitives]] — extends
- [[Loop-to-Graph Escalation]] — extends
- [[Multi-Agent Failure Modes at Scale]] — prerequisite-for
- [[Harness Orchestration]] — extends
- [[Send API Fan-out]] — instance-of
- [[n8n AI Workflow Builder]] — instance-of
