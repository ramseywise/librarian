---
title: Graph Engineering
tags: [llm, agents, infra, langgraph, concept]
summary: "The fifth layer of the stack — designing which nodes exist, which transitions are permitted, and how the runtime work graph mutates, so multi-agent work has an organizational structure rather than just more agents."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--README.md
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph--graph-engineering.md
---

# Graph Engineering

Graph engineering designs the **topology** of a multi-agent system: which nodes exist,
which transitions between them are permitted, and how the runtime work graph forms and
mutates.

Where [[Loop Engineering]] asks *"what cycle re-prompts this agent and decides when it
quits?"*, graph engineering asks *"who is allowed to hand work to whom, under what
condition, carrying what state?"*

> **Graphs make agent organizations programmable the way loops make individual agent
> behavior programmable.**

## Position in the Stack

prompt → context → harness → loop → **graph**. The harness supplies tools, state, and
guardrails ([[Harness Engineering]]); the loop decides how many times to use them and when
to stop; the graph decides **which loop runs next and who is accountable for it**.

Each layer presumes the one below. **A graph routing between unreliable loops inherits
every loop failure at organizational scale, and adds coordination failure on top.**

### Containment, not replacement

LangChain's sharpest line from three years of LangGraph:

> **"A loop is just a directed, cyclic graph."**

Loop and graph engineering are *complementary layers, not substitutes*. The framing that
graph engineering *replaces* loop engineering overstates the break.

What actually changes at the boundary is **the failure mode you are engineering against**.
A single loop fails by not converging. A graph fails by mis-routing, deadlocking,
double-writing shared state, or losing accountability for a decision. Gao Dalie's
diagnosis of why teams hit the wall:

> **"It's not that the agents aren't smart enough, but rather that the organizational
> structure isn't clear enough."**

### Where loop ends and graph begins

You are in graph territory once you need **more than one agent collaborating with
conditional handoffs and shared state across that collaboration**. A single agent with a
tool loop is loop engineering.

The narrower, more usable rule: reach for a graph when you have a **complex task with 3+
independent verification or research steps**. Below that bar, a sequential loop is cheaper
and simpler.

## Production Agents Are Not DAGs

The most load-bearing lesson from three years shipping LangGraph:

> **"Production agents need cycles: retrying failed tool calls, asking users for missing
> information, revising answers after validation, calling tools repeatedly until they have
> enough context."**

This is why the airflow/DAG mental model imported from data engineering breaks on agents.
A DAG is acyclic by definition; a production agent must be able to go A → B, discover B
failed, return to A, and *only then* reach C. **Graph engineering for agents is
cyclic-graph engineering. Anything that forbids cycles is a workflow engine, not an agent
framework.**

The second lesson: **static edges are insufficient.** Real systems mix known structure with
runtime variability — the set of nodes to run is often not known until runtime (fan out
over N retrieved documents, spawn one reviewer per changed file). Hence
[[Send API Fan-out]]: a node routes work to one or more downstream nodes dynamically,
without statically defining every transition.

## Core Primitives

See [[Graph Topology Primitives]] for the full treatment of nodes, edges, state,
durable execution, and typed edges. The load-bearing design question:

> **"Nodes do work. A node can be deterministic code, a single LLM call, a tool call, or a
> full agent with its own internal loop."**

That heterogeneity is the point. The skill is deciding, per node, **how much agency to
spend** — every node that could be deterministic code and isn't is a node you pay tokens
and variance for.

## Topology Patterns

| Pattern | Shape |
|---|---|
| **Supervisor** | A coordinator routes tasks to specialist workers by task type and aggregates results — the settled baseline for most multi-agent work |
| **Parallel fan-out / fan-in** | Multiple agents run simultaneously on independent branches; a synthesizer merges into shared state. Wins wall-clock, costs tokens |
| **Hierarchical (team-of-teams)** | A subgraph is itself a node in a parent graph — nested orchestration, reusable sub-topologies |
| **Handoff protocol** | An agent signals completion by writing a designated state key; the conditional edge reads that key to pick the next agent. Keeps coupling in state, not code |
| **Parallel review** | Planner → worker → three reviewer nodes (security, logic, style) in parallel → synthesizer → pass/fail gate. Reported ~3× faster wall-clock than the sequential equivalent |

