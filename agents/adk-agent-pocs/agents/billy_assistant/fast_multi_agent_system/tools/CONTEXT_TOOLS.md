# context_tools.py

Three tools that every agent in this system uses to communicate and coordinate.
They handle shared context, clarifying questions, and re-routing — all without
breaking Gemini's prefix cache.

---

## The three tools at a glance

| Tool                         | What it does                                                              |
|------------------------------|---------------------------------------------------------------------------|
| `get_conversation_context()` | Read what previous agents have found out                                  |
| `signal_follow_up()`         | Tell the router "I asked a question — send the reply back to me"          |
| `request_reroute(reason)`    | Tell the router "I'm the wrong agent for this — hand off to someone else" |

---

## `get_conversation_context()`

### What it returns

```python
{
    "conversation_log": [
        {"turn": 1, "agent": "invoice_agent", "request": "...", "outcome": "..."},
        {"turn": 2, "agent": "support_agent", "request": "...", "outcome": "..."},
    ],
    "facts": {
        "invoice_id": "456",
        "status": "draft",
        "missing_fields": ["vat_rate"],
    },
    "open_questions": [],
    "task_note": "..."   # only present when the router has a specific directive
}
```

- **`conversation_log`** — a compact record of every previous turn: which agent ran,
  what the user asked, and what was found. Truncated to 120/200 chars per entry.
- **`facts`** — normalised data accumulated across turns. If `invoice_agent` already
  fetched invoice 456, the facts will be here — no need to fetch it again.
- **`open_questions`** — questions that were asked but not yet answered.
- **`task_note`** — optional directive from the router (e.g. after an escalation).

### How to use it

Call it at the **start** of your agent's turn, before doing anything else:

```python
# In your agent's system prompt:
# "Call get_conversation_context() first. Read the returned conversation_log
#  and facts to understand what prior agents have established.
#  Do not repeat work that is already in the log."
```

This tells the agent to check what's already known before calling any domain tools.
If invoice 456 is already in `facts`, there's no reason to call `get_invoice_details`
again.

---

## `signal_follow_up()`

Call this when your agent's response ends with a question to the user, not a final answer.

```python
# The agent calls this tool, then asks its question in the response text.
# The router sees the signal and remembers which agent is waiting.
# When the user replies ("456", "yes", "draft"), the router sends them
# straight back to the same agent — no need for the user to repeat context.
```

**What it does internally:** writes the current agent's name to `public:follow_up_agent`
in session state. The root agent reads this at the start of the next turn.

**When NOT to call it:** if you've already produced a complete answer. Only call it
when you genuinely need more information before you can proceed.

---

## `request_reroute(reason)`

Call this when you realise you're the wrong agent for the request.

```python
# agent prompt says:
# "If the request clearly requires UI guidance, call request_reroute('support domain')
#  immediately and stop. Do not attempt a partial answer first."
```

The `reason` string must match one of the reroute reason constants defined in `state.py`:

| Reason string      | Routes to            |
|--------------------|----------------------|
| `"invoice domain"` | `invoice_agent`      |
| `"support domain"` | `support_agent`      |
| `"multi-domain"`   | `orchestrator_agent` |

**What it does internally:** writes `{"reason": "..."}` to `public:routing_escalation`.
The root agent checks this after every agent run and escalates accordingly.

**Important:** call this *before* generating any response text. If you write a partial
answer first and then reroute, the next agent starts from a confused state.

---

## Why these tools don't break Gemini's prefix cache

This is the main reason these tools exist in the first place. Here's the problem
they solve, explained step by step.

### What is prefix caching?

Gemini can cache the "prefix" of a request — the part that doesn't change between
calls. If the cache is warm, those tokens are not re-processed, which means:

- **Faster responses** — the model skips re-reading the static prefix
- **Lower cost** — cached tokens are charged at a fraction of the normal rate

The cache is keyed on a fingerprint of:

```
system_instruction + tools + first N conversation turns
```

If the fingerprint matches, you get a cache hit. If it changes, you get a miss and
pay full price.

