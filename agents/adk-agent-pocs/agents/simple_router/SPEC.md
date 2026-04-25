# simple_router — System Specification

## Overview

`simple_router` is a multi-agent system for invoice management and product support. A lightweight router classifies every user message and transfers it to one of four specialist agents. The router never answers users directly.

**Domains covered:**
- Invoice data — viewing, validating, and updating invoice fields
- Product support — how-to guidance, UI walkthroughs, troubleshooting

**Out of scope:** Anything else (expenses, receipts, payroll, …) is handled gracefully by the receptionist.

---

## Architecture

```
User
 │
 ▼
router_agent          ← flash-lite, pure classifier, no conversational output
 ├── invoice_agent    ← invoice data reads and writes
 ├── support_agent    ← how-to guidance and troubleshooting
 ├── receptionist_agent ← greetings, fallback, disambiguation
 └── orchestrator_agent  ← composite (invoice + support) requests
       ├── invoice_agent_helper   (AgentTool, stateless)
       └── support_agent_helper   (AgentTool, stateless)
```

Facts are delivered to expert agents via `inject_facts_callback` (a `before_model_callback`
that appends a `[session facts: {...}]` message to the conversation) — not via
`get_conversation_context` tool calls. Only `router_agent` still calls
`get_conversation_context` as a tool (to read `follow_up_agent` state).

---

## Performance Priorities

Three goals are treated as first-class constraints throughout the design — every architectural decision either serves one of them or explicitly trades one against the other:

1. **Minimize LLM calls per turn** — the baseline single-domain path is 2 calls (router → expert). Every shortcut is a deliberate reduction from that baseline.
2. **Maximize Gemini prefix cache hit rate** — a stable request fingerprint (system instruction + tools + conversation prefix) means every repeated call hits the cache rather than re-computing. Cache misses cost latency and tokens.
3. **Keep conversation history compact and agent-readable** — prior tool calls are stripped before each LLM call and structured data travels through session state rather than accumulating in the thread. This bounds token count per call, keeps the cache prefix stable (reinforcing goal 2), and ensures any expert receiving control mid-session can read a clean, meaningful dialogue.

### LLM call minimization

| Mechanism | Location | Savings vs baseline |
|-----------|----------|---------------------|
| `follow_up_shortcut` | `callbacks.py` | −1: router LLM skipped for clear follow-up answers (bare ID, yes/no, short fragment) |
| `static_route_shortcut` (opt-in: `SIMPLE_ROUTER_STATIC=1`) | `callbacks.py` + `routing.py` | −1: router LLM skipped for high-confidence keyword matches |
| `context_prefetch_shortcut` | `callbacks.py` | −1: eliminates the tool-decision LLM call on all LLM-path turns |
| Parallel helper execution in `orchestrator_agent` | `sub_agents/orchestrator_agent.py` | Invoice + support helpers run in one round-trip instead of sequentially |

All shortcuts emit structured log events so their hit rate is measurable in production (see Observability).

### Prefix cache design

**Router and receptionist — guaranteed cache hit every call**

These agents use `include_contents="none"`, so the LLM request is exactly `system_instruction + tools` — no conversation is appended. Because neither the instruction nor the tool list ever changes, the request fingerprint is always identical and every call hits the cache.

**Rules:** Never add dynamic content to their system instruction. Never change `include_contents` to `"default"`.

**Expert agents — stable prefix despite growing conversation history**

Expert agents need conversation history for multi-turn reasoning, so `include_contents="none"` is not an option. Instead, four design decisions work together to keep the cache prefix as stable as possible:

| Decision | Mechanism | Why it preserves the cache prefix |
|----------|-----------|-----------------------------------|
| System instruction never modified | `inject_facts_callback` appends to *contents*, not to `llm_request.config.system_instruction` | SI is always the same string → SI prefix is always a cache hit |
| Prior tool calls stripped | `strip_tool_history_callback` removes `function_call`/`function_response` parts from all prior turns | Removes noise that would otherwise make the history fingerprint differ turn-to-turn |
| Facts injected at the *end* of the current turn | `inject_facts_callback` inserts `[session facts: {...}]` *after* the last real user message — at the tail of `contents` | The `SI + prior conversation` prefix is unchanged; only the tail varies. Gemini can cache the prefix even when the tail is new |
| Prior thought parts stripped | `strip_tool_history_callback` removes `thought`/`thought_signature` parts from all prior turns alongside `function_call`/`function_response` | Prior-turn thought parts never appear in subsequent requests → stable prefix maintained |

**Rules for any new expert agent** (the expert registry applies these automatically — do not override):

- **Do NOT** modify `llm_request.config.system_instruction` at runtime — use `inject_facts_callback` for dynamic data
- **Do NOT** set `include_contents="none"` — expert agents need history for multi-turn reasoning
- **DO** let `expert_registry.py` inject `strip_tool_history_callback` and `inject_facts_callback` — do not bypass or reorder them
- **DO** set `generate_content_config` via `_THINKING_CONFIG` from `expert_registry.py` — this sets a
  thinking_budget and ensures prior-turn thought parts are stripped before any LLM call.
  Do not set thinking_budget=0 unless reverting to non-thinking mode intentionally.

