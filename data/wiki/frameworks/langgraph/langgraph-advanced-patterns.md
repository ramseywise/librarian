---
title: LangGraph Advanced Patterns
tags: [frameworks, langgraph, pattern]
summary: Advanced LangGraph patterns beyond the basics — subgraphs, Send API fan-out, streaming modes, time-travel, breakpoints/interrupts, error handling, and Plan-and-Execute.
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--05-graph-engineering--notes--04-durable-execution-and-interrupts.md
  - data/raw/claude-docs/playground/docs/archived/agentic-rag-copilot-research.md
  - data/raw/claude-docs/playground/docs/archived/adk-samples-patterns-analysis.md
  - data/raw/claude-docs/playground/docs/archived/rag-agent-template-research.md
  - data/raw/gdrive/2026-04-24-langgraph-yan.md
  - data/raw/agent-skills/langgraph-fundamentals/SKILL.md
  - data/raw/agent-skills/langgraph-human-in-the-loop/SKILL.md
  - data/raw/claude-skills/langgraph/langgraph.md
  - data/raw/claude-docs/playground/docs/frameworks/langgraph.md
  - data/raw/repos/playground/.claude--docs--frameworks--langgraph.md
  - data/raw/claude-docs/project-g/docs/frameworks/langgraph.md
  - data/raw/claude-docs/playground/docs/plans/hardening.md
  - data/raw/repos/playground/.claude--docs--plans--hardening.md
  - data/raw/papers/2026-11-07-ai-agents-definitive-guide-ch01-llms-agents-foundational-blueprint.md
  - data/raw/papers/2026-11-07-ai-agents-definitive-guide-ch02-architectures-patterns-planning-reactivity-multi.md
  - data/raw/papers/2026-11-07-learning-langchain-ch05-cognitive-architectures-langgraph.md
  - data/raw/papers/2026-11-07-learning-langchain-ch06-agent-architecture.md
  - data/raw/papers/2026-11-07-learning-langchain-ch07-agents-ii.md
  - data/raw/papers/2026-11-08-learning-langchain-ch08-patterns-to-make-the-most-of-llms.md
---

# LangGraph Advanced Patterns

## Subgraphs — Compose Without Coupling

```python
# CRAG pipeline as its own subgraph
crag_graph = build_crag_graph()  # returns compiled graph

# Plan-and-Execute as its own subgraph
plan_graph = build_plan_execute_graph()

# Copilot routes between them
copilot = StateGraph(CopilotState)
copilot.add_node("rag_pipeline", crag_graph)
copilot.add_node("action_pipeline", plan_graph)
copilot.add_conditional_edges("route", route_by_intent, {
    "q_and_a": "rag_pipeline",
    "task_execution": "action_pipeline",
})
```

Each subgraph is independently testable. The copilot graph only knows about interfaces.

**State sharing:** subgraphs inherit parent state keys they declare; private keys are isolated.

## Send API — Fan-Out Parallelism

See [[Send API Fan-out]] for full detail. Built-in for map-reduce patterns:

```python
def fan_out_queries(state: AgentState) -> list[Send]:
    return [
        Send("retrieve_single", {"query": q, "original_query": state["query"]})
        for q in state["expanded_queries"]
    ]
```

LangGraph waits for all fan-out nodes to complete before proceeding. `Annotated[list, add_messages]` reducer auto-merges results.

**Use for:** parallel retrieval across multiple query variants or knowledge bases simultaneously.

## Streaming Modes

| Mode | What you get | Use for |
|---|---|---|
| `values` | Full state snapshot after each node | Debugging, final state only |
| `updates` | State delta after each node | Progress indicators, partial results |
| `events` | Fine-grained: token, tool start/end, node start/end | Copilot UI (stream tokens + tool activity) |

### SSE endpoint using `events` mode

