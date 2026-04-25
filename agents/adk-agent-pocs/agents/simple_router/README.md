# simple_router

A multi-agent system for invoice management and product support. A lightweight router classifies every user message and transfers it to one of four specialist agents. The router never answers users directly.

## Architecture

```
User message
    │
    ▼
router_agent              ← LLM classifier, flash-lite, include_contents="none"
    │
    ├─ before_model_callback (checked in order, each can short-circuit):
    │     ├─ circuit_breaker            — router called > 5 times this turn → return apology, break loop
    │     ├─ reroute_guard              — expert called signal_reroute(); bypass all shortcuts,
    │     │                               let LLM re-classify freely (consumes public:reroute_requested)
    │     ├─ out_of_scope_shortcut      — OOS keyword detected → override instruction,
    │     │                               LLM generates decline in user's language (no transfer)
    │     ├─ follow_up_shortcut         — follow-up state set + short answer
    │     │                               → synthetic transfer (no LLM call)
    │     │                               (loop guard: same agent re-registering → fall through to LLM)
    │     ├─ static_route_shortcut      — high-confidence keyword score
    │     │                               → synthetic transfer (no LLM call)
    │     └─ context_prefetch_shortcut  — always fires on LLM-path turns; pre-executes
    │                                     get_conversation_context before the LLM call,
    │                                     reducing the router from 2 LLM calls to 1
    │
    ├─ STEP 1: HOW-TO Gate ──────────────────────► support_agent
    │           (how do I / how to / walk me through / …)
    │
    ├─ STEP 2: Content classification
    │     ├─ invoice vocab + action verb ──────────► invoice_agent
    │     ├─ two intents (data + guidance) ────────► orchestrator_agent
    │     │                                               ├── invoice_agent_helper  ┐ parallel
    │     │                                               └── support_agent_helper  ┘
    │     ├─ troubleshooting / UI error ────────────► support_agent
    │     └─ greeting / ambiguous / out-of-scope ───► receptionist_agent
    │
    └─ [public:follow_up_agent set, unclear intent] ─► agent named in public:follow_up_agent
                                                         (invoice_agent | support_agent | receptionist_agent)
```

> `public:follow_up_agent` is **not** an agent — it is a session-state key holding the name of
> whichever expert last called `signal_follow_up()`. The router reads this value and transfers
> to that existing agent. When the key is unset this last branch never fires.

## Performance design

Three mechanisms work together to keep response latency low:

| Mechanism | Goal | Details |
| --- | --- | --- |
| **Minimal LLM calls** | Fewer round-trips to Gemini | Router-bypass shortcuts cut single-domain turns from 2 calls to 1; orchestrator helpers run in parallel |
| **Gemini prefix caching** | Re-use cached system-prompt computation | `router_agent` and `receptionist_agent` get a guaranteed cache hit every call; expert agents maintain a stable history prefix |
| **Compact conversation history** | Fewer input tokens + stable cache prefix | Prior tool calls are stripped each turn; structured data travels through session state, not the conversation thread |

The sections below detail each mechanism. Every code-level decision in the system either serves one of these goals or explicitly trades one against another.

### LLM call budget per turn

| Path                                                        | LLM calls                                           |
| ----------------------------------------------------------- | --------------------------------------------------- |
| Follow-up shortcut fires (callback bypasses router)         | **1** — expert only                                 |
| Static route shortcut fires (high-confidence keyword match) | **1** — expert only (router LLM skipped)            |
| Single domain, normal turn                                  | **1** — context prefetch fires → expert only        |
| Multi-domain (orchestrator)                                 | **3** — router + orchestrator + helpers in parallel |
| Follow-up shortcut skips (new request detected)             | **1** — context prefetch fires → expert only        |

Static routing is **disabled by default**. Enable with `SIMPLE_ROUTER_STATIC=1`.

## Prefix caching

Two agents qualify for guaranteed Gemini prefix caching: `router_agent` and `receptionist_agent`.

