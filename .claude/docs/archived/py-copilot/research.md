# Research: Python Copilot Service — Upgrade Compatibility & Architecture

**Date:** 2026-04-15
**Scope:** `v2/py_copilot/` — upgrade impact analysis for incorporating `ts-copilot-upgrades` objectives into the Python port
**Related docs:**
- `backlog/ts-copilot/research.md` — TS service deep-dive (read first)
- `build/backlog/py-copilot/plan.md` — Python port implementation plan
- `build/backlog/ts-copilot/plan.md` — TS upgrades plan (the delta being analyzed here)

---

## What This Research Covers

The `py-copilot/plan.md` ports the 17-tool TS service to Python. The `ts-copilot` upgrades plan
adds 10 new tools, a multi-agent architecture, smart features, and infra. This research identifies
where the TS upgrade assumptions do or do not carry over to Python, and flags what must be decided
or verified before updating the Python plan.

---

## Part 1 — New Tools: Friction Assessment

| Tool group | Python friction | Notes |
|---|---|---|
| Bills (3 tools) | Low | `create_bill` needs `defaultExpenseAccount` lookup — same pattern as `get_default_sales_account()` already in `billy_client.py` |
| Transactions read-only (2) | None | Straight GET wrappers, identical to invoice read tools |
| VAT read-only (2) | None | Same |
| Financial reports (3) | None | Same |
| `get_status_summary` (smart feature) | Python advantage | `asyncio.gather()` makes the 3-way parallel call cleaner than TS `Promise.all()` |

### Schema: `table_type` Literal expansion

```python
# Before
table_type: Literal["invoices", "customers", "products", "quotes"] | None = None

# After
table_type: Literal["invoices", "customers", "products", "quotes", "bills"] | None = None
```

Pydantic v2 emits this correctly as an enum in JSON schema. Ripple: update all fixture responses
in `test_schema.py` that assert on the enum values. Small, but easy to miss.

---

## Part 2 — Core Architectural Decision: When to Split the Agent

### The TS approach: defer the split

The TS plan adds all tools first (reaching 28), runs a quality gate, then splits if quality degrades.
This is reasonable for TS because `FunctionTool` + Zod gives Gemini high-quality, explicitly described
schemas — the degradation curve is more gradual.

### Why Python should split from the start

ADK Python auto-generates tool schemas from type annotations and Google-style docstrings (`Args:` sections).
The schema quality is structurally lower than Zod's explicit `.describe()`. Lower schema quality means
Gemini's tool selection accuracy degrades at a lower tool count threshold.

**At 28 tools with lower-quality schemas, the Python single-agent path is higher risk than the TS equivalent.**

Starting with the multi-agent topology eliminates this risk entirely: each sub-agent holds ≤12 tools,
which is well within the safe zone for any Gemini Flash model.

### Recommended topology for Python

```
rootAgent (LlmAgent — routes only, no tools, no output_schema)
  ├── accountingAgent  (execution: invoices, bills, customers, products, quotes, emails — ~13 tools)
  ├── analystAgent     (insights: reports, vat, transactions, status summary — ~7 tools)
  └── helpAgent        (knowledge: fetch_support_knowledge — 1 tool)
```

Each sub-agent has `output_schema=AccountingOutput`. Root agent has `output_schema=None`.

---

## Blocking Unknown: ContextVar Propagation in Multi-Agent

### The problem

`py-copilot/plan.md` (Friction 1) establishes ContextVar as the auth mechanism:

```python
# FastAPI endpoint sets before runner.run_async()
set_billy_config(body.api_token, body.org_id)
```

This works for single-agent because ADK runs tool calls in the same asyncio task (verified against
0.5.x source). But `asyncio.create_task()` copies a context snapshot — mutations after creation
are invisible to the child task.

**Multi-agent hand-off almost certainly crosses a task boundary.** If the root agent's dispatch to
a sub-agent uses `create_task()` internally, `get_billy_config()` returns `None` in the sub-agent's
tools — silent runtime failure.

### Recommended resolution: session.state as primary auth channel for multi-agent

`session.state` is designed to survive agent transitions in ADK. It is the correct mechanism when
the execution graph crosses task boundaries.

```python
# FastAPI endpoint — write auth into session before runner call
session = await session_service.create_session(
    app_name="copilot-py",
    user_id=body.user_id,
    session_id=body.session_id,
    state={
        "billy_api_token": body.api_token,
        "billy_org_id": body.org_id,
    },
)

# Tool functions — read via ToolContext (multi-agent safe)
async def list_bills(tool_context: ToolContext) -> list[dict]:
    token = tool_context.state["billy_api_token"]
    org_id = tool_context.state["billy_org_id"]
    cfg = BillyConfig(api_token=token, organization_id=org_id)
    async with get_client(cfg) as client:
        ...
```