See the *Combined effect on prefix caching* table in the Conversation Context Design section for the per-agent summary.

### Compact conversation history

Prior tool call chains are stripped before every expert LLM call (`strip_tool_history_callback`). Structured data (invoice fields, validation results) is never left in the conversation thread — it lives in `public:session_facts` and is re-injected as a fresh `[session facts: {...}]` snapshot at the tail of each turn. This serves all three goals simultaneously:

| Goal served | How |
| --- | --- |
| Token count | No growing tool-response chains → fewer input tokens per call |
| Prefix cache | Stripped history is more uniform turn-to-turn → longer stable prefix → better cache reuse |
| Agent readability | Any expert receiving control sees user messages + agent text replies + current facts — a clean, meaningful dialogue with no internal plumbing visible |

**Rule:** Never leave structured data in the conversation thread. Always write it via `set_fact()` so it travels through session state and arrives via injection — not as raw tool responses that accumulate indefinitely.

---

**Key modules beyond agents and tools:**

| Module | Purpose |
| --- | --- |
| `routing.py` | Deterministic keyword scorer; produces `RoutingDecision` without an LLM call |
| `oos_detection.py` | Multilingual out-of-scope keyword vocabulary and instruction override |
| `follow_up_detection.py` | LLM-free follow-up classifier; `NEW_REQUEST_STARTS` and `is_follow_up_answer` |
| `_history.py` | `strip_tool_history_callback` — purges prior tool call/response parts from LLM context |
| `_facts_callbacks.py` | `inject_facts_callback`, `persist_facts_callback`, `router_force_context_callback` — fact lifecycle |
| `callbacks.py` | Router and receptionist `before_model_callback` chains |
| `expert_registry.py` | Single source of truth for domain experts and prompt loading |

---

## Shared State

State is stored as ADK session state under these keys:

| Key | Type | Owner | Lifecycle |
|-----|------|-------|-----------|
| `public:session_facts` | `dict[str, FactEntry]` | Any agent (via `set_fact`) | Persists for the session; accumulates invoice fields, validation results |
| `public:fact_history` | `list[HistoryEntry]` | `persist_facts_callback` | Append-only log of persisted facts; superseded entries are queryable |
| `public:follow_up_agent` | `str \| None` | Any agent | Set by `signal_follow_up()`; consumed (cleared) on the next `get_conversation_context()` call or `follow_up_shortcut` |
| `public:reroute_requested` | `bool \| None` | Any expert (via `signal_reroute`) | Set by `signal_reroute()`; consumed by `router_before_model_callback` at priority 0, bypassing all other shortcuts and letting the LLM re-classify |
| `router:static_bypass` | `bool \| None` | `static_route_shortcut` | Re-route guard; cleared on the next router invocation |
| `router:follow_up_last_fired` | `str \| None` | `follow_up_shortcut` | Loop-detection guard; stores the agent name from the previous shortcut fire; cleared when a new request is detected or a different agent fires |
| `_ctx_loaded_inv` | `str \| None` | `get_conversation_context` | Idempotency guard — stores invocation ID so repeat calls short-circuit |
| `router:prior_follow_up` | `str \| None` | `signal_follow_up` | Survives router consumption of `public:follow_up_agent`; read by `inject_facts_callback` on the **next** agent invocation to inject `_context_note`; cleared on consumption |
| `router:prior_follow_up_inv` | `str \| None` | `signal_follow_up` | Invocation ID when `router:prior_follow_up` was set; prevents `inject_facts_callback` from consuming the key within the same invocation (i.e., between LLM calls of the same agent turn) |
| `_follow_up_called_inv` | `str \| None` | `signal_follow_up` | Idempotency guard — stores invocation ID; second `signal_follow_up` call within the same invocation returns an error |

**`FactEntry` shape** (stored under each key in `public:session_facts`):
```json
{
  "status": "draft | persisted",
  "description": "Human-readable label",
  "value": "<string value>",
  "fact_id": "<uuid | null>",
  "loaded_at": "<ISO-8601 UTC timestamp>",
  "set_by": "<agent name>"
}
```

**`HistoryEntry` shape** (appended to `public:fact_history` by `persist_facts_callback`):
```json
{
  "fact_id": "<new uuid>",
  "supersedes_fact_id": "<previous uuid | null>",
  "key": "<fact key>",
  "description": "...",
  "fact": "<value>"
}
```

**Facts written by invoice tools (via `set_fact`):**

| Fact key | Written by |
|----------|-----------|
| `invoice_id` | `note_invoice_id`, `get_invoice_details` |
| `status`, `vendor_name`, `amount`, `due_date`, `vat_rate`, `missing_fields` | `get_invoice_details` |
| `validation_result` | `validate_invoice` |
| `<field_name>` (any) | `update_invoice_field` |