### The problem with putting dynamic data in the system instruction

The most obvious way to give an agent context is to bake it into the system
instruction:

```python
# TEMPTING — but this breaks caching
Agent(
    instruction=f"Previous findings: {session.state['public:facts']}",
    ...
)
```

Every time `public:facts` changes (which is every turn), the instruction string
changes, the fingerprint changes, and the cache misses. You lose caching entirely.

The same problem applies to ADK's template injection syntax:

```python
# Also breaks caching — {public:facts} changes every turn
instruction="Context: {public:facts}"
```

Even if `public:facts` were a valid injection key (it isn't — `public:` is not a
recognized ADK prefix), injecting dynamic values into the instruction kills the cache.

### Why tools are safe

Tools run *after* the cache lookup, not before it. Here's the exact sequence:

```
┌─────────────────────────────────────────────┐
│  1. system_instruction  ──┐                 │
│  2. tools list            ├─ fingerprint    │
│  3. conversation history ─┘ → cache lookup  │ ← CACHE DECISION MADE HERE
│                                             │
│  4. new user message appended to contents   │
│  5. model starts generating                 │
│  6. model calls get_conversation_context()  │ ← TOOL RUNS HERE
│  7. tool reads session.state and returns    │
│  8. model sees result, continues            │
│  9. model writes final text response        │ ← "Agent responds"
└─────────────────────────────────────────────┘
```

**What "conversation history" at step ③ actually contains:**
only the completed *previous* turns — `user` text messages and `model` text responses
that ADK has already committed. It is the stable beginning of the conversation used
to build the cached prefix.

**What the tool call adds** (steps ⑥–⑦): the `tool_use` request and `tool_result`
response are appended to the Gemini `contents` array as part of the *current* turn,
after the cache lookup. They do not affect the fingerprint for this turn.

**What "Agent responds" adds** (step ⑨): the model's final text response joins the
`contents` array. In *future* turns this becomes part of the conversation history at
step ③ — along with the tool call and its result from this turn. This is normal and
expected: the cached prefix is a stable window at the start of the conversation. New
turns accumulate in the uncached tail. ADK refreshes the cache periodically
(`cache_intervals=20`) to absorb more history into the prefix, but the stable part
never changes, so there is no repeated fingerprint churn.

By the time `get_conversation_context()` executes and returns the conversation log
and facts, the cache decision is already made. It doesn't matter what the tool
returns — the fingerprint is locked.

### The rule in one sentence

> Anything that must stay constant goes in the **system instruction**.
> Anything that changes every turn is fetched by a **tool at runtime**.

```python
# CORRECT — static instruction, dynamic context via tool
Agent(
    instruction=(Path("prompts/invoice_agent.txt").read_text()),  # never changes
    tools=[get_conversation_context, get_invoice_details, ...],
)

# The agent's prompt tells it:
# "Call get_conversation_context() first to read prior context."
```

The system instruction is loaded from a file once at import time and never changes.
The dynamic parts — conversation log, accumulated facts, task notes — are fetched
fresh each turn via `get_conversation_context()`, after the cache has already decided
to hit.

### What this looks like in practice

Turn 1 — user asks about invoice 456:
- Cache miss (first call, nothing cached yet)
- Agent calls `get_conversation_context()` → returns empty log, empty facts
- Agent calls `get_invoice_details("456")` → facts written to session state
- Agent responds

Turn 2 — user asks how to fix the missing VAT:
- **Cache hit** — system instruction and tools haven't changed
- Agent calls `get_conversation_context()` → returns turn 1 log + invoice facts
- Agent knows invoice 456 is missing VAT from `facts` — no need to re-fetch
- Agent calls `get_support_steps("missing_vat")` and responds

The cache hit on turn 2 (and every subsequent turn) means the model skips
re-processing the entire static prefix — which is typically the largest part of
the request.

---

## Is this a solid optimization pattern?

Yes — but it solves a specific problem, not every problem. It's worth understanding
exactly what it buys and where it doesn't help.

