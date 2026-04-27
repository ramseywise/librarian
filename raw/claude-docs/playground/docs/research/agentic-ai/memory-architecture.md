# Memory Architecture for VA Agents

**Sources:** langgraph_Yan.pptx, langgraph_extended.pptx, adk-agent-samples-main (playground VA implementations), librarian wiki (copilot-learning-loop.md)

---

## Three-Tier Memory Taxonomy (Cognitive Science Model)

Agents need three distinct memory types with different storage and retrieval patterns. Do not collapse these into a single "memory store."

| Tier | What it stores | Storage shape | Retrieval pattern | Update pattern |
|------|---------------|---------------|-------------------|----------------|
| **Semantic** | Facts, knowledge, entities | Profile (single JSON doc, evolving) or Collection (vector index) | Key lookup or semantic search | Upsert on new fact |
| **Episodic** | Past task records, conversation history, few-shot examples | Append-only log or vector index | Semantic search by similarity | Append only |
| **Procedural** | Rules, system prompt, tone, persona | Updatable prompt template | Direct load at session start | Rewrite on feedback |

### Semantic Memory — Two Sub-modes

**Profile mode** (single evolving document):
```python
# LangGraph Store — one record per user
store.put(("users", user_id), "profile", {
    "language": "da",
    "payment_method": "invoice",
    "preferred_contact": "email",
    "last_updated": "2026-04-26"
})
profile = store.get(("users", user_id), "profile").value
```

**Collection mode** (vector-indexed facts):
- Use when facts are too numerous or heterogeneous for a single JSON doc
- Each fact is a separate document; retrieval is semantic search
- LangGraph `Store` is key-value only — for vector search, use an external store (Chroma, pgvector, Pinecone) and reference IDs from `Store`

### Episodic Memory — Few-Shot Injection

Past task records become in-context examples:
```python
# Retrieve 3 most similar past tasks for few-shot context
similar_episodes = vector_store.similarity_search(
    query=current_task,
    k=3,
    filter={"user_id": user_id}
)
few_shot_context = format_as_examples(similar_episodes)
# Prepend to system prompt or inject into context window
```

### Procedural Memory — Self-Updating System Prompts

Agents can rewrite their own instructions based on feedback (reflection pattern — see below). Stored as a versioned prompt template:
```python
store.put(("agents", agent_id), "system_prompt", {
    "version": 7,
    "content": "You are a billing assistant for...",
    "updated_at": "2026-04-26",
    "updated_reason": "User corrected VAT calculation tone"
})
```

---

## SQLite Preference + Session Store (Lightweight Implementation)

For local dev and small deployments, a single SQLite table covers semantic (profile) and episodic (session summaries) memory:

```python
# schema
CREATE TABLE preference_store (
    user_id TEXT NOT NULL,
    key     TEXT NOT NULL,          -- "pref:language", "session:2026-04-26"
    value   TEXT NOT NULL,          -- JSON
    updated_at TEXT NOT NULL,
    PRIMARY KEY (user_id, key)
);
```

**Key namespacing convention:**
- `pref:*` — user preferences (semantic/profile tier)
- `session:YYYY-MM-DD` — session summaries (episodic tier)
- `proc:system_prompt` — current instruction version (procedural tier)

```python
import aiosqlite, json
from datetime import date

async def get_pref(db, user_id: str, key: str) -> dict | None:
    async with db.execute(
        "SELECT value FROM preference_store WHERE user_id=? AND key=?",
        (user_id, key)
    ) as cur:
        row = await cur.fetchone()
        return json.loads(row[0]) if row else None

async def set_pref(db, user_id: str, key: str, value: dict):
    await db.execute(
        "INSERT OR REPLACE INTO preference_store VALUES (?,?,?,?)",
        (user_id, key, json.dumps(value), date.today().isoformat())
    )
    await db.commit()
```

**Production upgrade path:** swap SQLite for Postgres without changing calling code — same async interface, just swap the connection.

---

## Context Window Management Strategies

Long-running VA conversations hit context limits. Three strategies, in order of complexity:

### 1. Message Trimming (fast, lossy)
Keep only the last N messages. Loses early context but is instant.
```python
def trim_messages(messages: list, max_messages: int = 20) -> list:
    if len(messages) <= max_messages:
        return messages
    # Always keep system message + last N-1 messages
    return [messages[0]] + messages[-(max_messages-1):]
```

### 2. LLM Summarization (slower, lossless for key facts)
Compress older messages into a summary before they fall out of window.
```python
async def summarize_and_compress(messages: list, llm, threshold: int = 15) -> list:
    if len(messages) < threshold:
        return messages
    to_compress = messages[1:-5]  # keep system + last 5
    summary = await llm.ainvoke(
        f"Summarize this conversation concisely, preserving all decisions and facts:\n{format_messages(to_compress)}"
    )
    return [messages[0], HumanMessage(content=f"[Earlier context]: {summary.content}")] + messages[-5:]
```

### 3. Selective Retention (agent-driven, most precise)
Agent explicitly decides what facts to carry forward and drops the rest.
- Agent writes key facts to episodic store mid-conversation
- History is discarded; facts are retrieved on demand
- Best for very long tasks (multi-hour sessions, multi-day workflows)

**Decision guide:**
- Single-session Q&A → trimming is fine
- Multi-turn task execution → summarization
- Multi-day or complex workflows → selective retention + episodic store

---

## Reflection Pattern (Self-Improving Agents)

Agents can improve their own procedural memory based on user feedback signals.

### Two Implementation Modes

**Hot-path reflection** (immediate, adds latency):
```
User message → Agent response → Reflection node → Update system prompt → Next turn
```
- Runs synchronously before the next response
- User sees improved behavior immediately
- Adds ~1-2s latency per corrected turn

**Background reflection** (async, no latency impact):
```
User message → Agent response → [background task: Reflection node → Update system prompt]
```
- Reflection runs after response is delivered
- System prompt update available for next session
- Preferred for production — no latency impact on current turn

### Reflection Trigger Signals
- User explicitly corrects the agent ("no, I meant...")
- User overrides an agent action
- Low confidence score on agent's output
- User rates response negatively

### Implementation Pattern
```python
async def reflection_node(state: AgentState) -> dict:
    if not should_reflect(state):  # check correction signals
        return {}
    
    current_prompt = await store.get(("agents", "billing"), "system_prompt")
    
    updated = await llm.ainvoke(
        f"Given this correction from the user: {state['last_correction']}\n"
        f"Update this system prompt to prevent the same mistake:\n{current_prompt.value['content']}"
    )
    
    await store.put(("agents", "billing"), "system_prompt", {
        "version": current_prompt.value["version"] + 1,
        "content": updated.content,
        "updated_at": date.today().isoformat(),
        "updated_reason": state["last_correction"][:100]
    })
    return {"reflection_applied": True}
```

---

## Memory Loading Pattern at Turn Start

Load all three memory tiers at the start of each turn before routing:

```python
async def load_memory_node(state: AgentState, store: BaseStore) -> dict:
    user_id = state["user_id"]
    
    # Semantic — user preferences
    prefs = await store.aget(("users", user_id), "profile")
    
    # Episodic — recent session summary
    today = date.today().isoformat()
    session = await store.aget(("users", user_id), f"session:{today}")
    
    # Procedural — current system prompt version
    system = await store.aget(("agents", "billing"), "system_prompt")
    
    return {
        "user_prefs": prefs.value if prefs else {},
        "session_context": session.value if session else {},
        "system_prompt": system.value["content"] if system else DEFAULT_PROMPT,
    }
```

---

## See Also
- [hitl-and-interrupts.md](hitl-and-interrupts.md) — HITL gates that trigger reflection
- [self-learning-agents.md](self-learning-agents.md) — DPO and training-time vs inference-time improvement
- [orchestration-patterns.md](orchestration-patterns.md) — how memory integrates with supervisor routing
- librarian wiki: `Copilot Learning Loop` — operational wrapper around these patterns