```python
async for event in graph.astream_events(
    {"messages": [HumanMessage(request.message)]},
    config={"thread_id": request.session_id},
    version="v2",
):
    if event["event"] == "on_chat_model_stream":
        yield f"data: {json.dumps({'type': 'token', 'content': event['data']['chunk'].content})}\n\n"
    elif event["event"] == "on_tool_start":
        yield f"data: {json.dumps({'type': 'tool_start', 'tool': event['name']})}\n\n"
```

## Time-Travel / State Rollback

Because every node execution is checkpointed, replay from any point:

```python
# List all checkpoints for a thread
checkpoints = list(graph.get_state_history(config))

# Roll back to before the last tool execution
old_config = checkpoints[2].config
graph.update_state(old_config, {"messages": [HumanMessage("Actually, cancel that")]})
graph.invoke(None, old_config)  # resume from that state
```

**Practical use:** "undo last action", try a different approach, debugging by replaying with modified state.

## Breakpoints — Controlled Interrupts

```python
graph.compile(
    interrupt_before=["tool_executor"],  # pause before any tool execution
    interrupt_after=["planner"],         # pause after plan is generated
    checkpointer=checkpointer,
)
```

After interrupting, the frontend shows the pending action/plan and waits for user approval. Resume with `graph.invoke(Command(resume="approved"), config)`.

This is the clean implementation of HITL confirm gates — no custom interrupt logic needed, just compiler flags.

## History Pruning (from ADK samples pattern)

```python
# shared/tools/history_pruning.py — remove prior tool responses before each LLM call
# Keeps: user messages + agent text + current turn tool calls
```

**Why:** neither rag_poc nor playground does this. Long sessions accumulate full tool history, causing context bloat and degraded performance.

**Summarization trigger:** 8-message trigger, 4-message overlap, Haiku for cost.

## Supervisor Multi-Agent Pattern

```
supervisor_graph:
    START
      ↓
    [plan_node]          ← intent, tool routing, clarification
      ↓ (route)
    [retrieval_subgraph] ← rewrite, multi-query, hybrid search, CRAG
      ↓
    [reranker_subgraph]  ← score, filter to top-k, set confidence_score
      ↓
    [generation_subgraph] ← prompt assembly, LLM call, citation
      ↓
    [confidence_gate]    ← confidence_score < threshold → escalate/clarify
      ↓
    END
```

Each subgraph:
- Has its own `StateGraph` and compiled `CompiledStateGraph`
- Communicates via `Command(goto=..., update={...})`
- Can be tested, swapped, and deployed independently

**Why multi-agent for RAG template:** independent testability, swappability, parallelism, per-subgraph traces in LangFuse.

## Command Routing Pattern

```python
def supervisor_route(state: SupervisorState) -> Command:
    if state["intent"] in {"chit_chat", "out_of_scope"}:
        return Command(goto="generation_subgraph", update={"skip_retrieval": True})
    return Command(goto="retrieval_subgraph")
```

## Workflows vs Agents

LangGraph supports two distinct execution models:

- **Workflows** — predetermined code paths defined at compile time. Fast and predictable. Use when every possible execution path can be anticipated (e.g. CRAG retry loop, HITL confirm gate).
- **Agents** — dynamic. The agent decides which tools to call and in what order at runtime. Use when the task space is open-ended.

Both are implemented with the same `StateGraph` API. The distinction is whether conditional edges route to fixed destinations or the LLM picks the next step.

## Checkpointer Backend Selection

Choose based on environment and scale:

| Backend | Environment | Characteristics |
|---|---|---|
| `MemorySaver` | Dev / unit tests | In-memory only. Lost on restart. Zero setup. |
| `SqliteSaver` | Local / prototype | SQLite file. Survives restarts. Not scalable. |
| `PostgresSaver` | Production | ACID, concurrent, horizontal scale. Used in LangSmith itself. |
| `RedisSaver` | High-perf production | <1ms checkpoint reads. TTL support. Distributed. |