---

## Conversation Context Design

The system is designed so that any expert can be handed control on any turn and immediately have access to everything it needs — without depending on prior tool results in the conversation thread. Two mechanisms work together to achieve this.

### Structured facts via session state and injection

Domain tools write structured data directly into `public:session_facts` (via `set_fact`) — not into the conversation. Before each LLM call, `inject_facts_callback` reads `public:session_facts` and `public:fact_history`, builds a structured view, and appends it as a `[session facts: {...}]` user message immediately after the last real user message.

The injected view format (from `_flat_facts`) is `{key: {"value": current, "previous": [older_values], "description": ..., "loaded_at": ..., "set_by": ...}, "_summary": "..."}` — not a simple `{key: value}` flat map. Each fact entry includes its current value, a chronological list of prior values (oldest-first), and metadata fields (`description`, `loaded_at`, `set_by`) from when the fact was last written. A top-level `_summary` key holds a plain-English overview so the LLM can scan state and history without navigating nested JSON.

This means every expert agent always sees current facts without calling `get_conversation_context`. Because facts persist in session state, an invoice ID noted in turn 1 is available to any agent receiving control in turn 3 without re-fetching.

This is the only cross-agent data channel. Agents must not assume they can read prior tool responses from conversation history — those are stripped.

**`inject_facts_callback` injection point (stable for prefix caching):**

Facts are appended at the **end** of `contents` — after any current-turn tool-call/response pairs — so the model always sees the most up-to-date facts immediately before generating its next response. Injecting between the user text and the model's prior function call broke Gemini's `thought_signature` validation on the second LLM call of a multi-step sequence, so facts now always go at the tail.

```text
turn N-1  [user  text]   "show me invoice 42"             ← kept
turn N-1  [model text]   "Invoice 42 — Acme, $1,200…"    ← kept

turn N    [user  text]   "update the VAT to 25%"          ← last real user msg (boundary)
turn N    [model fn]     validate_invoice(...)            ← current turn tool call (if any)
turn N    [user  text]   [session facts: {"invoice_id": "42", ...}]  ← injected at END
```

No invocation guard is needed — `strip_tool_history_callback` (which runs first in the callback chain) removes any prior `[session facts:]` injection before each LLM call, so inject always re-injects fresh facts without accumulation. The system instruction is NOT modified — keeping it stable for prefix caching.

**Fact lifecycle:**
1. A domain tool calls `set_fact(key, value, description, tool_context)` → entry written with `status="draft"`.
2. `inject_facts_callback` (before each LLM call) reads and injects the flat view.
3. `persist_facts_callback` (after agent turn completes) promotes all `status="draft"` entries to `status="persisted"` and appends them to `public:fact_history`.

### Follow-up signalling (`signal_follow_up`)

When an expert needs to ask the user a clarifying question it **must** call `signal_follow_up()` before responding. This writes the calling agent's name to `public:follow_up_agent`.

**Why it is required.** The router re-classifies every message independently. A bare reply like `"42"` carries no domain signal of its own — without the registered signal the router would route it incorrectly. `signal_follow_up()` pre-wires the return route for the expected reply.

**Signal lifecycle:**

1. Expert calls `signal_follow_up()` → `public:follow_up_agent = "<agent_name>"` set in session state.
2. Expert asks its clarifying question and stops. The tool's return value includes `next_action: "Do NOT call any more tools this turn"` — the agent must honour this.
3. On the next user message, the router's `before_model_callback` reads the signal:
   - Short non-command reply → `follow_up_shortcut` fires: signal cleared, direct transfer (no router LLM call).
   - New request detected → shortcut falls through: signal cleared inside `get_conversation_context()`, router LLM classifies normally.
4. `public:follow_up_agent` is always cleared on the first `get_conversation_context()` call of the next turn — exactly once, regardless of which path ran.

**Visibility constraint.** `get_conversation_context()` returns `follow_up_agent` **only to `router_agent`**. Expert agents never see the field — this prevents them from reading stale follow-up state and accidentally looping on `signal_follow_up()`.

**Invariant.** An expert must not call any further tools after `signal_follow_up()`. The signal and the clarifying question must be issued in the same turn — if the expert continues calling tools, the question may never be asked, leaving `public:follow_up_agent` set without a corresponding reply.

### Tool history stripping (`strip_tool_history_callback`)

`strip_tool_history_callback` (injected by `expert_registry.py` on every `direct_agent`) rewrites `llm_request.contents` before each LLM call in two passes:

**Pass 1 — remove noise from any position:**

- ADK `For context:` router messages (inserted by ADK when the router transfers to a sub-agent)
- Stale `[session facts:]` messages from prior turns (a fresh injection will be appended by `inject_facts_callback` immediately after)

**Pass 2 — strip tool call artefacts from prior turns:**

- Finds the last real user text message (ignoring `For context:` and `[session facts:]` items) to establish the current-turn boundary.
- Strips `function_call` and `function_response` parts from all turns before that boundary.
- Current-turn items are preserved so multi-step tool-call sequences within one turn still work.

