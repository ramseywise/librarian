# Fast Multi-Agent System — Reverse-Engineered Spec

Derived from the live codebase. Describes the actual system as implemented.

---

## System Overview

A hybrid invoice/support assistant built on ADK. Routes user requests deterministically
when possible (zero LLM calls), falls back to a lightweight LLM classifier, and escalates
to a full orchestrator only when multi-domain coordination is required.

**Key design goals:**
- Minimize LLM calls per turn (direct path = 1 call)
- Maintain conversation continuity across agents ("same room" model)
- Cache-friendly architecture (static system instructions, context via tools)
- Extensible expert registry (adding an expert requires ~5 steps, no root changes)

---

## Directory Layout

```
agents/fast_multi_agent_system/
├── __init__.py                  # exports root_agent
├── agent.py                     # HybridRootAgent + App entry point
├── state.py                     # State schema constants + typed helpers
├── routing.py                   # decide_route() — deterministic keyword scorer
├── expert_registry.py           # ExpertSpec + two-phase agent construction
├── agents/
│   ├── __init__.py
│   ├── orchestrator_agent.py    # Multi-domain coordinator
│   ├── receptionist_agent.py    # Front-desk fallback (greetings, out-of-scope)
│   └── router_agent.py          # LLM classifier — low-confidence fallback
├── experts/
│   ├── __init__.py
│   ├── invoice_agent.py         # Invoice domain expert (registered via ExpertSpec)
│   └── support_agent.py         # UI/support domain expert (registered via ExpertSpec)
├── prompts/
│   ├── orchestrator_agent.txt
│   ├── receptionist_agent.txt
│   ├── router_agent.txt
│   ├── invoice_agent.txt        # uses {reroute_section} placeholder
│   └── support_agent.txt        # uses {reroute_section} placeholder
├── tools/
│   ├── __init__.py
│   ├── context_tools.py         # get_conversation_context, signal_follow_up, request_reroute
│   ├── invoice_tools.py         # get_invoice_details, validate_invoice, update_invoice_field
│   └── support_tools.py         # get_support_steps, get_help_article
└── plugins/
    ├── __init__.py
    └── firewall.py              # FirewallPlugin
```

---

## LLM Call Budget

| Path                          | Steps                                              | LLM calls |
|-------------------------------|----------------------------------------------------|-----------|
| Direct (high confidence)      | root (0) + expert (1)                              | **1**     |
| Direct + LLM router           | root (0) + llm_router (1) + expert (1)             | **2**     |
| Planned                       | root (0) + orchestrator (1) + helpers (N)          | **2–4**   |
| Re-route (misrouted expert)   | root (0) + wrong expert (1) + orchestrator (1+N)   | **3–5**   |
| Follow-up continuation        | root (0) + same expert (1)                         | **1**     |

Context caching cuts effective token cost after warm-up. Helper agents use
`include_contents='none'`, eliminating full history re-send on each `AgentTool` call.

---

## Key Design Decisions

| Concern                    | Decision                                                                        |
|----------------------------|---------------------------------------------------------------------------------|
| Routing                    | `decide_route()` — scored keyword matching, returns `RoutingDecision`           |
| LLM routing fallback       | `llm_router_agent` — classifies when confidence < 0.6 or no signal             |
| Expert agents              | Registered via `ExpertSpec` (two-phase construction)                            |
| Expert variants            | Each expert has `direct_agent` (full history) + `helper_agent` (no history)    |
| Multi-step requests        | `orchestrator_agent` — called only when multi-domain or planning signal present |
| Helper delegation          | `AgentTool(skip_summarization=True)` — orchestrator keeps control               |
| Helper context             | `include_contents='none'` — saves tokens per AgentTool call                     |
| Agent response capture     | `output_key` on every agent — auto-writes final answer to state                 |
| Shared state               | `session.state` with typed `public:*` keys only                                 |
| Conversation continuity    | `get_conversation_context()` — agents pull state at runtime                     |
| Follow-up routing          | `signal_follow_up()` + `public:follow_up_agent` — reply goes back to same agent |
| Ephemeral tool chaining    | `temp:*` keys — per-invocation, not persisted                                   |
| Policy & safety            | `FirewallPlugin` registered on `App`                                            |
| Mutating tools             | `require_confirmation` callback on `FunctionTool`                               |
| Prompt caching             | `ContextCacheConfig` on `App` — amortises static system prompt tokens           |
| Grounding enforcement      | Agents must not answer when all tools return `found=false`                      |
| Session backend            | `App` default; `require_confirmation` incompatible with DB/Vertex               |