### Generate-then-verify is the highest-yield first graph

For a first graph, pick a job that **splits naturally into a produce step and an
independent check step** — draft-then-review, research-then-write, build-then-test.

**The separation is what creates the value; the parallelism is a bonus.** This is the same
generator/evaluator split that [[Verification Loops]] enforces inside a single loop, lifted
to the topology level.

## When NOT to Build a Graph

LangChain is explicit that some work is too fluid to pin down:

> Generic deep research **"requires planning and delegation in ways that are hard to pin
> down ahead of time"** — forcing agentic tasks **"into deterministic paths is the wrong
> move."** Use an agent harness instead.

The heuristic: **structure what you know, leave agency where you don't.** If you cannot
name the nodes before the run starts and the Send API can't derive them from a known step,
you want a harness with a good loop, not a graph.

Cost is the other gate:

| Metric | Loop | Graph |
|---|---|---|
| Wall-clock time | High | Low |
| Token cost per cycle | Lower | ~3× higher |
| Break-even pass rate | — | ~50% |

Graphs win on cost when per-cycle success rates are 50%+; they lose on simple,
low-pass-rate tasks where you pay fan-out cost for work that will be redone anyway.
Anthropic's own multi-agent research system runs at *"roughly 15× the tokens of a chat
turn"* — **graph engineering requires genuine job separation to justify the overhead.**

See [[Loop-to-Graph Escalation]] for the decision procedure.

## Failure Modes at Scale

A control-theory reading of why independent loops degrade once there are many of them —
four structural failures:

1. **Goodhart's Law** — metrics detach from their original meaning under aggressive optimization.
2. **Upward blindness** — a loop cannot question its own targets or reference values.
3. **Inter-loop conflict** — independent loops fight over shared resources with no awareness of each other.
4. **Measurement decay** — sensors drift and definitions shift while loops keep running on stale data.

Failure 2 is the same boundary [[Evolve Loop]] hits: a mechanism that optimizes within a
frame cannot interrogate the frame. The graph's answer is to put the frame in a *slower*
loop that owns it.

Four design principles, which read as the governance layer of graph engineering:

| Principle | Description |
|---|---|
| **Paired metrics** | Every optimization metric gets a counter-metric and an anchor metric |
| **Owned references** | Targets are owned by slower loops, so objectives can't change silently |
| **Separated cadences** | Fast loops *escalate* to slower loops rather than overriding them |
| **Frozen nodes** | Some measurements are intentionally non-tunable |

### Anchors

> **Anchors are "external fixed nodes the internal machinery is forbidden to rewrite."**

Held-out test sets, physical inventory counts, banked revenue, safety specifications.
Without anchors a graph becomes *"perfectly self-consistent while drifting arbitrarily far
from reality."*

**An anchor made tunable is an anchor that will eventually be tuned.** This is the same
write-boundary discipline [[Recursive Self-Improvement]] enforces by filesystem
permissions, generalized to the organizational layer.

## Production and Governance

The enterprise angle is mostly about **attribution**: once work fans out across nodes,
"the graph did it" is not an acceptable audit answer. See
[[Graph Governance and Attribution]] for the identity, cost-control, and checkpoint
patterns plus the seven-item production checklist.

The one insight worth stating here: **consequence concentrates at specific edges**, so
approval gates belong at those edges — not uniformly across every node.

## Graph Engineering in Claude Code

The concepts already exist in the harness under different names:

- **Subagents are nodes** — *"each subagent is a separate agent instance with its own
  context window, its own system prompt, and scoped tool access."*
- **Orchestration decisions are edges** — *"your main Claude session is itself a node, and
  its decisions about which subagent to spawn, when, and with what brief are the edges."*
- **State flows by return value** — a subagent's final output flows back to the
  orchestrator, which passes the relevant piece to the next node.

