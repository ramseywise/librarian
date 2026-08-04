---
title: Memory Architecture for VA Agents
tags: [memory, langgraph, adk, pattern, concept]
summary: Three-tier cognitive memory model (semantic/episodic/procedural), SQLite implementation pattern, context window management strategies, and self-improving reflection pattern for VA agents.
updated: 2026-07-05
sources:
  - raw/claude-docs/playground/docs/research/agentic-ai/memory-architecture.md
---

# Memory Architecture for VA Agents

## Three-Tier Memory Model

Mirrors cognitive science: semantic (what you know), episodic (what you experienced), procedural (how you behave).

| Tier | What it stores | Storage shape | Retrieval | Update trigger |
|---|---|---|---|---|
| **Semantic** | Facts, user preferences, entity profiles | Profile (single JSON) or Collection (vector index) | Key lookup or semantic search | Explicit correction or new information |
| **Episodic** | Past task records, conversation history, examples | Append-only log or vector index | Semantic search by query | Every completed task |
| **Procedural** | Rules, system prompt, tone, persona | Updatable prompt template | Direct load at session start | Reflection / deliberate policy update |

**Loading pattern:** at every turn start, load all three tiers before the first LLM call.

```python
def memory_load_node(state: AgentState) -> dict:
    user_id = state["user_id"]
    thread_id = state["thread_id"]

    # Semantic: user preferences profile
    prefs = store.get(namespace=("pref", user_id), key="profile")

    # Episodic: recent session summary
    session_summary = store.get(namespace=("session", thread_id), key="summary")

    # Procedural: current system prompt version
    proc = store.get(namespace=("proc", "global"), key="system_prompt_v")

    system_msg = build_system_message(prefs, session_summary, proc)
    return {"messages": [SystemMessage(content=system_msg)] + state["messages"]}
```

## SQLite Store Pattern

Lightweight implementation without requiring Redis or Postgres in dev:

```python
# Key namespacing convention
"pref:{user_id}"      # semantic preferences
"session:{thread_id}" # episodic session
"proc:{version}"      # procedural prompt

# Schema
CREATE TABLE preference_store (
    namespace TEXT NOT NULL,
    key       TEXT NOT NULL,
    value     TEXT NOT NULL,   -- JSON
    updated   TEXT NOT NULL,
    PRIMARY KEY (namespace, key)
);
```

Swap to Postgres in production by changing the `store` backend behind the same interface.

## Context Window Management

Three strategies — choose based on latency tolerance and memory requirements:

| Strategy | How | Tradeoff |
|---|---|---|
| **Message trimming** | Keep last N messages only | Fast, lossy — loses facts from earlier in conversation |
| **LLM summarization** | Haiku compresses older turns into a summary message | ~200ms overhead, preserves key facts |
| **Selective retention** | Agent explicitly marks messages to retain | Most precise, requires agent decision |

**Default:** summarization triggers at 8 messages, keeps last 4 verbatim, compresses earlier turns.

```python
SUMMARIZE_THRESHOLD = 8
KEEP_LAST_N = 4

def trim_history_node(state: AgentState) -> dict:
    msgs = state["messages"]
    if len(msgs) < SUMMARIZE_THRESHOLD:
        return {}
    to_summarize = msgs[:-KEEP_LAST_N]
    recent = msgs[-KEEP_LAST_N:]
    summary = haiku.invoke(f"Summarize this conversation: {to_summarize}")
    return {"messages": [SystemMessage(content=f"Summary: {summary.content}")] + recent}
```

See also [[Summarization Node]].

## Reflection Pattern (Self-Improving Agents)

Two modes for updating procedural memory from feedback signals:

| Mode | When | Latency impact |
|---|---|---|
| **Hot-path** | Immediately after each turn | +200–500ms per turn |
| **Background** | Async after response is sent | Zero latency impact |

**Trigger signals** (when to fire reflection):
- Explicit user correction: "That's wrong, it should be..."
- Override: user immediately undoes agent action
- Low confidence score from grader
- Negative rating signal

**Background reflection pattern:**

```python
async def background_reflect(response, user_feedback, store, user_id):
    if not should_reflect(response, user_feedback):
        return
    insight = await haiku.ainvoke(
        f"What should the agent do differently? Feedback: {user_feedback}\nResponse: {response}"
    )
    existing = store.get(("proc", user_id), "insights") or []
    store.put(("proc", user_id), "insights", existing + [insight.content])
```

## Cross-Agent Memory Sharing

For multi-agent systems: use `namespace` to scope memory correctly.

```python
# User-level: shared across all agents for this user
store.get(namespace=("user", user_id), key="preferences")

# Session-level: scoped to this conversation thread
store.get(namespace=("session", thread_id), key="context")

# Agent-level: only this sub-agent can access
store.get(namespace=("agent", agent_name, user_id), key="history")
```

## See Also
- [[Memory Lifecycle]] <!-- auto-linked -->
- [[Agent Memory Types]]
- [[Self-Learning Agents]]
- [[LangGraph BaseStore]]
- [[Summarization Node]]
- [[HistoryCondenser]]