```python
# Development
checkpointer = MemorySaver()

# Production (multi-instance Fargate)
checkpointer = AsyncRedisSaver(ttl=86400)  # 24h TTL
```

Template: `MemorySaver` default, `checkpointer` param for injection.

**In-process session wrappers need a TTL too.** A gateway kept a plain `dict[session_id, _Session]` (interrupt queue, lock) that grew without bound: a memory leak under load. Since the Postgres checkpointer holds the actual conversation state, evicting the wrapper loses nothing except in-flight interrupt state. The next request rebuilds it and resumes from the checkpoint. The fix was to swap in `cachetools.TTLCache(maxsize=500, ttl=1800)`, a `MutableMapping`, so the call sites didn't change. Both values are env-tunable.

## Time Travel — Replay vs Fork

Two distinct time travel modes built on top of checkpoints:

- **Replay** — re-execute from a prior checkpoint. Same inputs, same graph. Use for debugging or retrying after a failure.
- **Fork** — branch from a prior checkpoint with *modified* state. Creates an alternative execution path without affecting the original thread. Use for "what if" exploration and test harnesses.

```python
# List all checkpoints for a thread
checkpoints = list(graph.get_state_history(config))

# Replay from checkpoint 2
graph.invoke(None, checkpoints[2].config)

# Fork with modified state
graph.update_state(checkpoints[2].config, {"messages": [HumanMessage("Try differently")]})
graph.invoke(None, checkpoints[2].config)
```

## HITL: Static Breakpoints vs Dynamic `interrupt()`

Two mechanisms — choose based on where in execution you need to pause:

**Static breakpoints** (compile-time, fires at node boundaries):
```python
graph.compile(
    interrupt_before=["tool_executor"],  # pause before any tool execution
    interrupt_after=["planner"],          # pause after plan is generated
    checkpointer=checkpointer,
)
```

**Dynamic `interrupt()`** (runtime, fires inside a node mid-execution):
```python
from langgraph.types import interrupt

def review_node(state: AgentState) -> AgentState:
    draft = generate_draft(state)
    approved = interrupt({"draft": draft, "prompt": "Approve?"})  # suspends here
    if not approved:
        return {"messages": [HumanMessage("Revise: ...")]}
    return {"output": draft}
```

Use static for predictable pause points (before/after known nodes). Use dynamic when the pause decision depends on runtime state computed inside the node.

See [[HITL Annotation Pipeline]] for the broader annotation workflow pattern.

## HITL: Idempotency Before interrupt()

When a graph resumes, the node restarts from the **beginning** — all code before `interrupt()` re-runs. In subgraphs, both parent and subgraph node re-execute.

**Safe before interrupt():** upsert operations, check-before-create patterns.
**Unsafe before interrupt():** inserts, list appends — these create duplicates on each resume.

Always place non-idempotent side effects **after** `interrupt()`, or extract them to a separate node that runs before the interrupt node.

## HITL: Validation Loop

`interrupt()` can be used inside a loop to re-prompt until input is valid:

```python
def get_age_node(state):
    prompt = "What is your age?"
    while True:
        answer = interrupt(prompt)
        if isinstance(answer, int) and answer > 0:
            break
        prompt = f"'{answer}' is not valid. Please enter a positive number."
    return {"age": answer}
```

## HITL: Multiple Parallel Interrupts

When parallel branches each call `interrupt()`, resume all with a single `Command` mapping interrupt IDs to values:

```python
result = graph.invoke({"vals": []}, config)
resume_map = {i.id: f"answer for {i.value}" for i in result["__interrupt__"]}
result = graph.invoke(Command(resume=resume_map), config)
```

## HITL: Command(resume) Warning

`Command(resume=...)` is the **only** Command pattern intended as `invoke()` input. Do NOT pass `Command(update=...)` as invoke input — the graph appears stuck (resumes from latest checkpoint but the update is not applied as expected).

## Error Handling Strategy

Match error type to the right handler:

| Error Type | Who Fixes | Strategy |
|---|---|---|
| Transient (network, rate limits) | System | `RetryPolicy(max_attempts=3)` on `add_node` |
| LLM-recoverable (tool failures) | LLM | `ToolNode(tools, handle_tool_errors=True)` |
| User-fixable (missing info) | Human | `interrupt({"message": ...})` |
| Unexpected | Developer | Let bubble up — `raise` |

```python
from langgraph.types import RetryPolicy
from langgraph.prebuilt import ToolNode

workflow.add_node(
    "search",
    search_node,
    retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0)
)

tool_node = ToolNode(tools, handle_tool_errors=True)
workflow.add_node("tools", tool_node)
```

## Custom Stream Writer

Emit progress updates from inside a node:

```python
from langgraph.config import get_stream_writer

def my_node(state):
    writer = get_stream_writer()
    writer("Processing step 1...")
    # do work
    writer("Complete!")
    return {"result": "done"}

for chunk in graph.stream({"data": "test"}, stream_mode="custom"):
    print(chunk)
```

## Command + Static Edge Warning

`Command(goto="node_c")` adds a **dynamic** edge only. If you also have `graph.add_edge("node_a", "node_b")`, **both** `node_b` and `node_c` will run. Only use `Command` routing when the node has no static outgoing edges.

## Agents as state machines, and supervisor, hierarchical and swarm builds (Definitive Guide ch. 1-2)

A book on LangGraph agents maps agent control onto finite state machines: states, events, guard checks that choose a transition, and a checkpoint at each node for crash recovery. A hierarchical state machine puts shared policy (rate limits, safety filters, circuit breakers) on a parent state so its child states inherit it, which LangGraph subgraphs express. Guards are meant to stay plain deterministic code so they remain auditable. The author also recommends a step cap on tool loops with a closing instruction, so a final answer exists when the cap is hit, and a checkpointer with thread ids for per-thread state.

Chapter 2 compares supervisor (suits small teams, but with one coordinator that can bottleneck and fail the whole team), hierarchical (supervisors of supervisors) and swarm (peers hand off control; the handoff tool passes the full message history unless filtered). It advises keeping side effects out of the node that calls the interrupt, since the node re-runs on resume.

**Limits of this source:** an early-release draft with single demo runs. The hierarchical team wrote a white paper in about two minutes and the swarm answered in about 30 seconds (both self-reported single runs with no stated model settings or repeats). The chapter says agents cannot redesign their own control graph. Its weather tool-trace example looks inconsistent in printed output.

## Cognitive architectures, the agent loop, reflection and multi-agent (Learning LangChain, ch. 5-8)

**Agency against reliability.** Oshin and Campos use "cognitive architecture" for the recipe of steps an LLM application follows, and rank autonomy by what the LLM decides: the output of a step, which step comes next, or which steps exist. Their running example is an email assistant that can archive, reply or flag for review, and they advise writing down the application's constraints before choosing. The chapter defines architecture 0 (plain code), a single LLM call, a chain (several LLM calls in a set order; some authors call this flow engineering) and a router (an LLM chooses among predefined steps). Examples are `StateGraph`s. Separate `input` and `output` schemas govern what a caller sends and gets back, though internal keys still appear in `stream()` output, and a conditional edge turns the router's choice into the next node. In their text-to-SQL chain, generating SQL runs at temperature 0.1 and explaining it at 0.7. The router's label is free text from the LLM, so the `Literal` type hint is not checked at run time.

**The agent loop (ch. 6).** The agent is a plan/execute loop run by the LLM, which also decides when to stop, through a conditional edge. In LangGraph, `ToolNode` executes the tool calls found in the latest AI message and answers each with a `ToolMessage`, so a tool exception reaches the LLM as a message; `tools_condition` sends the graph to the tools node if the latest message has tool calls and ends it otherwise. Two extensions: when a tool should run first every time, add a node that produces that tool call itself, which saves an LLM call and keeps the model from skipping it; and when there are many tools, embed their descriptions and retrieve a subset per query (see [[Dynamic Tool Discovery]]). The book asserts that planning quality starts to suffer beyond about 10 tools and notes that preselection adds latency, so it should wait until performance drops. In its one-query example the model computed 1933 - 1872 and answered 61, while the search result said 60.

