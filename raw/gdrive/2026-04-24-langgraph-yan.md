# Langgraph_Yan — A Visual Guide to Stateful AI Agents

**Source:** Google Drive (shared by Yan Zhang, yan.zhang@shine.co)
**File ID:** 1LrhkKGe4nyrtt9bgQlHtMcTWG_u3AkPTD4v-nARD0wo
**Created:** 2026-04-21 | **Modified:** 2026-04-24
**Type:** Google Slides presentation

---

## Part 1: Why — From Chains to Graphs

Traditional AI pipelines are linear and single-pass. LangGraph replaces them with cyclic, stateful graphs — enabling loops, branching, self-correction, and collaboration. This is the primary reason sevDesk switched from LangChain to LangGraph to support agentic RAG.

**Pipelines — Traditional AI**
- Sequential, predictable, single-pass
- Excellent for defined, repeatable tasks
- Cannot pause, loop, or self-correct
- No memory across steps — every run starts fresh

**Graphs — LangGraph**
- Cyclic, stateful, and autonomous
- Agents reason, evaluate, loop, and collaborate
- Continuous execution and adaptation
- Persistent memory across steps and sessions

---

## Part 2: What — Nodes, Edges, State, Reducers

### Nodes & Edges

A LangGraph workflow is a directed graph. Nodes do the work; edges control the flow.

**What a node can be:**
- LLM call — ask the model a question or generate a response
- Tool execution — run a search, DB query, API call, or code
- Human step — wait for human input, approval, or review
- Sub-graph — nest an entire graph as a single node
- Custom logic — any Python function (data transform, validation)

**Edges:**
- Fixed edge — always goes to the same next node
- Conditional edge — routes based on current state

### State

State is the shared context that flows through every node. Each node can read from it and write partial updates back.

**What state contains:**
- `messages` — all conversation turns (with `add_messages` reducer)
- `tool_outputs` — results from every tool call
- `decisions` — routing choices and conditions met
- `custom fields` — anything the workflow needs to track

### Reducers for State

A reducer is a function attached to a state field that defines HOW updates are merged — especially when nodes run in parallel.

| Reducer | Behaviour |
|---|---|
| Default (overwrite) | Last write wins. Simple fields like a status flag. |
| `operator.add` | Appends to a list. Most common pattern for messages. |
| `add_messages` | Smart append for chat — deduplicates by message ID. |
| Custom function | Write any merge logic: sum numbers, pick max score, merge dicts. |

### Workflows vs Agents

- **Workflows** — predetermined code paths, designed to operate in a certain order
- **Agents** — dynamic, define their own processes and tool usage

---

## Part 3: Capabilities

### Persistence & Durable Execution

LangGraph has a built-in persistence layer that saves graph state as checkpoints after every super-step, organized into threads. Enables HITL workflows, conversational memory, time travel debugging, and fault-tolerant execution.

**Checkpointer backends:**

| Backend | Environment | Notes |
|---|---|---|
| `MemorySaver` | Dev/Testing | In-memory only. Lost on restart. Zero setup. |
| `SqliteSaver` | Local/Prototype | SQLite file. Survives restarts. Not scalable. |
| `PostgresSaver` | Production | ACID, concurrent, horizontal scale. Used in LangSmith. |
| `RedisSaver` | High-perf Production | <1ms checkpoint reads. TTL support. |

**Reducers & Super-steps:** When parallel nodes run simultaneously, their outputs are merged by a Reducer — preventing collisions.

**Time Travel:**
- **Replay** — retry from a prior checkpoint
- **Fork** — branch from a prior checkpoint with modified state

### Memory: Short-term

Short-term memory lives within a single conversation thread via the State object + Checkpointers.

**How it works:** State schema (TypedDict + reducers) → Checkpointer compiles with graph → Thread ID scopes state → Resume provides same thread_id

**Managing context window growth:**
- **Message Trimming** — keep last N messages. Fast but loses older context.
- **Summarisation** — LLM compresses older messages into a summary. Preserves meaning.
- **Selective Retention** — agent decides which facts to keep.

### Memory: Long-term

Persists across sessions using the LangGraph Store — a namespaced key-value database.

| Type | What | How Stored |
|---|---|---|
| **Semantic** | Facts, concepts, knowledge about users/domains | Profile (single JSON) or Collection (many docs, semantic search) |
| **Episodic** | Past experiences, actions, task executions, few-shot examples | Examples retrieved as few-shot prompts |
| **Procedural** | Rules, instructions, system prompt/persona — self-updated via Reflection | Updatable prompt in LangGraph Store |

**Write timing:** Hot path (during run, adds latency) vs Background (async after run, no latency impact)

### Human-in-the-Loop (HITL)

Interrupts pause graph execution and wait for external input before continuing.

**Four use cases:**
1. Getting approval before critical actions (DB writes, financial transactions)
2. Human reviews/edits LLM-generated content before use
3. Pausing before a tool executes
4. Collecting and validating human input in a loop

**Types:**
- Static breakpoints — fire before/after a node boundary
- Dynamic `interrupt()` — fires inside a node (mid-execution)

### Subgraphs

A subgraph is a graph used as a node inside a parent graph.

**Useful for:**
- Building multi-agent systems
- Reusing a set of nodes in multiple graphs
- Distributing development across teams (interface = input/output schema)

---

## Part 4: Production

### Streaming

LangGraph supports token streaming, event streaming, and custom streaming modes.

### Agent Chat UI

LangGraph Cloud provides a hosted agent UI for streaming chat interfaces.

### Observability & Tracing (LangSmith)

**Execution Tracing:**
- Visualise exact path through the graph
- Inspect every node's input/output state
- Measure latency and token count per step
- Identify where loops occur and why
- Replay any historical run from its checkpoint

**Automated Evals:**
- Action advancement, context adherence, hallucination check
- Detect infinite loops before production
- Run evaluations automatically on every deployment

**Production Monitoring:**
- Dashboards for performance over time
- Alerts on quality/cost regressions
- A/B test different graph configurations
- Monitor token cost per run
- Collect user feedback ratings

### Key Takeaways

1. **Graphs beat chains** — cyclic graphs enable loops, branching, self-correction
2. **Three building blocks** — Nodes (actors) + Edges (logic) + State (memory)
3. **Decision making** — conditional edges + intent routing for branching logic
4. **Multi-agent = scale** — Supervisor, Handoff, Parallel Swarm trade-offs
5. **Two tiers of memory** — Short-term (State + Checkpointers) / Long-term (Store + vector DBs)
6. **Durability requires DB** — MemorySaver → SQLite → PostgreSQL → Redis
7. **Humans stay in control** — interrupt points + time travel

---

## Part 5: ADK vs LangGraph Comparison

*(Slides present a comparison between ADK and LangGraph — detail not captured in text extraction)*
