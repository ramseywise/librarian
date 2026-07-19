# Hardening Plan

**Date:** 2026-04-29
**Status:** Complete — all items implemented and tested
**Source:** Open items #8, #9, #12 from pre-merge-refactor review

---

## #8 — Session TTL (runner.py memory leak)

**Problem:** `va-langgraph/gateway/runner.py` — `_sessions: dict[str, _Session] = {}` at line 42 grows unbounded. Each new `session_id` adds an entry that is never evicted. Under load this leaks memory indefinitely.

**Note:** The Postgres checkpointer holds conversation state independently of this dict. The `_Session` object is just an in-process wrapper (interrupt queue, lock, etc.), so evicting it does not lose conversation history — the next request simply recreates the wrapper and resumes from Postgres.

**Fix:** Replace the plain dict with `cachetools.TTLCache`.

### Steps

1. Add `cachetools` to `va-langgraph/pyproject.toml` dependencies
2. In `va-langgraph/gateway/runner.py`:
   ```python
   from cachetools import TTLCache
   # ...
   _SESSION_TTL = int(os.getenv("SESSION_TTL_SECONDS", "1800"))  # 30 min default
   _SESSION_MAXSIZE = int(os.getenv("SESSION_MAXSIZE", "500"))

   self._sessions: TTLCache[str, _Session] = TTLCache(
       maxsize=_SESSION_MAXSIZE, ttl=_SESSION_TTL
   )
   ```
3. The rest of `get_or_create()` and `delete()` are unchanged — `TTLCache` is a `MutableMapping`, so the existing dict access patterns work without modification.
4. Add `SESSION_TTL_SECONDS` and `SESSION_MAXSIZE` to `.env.example` with defaults documented.
5. Add to `va-gateway-lg` environment block in `docker-compose.va.yml`.

**TTL rationale:** 30 min matches a typical browser session. Users who are inactive for >30 min will lose any in-flight interrupt state (rare in practice; their Postgres checkpoint is unaffected). Tune via env var.

---

## #9 — Empty tool sets graceful failure

**Problem:** `va-google-adk/sub_agents/` has two stubs with empty tool frozensets:
- `_EMAIL_TOOLS = frozenset([])` (line 57 of `domains.py`)
- `_INVITATION_TOOLS = frozenset([])` (line 59 of `domains.py`)

When the router sends a query to one of these domains, the domain subgraph invokes a tool call against an empty set, which produces a silent failure or cryptic LLM error rather than a clear "not available yet" response.

The same issue exists in `va-google-adk` for the email/invitation sub-agents once a backend test account is ready — but the immediate fix is the LangGraph domain.

**Fix:** Guard at the top of each domain subgraph node — before any tool call, check whether the domain's tool set is populated; if not, return a structured "not available" response and skip the LLM call.

### Steps

**va-langgraph (`graph/subgraphs/domains.py`)**

1. Add a `_domain_available(tools: frozenset) -> bool` helper at module level.
2. At the start of each domain node function, call the guard:
   ```python
   if not _domain_available(_EMAIL_TOOLS):
       return {
           "tool_results": [{"status": "not_available",
                             "message": "Email management is not yet available."}],
           "done": True,
       }
   ```
3. Apply the same guard to `_INVITATION_TOOLS`.
4. The guard is a no-op for domains with populated tool sets — no behaviour change for invoice, quote, customer, product, support.

**va-google-adk (future — apply when a backend test account is ready)**

- The `email_agent` and `invitation_agent` stubs in `sub_agents/` should return `AssistantResponse(message="...", intent="email", ...")` with a not-available message, rather than attempting tool calls.
- Document the `TODO(2)` comment in each stub as the trigger point.

---

## #12 — Unit tests for eval graders

**Problem:** The eval framework has no unit tests for its graders or metric helpers. A silent regression in `FrictionJudge`, `EscalationJudge`, or `compute_routing_metrics()` would only surface when a full eval run is interpreted by eye.

**Target:** `va-langgraph/tests/unit/eval/`

### Test files to create

```
va-langgraph/tests/unit/eval/
  test_friction_grader.py
  test_escalation_grader.py
  test_routing_metrics.py
  test_safety_metrics.py
```

### Coverage targets

**`test_friction_grader.py`**
- Grade a low-effort response (CES 1–2) → `is_correct=True`, `score ≥ 0.8`
- Grade a high-effort response (CES 6–7) → `is_correct=False`, `score ≤ 0.3`
- `dimensions` dict present and contains at least `clarity`, `completeness`
- Stub the LLM call (monkeypatch or `respx`) — grader logic should be testable without live API

**`test_escalation_grader.py`**
- `escalation_signal=True` task + agent response that escalates → `is_correct=True`
- `escalation_signal=True` task + agent response that does NOT escalate → `is_correct=False`
- `escalation_signal=False` task → grader is skipped / returns neutral

**`test_routing_metrics.py`**
- `compute_routing_metrics(results)` with all-correct results → `f1 = 1.0`, `precision = 1.0`, `recall = 1.0`
- With mixed results → expected F1 < 1.0, consistent with sklearn reference
- Empty results list → returns zeros or raises `ValueError` (decide and document)
- Per-intent breakdown present

**`test_safety_metrics.py`**
- PII-coverage metric: tasks with `contains_pii=True`, all scrubbed → `pii_coverage = 1.0`
- Injection FNR: tasks with `expected_blocked=True`, none blocked → `injection_fnr = 1.0`
- Mixed case: verify metric arithmetic

### Notes
- Use `pytest-asyncio` for any async graders
- Do not call live LLM APIs in unit tests — stub at the `httpx` or model boundary
- Add a `tests/unit/eval/__init__.py` to make the package importable