**Reflection (ch. 7).** Two nodes alternate, one writing and one revising, and the reflect node swaps message roles so the critic thinks it is grading a user's essay. The example ends when the message list passes 6 (three rounds of two messages), finishing on the generate step so the last revision lands; the reflect step could instead decide when to stop. The authors say reflection can sometimes help and strongly recommend grounding the critique outside the model, such as running code through a linter or compiler before reflecting. Appended to an agent, it adds latency.

**Subgraphs and multi-agent (ch. 7).** A subgraph that shares state keys with its parent can be added as a node directly; if the schemas differ, wrap it in a function. The book lists four multi-agent shapes: network (any agent may call any other), supervisor (one agent picks who runs next; a special case makes the supervisor an LLM call with tools), hierarchical (supervisors of supervisors) and custom (each agent talks to a subset, with parts of the flow fixed). Its supervisor example is gpt-4o (temperature 0) returning structured output with three possible choices, and sub-agents need distinct, self-explanatory names or descriptions in the supervisor prompt. The authors caution against reaching for these first; begin with the ch. 6 agent.

**Four controls on the frontier (ch. 8).** Chains trade agency for reliability and agents do the reverse; the chapter lists four techniques to push the frontier outward:

- *Structured output:* low temperature, a description on every schema field (the LLM decides what goes where from name plus description), and tool calling or JSON mode in preference to prompting alone, which only suggests a format.
- *Intermediate output:* send node-by-node updates to the client (`stream_mode` set to `updates`, `values` or `debug`) so waiting through several steps is tolerable.
- *Human-in-the-loop:* every mode needs a checkpointer and a `thread_id` (UUIDs; a fresh id drops the state). *Authorize* puts `interrupt_before` on the tools node. *Interrupt* lets the user halt streaming, with state kept at the last finished step. From a pause you can resume (send `None`), start over with new input, change state with `update_state`, or fork by replaying `get_state_history`. If you keep partial state after an interrupt, tidy up unanswered tool-call messages, or the run may stall.
- *Double texting:* a second message arriving mid-run; see [[LangGraph Platform Data Model and Double-Texting]].

## Limits

- Ch. 5-8 of Learning LangChain report no experiments. Claims about reflection, multi-agent designs and the frontier are unquantified, and the demos are single runs (one essay, one date question).
- The ch. 7 supervisor code is partial: the researcher and coder workers are placeholders, the Python `AgentState` declares only `next` although nodes return messages, and the conditional edge never maps `FINISH` to `END` (the JavaScript version does).
- Ch. 6's calculator tool uses `ast.literal_eval`, which handles literals, not arithmetic. Figure 5-1 also lists architectures 4 (state machine) and 5 (autonomous), which the text postpones.
- The code is 2025-era LangGraph and LangChain and may have changed.

## See Also
- [[LangGraph CRAG Pipeline]]
- [[LangGraph State Reducers]]
- [[Agent Memory Types]]
- [[Plan and Execute Pattern]]
- [[ADK Context Engineering]]
- [[A2A Agent Protocol]]
- [[HITL Annotation Pipeline]]
- [[Framework Selection — LangChain vs LangGraph vs Deep Agents]]
- [[Deep Agents Framework]]
- [[Voice Agent Patterns]]
- [[LangChain Fundamentals — create_agent, Tools, Structured Output]]
- [[LangChain Agent Middleware]]
- [[Graph Topology Primitives]] — extends (node kinds, `Command`, back-edge bounds, gate placement)
- [[LangGraph Platform Data Model and Double-Texting]] — extends (hosted runtime and the double-texting strategies)
