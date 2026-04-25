# Fact lifecycle design changes

## Why this change is needed

This document extends the current design described in `SPEC.md` and `README.md`.

The current implementation is too slow because each agent calls `get_conversation_context` to reconstruct facts and routing context before it can continue. This introduces an extra tool call and typically also an extra LLM-driven step per agent invocation. In multi-agent flows, these extra calls accumulate and create too much latency for the user.

The goal of this change is to reduce latency by making the required facts available directly in the LLM context via a `before_model_callback`, instead of requiring each expert agent to call `get_conversation_context` as a tool every turn.

### How facts will reach the LLM without a tool call

Facts stored in the session layer will be injected into the conversation history (`llm_request.contents`) by a `before_model_callback` on each expert agent, prepended to the current turn. The callback reads `public:session_facts` from session state and inserts a synthetic `get_conversation_context` function-call + function-response pair into the conversation history before each LLM call. This means:

- Experts no longer need to call `get_conversation_context` to see current facts
- The tool call and the extra LLM-driven step it causes are eliminated
- The system instruction stays fully static — prefix cache is not broken
- Any agent that receives control in the same turn sees the same facts block via its own callback invocation
- The router still calls `get_conversation_context` to consume `public:follow_up_agent` (see below)

The injected pair looks to the LLM exactly like a real `get_conversation_context` call it had already made:

```text
[static system instruction]           ← unchanged, still cacheable
[prior conversation turns, stripped]  ← as today (strip_tool_history_callback)
[turn N user message]                 ← boundary
[fn_call:  get_conversation_context]  ← injected by before_model_callback
[fn_resp:  {"facts": {...}}]          ← injected by before_model_callback
```

`strip_tool_history_callback` already preserves everything from the current-turn boundary onward, so the injected pair survives within the turn and is stripped on the next turn automatically — exactly like a real tool call.

### Changes to `get_conversation_context`

`get_conversation_context` is retained for the router. Expert agents no longer need to call it to get facts — the callback injection covers that. However, `get_conversation_context` remains the correct way for the router to consume (clear) `public:follow_up_agent`, preserving the existing follow-up routing contract.

The `routing_context` structured log event currently emitted by `get_conversation_context` is retained with an updated schema to reflect the new state key names:

```json
{
  "event": "routing_context",
  "agent": "<agent_name>",
  "invocation_id": "<inv_id>",
  "follow_up_agent": "<agent_name or null>",
  "session_fact_keys": ["invoice_id", "status"],
  "history_fact_count": 3,
  "ts": 1234567890.123
}
```

`facts_keys` is replaced by `session_fact_keys` and `history_fact_count`. Any Cloud Logging queries or dashboards targeting `facts_keys` must be updated when this change ships.

### `follow_up_agent` consumption for expert agents

Currently, expert agents clear `public:follow_up_agent` as a side effect of calling `get_conversation_context`. With experts no longer making that call, a dedicated `before_model_callback` on each expert agent must clear `public:follow_up_agent` at the start of the turn. This maintains the existing invariant: the signal is consumed exactly once per turn, regardless of which path ran.

The router's `follow_up_shortcut` callback already clears the signal when the router LLM is bypassed — that path is unchanged.

### Migration of existing fact-writing tools

All domain tools that currently write to `public:facts` directly must be migrated to call `set_fact` instead:

| Tool                  | Current write                      | New write                                                    |
|-----------------------|------------------------------------|--------------------------------------------------------------|
| `note_invoice_id`     | `public:facts["invoice_id"] = ...` | `set_fact(key="invoice_id", ...)`                            |
| `get_invoice_details` | merges dict into `public:facts`    | calls `set_fact` per field                                   |
| `validate_invoice`    | reads from `public:facts`          | reads from `public:session_facts` or calls `get_latest_fact` |

`public:facts` is removed. All reads and writes go through `public:session_facts` (session layer) and `public:fact_history` (history layer) accessed via the new tools.

### Migration of expert prompts

Because the facts injection callback delivers context automatically, expert agents must no longer be instructed to call `get_conversation_context` themselves. If the prompt still tells the agent to call it, the agent will call the real tool anyway, injecting a duplicate response into the turn and re-introducing the extra LLM round-trip this change is designed to eliminate.

Required prompt changes:

- `prompts/shared_rules.txt` line 2 — replace the "Context first: call get_conversation_context ONCE per invocation" rule with:
  `"Context first: session facts are already available in the conversation above — do NOT call get_conversation_context. Start your action sequence directly with the first domain tool."`
  Do not delete the rule entirely — a replacement keeps the LLM explicitly informed that facts are present and prevents it from attempting the tool call.