---

## State Schema (`state.py`)

All `session.state` keys are constants. No magic strings outside this module.

### Public keys — visible to all agents

```python
PUBLIC_REQUEST             = "public:request"              # {"user_text": str}
PUBLIC_ROUTING             = "public:routing"              # RoutingDecision serialized
PUBLIC_PLAN                = "public:plan"                 # list[str]
PUBLIC_FACTS               = "public:facts"                # dict — normalized facts
PUBLIC_OPEN_QUESTIONS      = "public:open_questions"       # list[str]
PUBLIC_PROPOSED_ACTION     = "public:proposed_action"      # dict | None — firewall audit
PUBLIC_LAST_SUMMARY        = "public:last_agent_summary"   # str — written by output_key
PUBLIC_FINAL_ANSWER        = "public:final_answer"         # str | None — orchestrator output
PUBLIC_LAST_ANSWER         = "public:last_answer"          # str — persists across turns
PUBLIC_CONVERSATION_LOG    = "public:conversation_log"     # list[dict] — per-turn records
PUBLIC_ROUTING_ESCALATION  = "public:routing_escalation"   # {"reason": str} | None
PUBLIC_TASK_NOTE           = "public:task_note"            # str | None — router directive
PUBLIC_FOLLOW_UP_AGENT     = "public:follow_up_agent"      # str | None — agent awaiting reply
```

### Private prefixes — local to one agent

```python
PRIVATE_INVOICE       = "private:invoice:"
PRIVATE_SUPPORT       = "private:support:"
PRIVATE_ORCHESTRATOR  = "private:orchestrator:"
PRIVATE_FIREWALL      = "private:firewall:"
```

### Temp prefix — per-invocation, not persisted

```python
TEMP_PREFIX = "temp:"
```

### Reroute reason constants

```python
REROUTE_INVOICE = "invoice domain"
REROUTE_SUPPORT = "support domain"
REROUTE_MULTI   = "multi-domain"
REROUTE_ALL     = {REROUTE_INVOICE, REROUTE_SUPPORT, REROUTE_MULTI}
```

### Helper functions

```python
init_public_state(state, user_text)
    # Reset per-turn keys; preserve cross-turn keys with setdefault.
    # Called once at start of each root agent turn.

append_conversation_log(state, agent, request, outcome)
    # Append compact per-turn record. Called by root agent only.
    # request truncated to 120 chars; outcome truncated to 200 chars.
```

---

## Expert Registry (`expert_registry.py`)

### Two-phase construction

Experts are registered as `ExpertSpec` objects. The registry builds agent instances in
two phases to allow each expert's prompt to reference all other experts in its reroute
section.

**Phase 1 — `register(spec)`:**
- Validates: description, domain_tools, routing_terms, prompt file exists
- Stores spec in registry

**Phase 2 — `_finalize()`:**
- Compiles `{reroute_section}` placeholder in each prompt with actual expert names/descriptions
- Builds two agent variants per expert:
  - `direct_agent` — Flash model, full instruction, context + routing + domain tools, history included
  - `helper_agent` — Flash model, instruction, domain tools only, `include_contents='none'`

### ExpertSpec fields

```python
@dataclass
class ExpertSpec:
    # Provided at registration:
    agent_template: Agent         # name, model, description, tools (domain only)
    routing_terms: list[str]      # keywords for decide_route() scoring
    reroute_reason: str           # reason string used in request_reroute() calls

    # Derived after finalization:
    name: str                     # from agent_template.name
    description: str              # from agent_template.description
    domain_tools: list            # from agent_template.tools
    direct_agent: Agent           # full direct-path agent
    helper_agent: Agent           # stripped helper for AgentTool use
    tool_names: set[str]          # names of direct_agent tools (excl. context tools)
```

### Registered experts