What the LLM receives after stripping and facts injection:

```text
turn N-1  [user  text]   "show me invoice 42"                     ← kept
turn N-1  [model text]   "Invoice 42 — Acme, $1,200…"            ← kept
          (all tool calls/responses from turn N-1 stripped)

turn N    [user  text]   "update the VAT to 25%"                  ← kept  ← boundary
turn N    [model fn]     validate_invoice(...)                    ← kept (current turn)
turn N    [user  text]   [session facts: {"invoice_id": "42", ...}]  ← injected at END by inject_facts_callback
```

**Why this is safe:** structured data (invoice fields, validation results) lives in `public:session_facts` and is re-injected each turn via `inject_facts_callback`. The LLM does not need prior tool responses to reason correctly — it needs the user dialogue and the current turn's injected facts snapshot.

**Invariant:** `function_response` entries are never used as the boundary. Using one would strip the preceding `function_call`, leaving an unpaired response and causing the agent to repeat the tool call in a loop.

### Router force-context guard (`router_force_context_callback`)

An `after_model_callback` on `router_agent`. When the router LLM issues a direct `transfer_to_agent` without first calling `get_conversation_context`, this callback intercepts the response and replaces it with a `get_conversation_context` call. ADK executes the tool, appends its result to the conversation, and calls the LLM again — ensuring `get_conversation_context` always appears in the tool trajectory.

No-ops if `get_conversation_context` was already called this invocation (checked via `_ctx_loaded_inv`).

### Agent isolation (`disallow_transfer_to_parent` / `disallow_transfer_to_peers`)

All sub-agents set `disallow_transfer_to_parent=True` so ADK's `_find_agent_to_run` always falls back to `router_agent` (root_agent) at the start of each new turn — preventing any expert from being silently resumed without going through the router.

Expert `direct_agents` additionally set `disallow_transfer_to_peers=True` to prevent expert-to-expert transfers (e.g. `invoice_agent → orchestrator_agent`). All cross-domain escalation must pass through the router.

### Combined effect on prefix caching

See Performance Priorities for the design rules behind these choices.

| Agent | `include_contents` | Tool history stripped | Facts delivery | Cache fingerprint |
| --- | --- | --- | --- | --- |
| `router_agent` | `none` | N/A | via `context_prefetch_shortcut` (pre-executed before LLM) + result in contents | SI always cached; real LLM call sees `[SI][User][Model: gc_call][Tool: gc_result]` |
| `receptionist_agent` | `none` | N/A | via `signal_follow_up` only | `system_instruction + tools` — never changes; guaranteed hit |
| `invoice_agent` | `default` | Yes | via `inject_facts_callback` | Compact, stable history; cache reuse improves across similar turns |
| `support_agent` | `default` | Yes | via `inject_facts_callback` | Compact, stable history; cache reuse improves across similar turns |
| `orchestrator_agent` | `default` | Yes | via `inject_facts_callback` | Compact, stable history; cache reuse improves across similar turns |

---

## Routing Rules

The three callback shortcuts (`follow_up_shortcut`, `static_route_shortcut`, `context_prefetch_shortcut`) each eliminate one router LLM call — see Performance Priorities for context.

Classification happens in two steps, applied in order:

### Step 1 — HOW-TO Gate
If the message begins with any phrase in `prompts/howto_triggers.txt`:
- `"how do I"`, `"how to"`, `"how can I"`, `"what steps"`, `"walk me through"`, `"where do I"`

→ Transfer to `support_agent`. Unconditional. Fires even when the sentence also mentions invoice IDs or billing terms.

### Step 2 — Content Classification

| Target | Condition |
|--------|-----------|
| `orchestrator_agent` | Two separate intents (invoice data AND how-to/guidance) joined by: `and`, `also`, `plus`, `—`, `+`, `/`, or a comma |
| `invoice_agent` | Invoice/billing vocabulary (`invoice`, `VAT`, `billing`, `payment`, `vendor`, `charge`, `due date`) with action verbs (`show`, `update`, `validate`) |
| `support_agent` | Troubleshooting, UI errors, non-how-to operational questions |
| `receptionist_agent` | Greetings, out-of-scope, ambiguous |

### Follow-up Routing

When `public:follow_up_agent` is set:
- Short answer (≤ 5 words, no command/question opener) → transfer to the registered agent
- Unambiguous new request for a different domain → route by content, ignore follow-up
- Ambiguous → transfer to the registered agent

The `follow_up_shortcut` `before_model_callback` short-circuits the router LLM for clear follow-up answers (bare IDs, "yes"/"no", short non-command fragments), saving one LLM call per follow-up turn.