- `prompts/invoice_agent.txt` — remove step 1 (`get_conversation_context`) from every tool sequence (READ, VALIDATE, WRITE, MENTION) and remove the "CRITICAL: call get_conversation_context EXACTLY ONCE" block at the top.
- `prompts/support_agent.txt`, `prompts/orchestrator_agent.txt` — same: remove `get_conversation_context` from all tool sequences.
- `prompts/router_agent.txt` — no change. The router still calls `get_conversation_context` to consume `public:follow_up_agent`.
- `prompts/receptionist_agent.txt` — no change. The receptionist uses `include_contents="none"` and does not rely on facts.

After updating the prompts, `context.facts` references in the prompt sequences (e.g. `context.facts["invoice_id"]`) should be updated to `facts["invoice_id"]` to match the injected response format.

### Updated performance model

The performance table in `SPEC.md` counts agent-level calls and does not show the internal LLM round-trips within each agent. This change reduces those internal round-trips. `SPEC.md` must be updated to reflect the actual call counts:

| Path                        | LLM calls before                           | LLM calls after                        | Saved |
|-----------------------------|--------------------------------------------|----------------------------------------|-------|
| Static / follow-up shortcut | 2 (expert: ctx + respond)                  | 1 (expert: respond)                    | 1     |
| Single domain (normal)      | 4 (router: ctx+route, expert: ctx+respond) | 3 (router: ctx+route, expert: respond) | 1     |
| Multi-domain                | 8 (router: 2, orch: 2, 2×helper: 2)        | 5 (router: 2, orch: 1, 2×helper: 1)    | 3     |

The router's two internal calls (ctx + route decision) are unchanged because the router still calls `get_conversation_context` to consume `public:follow_up_agent`.

---

## Scope of the incremental change

We maintain facts in two layers, stored under these ADK session state keys:

| State key              | Layer   | Content                                                            |
|------------------------|---------|--------------------------------------------------------------------|
| `public:session_facts` | Session | Dict of `fact_key → {status, description, value}`                  |
| `public:fact_history`  | History | List of `{fact_id, supersedes_fact_id, description, fact}` entries |

1. **Session layer** (`public:session_facts`)
   - Holds newly discovered facts.
   - Each fact has:
     - status
     - description
     - fact value

2. **History layer** (`public:fact_history`)
   - Holds facts that should persist in compressed or durable conversation history.
   - Stores the full fact directly in the current version.

## Fact lifecycle

- New facts are created in the session layer with status `draft`.
- Facts should normally be inserted into history after the visible agent response is produced.
- An after-callback moves eligible facts into history once the response is complete.
- Facts may be inserted earlier only when they are required for same-turn orchestration or tool execution (see Early persistence below).
- When moved, the status is updated to `persisted`.
- If history is compressed, facts may later be re-added in compact form.
- Large facts are not externalized in the current version.

## Session layer

The session layer holds working facts discovered during the current interaction.

Each fact may include:

- **status**
- **description**
- **fact value**

Suggested statuses:

- `draft`
- `persisted`

A fact in the session layer is mutable while it is in `draft` state. If the fact changes before persistence, it is updated in place. Supersession applies to history entries, not session facts.

## History layer

The history layer stores facts that should remain available over time.

Each history entry may include:

- **description**
- **fact**
- **fact_id**
- **supersedes_fact_id**

In the current version, history stores the fact content directly and does not use `ref_fact`.
A future version may introduce `ref_fact` for cases where fact content is too large to store inline.

History should be append-only.
Existing history entries are not replaced in place.
If a persisted fact is later corrected, a new history entry should be appended and linked to the previous entry through `supersedes_fact_id`.

Supersession is therefore represented in the history layer, not as a separate session status.

## Callback behavior

### Facts injection callback (before-model, all expert agents)

A `before_model_callback` on each expert agent reads `public:session_facts` and prepends a synthetic `get_conversation_context` function-call + function-response pair to the current turn in `llm_request.contents`. This replaces the real `get_conversation_context` tool call for experts. The system instruction is not modified, so prefix caching is preserved.

The callback also consumes (clears) `public:follow_up_agent` so that experts do not see stale follow-up state from a prior turn.

**Double-injection guard.** The `before_model_callback` runs before every LLM call within an invocation, not just the first. On multi-step turns where an expert calls a domain tool and then gets a second LLM call to compose the response, the callback would run again. Without a guard it would inject a second facts pair, producing duplicate context. The callback must check whether a synthetic `get_conversation_context` pair is already present in `llm_request.contents` for the current turn and skip injection if so. This mirrors the `_CTX_LOADED_KEY` guard in the real `get_conversation_context` tool.