| Expert          | Routing terms                                                         | Reroute reason   |
|-----------------|-----------------------------------------------------------------------|------------------|
| `invoice_agent` | invoice, bill, approval, vat, amount, due date                        | "invoice domain" |
| `support_agent` | how do i, how to, where, screen, button, ui, workflow, help, upload, submit | "support domain" |

### Adding a new expert

1. Create `tools/expert_tools.py` with domain-specific tools
2. Create `prompts/expert_agent.txt` with `{reroute_section}` placeholder
3. Add `REROUTE_EXPERT` constant to `state.py` and include in `REROUTE_ALL`
4. Create `experts/expert_agent.py` calling `register(ExpertSpec(...))`
5. Import the module in `expert_registry.py`

Everything else (firewall allowlist, orchestrator helpers, routing terms) wires automatically.

---

## Routing Logic (`routing.py`)

Deterministic. No LLM call. Returns `RoutingDecision` with per-domain scores and
confidence so callers and observability tools can inspect routing decisions.

### RoutingDecision

```python
@dataclass
class RoutingDecision:
    mode: str           # "direct" | "planned" | "no_signal"
    selected_agent: str # expert name or "orchestrator_agent"
    reason: str         # human-readable explanation
    scores: dict        # {expert_name: int, ..., "planning": int}
    confidence: float   # 0.0 – 1.0
```

### Scoring priority

1. **Planning signals** (highest priority) — if any match → `orchestrator_agent`
   - Signals: "and then", "check whether", "validate and", "make sure", "before I",
     "after that", "if invalid", "if it fails", "if missing", "explain how to fix", "compare"
   - `confidence = min(1.0, planning_count / 3)`

2. **Multi-domain** — if ≥2 experts both score ≥2 → `orchestrator_agent`
   - Weak secondary signal (one domain ≥2, other = 1) → `no_signal` → triggers LLM router

3. **Single domain winner** — highest scoring expert → `direct` routing
   - `confidence = winner_score / total_score`

4. **No signal** — no domain keywords matched → `no_signal` → triggers LLM router

### Confidence threshold: `0.6`

Below this value on a `direct` decision, root agent bypasses the keyword winner and
invokes `llm_router_agent` instead.

---

## Agent Definitions

### `HybridRootAgent` (`agent.py`)

Custom `BaseAgent`. No LLM call of its own — purely orchestrates sub-agents.

**Turn flow:**

```
1. init_public_state(user_text)
2. decide_route(user_text) → RoutingDecision
3. Check public:follow_up_agent — if set and user text has no new domain signal,
   route back to same agent (skip steps 4–5)
4. If needs_llm_routing (no_signal or confidence < threshold):
   - Run llm_router_agent (strips its events from session)
   - Update public:routing with LLM result
5. Escalation loop (max depth 2):
   a. Run selected agent
   b. Check public:routing_escalation
   c. Map reroute reason → next agent, set public:task_note
   d. Repeat until no escalation or depth exceeded
6. Fallback to receptionist if no final response produced
7. append_conversation_log(...)
```

**Follow-up detection:**
- If `public:follow_up_agent` is set, check whether user message contains new domain
  signals (domain keywords present, or ≥3 words with no_signal)
- If no new signal: route back to the waiting agent, clear `follow_up_agent`
- If new signal: treat as fresh request, clear `follow_up_agent`

**Escalation chain:**
- `REROUTE_INVOICE` → `invoice_agent`
- `REROUTE_SUPPORT` → `support_agent`
- `REROUTE_MULTI`   → `orchestrator_agent`
- Unknown reason    → `orchestrator_agent` (with warning)

---

### `orchestrator_agent` (`agents/orchestrator_agent.py`)

Model: `gemini-2.5-flash`

Tools: `get_conversation_context`, `signal_follow_up`, `AgentTool(helper)` per expert

**Responsibilities:**
- Decide smallest plan to fully answer user request
- Call expert helpers (can run in parallel when independent)
- Synthesize one final answer
- Ask one clarifying question via `signal_follow_up()` if blocked on missing input

**Rules:**
- Call `get_conversation_context()` first
- Follow `public:task_note` as primary directive when set
- Parameter check before calling any helper — if input missing, call `signal_follow_up()` and stop
- MUST write non-empty final answer
- Only include information helpers actually returned (strict grounding)
- Output captured via `output_key = "public:final_answer"`