**Loop detection.** If the shortcut fired for agent X last turn and agent X re-registers itself (i.e. it called `signal_follow_up()` again — meaning it couldn't handle the answer), the shortcut detects the repeat via `router:follow_up_last_fired` and falls through to the router LLM, which can re-route to the correct agent. The guard is cleared whenever a new request is detected or a different agent fires.

---

## Agent Contracts

### router_agent

| Property | Value |
|----------|-------|
| Model | `gemini-3.1-flash-lite-preview` |
| Output | Never answers user; always transfers |
| Tools | `get_conversation_context` |
| `include_contents` | `none` |
| `before_model_callback` | `router_before_model_callback` (chains: circuit_breaker → reroute_guard → OOS → follow_up_shortcut → static_route_shortcut → context_prefetch_shortcut) |
| `after_model_callback` | `router_force_context_callback` (intercepts direct transfers that skipped `get_conversation_context`) |
| `generate_content_config` | `thinking_budget=0` — thinking disabled; router is a pure classifier, no reasoning required |
| Prefix cache | Yes — fully static prompt + `include_contents="none"` |

**Invariants:**
- Must not produce conversational text
- Must not call any tool other than `get_conversation_context`
- `get_conversation_context` must appear in the tool trajectory for every LLM-path turn; `context_prefetch_shortcut` pre-executes it before the LLM call; `router_force_context_callback` is the safety net for any edge case that bypasses the prefetch

---

### invoice_agent

| Property | Value |
|----------|-------|
| Model | `gemini-3-flash-preview` |
| Tools | `signal_follow_up`, `get_invoice_details`, `validate_invoice`, `update_invoice_field`, `note_invoice_id` |
| `include_contents` | default |
| `before_model_callback` | `strip_tool_history_callback` → `inject_facts_callback` → `receptionist_before_model_callback` |
| `after_agent_callback` | `persist_facts_callback` |
| `disallow_transfer_to_parent` | `True` |
| `disallow_transfer_to_peers` | `True` |

Facts are delivered via `inject_facts_callback` (as `[session facts: {...}]` user message) — the agent does not call `get_conversation_context`.

**Request classification and tool sequence:**

| Request type | Signal | Tool sequence |
|---|---|---|
| READ | "show", "display", "what is", "inspect" | resolve ID → `get_invoice_details` |
| VALIDATE | "validate", "check", "verify" | resolve ID → `get_invoice_details` → `validate_invoice` |
| WRITE | "update", "set", "change", "fix" | resolve ID → `get_invoice_details` → `validate_invoice` → `update_invoice_field` |
| HISTORY | "what invoice did I see", "what invoice number did I see before", "what was the last invoice" | No tools — read `_summary` from injected session facts. Answer with the invoice number only: `"You previously viewed invoice #<id>."` STOP. Do NOT include other fields, warnings, or context from prior topics. |
| MENTION | User states an invoice ID with no clear action | `note_invoice_id` → `signal_follow_up` → ask one question, STOP |
| HOW-TO | Defense-in-depth escape hatch | Transfer to `support_agent` immediately (blocked by `disallow_transfer_to_peers`; agent should decline gracefully) |

**Invoice ID resolution order:**
1. Current message (explicit)
2. `context.facts["invoice_id"]` from injected session facts (only for short follow-up messages)
3. Not resolved → `signal_follow_up()` + ask, STOP

**Sensitive fields** (require `update_invoice_field` confirmation): `vat_rate`, `due_date`, `amount`, `vendor_name`. Enforced at the ADK tool layer via `FunctionTool(require_confirmation=…)` — cannot be bypassed by prompt drift.

**Response format:**
- READ: labelled field list + one-line status summary; list missing fields with ⚠️
- VALIDATE: same markdown block as READ, then list each issue with ⚠️, then one sentence telling the user what to do next; if no issues: "✅ Invoice #N is valid."
- WRITE: confirm field + new value (one sentence)
- ERROR: state what went wrong (one sentence)

---

### support_agent

| Property | Value |
|----------|-------|
| Model | `gemini-3.1-flash-lite-preview` |
| Tools | `signal_follow_up`, `get_support_steps`, `get_help_article` |
| `include_contents` | default |
| `before_model_callback` | `strip_tool_history_callback` → `inject_facts_callback` |
| `after_agent_callback` | `persist_facts_callback` |
| `disallow_transfer_to_parent` | `True` |
| `disallow_transfer_to_peers` | `True` |

Facts are delivered via `inject_facts_callback` — the agent does not call `get_conversation_context`.

**Scope:** Owns any message starting with a how-to trigger phrase, regardless of subject matter. Only transfers for explicit data requests ("show me invoice X", "update field Y") — blocked by `disallow_transfer_to_peers`; agent should decline gracefully.

**Tool sequence:** For every how-to question: `get_support_steps(question)` then `get_help_article(question)`. Both called with the current question text.

**Response format:**
1. One-line confirmation of what is being explained
2. Numbered steps with **bold** button/menu names
3. If both tools return `found=false` → `"I don't have guidance on that topic."`

---

### receptionist_agent

| Property | Value |
|----------|-------|
| Model | `gemini-3.1-flash-lite-preview` |
| Tools | `signal_follow_up` |
| `include_contents` | `none` |
| `before_model_callback` | `receptionist_before_model_callback` (OOS detection) |
| `disallow_transfer_to_parent` | `True` |
| Prefix cache | Yes |

**Responsibilities:**
- First contact: greet warmly
- Conversational turns: acknowledge + invite next question
- Ambiguous requests: `signal_follow_up()` + one clarifying question
- Out-of-scope: graceful decline (covers invoice management and product support only)
- Unambiguous domain match: transfer immediately without asking

**Invariants:** Never answers domain questions (invoice data, how-to). Always transfers when a pattern matches. Does not receive facts injection (no `inject_facts_callback`) — `include_contents="none"` and no domain tools.

---

### orchestrator_agent

| Property | Value |
|----------|-------|
| Model | `gemini-3-flash-preview` |
| Tools | `signal_follow_up`, `invoice_agent_helper` (AgentTool), `support_agent_helper` (AgentTool) |
| `include_contents` | default |
| `before_model_callback` | `strip_tool_history_callback` → `inject_facts_callback` |
| `after_agent_callback` | `persist_facts_callback` |
| `disallow_transfer_to_parent` | `True` |

Facts are delivered via `inject_facts_callback` — the agent does not call `get_conversation_context`.

**Responsibilities:** Handles messages containing two separate intents — invoice data AND guidance/how-to.

**Tool sequence:**
1. Facts are already injected by `inject_facts_callback` — no context tool call needed
2. Issue ALL required helper calls **simultaneously** in a single response (parallel execution)
   - Invoice slice → `invoice_agent_helper(input="<invoice request only>")`
   - How-to slice → `support_agent_helper(input="<how-to question only>")`
3. Compose one coherent response from all helper results
4. If invoice ID required but missing → `signal_follow_up()`, ask once, STOP

**Grounding rule:** Only report what helpers actually returned. Never invent content.

**Helper agents** are stateless variants built by the expert registry:
- `include_contents="none"`, no `signal_follow_up`, no agent transfers
- Write results to `public:{name}_helper_result` state key
- Appear in debug traces as `invoice_agent_helper` / `support_agent_helper` — they are NOT listed in `agent.py` sub_agents

---

## Tools

### Context tools (`tools/context_tools.py`)

| Tool | Used by | Description |
|------|---------|-------------|
| `get_conversation_context()` | `router_agent` only | Returns `{"facts": dict, "follow_up_agent": str\|None, "fact_history": list}`. `facts` uses the `_flat_facts` structured format (see above). `follow_up_agent` and `fact_history` are only populated for `router_agent` calls; `fact_history` contains superseded (non-current) entries only, ordered oldest-first, as `[{"key": ..., "fact": ...}]`. Consumes and clears the follow-up agent key. Idempotent per invocation — repeat calls return an error. Emits `routing_context` JSON to stderr. |
| `signal_follow_up()` | All expert agents | Registers the calling agent as the expected recipient of the next user reply. Sets `public:follow_up_agent` to the agent's name. Also sets `router:prior_follow_up` (survives router consumption of `public:follow_up_agent`; consumed by `inject_facts_callback` on the next agent invocation to inject `_context_note`) and `router:prior_follow_up_inv` (current invocation ID; prevents `inject_facts_callback` from consuming within the same invocation). Idempotent per invocation — a second call within the same invocation returns an error directing the agent to stop. Returns `{"status": "follow_up_registered", "agent": name, "next_action": "...Do NOT call any more tools this turn"}`. |
| `signal_reroute()` | All expert agents | Signals that the current request is outside the agent's domain and must be rerouted. Clears `public:follow_up_agent`, sets `public:reroute_requested=True`. Returns `{"status": "reroute_requested", "next_action": "...STOP"}`. The router consumes this flag at priority 0, bypassing all shortcuts so the LLM can re-classify freely. |
| `set_fact(key, value, description)` | Domain tools (internal) | Writes a `FactEntry` with `status="draft"` to `public:session_facts`. Returns `{"status": "noted", key: value}`. Called by domain tools internally; not exposed to LLM agents directly. |
| `search_facts(query, search_in)` | Domain tools (internal) | Searches session and/or history layers. Returns `{"results": [...], "count": int}`. |
| `get_latest_fact(key)` | Domain tools (internal) | Retrieves the most recent non-superseded value for a logical fact key from session or history. Returns `{"found": bool, "source": ..., ...}`. |

### Facts callbacks (`_facts_callbacks.py`)

| Callback | Hook | Description |
|----------|------|-------------|
| `inject_facts_callback` | `before_model_callback` (all expert direct agents, orchestrator) | Reads `public:session_facts`, builds a flat facts view, appends it as `[session facts: {...}]` user message at the end of contents. Does not modify the system instruction. No invocation guard — `strip_tool_history_callback` (which runs first) removes any prior `[session facts:]` injection before each call, so fresh injection is always safe. Also handles early persistence for facts flagged with `persist_now=True`. When `router:prior_follow_up` is set from a previous invocation, clears it and injects a `_context_note` key into the facts view reminding the agent to apply MANDATORY DISAMBIGUATION CHECK before acting on the current message. |
| `persist_facts_callback` | `after_agent_callback` (all expert direct agents, orchestrator) | Moves all `status="draft"` facts to `public:fact_history` (appending with `fact_id`/`supersedes_fact_id`), updates their `status` to `"persisted"`. Returns None to preserve the agent's response. |
| `router_force_context_callback` | `after_model_callback` (router only) | Intercepts any direct `transfer_to_agent` response that skipped `get_conversation_context`. Replaces it with a `get_conversation_context` call so the tool trajectory is always correct. No-ops if context was already loaded this invocation. |

### History callback (`_history.py`)

`strip_tool_history_callback` is injected automatically by `expert_registry.py` as the first `before_model_callback` on every expert `direct_agent` and on `orchestrator_agent`.

**Why a separate file with an underscore.** The natural home for a callback is `callbacks.py`, but placing it there would create a circular import: `expert_registry` → `callbacks` → `routing` → `expert_registry`. `_history.py` has zero local imports, so both `expert_registry.py` and `sub_agents/orchestrator_agent.py` can import it without a cycle. The leading underscore marks it as an internal infrastructure module.

**Contract:** Before each LLM call, finds the last real user TEXT message in `llm_request.contents` (not a `function_response` entry, which also carries `role="user"` in the ADK protocol). Everything before that boundary has its `function_call` and `function_response` parts stripped in place. Everything from the boundary onward — including the current turn's tool calls — is preserved so multi-step reasoning within the turn still works.

**Invariant:** `function_response` entries are never used as the boundary. Using one would strip the preceding `function_call`, leaving an unpaired response and causing the agent to repeat the tool call in a loop.

### Invoice tools (`tools/invoice_tools.py`)

| Tool | Description |
|------|-------------|
| `note_invoice_id(invoice_id)` | Wrapper around `set_fact("invoice_id", ...)`. Persists a user-stated invoice ID into `public:session_facts`. Returns `{"status": "noted", "invoice_id": id}`. |
| `get_invoice_details(invoice_id)` | Returns invoice dict; persists all fields via `set_fact`. |
| `validate_invoice(invoice_id)` | Returns `{"valid": bool, "issues": list}`. Reads `missing_fields` from `public:session_facts`. |
| `update_invoice_field(invoice_id, field_name, value)` | Updates one field via `set_fact`. Requires user confirmation for sensitive fields. Wrapped as `FunctionTool`. |

### Support tools (`tools/support_tools.py`)

| Tool | Description |
|------|-------------|
| `get_support_steps(issue_code)` | Returns `{"found": bool, "steps": list}`. Exact match then keyword match against built-in step database. |
| `get_help_article(topic)` | Returns `{"found": bool}`. POC stub — always `found=false`. |

---

## Expert Registry

`expert_registry.py` is the single source of truth for domain experts. It automatically constructs two agent variants from each registered template:

| Variant | Used by | Differences from template |
|---------|---------|--------------------------|
| `direct_agent` | router `sub_agents` list | Adds `signal_follow_up`; injects `_direct_cb` (`strip → inject_facts → [existing_cb]`); adds `persist_facts_callback` as `after_agent_callback`; adds `_log_thoughts_callback` as `after_model_callback`; sets `disallow_transfer_to_parent=True`, `disallow_transfer_to_peers=True`, `generate_content_config` (`thinking_level="low"`, `include_thoughts=True`) |
| `helper_agent` | orchestrator `AgentTool` list | `include_contents="none"`, no `signal_follow_up`, adds HELPER MODE suffix (no transfers), `output_key` set, `generate_content_config` (`thinking_level="low"`, `include_thoughts=True`) |

**Adding a new expert (7 steps):**

Steps that auto-wire (1–4):
1. `tools/{name}_tools.py` — domain tools
2. `prompts/{name}_agent.txt` — agent prompt (can use `{shared_rules}`, `{howto_triggers}`)
3. `sub_agents/{name}_agent.py` — call `register(Agent(...))`, no assignment needed
4. Import in `sub_agents/__init__.py` before `build_orchestrator_agent()`

Steps requiring manual edits (5–7):
5. Add `direct_agent` to `sub_agents` list in `agent.py`
6. Add routing rule to `prompts/router_agent.txt`
7. Add routing patterns to `prompts/receptionist_agent.txt`

The new expert's `description` field auto-propagates to the orchestrator `{domains}` prompt with no additional changes.

---

## Prompt Composition

`load_prompt(name)` loads `prompts/{name}.txt` and applies these substitutions at startup:

| Placeholder | Source file | Purpose |
|-------------|-------------|---------|
| `{shared_rules}` | `prompts/shared_rules.txt` | Context-first, grounding, hygiene rules applied to all experts |
| `{howto_triggers}` | `prompts/howto_triggers.txt` | Single source of truth for how-to trigger phrases |
| `{domains}` | Built dynamically by `build_domains_summary()` | Expert domain list for orchestrator and receptionist |

Substitutions are no-ops when a placeholder is absent — safe to call on any prompt.

---

## Performance Model

See Performance Priorities for the design rationale behind these numbers.

| Path | LLM calls |
|------|-----------|
| Static route shortcut fires (`SIMPLE_ROUTER_STATIC=1`) | 1: expert only (keyword scorer bypasses router LLM) |
| Follow-up shortcut fires | 1: expert only (router LLM bypassed by callback) |
| Single domain (normal) | **1**: context prefetched by callback → router LLM routes directly |
| Follow-up shortcut skips (new request detected) | **1**: context prefetched by callback → router LLM routes directly |
| Multi-domain | 3: router → orchestrator → helpers (helpers run in parallel) |

**Static routing** is **disabled by default** (`SIMPLE_ROUTER_STATIC=0`). Enable with `SIMPLE_ROUTER_STATIC=1`. When disabled, all routing goes through the router LLM. A re-route guard (`router:static_bypass` state key) prevents a loop if an expert escape-hatches back through the router.

**Prefix caching:**

- `router_agent` and `receptionist_agent` qualify: fully static system prompt + `include_contents="none"` → fingerprint never changes → guaranteed cache hit every call
- Expert agents (`invoice_agent`, `support_agent`, `orchestrator_agent`) include conversation history for multi-turn context; `strip_tool_history_callback` removes prior tool call noise and `inject_facts_callback` appends facts at the end of the current turn (after stable history) — keeping the history compact and the caching prefix stable

---

## Observability

### Structured logs (always-on, stderr)

`routing_context` — emitted by every `get_conversation_context()` call (router only):
```json
{
  "event": "routing_context",
  "agent": "router_agent",
  "invocation_id": "...",
  "follow_up_agent": null,
  "session_fact_keys": ["invoice_id", "status"],
  "history_fact_count": 2,
  "ts": 1234567890.123
}
```

`bypass_follow_up` — emitted when the follow-up shortcut fires (router LLM skipped):
```json
{
  "event": "bypass_follow_up",
  "ts": 1234567890.123,
  "invocation_id": "...",
  "target_agent": "invoice_agent",
  "msg_preview": "42"
}
```

`prefetch_context` — emitted when the context prefetch shortcut fires (tool pre-executed, one LLM call saved):
```json
{
  "event": "prefetch_context",
  "ts": 1234567890.123,
  "invocation_id": "..."
}
```

`bypass_static` — emitted when the static route shortcut fires (router LLM skipped):
```json
{
  "event": "bypass_static",
  "ts": 1234567890.123,
  "invocation_id": "...",
  "target_agent": "invoice_agent",
  "confidence": 0.75,
  "scores": {"invoice_agent": 3, "support_agent": 0},
  "reason": "3 term(s) matched for invoice_agent (confidence 0.75)",
  "msg_preview": "show me invoice 42"
}
```

### Debug callbacks (opt-in)

Set `SIMPLE_ROUTER_DEBUG=1` to attach per-agent lifecycle and tool call logging with elapsed times:
```
[AGENT:router_agent] ▶ start
[TOOL →get_conversation_context] {}
[TOOL ←get_conversation_context] (3ms) {"facts": {}, ...}
[AGENT:router_agent] ◀ end  (142ms)
```

---

## Evaluation

```
make test   # unit tests (pytest, no LLM calls)
make eval   # integration eval (calls Gemini)
```

**Eval suites:**

| Suite | File | Metric | Threshold | Cases |
| --- | --- | --- | --- | --- |
| Routing | `eval/routing_evalset.json` | `tool_trajectory_avg_score` | 1.0 | 30 |
| Response | `eval/response_evalset.json` | `final_response_match_v2` | 1.0 | 11 |
| Behavior | `eval/behavior_evalset.json` | `rubric_based_final_response_quality_v1` | 0.8 | 8 |
| Error | `eval/error_evalset.json` | `rubric_based_final_response_quality_v1` | 0.8 | 3 |

Selected routing cases and what they cover:

| Case | What it covers |
|------|---------------|
| `single_domain_invoice` | Basic invoice routing |
| `single_domain_support` | Basic support routing |
| `multi_domain_orchestrator` | Two-intent composite routing |
| `out_of_scope_to_receptionist` | Unknown domain fallback |
| `cross_turn_invoice_id` | Invoice ID persisted across turns |
| `how_to_with_invoice_vocab` | HOW-TO gate fires over invoice vocabulary |
| `greeting_then_invoice` | Routing after conversational opener |
| `topic_change_bypasses_follow_up` | New request overrides follow-up signal |
| `follow_up_shortcut_fires` | Pre-seeded follow-up state + bare ID → shortcut routes directly |
| `static_route_guard_releases_next_turn` | Re-route guard clears after one turn |

**Scoring:** Routing correctness verified via `intermediate_responses`. Extra tool calls and latency regressions are not captured by the eval metric — unit tests in `tests/test_callbacks.py` cover shortcut logic precisely.