### What it actually saves

#### 1. Prefix cache hits on every turn

Without this pattern, the natural alternative is to inject dynamic context into the
system instruction. That breaks caching entirely. On a 2 000-token system prompt, a
cache miss costs roughly 5–8× more than a hit. Across a multi-turn session with
several agents, the savings compound quickly.

#### 2. Redundant domain tool calls

Facts written to `public:facts` by one agent are available to all subsequent agents.
If `invoice_agent` fetched invoice 456 in turn 1, `support_agent` in turn 2 reads
those facts from state instead of calling `get_invoice_details` again — saving a
tool round-trip and the LLM reasoning step that follows.

### When it isn't the right pattern

If your agents are stateless (each request is independent with no session), or your
facts don't accumulate across turns, the benefit disappears. You'd be adding a tool
call for no gain. This pattern is specifically valuable in **multi-turn, multi-agent
sessions** where agents hand off work to each other.

---

## Does it add an extra LLM call?

Not an extra *agent invocation*, but yes — one extra **API round-trip within the same
agent turn**. Here is what actually happens inside a single `agent.run_async()` call:

```text
agent.run_async() ─────────────────────────────────────────────
                                                               │
  API request #1 ──► Gemini                                    │
    model sees: system instruction + tools + user message      │
    model responds: tool_use → get_conversation_context()      │
                                                               │
  Tool executes (Python, reads session.state — microseconds)   │
                                                               │
  API request #2 ──► Gemini   ← extra round-trip              │
    model sees: previous + tool result (log + facts)           │
    model responds: final answer                               │
                                                               │
agent.run_async() returns ─────────────────────────────────────
```

The LLM call budget table in the README counts agent invocations, not API requests.
That is why a direct path still shows "1 LLM call" even though the agent makes two
API requests internally.

### Why the extra round-trip is worth it

| Extra cost                                  | What it buys back                                                                       |
|---------------------------------------------|-----------------------------------------------------------------------------------------|
| +1 API round-trip (~100–300 ms)             | Prefix cache hit — skips re-processing the entire static system prompt                  |
| Tool result adds ~200 tokens to context     | No redundant `get_invoice_details` call in turn 2+ (saves tool latency + LLM reasoning) |
| Prompt must instruct agent to call it first | Helper agents with `include_contents='none'` skip full history entirely                 |

The prefix re-processing cost on a cache miss is consistently larger than the
round-trip cost of this tool call. The net effect across a session is faster
responses and lower cost, not slower.

### The one real weakness

There is no enforcement. The tool only helps if the agent actually calls it.
It is a prompt instruction — if the model skips it (prompt drift, distraction from
a complex request), the cache still hits but fact-reuse doesn't happen and the agent
runs blind. In production, monitor tool call sequences in traces to catch agents
that routinely skip the call.

---

## Common mistakes

**Calling domain tools before `get_conversation_context()`**

```python
# Agent prompt says this — follow it
"Call get_conversation_context() FIRST. Do not call other tools before reading context."
```

If the agent fetches invoice 456 again when the facts are already in state, you
pay for a redundant tool call and a redundant LLM reasoning step.

**Calling `signal_follow_up()` on a completed answer**

Only call it when the response genuinely ends with a question. Calling it when
you've already answered just causes the next user message to be routed back to you
unnecessarily.

**Calling `request_reroute()` after writing part of an answer**

```python
# Wrong order:
# 1. "I can see invoice 456 has a missing VAT rate..."  ← partial answer written
# 2. request_reroute("support domain")                  ← too late

# Correct order:
# 1. request_reroute("support domain")                  ← before any text
# 2. (stop — return immediately)
```

The escalated agent starts from session state, not from the previous agent's
partial text. Partial answers left in the response create confusion.

**Trying to inject `public:` keys into the instruction template**

```python
# Does NOT work — public: is not a recognized ADK injection prefix
instruction="Context: {public:conversation_log}"  # left as literal text
```

Use `get_conversation_context()` instead.