Three implementation levels, in increasing determinism:

1. **Markdown subagents** in `.claude/agents/` — fastest way to stand up a multi-node graph.
2. **Hooks as deterministic edges** — when probabilistic routing isn't good enough, a hook *guarantees* the transition.
3. **Claude Agent SDK** — programmatic graph definition, for unattended operation and for making the topology testable.

The same 15×-token warning applies: fan out only where the work genuinely separates.

## The Knowledge-Graph Facet

Graphs appear in a second, distinct sense — **knowledge graphs as retrieval structure**
rather than execution topology. The distinction is worth keeping sharp:

| | Agent graph | Knowledge graph |
|---|---|---|
| Nodes are | Units of computation | Entities |
| Edges are | Permitted transitions | Typed relationships |
| The graph is | Execution topology | Data structure for retrieval |
| Runtime concern | Routing, state, cost | Traversal, entity resolution |

Both live in this pillar. See [[Knowledge Graph Retrieval]] for the retrieval side and
[[Knowledge Graph as Shared Agent Memory]] for where the two senses converge.

## Adoption Methodology

1. **AUDIT** — document current workflows and where they bottleneck.
2. **IDENTIFY** — find the steps that are genuinely independent (i.e. parallelizable).
3. **DESIGN** — sketch the topology; start at 3–5 nodes.
4. **IMPLEMENT** — build it and measure a baseline before optimizing.
5. **TYPE** — add relationship semantics to edges.

> **A 3–5 node graph with one honest verification step beats a twelve-node topology whose
> failure modes you can't reason about.**

## Reference Implementation

```python
from langgraph.graph import StateGraph, MessagesState, START, END

def node_a(state: MessagesState) -> MessagesState:
    # read state, do work, return updates
    return {"messages": [...]}

def router(state: MessagesState) -> str:
    # conditional logic → returns node name
    return "node_b" if condition else END

builder = StateGraph(MessagesState)
builder.add_node("node_a", node_a)
builder.add_node("node_b", node_b)
builder.add_edge(START, "node_a")
builder.add_conditional_edges("node_a", router)
graph = builder.compile()
```

Add a checkpointer at `compile(checkpointer=...)` to get durable execution, resume, and
human-in-the-loop interrupts **from the same mechanism**.

## Tooling Landscape (2026)

- **LangGraph** — the canonical implementation; three years of production feedback behind its primitives.
- **OpenClaw Code Mode** — the model *"writes a small JavaScript or TypeScript program instead of choosing directly from a long list of tools,"* making topology expressible as code rather than tool-choice sequences.
- **OpenAI Codex "graph-max"** — sketch a workflow diagram, send it to Codex, execute as multi-agent code.
- **Claude Code** — subagents, hooks, and the Agent SDK.
- **Google ADK** — workflow agents (sequential, parallel, loop) as composable topology primitives.

## Topic Notes

- [[Graph Topology Primitives]] — nodes, edges, state, reducers, interrupts, typed edges
- [[Loop-to-Graph Escalation]] — the default-plus-escalation rule and the five signals
- [[Graph Governance and Attribution]] — identity, cost control, approval checkpoints
- [[Knowledge Graph Retrieval]] — the KG facet as retrieval structure
- [[Knowledge Graph as Shared Agent Memory]] — loop → swarm → graph, and the cost of the swarm tier
- [[n8n AI Workflow Builder]] — a shipped supervisor-pattern graph with published constants

## See Also
- [[LangChain Agent Middleware]] <!-- auto-linked -->
- [[Single Agent With Tools]] <!-- auto-linked -->
- [[Loop Engineering]] — depends-on (the layer below: the graph decides which loop runs next)
- [[Harness Engineering]] — depends-on
- [[Send API Fan-out]] — instance-of (dynamic edges in LangGraph)
- [[LangGraph State Reducers]] — instance-of (the concurrency primitive for fan-in)
- [[Verification Loops]] — complements (generate-then-verify, lifted to topology)
- [[LangGraph Advanced Patterns]] — complements