### After-callback (all expert agents)

An `after_agent_callback` is responsible for:

- identifying new facts that should be persisted
- inserting them into `public:fact_history`
- updating their status from `draft` to `persisted`

These status names are intended to reflect lifecycle state rather than storage location.

### Early persistence

Facts may be inserted into history before the after-callback when they are required for same-turn orchestration — for example, when the orchestrator's helper agents need a fact to be in history before they run in parallel.

To trigger early persistence, a tool or agent sets `"persist_now": true` on the session fact entry. The facts injection callback checks this flag and persists eligible facts immediately rather than waiting for the after-callback.

## Compression behavior

After history compression, facts can be added back into history when they are still important.

This allows:

- restoring important facts after summarization
- keeping history compact while preserving important durable facts

## Tools

In scope for this change:

- `set_fact`
  - Stores or updates a fact in the session layer (`public:session_facts`)
  - Can be called by the agent or by a tool agent
  - Replaces direct writes to `public:facts` in all existing domain tools
  - If a changed fact is later persisted, history should append a new entry rather than replace an old one

- `search_facts`
  - Searches facts in `session`, `history`, or `both`
  - Returns the most relevant matching facts for a query
  - History results should exclude superseded entries by default

- `get_latest_fact`
  - Retrieves the latest non-superseded version of a fact
  - Can resolve by `fact_id`, logical key, or other system-defined identifier

Not in scope for this change — see Future extensions below:

- `get_ref_fact`

## Retrieval rules

History is only useful if persisted facts can later be retrieved.

Default retrieval behavior should be:

- search history and return only the latest non-superseded entries
- hide older superseded entries unless explicitly requested for audit or debugging
- allow searching session facts, history facts, or both

This means the system, not the agent prompt, is responsible for resolving supersession chains and returning the current version by default.

## Failure handling

If persistence fails in the after-callback, the user may already have seen a response that assumes the fact was saved.

To handle this safely:

- persistence should be idempotent
- the system should retry failed persistence operations
- stranded `draft` facts should be checked at the start of the next turn and retried if they still meet persistence criteria
- the system should not assume a fact is in history until persistence succeeds

## Concurrency and conflict handling

In the current version, session writes should be serialized per conversation or session.

If multiple components attempt to update the same session fact in one turn, the system should use a simple deterministic rule such as last write wins within the session layer.

History persistence remains append-only and should not rewrite existing entries.

## Future extensions

### ref_fact

A future version may introduce `ref_fact` when fact content becomes too large to store directly in history.

A new tool `get_ref_fact` will resolve and retrieve a referenced fact when needed.

Suggested minimal metadata:

- `ref_id`
- `description`
- `kind`
- `storage_uri`
- `content_hash`
- `created_at`
- `created_by`
- `source`

Field purpose:

- `ref_id`: stable internal identifier used by `get_ref_fact`
- `description`: short human-readable summary of the referenced fact
- `kind`: type of referenced content, such as `json_blob`, `tool_result`, or `document_chunk`
- `storage_uri`: pointer to where the full content is stored
- `content_hash`: integrity and deduplication check
- `created_at`: timestamp for when the reference was created
- `created_by`: agent or tool that created the reference
- `source`: origin of the fact, such as `user_message`, `tool_output`, `retrieval`, or `system_derived`

## Rule for moving facts from session to history

A fact moves from session to history only if all of the following are true:

1. **The fact is stable enough**
   - It is no longer just a transient intermediate step or partial tool output.
   - The agent considers it usable beyond the current immediate reasoning step.

2. **The fact is response-relevant or future-useful**
   - It is needed to understand the assistant response, continue the conversation, or support later turns.

3. **The fact is sufficiently grounded**
   - It comes from the user, a trusted tool result, or a derived conclusion the system is willing to keep.
   - It is not just speculation.

4. **The turn has reached completion**
   - By default, persistence happens in the after-callback after the visible response is produced.

5. **The fact passes persistence filters**
   - It is not trivial, duplicate, obsolete, or purely ephemeral.

Practical decision rule — a fact should be persisted only if it is:

- stable
- grounded
- useful beyond the current step
- worth keeping across turns
- not already persisted in equivalent form

Examples of facts that should usually be persisted:

- user-provided constraints or preferences relevant to the conversation
- facts referenced in the visible answer
- important tool results needed for follow-up turns
- durable derived facts such as a resolved status, classification, or chosen plan
- corrections that supersede an older persisted fact

Examples of facts that should remain only in session:

- partial reasoning state
- temporary routing decisions
- incomplete extraction results
- low-confidence guesses
- raw intermediate tool payloads only needed within the current turn
- duplicate restatements of already persisted facts

## Implementation phases

### Phase 1 — disable static routing

Set `_STATIC_ROUTING_DEFAULT = "0"` in `callbacks.py` at the start of the implementation. This simplifies verification:

- Every turn goes through the router LLM, which calls `get_conversation_context` unconditionally
- All evalset `tool_uses` assertions for `get_conversation_context` are satisfied by the router's real call, regardless of which expert handles the request
- No evalset changes are needed to get the routing eval to pass in this phase

Re-enable static routing (`_STATIC_ROUTING_DEFAULT = "1"`) only after all three success criteria pass with it disabled.

### Phase 2 — re-enable static routing and update the evalset ⚠️ requires explicit approval before starting

When static routing is re-enabled, one routing eval case breaks: `static_route_howto_gate_over_invoice_vocab`. In that case the static route callback bypasses the router LLM entirely, so no real `get_conversation_context` call is made by anyone — the expert receives a synthetic injection only, which does not appear in `tool_uses`. The assertion must be updated:

In `eval/routing_evalset.json`, case `static_route_howto_gate_over_invoice_vocab`, change `tool_uses` from:

```json
[{ "name": "get_conversation_context", "args": {} }]
```

to:

```json
[]
```

The `intermediate_responses` assertion (routing to `support_agent`) is unchanged and remains the correctness check for this case.

After this evalset update, re-run `make -C agents/simple_router eval-routing` and confirm `tool_trajectory_avg_score` is 1.0 before restoring `_STATIC_ROUTING_DEFAULT = "1"` as the permanent value.

## Evalset updates summary

| Evalset case                                 | Change required                                    | When                                            |
|----------------------------------------------|----------------------------------------------------|-------------------------------------------------|
| `static_route_howto_gate_over_invoice_vocab` | Remove `get_conversation_context` from `tool_uses` | Phase 2 only (after re-enabling static routing) |

All other existing cases pass without modification in both phases.

## Success criteria

The implementation is complete when all three of the following pass with no regressions:

```bash
# Unit tests — must pass with zero failures
make -C agents/simple_router test

# Routing eval — tool_trajectory_avg_score must be 1.0
make -C agents/simple_router eval-routing

# Response eval — response_match_score must meet threshold (0.7)
make -C agents/simple_router eval-response
```

**Debugging individual cases** — pass a comma-separated list of eval IDs via `CASES` to isolate a failure without running the full suite:

```bash
make -C agents/simple_router eval-routing CASES=topic_change_bypasses_follow_up,static_route_guard_releases_next_turn

make -C agents/simple_router eval-response CASES=out_of_scope_danish
```

**Purpose of each target:**

- `make test` — validates code correctness without LLM calls. Catches import errors, broken callback wiring, wrong state key names, and logic bugs in the new tools and injection guard. Fast and cheap; run first. Does not test agent behavior.

- `make eval-routing` — the primary functional gate. Runs the agent end-to-end against Gemini and verifies that every message reaches the correct expert and that the expected domain tools are called. Threshold 1.0 means zero routing regressions are acceptable. This is what proves the synthetic injection delivers facts correctly, the prompt changes do not confuse routing, and cross-turn state (`invoice_id` persisted via `set_fact`) still works across invocations.

- `make eval-response` — validates response quality against a judge model. Threshold 0.7. Catches cases where routing is correct but the agent produces a wrong or degraded answer — for example, if the LLM misreads the injected facts format or behaves differently after the prompt rewrite. This is the canary for the response eval uncertainty described in the prompt migration section.

  If this eval fails after the prompt changes, inspect the failing cases before drawing conclusions:
  - If the agent answer is **substantively wrong** (missing data, wrong invoice field, incorrect guidance) — fix the code or prompts, do not update the evalset.
  - If the agent answer is **correct but differently worded** (rephrased confirmation, slightly different structure) — update the expected response in `eval/response_evalset.json` for that case. This is intentional behavioral change, not a regression.

  Do not adjust the 0.7 threshold itself.

Once all three pass, update the following documents to reflect the new design:

- `SPEC.md` — update the Performance Model table to show actual LLM round-trip counts per path (before/after), update the Shared State section to replace `public:facts` with `public:session_facts` and `public:fact_history`, update the Tools section to document `set_fact`, `search_facts`, and `get_latest_fact`, and remove the statement that all agents call `get_conversation_context` as their first action each turn.
- `README.md` — update any description of how agents access shared context to reflect callback injection rather than a tool call.