**Impact on py-copilot/plan.md:** Friction 1 mitigation (ContextVar) should be revised to use
`session.state` as the primary path when multi-agent is chosen. Keep ContextVar as a fallback
or single-agent-only path. `test_context.py` scope changes: test `session.state` propagation
through the root → sub-agent transition rather than ContextVar through runner.

---

## Three Research Items (blocking before updating the plan)

| # | Question | How to resolve | Blocks |
|---|---|---|---|
| R1 | Does ADK Python 0.5.x multi-agent dispatch use `asyncio.create_task()`? | Read `google/adk/agents/llm_agent.py` source (installed package) or write minimal propagation test | ContextVar vs session.state decision |
| R2 | What is the exact API for pre-populating `session.state` before `run_async()`? | Check `DatabaseSessionService.create_session()` or `get_or_create_session()` signature — `state` vs `initial_state` param | FastAPI endpoint implementation |
| R3 | Does `event.is_final_response()` correctly identify the leaf agent's output in multi-agent? | Write a multi-agent test with two sub-agents and assert which event carries the structured output | Output extractor in `interfaces/api.py` |

**Fastest path for R1:** `pip show google-adk` → find site-packages path → read
`google/adk/agents/llm_agent.py`, search for `create_task`. This is a 2-minute check that
determines the entire auth architecture.

---

## `output_schema` Placement Rule

In multi-agent, `output_schema` belongs on the leaf agents only. The root router has no schema.

**Risk if schema is set on root:** ADK enforces that the router's routing-decision text conforms
to `AccountingOutput`. It won't, and the call fails with a validation error that looks like a
model output problem, not a config problem.

**Test required:** Integration test that runs a full `rootAgent → accountingAgent` call and
confirms `AccountingOutput.model_validate()` succeeds on the extracted event.

---

## Smart Features: Python-Specific Notes

| Feature | Python friction | Notes |
|---|---|---|
| Proactive nudges (`get_status_summary`) | Python advantage | `asyncio.gather()` for 3-way parallel API calls; assign to `analystAgent` |
| `parentUrl` context injection | None | `urllib.parse` + regex in FastAPI handler; same logic as TS |
| Frustration detection | None | Instruction copy-paste; eval pipeline is Python-native — writes directly to playground eval format |
| Receipt upload (nav-only) | None | No tool needed; navigation guidance only |

### `parentUrl` parsing (Python)

```python
from urllib.parse import urlparse
import re

def extract_context_hint(parent_url: str | None) -> str | None:
    if not parent_url:
        return None
    # Match only known resource types with safe ID patterns
    match = re.search(
        r'/(invoices|bills|quotes|clients|vat-declarations)/([A-Za-z0-9_-]{4,})',
        parent_url,
    )
    if match:
        resource_type, resource_id = match.groups()
        return f"[Context: User is on /{resource_type}/{resource_id}]"
    return None
```

Inject as prefix to `body.message` before the runner call.

---

## Infrastructure: Python Advantages

| Item | Notes |
|---|---|
| Session summary API | Already scaffolded in plan (`GET /sessions/{id}/summary`). One-shot runner call using `helpAgent` (no tools, summarizer instruction). Load session history via session_id — no manual history injection needed. |
| Feedback → eval pipeline | Playground `src/eval/` is Python-native. Polars for data transformation, existing `CopilotKnowledgeExperiment` harness for labeling. No cross-language boundary. |
| boto3 sync wrapping | `run_in_executor` pattern is agent-agnostic — same in multi-agent as single-agent. No new friction from the topology change. |

---

## Decisions Summary

| Decision | Recommendation | Confidence |
|---|---|---|
| Agent architecture | **Multi-agent (Option B) from the start** — Python schema quality lowers the degradation threshold; don't defer | High |
| Auth context mechanism | **`session.state`** for multi-agent — ContextVar is unsafe across task boundaries | High (pending R1 confirmation) |
| `output_schema` placement | **Leaf agents only** — root router has no output schema | High |
| When to run quality gate | **After single-agent baseline** (17 tools), before adding upgrade tools — establishes the comparison point | Medium |

---

## Impact on py-copilot/plan.md

When the plan is updated to incorporate the upgrades, these sections change:

1. **Friction 1 (ContextVar)** — revise to `session.state` as primary mechanism for multi-agent;
   keep ContextVar as single-agent fallback only
2. **Step 3 (Execution Tools)** — extend port list with bills, transactions, VAT, reports tools
   (same file/pattern as existing tools)
3. **Step 5 (LlmAgent)** — replace single `accounting_agent` with multi-agent topology;
   add `root.py`, `analyst.py`, `help.py`
4. **Schema** — add `"bills"` to `table_type` Literal + fixture updates
5. **New section: Smart Features** — `get_status_summary`, `parentUrl` context injection,
   frustration→eval pipeline
6. **test_context.py scope** — test `session.state` propagation through root→sub-agent transition
