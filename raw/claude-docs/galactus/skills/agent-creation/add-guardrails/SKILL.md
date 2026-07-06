---
name: add-guardrails
description: "Wire the galactus 5-layer safeguard pipeline into any agent. Reads the target agent first, generates integration code that fits the existing framework. Triggers on: 'add guardrails', 'wire safeguards', 'add input guard', 'add grounding check', 'add PII redaction'."
allowed-tools: Read Grep Glob Bash Write
---

You are wiring the shared galactus guardrail pipeline into an existing agent.

## Step 1 — Read the ref docs

Before generating any code, read:
1. `docs/support-agents/safeguards-architecture.md` — 5-layer model, what each layer does
2. `docs/support-agents/invocation-flow.md` — how guards wrap the request/response cycle
3. `docs/support-agents/grounding-methodology.md` — citation tiers for Layer 4

## Step 2 — Read the target agent

From `$ARGUMENTS` parse the agent path. Read `agent.py` / `main.py` to understand the framework. Read `src/guardrails/` to confirm the shared pipeline exists.

If no agent path given, ask: "Which agent? (e.g. `src/support_agents/hc_lg`)"

## Step 3 — Layer integration by framework

The shared pipeline is in `src/guardrails/`. Use it — do not duplicate.

### Layer 1 — Input guard (all frameworks)

```python
from src.guardrails import run_input_guard, InputGuardResult

# At the entry point (before any LLM call):
guard: InputGuardResult = run_input_guard(user_message)
if guard.blocked:
    return AssistantResponse(
        message=guard.refusal_message,
        contact_support=guard.escalate,
    )
```

### Layer 4 — Output grounding (all frameworks)

```python
from src.guardrails import run_output_guard, OutputGuardResult

# After generating the response, before returning:
grounding: OutputGuardResult = run_output_guard(
    response=response.message,
    urls=[p.url for p in passages],
)
if not grounding.passed:
    response.sources = []          # strip ungrounded sources
    response.contact_support = True
```

### LangGraph — nodes

```python
# graph/nodes/guardrail.py  (Layer 1)
# graph/nodes/grounding.py  (Layer 4)
# Wire: START → guardrail → retrieve → generate → grounding → END
```

### ADK — callbacks

```python
# callbacks.py
from google.adk.agents import CallbackContext

async def input_guard_callback(ctx: CallbackContext) -> None:
    guard = run_input_guard(ctx.user_message)
    if guard.blocked:
        ctx.stop(AssistantResponse(message=guard.refusal_message, contact_support=guard.escalate))

# Register: agent = Agent(..., before_model_callback=input_guard_callback)
```

### Layer 5 — Escalation path

For agents that need escalation routing, check the `contact_support` flag downstream. The escalation pattern for LangGraph: `graph/builder.py:_escalation_node`. For ADK: match `_ESCALATION_RE` in the agent's after-model callback.

## Step 4 — Update the safeguards table in CLAUDE.md

Add the agent to the 5-layer table if it's new:

```
| 1 — Input guardrail | ✅ `main.py:entry` | ...
| 4 — Post-gen citation | ✅ `agent.py:grounding` | ...
```

## Done when

- Layer 1 blocks injection/PII at entry point
- Layer 4 strips ungrounded sources before response leaves the agent
- Run: `uv run pytest tests/ -k "guardrail or grounding" --tb=short -q`
- CLAUDE.md safeguards table updated