---

### `receptionist_agent` (`agents/receptionist_agent.py`)

Model: `gemini-2.5-flash`

Tools: `signal_follow_up`, `request_reroute`

**Responsibilities:**
- Greet users on first contact
- Handle lightweight turns: thanks, goodbye, "what can you help with?"
- Route unambiguous domain requests via `request_reroute(reason)`

**Rules:**
- When ambiguous: call `signal_follow_up()` first, then ask one question
- Never answer invoice/support domain questions — reroute immediately
- Never produce partial answer before calling `request_reroute()`
- Output captured via `output_key = "public:last_agent_summary"`

---

### `llm_router_agent` (`agents/router_agent.py`)

Model: `gemini-3.1-flash-lite-preview` (fast, minimal)

`include_contents='none'` — sees only current user turn.

**Output schema:** `LlmRouteOutput`
```python
selected_agent: str   # one of the routing targets
reason: str           # brief explanation
```

**Routing targets:**
- `invoice_agent` — invoice domain operations
- `support_agent` — UI guidance, how-to questions
- `orchestrator_agent` — simultaneous multi-domain requests
- `receptionist_agent` — greetings, ambiguous, out-of-scope

Uses `public:last_answer` from state as context for ambiguous follow-ups.

Output written to `temp:llm_route`. Root agent reads and updates `public:routing`.

---

### `invoice_agent` (`experts/invoice_agent.py`)

Model: `gemini-3.1-flash-lite-preview`

**Domain tools:** `get_invoice_details`, `validate_invoice`, `update_invoice_field`

**Direct-path tools (additional):** `get_conversation_context`, `request_reroute`, `signal_follow_up`

**Responsibilities:**
- Answer invoice status, validation, field, amount, VAT, due date questions
- Inspect facts and identify issues
- Execute field updates (with user confirmation for sensitive fields)

**Key rules:**
- READ requests: if invoice ID present, return all fields. If no ID, call `signal_follow_up()` first.
- WRITE requests: if required field missing, call `signal_follow_up()` first.
- HOW-TO requests ("how do I…"): out of scope — one sentence, then stop.
- Only report what tools returned (strict grounding, no invented data).
- Write normalized facts to `public:facts` via tool calls.
- NEVER mention routing infrastructure to user.
- Output captured via `output_key = "public:last_agent_summary"`.

---

### `support_agent` (`experts/support_agent.py`)

Model: `gemini-3.1-flash-lite-preview`

**Domain tools:** `get_support_steps`, `get_help_article`

**Direct-path tools (additional):** `get_conversation_context`, `request_reroute`, `signal_follow_up`

**Responsibilities:**
- Answer product/workflow questions: screen navigation, UI steps, process guidance
- Explain how to use the system

**Key rules:**
- HOW-TO questions ("how do I", "how to", "where do I") are ALWAYS this agent's scope —
  never reroute on how-to, even if the subject involves invoices.
- Only reroute for explicit data requests: "show me invoice X", "update field Y".
- If all tools return `found=false`, tell user you don't have guidance — never supplement
  with general knowledge or invented UI steps.
- Call `signal_follow_up()` if a critical detail is missing.
- Output captured via `output_key = "public:last_agent_summary"`.

---

## Tools

### `tools/context_tools.py`

**`get_conversation_context(tool_context)`**
- Returns `{conversation_log, facts, open_questions}` from public state
- If `public:task_note` is set, includes it in the return dict
- Called at start of each agent turn — zero cache fingerprint impact

**`signal_follow_up(tool_context)`**
- Sets `public:follow_up_agent = current_agent_name`
- Call when response ends with clarifying question (not a final answer)
- Root agent routes next user reply back to this agent automatically

**`request_reroute(reason, tool_context)`**
- Sets `public:routing_escalation = {"reason": reason}`
- Must be called BEFORE generating any response text
- Root agent escalates to appropriate agent based on reason

---

### `tools/invoice_tools.py`

**`get_invoice_details(invoice_id, tool_context)`**
- Returns invoice fields: id, status, vendor, amount, due_date, vat_rate, missing_fields
- Merges result into `public:facts`