```python
Agent(
    model="gemini-3.1-flash-lite-preview",
    instruction=load_prompt("router_agent"),   # loaded from .txt at import time, never changes
    tools=[get_conversation_context],          # defined once, never mutated
    include_contents="none",                   # ← conversation history excluded from fingerprint
)
```

The cache fingerprint is `system_instruction + tools`. Both are static. `include_contents="none"` removes conversation history from the request entirely, so the fingerprint is identical on every call — Gemini can cache the system-prompt prefix across every routing turn.

`invoice_agent`, `support_agent`, and `orchestrator_agent` do **not** set `include_contents="none"` — they need conversation history for multi-turn context — so they do not qualify for the guaranteed-hit path. They still benefit from `strip_tool_history_callback` (compact history) and `inject_facts_callback` (facts appended at the tail, after the stable prefix), which together keep their history compact and stable (see [Shared state and clean conversation history](#shared-state-and-clean-conversation-history)).

### Request lifecycle

Understanding *when* the cache lookup happens explains why the tool approach is safe.

```
① system_instruction   ─┐
② tools list            ├── fingerprint hashed → cache lookup   ← decision made here
③ conversation history ─┘   (excluded via include_contents="none" for router/receptionist)
             │
             ▼
④ new user message appended to contents
⑤ model starts generating
⑥ model calls get_conversation_context()                        ← tool runs here
⑦ tool reads session.state, returns facts + follow_up_agent
⑧ model sees result, decides routing target
```

The cache hit or miss is decided at step ③. The tool executes at step ⑥. Whatever `get_conversation_context()` returns — accumulated facts, follow-up agent state — has no effect on the fingerprint because the decision is already made.

### What keeps the fingerprint stable

This table applies to `router_agent` and `receptionist_agent` only — the two agents that use `include_contents="none"`.

| Element | In the LLM request? | How |
| --- | --- | --- |
| `system_instruction` | Yes — stable | Loaded from `.txt` at import time via `load_prompt()`, never mutated |
| `tools` list | Yes — stable | Defined once per agent, never changed at runtime |
| Conversation history | **No — not sent** | `include_contents="none"` removes it from the request entirely. The router does not need history: it classifies the *current message only*, and any session context it needs (accumulated facts, follow-up agent) arrives via the `get_conversation_context()` tool call *after* the cache hit (see lifecycle diagram above). |
| Dynamic context (facts, follow-up state) | **No — not sent** | Delivered by `get_conversation_context()` tool after cache lookup — never touches the fingerprint |

### What would break it

```python
# BREAKS — instruction changes every turn as facts accumulate
Agent(instruction=f"Follow-up agent: {session.state['public:follow_up_agent']}")

# BREAKS — modifying system_instruction inside before_model_callback
# changes the prefix the model sees, invalidating the cached version
def before_model_callback(callback_context, llm_request):
    llm_request.config.system_instruction += f"\nContext: {facts}"  # don't do this

# BREAKS — removing include_contents="none" re-introduces conversation history
# into the fingerprint; every turn has a different history → miss every call
Agent(
    instruction=load_prompt("router_agent"),
    # include_contents="none"  ← removed: fingerprint now changes each turn
)

# SAFE — static instruction, dynamic data fetched by tool after cache lookup
Agent(
    instruction=load_prompt("router_agent"),   # never changes
    tools=[get_conversation_context],          # never changes
    include_contents="none",                   # history excluded from fingerprint
)
```

If you need to inject per-call dynamic data (user role, tenant ID, etc.), append it as a `Content(role="user")` entry to `llm_request.contents` inside `before_model_callback`. Content added after the cached prefix is not part of the fingerprint and does not cause a miss.

**One intentional exception — out-of-scope detection.** When `out_of_scope_shortcut` detects an OOS keyword it replaces `system_instruction` with a tailored decline prompt. This deliberately breaks the cache for that call in exchange for a correctly localized refusal. OOS requests are rare edge cases where correctness matters more than latency, so the trade-off is accepted. Normal routing turns are unaffected.

## Shared state and clean conversation history

Two mechanisms work together to give every agent a clean, focused view of the conversation: **structured facts** written to session state and **tool history stripping** that keeps the LLM context free of noise.

### Why it matters

The router transfers control to whichever expert matches each turn. When `invoice_agent` handles turn 3, it should not see `support_agent`'s internal tool calls from turn 1 — only the user's words, prior agent text responses, and any structured data collected along the way. Tool call chains from prior turns add tokens, confuse reasoning, and break prefix caching. The goal is for every agent to share one clean dialogue that any of them could pick up and continue.

### How facts flow through the session

Domain tools write structured data directly into `public:session_facts` in ADK session state via `set_fact()`. Before each LLM call, `inject_facts_callback` reads `public:session_facts` and `public:fact_history`, builds a structured view via `_flat_facts`, and appends it as a `[session facts: {...}]` user message immediately after the last real user message. Expert agents do **not** call `get_conversation_context()` — they receive facts via injection:

```
User:           "show me invoice 42"
inject_facts_callback fires → appends: [session facts: {"_summary": "No facts loaded yet."}]
invoice_agent:  get_invoice_details("42")  → calls set_fact() for each field:
                                              public:session_facts = {
                                                invoice_id: {value: "42", status: "draft"},
                                                status:     {value: "OPEN", status: "draft"},
                                                vendor_name:{value: "Acme", status: "draft"},
                                                amount:     {value: "1250.00", status: "draft"}
                                              }
                responds: "Invoice 42 — Acme, $1,200, due 2026-04-01"
                persist_facts_callback fires → promotes all drafts to "persisted"

User:           "update the VAT rate to 25%"
inject_facts_callback fires → appends: [session facts: {
  "invoice_id":  {"value": "42",      "previous": []},
  "status":      {"value": "OPEN",    "previous": []},
  "vendor_name": {"value": "Acme",    "previous": []},
  "amount":      {"value": "1250.00", "previous": []},
  "_summary": "Current: invoice_id=\"42\", status=\"OPEN\", vendor_name=\"Acme\", amount=\"1250.00\"."
}]
invoice_agent:  sees current facts in the injected message — no re-fetch needed
```

The injected view format is `{key: {"value": current, "previous": [older_values], "description": ..., "loaded_at": ..., "set_by": ...}, "_summary": "..."}`. The `previous` list contains prior values oldest-first (empty when the fact has never been updated). Metadata fields (`description`, `loaded_at`, `set_by`) record what the fact represents, when it was last written, and which agent wrote it. The `_summary` key provides a plain-English scan line. When a fact has been updated across turns, `previous` shows the history without requiring the LLM to navigate nested JSON.

Facts accumulated during the session — invoice ID, validation results, field values — are available to any agent on any subsequent turn without re-fetching. The session facts key is `public:session_facts`; each raw entry carries `{status, description, value, fact_id}`.

### How follow-up routing works (`signal_follow_up`)

When an expert asks the user a clarifying question it calls `signal_follow_up()` before responding. This writes the calling agent's name to `public:follow_up_agent` in session state — a one-shot signal telling the router that the next user message belongs to this expert.

Without it the router re-classifies every message from scratch. A bare reply like `"42"` after `invoice_agent` asked `"Which invoice ID?"` carries no domain signal of its own — the router would have to guess. `signal_follow_up()` makes the intent explicit:

```
invoice_agent:  needs an invoice ID, asks the user
                → calls signal_follow_up()
                  writes: public:follow_up_agent = "invoice_agent"
                → responds: "Which invoice are you referring to?"
                → stops. No more tool calls this turn.

User:           "42"

router_before_model_callback fires before any LLM call:
  1. reads  public:follow_up_agent = "invoice_agent"
  2. "42" is short, no command/question opener
     → follow_up_shortcut fires
     → clears public:follow_up_agent  (consumed)
     → returns synthetic transfer_to_agent("invoice_agent")
                                        ↑ no router LLM call

inject_facts_callback fires → appends [session facts: {"invoice_id": ...}] for invoice_agent
invoice_agent:  sees current facts and the user's reply "42"
```

**Three properties guarantee correctness:**

**Consumed exactly once.** Whether the follow-up shortcut fires or the router LLM runs, `public:follow_up_agent` is always cleared on the first `get_conversation_context()` call of the next turn. The signal never persists across two turns accidentally.

**New requests override it.** If the user sends a new command (`"show me invoice 99"`) while a follow-up is registered, the shortcut detects a new-request opener, falls through to the router LLM, and the signal is cleared when the LLM calls `get_conversation_context()`. Routing proceeds by content.

**Not visible to sub-agents.** `get_conversation_context()` returns `follow_up_agent` only to `router_agent`. Expert agents never see it, so they cannot accidentally act on a signal meant for the router.

### How tool history is stripped (`_history.py`)

`strip_tool_history_callback` is injected automatically by `expert_registry.py` as a `before_model_callback` on every expert's `direct_agent`. Before each LLM call it rewrites `llm_request.contents` in two passes:

**Pass 1** — removes noise from any position in the contents list:

- ADK `For context:` messages (inserted by ADK when the router transfers to a sub-agent)
- Stale `[session facts:]` messages from prior turns (a fresh one is appended by `inject_facts_callback` immediately after)

**Pass 2** — strips tool call artefacts from prior turns:

- Finds the last real user text message (ignoring `For context:` and `[session facts:]` entries) to establish the current-turn boundary.
- Removes `function_call` and `function_response` parts from all turns before that boundary.
- Everything at or after the boundary (current turn) is left intact so multi-step reasoning within the turn still works.

**Why it is its own file.** The natural home for a callback is `callbacks.py`, but that would create a circular import: `expert_registry` → `callbacks` → `routing` → `expert_registry`. By living in `_history.py` — a file with zero local imports — `expert_registry.py` and `sub_agents/orchestrator_agent.py` can both import it safely. The leading underscore signals it is an internal infrastructure module with no standalone public API, not intended to be imported directly by external consumers.

```
Conversation contents sent to the LLM (after stripping + facts injection):

  [For context: ...]                                               ← stripped (Pass 1)

  turn 1  [user  text]             "show me invoice 42"           ← kept
  turn 1  [model function_call]    get_invoice_details("42")      ← stripped (Pass 2)
  turn 1  [user  function_response] {invoice_id: "42", ...}       ← stripped (Pass 2)
  turn 1  [model text]             "Invoice 42 — Acme, $1,200…"  ← kept

  turn 2  [user  text]             "update the VAT to 25%"        ← kept  ← boundary
  turn 2  [model function_call]    validate_invoice("42")         ← kept (current turn)
  turn 2  [user  function_response] {valid: false, issues: [...]} ← kept (current turn)
  turn 2  [user  text]             [session facts: {...}]          ← injected at END by inject_facts_callback
```

The boundary is the **last real user text message** — not a `function_response` entry, which also carries `role="user"` in the ADK protocol. Everything before the boundary has its tool parts stripped; the current turn is left intact so multi-step reasoning within the turn still works.

The result: each expert sees a clean dialogue of user messages and agent text responses, plus the injected facts snapshot and the current turn's tool calls. Structured facts travel through `public:session_facts` session state and are re-injected each turn — not carried in the conversation thread.

### Combined effect on prefix caching

The mechanisms reinforce each other:

| Agent | `include_contents` | Tool history stripped | Facts delivery | Cache behaviour |
| --- | --- | --- | --- | --- |
| `router_agent` | `none` | N/A | pre-executed by `context_prefetch_shortcut` before LLM call | Perfect hit every call — fingerprint is always `system_instruction + tools` |
| `receptionist_agent` | `none` | N/A | (none — no domain tools) | Perfect hit every call |
| `invoice_agent` | `default` | Yes | via `inject_facts_callback` (tail injection) | Smaller, stable history → better cache reuse |
| `support_agent` | `default` | Yes | via `inject_facts_callback` (tail injection) | Smaller, stable history → better cache reuse |
| `orchestrator_agent` | `default` | Yes | via `inject_facts_callback` (tail injection) | Smaller, stable history → better cache reuse |

Router and receptionist exclude conversation history entirely — their fingerprint never changes, so every call is a guaranteed cache hit. Expert agents include conversation history for multi-turn context, but the stripped version is much smaller and contains only what matters: what the user said and what each agent replied. Facts are appended **after** the stable history prefix (as a tail injection), so the prefix Gemini can cache is the full `SI + prior conversation` — only the tail varies turn-to-turn.

## Running

```bash
# Start the agent
uv run adk web agents/simple_router

# Run unit tests (no LLM calls)
make -C agents/simple_router test

# Run all integration evals (calls Gemini)
make -C agents/simple_router eval

# Run only routing accuracy evals (tool trajectory, threshold 1.0)
make -C agents/simple_router eval-routing

# Run specific routing eval cases (comma-separated eval IDs)
make -C agents/simple_router eval-routing CASES=follow_up_shortcut_fires,static_route_guard_releases_next_turn

# Run only response quality evals (final_response_match_v2, threshold 1.0)
make -C agents/simple_router eval-response

# Run specific response eval cases
make -C agents/simple_router eval-response CASES=out_of_scope_danish

# Run behavioral compliance evals (rubric-based, threshold 0.8)
make -C agents/simple_router eval-behavior
make -C agents/simple_router eval-behavior CASES=behavior_oos_decline_danish

# Run error/robustness evals (rubric-based, threshold 0.8)
make -C agents/simple_router eval-error

# Run subagent eval suites independently (no router involved)
make -C agents/simple_router eval-subagents

# Run a single subagent eval
make -C agents/simple_router eval-invoice-agent
make -C agents/simple_router eval-support-agent
make -C agents/simple_router eval-receptionist-agent
make -C agents/simple_router eval-orchestrator-agent
```

Set `SIMPLE_ROUTER_DEBUG=1` to enable per-agent lifecycle and tool call logging with elapsed times.

## Routing at a glance

**Step 1 — HOW-TO Gate (checked first, always):**
Messages starting with `"how do I"`, `"how to"`, `"how can I"`, `"what steps"`, `"walk me through"`, or `"where do I"` → `support_agent`. Fires even when the message also mentions invoice IDs or billing terms.

**Step 2 — Content classification:**

| Agent | When |
|-------|------|
| `orchestrator_agent` | Two separate intents (invoice data + guidance) joined by `and`, `also`, `plus`, `—`, `+`, `/`, or a comma |
| `invoice_agent` | Invoice/billing vocabulary + action verb (`show`, `update`, `validate`) |
| `support_agent` | Troubleshooting, UI errors, non-how-to operational questions |
| `receptionist_agent` | Greetings, out-of-scope, ambiguous |

## How to add a new expert

The expert registry auto-wires most of the plumbing. You only need to follow these 7 steps.

### Steps 1–4 (auto-wire after this)

**1. Create your domain tools**

```python
# tools/expense_tools.py
from google.adk.tools import ToolContext
from .context_tools import set_fact

def get_expense_report(expense_id: str, tool_context: ToolContext) -> dict:
    """Load an expense report by ID."""
    report = {...}
    set_fact("expense_id", expense_id, "Expense report ID", tool_context)
    return report
```

Export from `tools/__init__.py`:
```python
from .expense_tools import get_expense_report
```

**2. Create the agent prompt**

```
# prompts/expense_agent.txt
{shared_rules}

You are the expense agent. Answer questions about expense reports only.

...
```

Available placeholders:
- `{shared_rules}` — context-first, grounding, and hygiene rules common to all agents
- `{howto_triggers}` — the canonical list of how-to question openers

**3. Register the agent**

```python
# sub_agents/expense_agent.py
from google.adk.agents import Agent
from ..expert_registry import register
from ..tools import get_expense_report

register(
    Agent(
        name="expense_agent",
        model="gemini-3.1-flash-lite-preview",
        description=(
            "Handles expense reports: viewing, submitting, and approving expense claims."
        ),
        tools=[get_expense_report],
    )
)
# No assignment needed — register() does all the wiring.
```

The registry automatically builds two variants:
- **`direct_agent`** — used by the router; gets `signal_follow_up` added; facts delivered via `inject_facts_callback` (before_model_callback) and persisted via `persist_facts_callback` (after_agent_callback); `_log_thoughts_callback` as after_model_callback; `disallow_transfer_to_parent=True`, `disallow_transfer_to_peers=True`; thinking enabled (`thinking_level="low"`, `include_thoughts=True`)
- **`expense_agent_helper`** — stateless AgentTool for orchestrator; `include_contents="none"`, no `signal_follow_up`, no transfers, `output_key` set; thinking enabled (`thinking_level="low"`, `include_thoughts=True`)

The `description` field doubles as the orchestrator domain label — keep it specific.

**4. Import before orchestrator build**

```python
# sub_agents/__init__.py  (add before orchestrator build line)
from . import expense_agent as _  # noqa: F401
```

### Steps 5–7 (manual edits required)

**5. Add to router's sub_agents list**

```python
# agent.py
from .sub_agents import expense_agent  # add import

router_agent = attach(Agent(
    ...
    sub_agents=[
        ...
        attach(expense_agent, debug=_DEBUG),   # add here
    ],
))
```

**6. Add a routing rule**

```
# prompts/router_agent.txt — add a new entry under ROUTING TARGETS

  expense_agent
    → requests about expense reports, reimbursements, or travel claims
      e.g. "show me expense report 5", "submit my travel claim"
      NOT: "show me invoice 10" → that's invoice_agent
```

Update the orchestrator separators section if the new agent can appear in composite requests.

**7. Add routing patterns to the receptionist**

```
# prompts/receptionist_agent.txt — add to DIRECT ROUTING PATTERNS

expense_agent:
- "show me expense", "expense report", "submit expense", "travel claim"
- Explicit expense ID references
```

### Verify

```bash
make -C agents/simple_router test   # unit tests pass
make -C agents/simple_router eval   # integration evals pass (router-level)
```

Add routing cases to `eval/routing_evalset.json` covering: basic routing, a follow-up ID flow, and an out-of-scope negative.

Add a subagent eval app under `eval_apps/<agent_name>/` so the new agent can be evaluated independently of the router. Copy an existing eval app as a template and add an `evalset.json` with cases for the agent's core tools. Run with:

```bash
make -C agents/simple_router eval-<agent_name>
```

## Project structure

```
agents/simple_router/
├── agent.py                    # Root agent — router wiring
├── expert_registry.py          # Expert registration and variant building
├── callbacks.py                # before_model_callback shortcuts (reroute guard, OOS decline, follow-up, static route, context prefetch)
├── oos_detection.py            # OOS keyword vocabulary (multilingual) and instruction override
├── follow_up_detection.py      # LLM-free follow-up classifier (NEW_REQUEST_STARTS, is_follow_up_answer)
├── routing.py                  # Deterministic keyword scorer (RoutingDecision, no LLM)
├── _facts_callbacks.py         # inject_facts_callback, persist_facts_callback, router_force_context_callback
├── _history.py                 # strip_tool_history_callback (no local imports — avoids circular import)
├── debug.py                    # Optional per-agent debug callbacks with timing
├── SPEC.md                     # Full system specification
│
├── prompts/
│   ├── router_agent.txt        # Routing policy
│   ├── invoice_agent.txt       # Invoice domain behavior
│   ├── support_agent.txt       # Support domain behavior
│   ├── receptionist_agent.txt  # Fallback/conversational behavior
│   ├── orchestrator_agent.txt  # Multi-domain composition
│   ├── shared_rules.txt        # Rules injected into all expert prompts
│   └── howto_triggers.txt      # How-to trigger phrases (single source of truth)
│
├── sub_agents/
│   ├── __init__.py             # Import order + orchestrator build
│   ├── invoice_agent.py        # register(Agent(...))
│   ├── support_agent.py        # register(Agent(...))
│   ├── receptionist_agent.py   # Standalone (not registry-managed)
│   └── orchestrator_agent.py   # Built dynamically after all experts registered
│
├── tools/
│   ├── context_tools.py        # get_conversation_context, signal_follow_up, signal_reroute, set_fact, search_facts, get_latest_fact
│   ├── invoice_tools.py        # Invoice domain tools (note_invoice_id, get_invoice_details, …)
│   └── support_tools.py        # Support domain tools
│
├── tests/
│   ├── test_callbacks.py       # Unit tests for routing callbacks
│   ├── test_facts_callbacks.py # Unit tests for inject/persist facts callbacks
│   ├── test_history.py         # Unit tests for strip_tool_history_callback
│   └── test_expert_registry.py # Unit tests for HOWTO_TRIGGERS and get_direct
│
├── eval/
│   ├── routing_evalset.json      # Routing accuracy (30 cases)
│   ├── routing_eval_config.json  # Scoring: tool_trajectory_avg_score, threshold 1.0
│   ├── response_evalset.json     # Response quality (out-of-scope declines, etc.)
│   ├── response_eval_config.json # Scoring: final_response_match_v2, threshold 1.0
│   ├── behavior_evalset.json     # Behavioral compliance (8 cases: OOS language, orchestrator, confidentiality, stale-context)
│   ├── behavior_eval_config.json # Scoring: rubric_based_final_response_quality_v1, threshold 0.8
│   ├── error_evalset.json        # Robustness & error handling (3 cases)
│   └── error_eval_config.json    # Scoring: rubric_based_final_response_quality_v1, threshold 0.8
│
└── eval_apps/                    # Thin wrappers to eval each subagent independently
    ├── invoice_agent/            # tool_trajectory_avg_score (4 cases: show, validate, multi-turn, state)
    ├── support_agent/            # rubric_based_final_response_quality_v1 (4 cases: how-to flows)
    ├── receptionist_agent/       # tool_trajectory_avg_score (4 cases: greeting, capabilities, intent, OOS)
    └── orchestrator_agent/       # rubric_based response + tool_use quality (3 cases: combined requests)
```

## Key design decisions

**Router is a pure classifier.** It never produces conversational output. Every turn ends with a transfer.

**Prefix caching.** Router and receptionist use `include_contents="none"` + fully static prompts, making their system-prompt prefix cache-eligible on every call. Expert agents achieve stable prefixes by: (1) never modifying the system instruction at runtime, (2) stripping prior tool calls from history, (3) injecting facts as a tail message after the stable history prefix.

**Facts delivered via injection, not tool calls.** Expert agents receive `public:session_facts` as a `[session facts: {...}]` user message injected by `inject_facts_callback` before each LLM call. This keeps the system instruction static (good for caching) and eliminates a mandatory `get_conversation_context()` tool call from every expert turn. Only the router still calls `get_conversation_context()` — it needs to read `public:follow_up_agent`.

**Follow-up shortcut.** When an agent calls `signal_follow_up()` and the user replies with a short non-command answer (bare ID, "yes"/"no", ≤ 5 words), the `before_model_callback` injects a synthetic `transfer_to_agent` response without invoking the router LLM. Saves one flash-lite call per follow-up turn.

**Thinking enabled on expert agents.** `ThinkingConfig(thinking_budget=2048)` is applied to all expert `direct_agents` and helpers. Prior-turn thought parts are stripped by `strip_tool_history_callback` before each LLM call — without stripping, thought signatures would accumulate in conversation history, making the history fingerprint unpredictable and breaking prefix caching.

**Helper agents are stateless.** Orchestrator helpers run via `AgentTool` with `include_contents="none"` and a HELPER MODE suffix that prevents them from triggering agent transfers.

**Sensitive field writes require confirmation.** `update_invoice_field` is wrapped in `FunctionTool(require_confirmation=...)`, enforced at the ADK framework layer regardless of prompt content.
