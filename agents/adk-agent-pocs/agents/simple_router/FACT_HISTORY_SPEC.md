# Fact History Visibility — Feature Spec

## Problem

The `[session facts: {...}]` message injected by `inject_facts_callback` contains
only the **current** value for each key. When a fact is updated (e.g. a second
invoice is loaded), the previous value is moved to `public:fact_history` but
never becomes visible to the LLM.

As a result, agents cannot answer questions about previously seen values:

> "What invoice number did I see before?"
> "What was the amount on the first invoice?"

Neither the router nor any expert has a tool to query history, so the gap is
total — the information exists in session state but is unreachable.

---

## Root Cause

The current design has one fundamental tension that drives all the complexity:

```text
prefix caching goal
  → strip tool responses from prior turns         (_history.py)
    → facts lost across turn boundaries
      → [session facts:] injection needed          (_facts_callbacks.py)
        → [session facts:] goes stale each turn
          → strip old [session facts:] each turn   (_history.py)
            → history never visible to agents
```

Everything is a consequence of that chain. The fix must stay within the
existing injection mechanism — not introduce new message types or callbacks.

---

## Design Constraints

- **No new tool calls.** Facts must remain passively visible via the existing
  injection mechanism. Adding a tool call to retrieve history would add latency
  and require prompt changes to every expert.
- **History is append-only.** Old facts are never deleted or overwritten. When a
  value changes, a new `HistoryEntry` is appended with `supersedes_fact_id`
  pointing to the previous entry. This is already enforced by `_persist_drafts`.
- **`supersedes_fact_id` lives in the history layer, not the session layer.**
  Session facts remain a simple current-value store (`draft` → `persisted`).
  Supersession is expressed only in `public:fact_history`.
- **Prefix caching must not regress.** The stable prefix — SI + tools + prior
  conversation history — must remain unchanged. Injected messages must only
  appear at the tail of the current turn.
- **No new message types.** Adding a second synthetic message type creates
  placement, stripping, and ordering complexity. The existing `[session facts:]`
  mechanism must be extended, not supplemented.

---

## Solution

Three changes, in order of impact:

### 1. Enrich `[session facts:]` with the previous value per key

Replace the flat `{key: value}` injection with a structured value that includes
`previous` when a fact has been superseded at least once.

**Current injection:**

```text
[session facts: {"invoice_id": "456", "vendor_name": "Acme", "amount": "1250.00"}]
```

**Proposed injection:**

```json
[session facts: {
  "invoice_id": {"value": "456", "previous": ["789", "123"]},
  "vendor_name": {"value": "Acme", "previous": []},
  "amount": {"value": "1250.00", "previous": []}
}]
```

Rules:

- Every fact uses the uniform structured form `{"value": ..., "previous": [...]}`.
- `value` is always the current value.
- `previous` is a list of all prior values for that key, oldest-first.
  It is an empty list `[]` for facts that have never been updated.
- The consistent shape means agents never branch on type — always
  use `facts["key"]["value"]` for the current value and
  `facts["key"]["previous"]` for history.
- No new message types, no stripping changes, no placement problems.

`_flat_facts` in `context_tools.py` is the only function that needs to change —
it builds the dict that becomes `[session facts:]`. It must read
`public:fact_history` to look up whether each key has a superseded entry.

### 2. Store the logical key in `HistoryEntry`

`HistoryEntry` currently stores only `description`, which means `get_latest_fact`
must match by `description.lower() == key.lower()` — fragile if descriptions
and keys diverge. Add `key` to the schema.

**Current `HistoryEntry`:**

```json
{
  "fact_id": "<uuid>",
  "supersedes_fact_id": "<uuid | null>",
  "description": "Human-readable label",
  "fact": "<value>"
}
```

**Proposed `HistoryEntry`:**

```json
{
  "fact_id": "<uuid>",
  "supersedes_fact_id": "<uuid | null>",
  "key": "invoice_id",
  "description": "Human-readable label",
  "fact": "<value>"
}
```

`_persist_drafts` writes each entry using the dict key from `session_facts` —
that key is already available at write time, just not stored. This is a one-line
change. `get_latest_fact` can then match by `entry.get("key") == key` instead
of description substring matching.

### 3. Extend `get_conversation_context` to include history for the router