**`validate_invoice(invoice_id, tool_context)`**
- Returns `{valid: bool, issues: list[str]}`
- Reads `public:facts`, merges `validation_result` back

**`update_invoice_field(invoice_id, field_name, value, tool_context)`**
- Implemented as `FunctionTool` with `require_confirmation` callback
- Confirmation required for sensitive fields: `vat_rate`, `due_date`, `amount`, `vendor_name`
- Returns `{status, invoice_id, field_name, value}`

---

### `tools/support_tools.py`

**`get_support_steps(issue_code, tool_context)`**
- Returns `{found: bool, issue_code, steps: list[str]}`
- Known codes: `missing_vat`, `approval_failed`, `upload_invoice`
- Returns `found=false` for unknown codes
- Agents MUST NOT answer if `found=false`

**`get_help_article(topic, tool_context)`**
- Returns `{found: bool, topic}`
- POC stub — always returns `found=false`
- Placeholder for future knowledge base integration

---

## Plugin (`plugins/firewall.py`)

**`FirewallPlugin(BasePlugin)`**

Allowed tools are auto-derived from the expert registry:
```
ALLOWED_TOOLS = context_tools | domain_tools | agent_tools (per expert)
```

**`before_model_callback`**
- Returns `None` (pass through)
- Does NOT modify `system_instruction` — would break cache fingerprint
- To inject dynamic context: append `Content(role='user')` to `llm_request.contents`

**`before_tool_callback`**
- Rejects any tool not in `ALLOWED_TOOLS` → returns error dict
- For `update_invoice_field`: records `PUBLIC_PROPOSED_ACTION` for audit trail
- Returns `None` to allow through

**`after_tool_callback`**
- Removes `raw_payload` and `internal_trace` from result dicts
- Returns sanitized result

---

## App Configuration (`agent.py`)

```python
app = App(
    name="fast_multi_agent_system",
    root_agent=root_agent,
    plugins=[FirewallPlugin()],
    context_cache_config=ContextCacheConfig(
        min_tokens=512,
        cache_intervals=20,
        ttl_seconds=3600,
    ),
)
```

Cache fingerprint = `system_instruction + tools`. Never mutated after init.
Dynamic context is appended to `llm_request.contents` (after cached prefix).

---

## Prefix Caching Design

### What ADK caches

`ContextCacheConfig` uses Gemini context caching. Cache hit = those tokens not
re-processed. Fingerprint = `system_instruction + tools + tool_config + first N turns`.

### What must stay static

`Agent.instruction` must be a static string. Any dynamic injection changes the
fingerprint → cache miss every call.

| Approach                                        | Cache impact     |
|-------------------------------------------------|------------------|
| Static string loaded from file                  | HIT — every call |
| `{app:something}` in instruction template       | MISS — every turn|
| Dynamic context appended to `contents` array    | HIT — no impact  |
| `get_conversation_context()` tool call          | HIT — no impact  |

### Why `get_conversation_context()` is correct

Tools are called after cache lookup — they have zero cache fingerprint impact.
Agents call this tool explicitly at turn start to pull conversation log and facts.
System instruction stays static → maximum cache hit rate.

---

## Routing Flows

### Direct — 1 LLM call

```
User: "What is wrong with invoice 456?"
  decide_route() → scores: {invoice: 1, support: 0, planning: 0}, confidence: 1.0
  mode: "direct", selected: "invoice_agent"
  → invoice_agent (LLM call 1):
      get_invoice_details("456") → writes public:facts
      responds → output_key writes to public:last_agent_summary
  → append_conversation_log(agent="invoice_agent", ...)
```

### LLM-assisted route — 2 LLM calls

```
User: "I need help with something on my account"
  decide_route() → scores all zero, confidence: 0.0, mode: "no_signal"
  → llm_router_agent (LLM call 1, no history):
      output: selected_agent="support_agent"
  → support_agent (LLM call 2):
      responds → output_key writes to public:last_agent_summary
  → append_conversation_log(agent="support_agent", ...)
```

### Planned — 3–4 LLM calls

```
User: "Check invoice 456 and explain how to fix the missing VAT in the UI."
  decide_route() → planning signal ("explain how to fix"), mode: "planned"
  → orchestrator_agent (LLM call 1):
      get_conversation_context()
      calls invoice_tool + support_tool (parallel)
        → invoice_agent helper (LLM call 2, no history)
        → support_agent helper (LLM call 3, no history)
  → orchestrator_agent synthesizes (LLM call 4 or same as call 1):
      output_key writes to public:final_answer
  → append_conversation_log(agent="orchestrator_agent", ...)
```

### Re-route — 2 LLM calls

```
User: "Where on the invoice screen do I set the VAT rate?"
  decide_route() → scores: {invoice: 2, support: 1, planning: 0}, confidence: 0.67
  mode: "direct", selected: "invoice_agent"
  → invoice_agent (LLM call 1):
      get_conversation_context()
      determines: UI guidance question, outside invoice domain
      request_reroute("support domain")
      → public:routing_escalation = {"reason": "support domain"}
  → root escalation handler:
      maps "support domain" → support_agent
      sets public:task_note with context
  → support_agent (LLM call 2):
      ... answers UI question
  → append_conversation_log(agent="support_agent", ...)
```

### Follow-up continuation — 1 LLM call

```
Turn N: invoice_agent calls signal_follow_up()
  → public:follow_up_agent = "invoice_agent"
  → invoice_agent asks: "What is the invoice ID?"

Turn N+1 — User: "456"
  root detects public:follow_up_agent = "invoice_agent"
  user text has no new domain signals → route back to invoice_agent
  → invoice_agent (LLM call 1): continues with invoice ID "456"
```

### Mutation — 1 LLM call + confirmation pause

```
User: "Update invoice 456 with VAT 25%."
  → invoice_agent (LLM call 1):
      proposes update_invoice_field("456", "vat_rate", "25%")
  → FirewallPlugin.before_tool_callback:
      records public:proposed_action
  → ADK confirmation pause: prompts user
  → user confirms → tool executes → invoice_agent responds
```

---

## Delegation Rules

| Path    | Owns the turn        | May ask clarifying questions |
|---------|----------------------|------------------------------|
| Direct  | Routed expert        | The expert only              |
| Planned | `orchestrator_agent` | The orchestrator only        |

- Direct-path expert MUST NOT delegate to another expert unless the request clearly
  became multi-domain mid-turn. Use `request_reroute()` instead.
- On the planned path, helpers return structured results; orchestrator synthesizes the
  final answer.

---

## What Not To Do

| Anti-pattern                                              | Why                                                         |
|-----------------------------------------------------------|-------------------------------------------------------------|
| Route every request through orchestrator                  | Adds latency and an unnecessary LLM call                    |
| All agents reason every turn                              | Creates committee behavior and duplicated questions         |
| Put chain-of-thought or raw tool dumps in `public:*`      | Pollutes shared whiteboard                                  |
| Use `transfer` instead of `AgentTool`                     | Loses orchestrator ownership of the turn                    |
| Rely on confirmation alone for security                   | Confirmation is UX, not an auth mechanism                   |
| Store non-serializable objects in `session.state`         | Breaks ADK session persistence                              |
| Use `DatabaseSessionService` or `VertexAiSessionService`  | Not supported with `require_confirmation` (experimental)    |
| Set `include_contents='none'` on direct-path agents       | They need full history for "same room" continuity           |
| Write `public:last_agent_summary` manually inside tools   | `output_key` handles it; manual writes create duplicates    |
| Modify `system_instruction` in `before_model_callback`    | Changes cache fingerprint; causes miss every call           |
| Call `request_reroute()` after producing a partial answer | Leaves partial state; escalated agent must start clean      |
| Call `request_reroute()` on uncertainty alone             | Try first; reroute only when clearly out of domain          |
| Call `signal_follow_up()` on the orchestrator's behalf    | Helpers never own the conversation; orchestrator asks       |
| Give `llm_router_agent` tools or history                  | It is a pure classifier — tools add latency and confusion   |
| Use a large/slow model for `llm_router_agent`             | Fast model only — classifier overhead must stay minimal     |
| Answer when all support tools return `found=false`        | Never supplement with general knowledge or invented steps   |

---

## `__init__.py`

```python
from .agent import root_agent
```

ADK's module loader expects `root_agent` importable from the package root.