The router calls `get_conversation_context` and receives `{"facts": flat}` —
current values only, no history. It cannot route "what did I see before?"
correctly without knowing that prior values exist.

**Current return value:**

```json
{"facts": {"invoice_id": "456", ...}, "follow_up_agent": null}
```

**Proposed return value:**

```json
{
  "facts": {"invoice_id": "456", ...},
  "fact_history": [{"key": "invoice_id", "fact": "123"}, ...],
  "follow_up_agent": null
}
```

`fact_history` contains only the superseded (non-current) entries, ordered
oldest-first — the same set that `_flat_facts` uses for the `previous` field.
The router does not need the full history chain, only awareness that prior
values exist.

### 4. Update `shared_rules.txt` to explain the enriched format

**Current rule:**

```text
- Context first: session facts are provided as a [session facts: {...}] message
  in this conversation immediately after your last response — do NOT call
  get_conversation_context. Start your action sequence directly with the first
  domain tool.
```

**Proposed:**

```text
- Context first: session facts are provided as a [session facts: {...}] message
  in this conversation immediately after your last response — do NOT call
  get_conversation_context. Start your action sequence directly with the first
  domain tool. Every fact has the form {"value": "current_value", "previous": [...]}
  where "value" is the current value and "previous" is a list of all prior values
  for that fact, oldest-first (empty list if never changed). Use
  facts["key"]["value"] for the current value and facts["key"]["previous"] for history.
```

---

## Data Flow (after this change)

```text
Turn 1 — user loads invoice 123:

  inject_facts_callback builds:
    [session facts: {"invoice_id": {"value": "123", "previous": []}, ...}]

Turn 2 — user loads invoice 456:

  _persist_drafts promotes invoice 123 fields to history with fact_ids
  inject_facts_callback detects superseded entries for invoice_id etc., builds:
    [session facts: {
      "invoice_id": {"value": "456", "previous": ["123"]},
      "vendor_name": {"value": "Bob Corp", "previous": ["Acme"]},
      ...
    }]

Turn 3 — user asks "what invoice did I see before?":

  Agent reads [session facts:] tail → invoice_id.previous = "123"
  Answers directly. No tool call.
```

---

## Acknowledged Gaps

**Helper agents do not see any injection.**
Helper agents (`invoice_agent_helper`, `support_agent_helper`) run with
`include_contents="none"` and have no `before_model_callback`. They never
receive `[session facts:]`. This is intentional — helpers are stateless
sub-tools that operate on a specific sub-task within a single orchestrator
turn and do not need session history.

---

## Files to Change

| File | Change |
| --- | --- |
| `tools/context_tools.py` | Extend `_flat_facts` to read `public:fact_history` and include `{"value": ..., "previous": ...}` for superseded keys. Update `get_conversation_context` to include `fact_history` in its return value (router only). Update `get_latest_fact` to match by `key` field instead of description. |
| `_facts_callbacks.py` | No logic changes — `_flat_facts` handles the enrichment. |
| `_history.py` | No changes. |
| `prompts/shared_rules.txt` | Extend the "Context first" rule to explain the `previous` field. |

State schema changes:

| Schema | Change |
| --- | --- |
| `HistoryEntry` | Add `key` field (written by `_persist_drafts` from the `session_facts` dict key). |

No changes to agent tool lists, callback chains, routing logic, or
`session_facts` schema.

---

## What Does Not Change

- `inject_facts_callback` injection point and stripping logic — unchanged.
- `strip_tool_history_callback` — no new prefixes to handle.
- `persist_facts_callback` and `_persist_drafts` supersession logic — unchanged
  except for adding `key` to the written `HistoryEntry`.
- `public:session_facts` schema (`FactEntry`) — unchanged.
- No new tools, no new tool calls, no new message types.

---

## Acceptance Criteria

1. When a fact is set for the first time, `[session facts:]` shows it as a plain
   string value — no `previous` field.
2. When a fact is updated, `[session facts:]` shows `{"value": "new", "previous": "old"}`
   for that key. Other unchanged keys remain plain strings.
3. An expert agent can answer "what invoice did I see before?" from `[session facts:]`
   alone — no tool call is made.
4. `get_conversation_context` returns `fact_history` containing superseded entries
   so the router has the same visibility.
5. `get_latest_fact` resolves by `key` field in history, not description matching.
6. All existing routing and response evals pass without regression.
