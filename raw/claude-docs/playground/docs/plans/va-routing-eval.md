# VA Routing Eval Plan

**Date:** 2026-05-07
**Status:** Ready to run
**Goal:** Establish a real routing baseline for va-langgraph against 278 corpus-a German tickets

---

## What we're testing

Intent routing accuracy of va-langgraph's `analyze_node` (the LLM classifier in
`graph/nodes/analyze.py`). Given a German customer support message, does the router
classify the correct intent (`invoice`, `quote`, `customer`, `expense`, `banking`,
`accounting`, `support`, etc.)?

This is the most important baseline before migrating or modifying anything — routing
failures cascade downstream (wrong subgraph → irrelevant tool calls → bad answer).

---

## Bug fixed before first run

`va-eval-base/harness.py` had ports swapped vs docker-compose. Corrected:

| Service | Before (wrong) | After (correct) |
|---|---|---|
| va-langgraph | `:8000` | `:8001` (va-gateway-lg) |
| va-google-adk | `:8001` | `:8000` (va-gateway-adk) |
| va-support-rag | `:8002` | `:8002` (unchanged) |

---

## How to run

### Option A — One shot (fresh environment)

```bash
cd playground
make va-baseline
```

Starts all services in background → waits for health → runs routing eval.
Saves JSON to `results/routing-<timestamp>.json`, prints summary to stdout.
First run: 5-10 min (Docker build). Subsequent runs: ~2 min.

### Option B — Services already running

```bash
make va-eval-routing
```

### Option C — Full eval (adds service-specific LLM graders, slower)

```bash
make va-eval-baseline
```

### If you only want LangGraph + RAG (skip slow ADK build)

```bash
make va-rag-up     # starts va-support-rag + postgres
# separately start va-gateway-lg:
docker compose -f infrastructure/containers/docker-compose.yml --env-file .env \
    up --build -d va-gateway-lg
make va-wait
make va-eval-routing
```

va-gateway-adk is optional for routing eval — harness handles connection errors
gracefully (scores 0 for that service, still runs langgraph + support-rag).

---

## What the results mean

The routing eval (`--baseline-only`) runs three graders:

| Grader | What it checks | Pass condition |
|---|---|---|
| `schema` | Response has `message`, `suggestions`, `nav_buttons` | All fields present |
| `message_quality` | Message non-empty, 10–5000 chars | Both criteria pass |
| `routing` | `classified_intent` matches `expected_intent` in corpus-a fixture | Exact match |

**Key number to watch: `routing` pass rate for va-langgraph.**

| Score | Interpretation | Action |
|---|---|---|
| > 85% | Routing is solid | Proceed with migration |
| 70–85% | Acceptable, some prompt tuning needed | Note failure clusters, proceed |
| < 70% | Routing is broken | Fix router prompt before anything else |

The routing grader requires `classified_intent` to be returned in `metadata` of the
va-langgraph response. If this field is missing, all routing checks score 0 — verify
with: `curl -X POST http://localhost:8001/chat -d '{"session_id":"test","request_id":"1","message":"Zeig mir meine Rechnungen","user_id":"eval"}'`

---

## Interpreting failure clusters

After the run, load the JSON results and group failures by `expected_intent`:

```python
import json, collections
with open("results/routing-<ts>.json") as f:
    data = json.load(f)

failures = [r for r in data["results"] if r["grader_type"] == "routing" and not r["is_correct"]]
by_intent = collections.Counter(r.get("dimensions", {}).get("expected_intent") for r in failures)
print(by_intent.most_common())
```

Common patterns to look for:
- **`support` misrouted to another intent** — router prompt needs stronger support fallback
- **`insights` confused with `accounting`** — boundary definitions need sharpening
- **`banking` vs `expense`** — ambiguous German phrasing; consider examples in router prompt

---

## Next steps after baseline

1. **If routing > 85%**: move to migrating va-langgraph into project-g for Danish eval
2. **If routing 70-85%**: update `prompts/router.txt` with correction examples for top
   failure intents, re-run `make va-eval-routing` to verify improvement
3. **Support retrieval quality**: after routing baseline, run a retrieval spot-check —
   send 20 `expected_intent = support` tickets to va-support-rag `/api/v1/retrieval`
   and inspect returned document quality by eye (no golden set needed for initial pass)

---

## Files involved

| File | Role |
|---|---|
| `va-eval-base/harness.py` | HTTP transport to all 3 services |
| `va-eval-base/graders.py` | `SchemaGrader`, `MessageQualityGrader`, `RoutingGrader` |
| `va-eval-base/runner.py` | Orchestration, result aggregation |
| `va-eval-base/cli.py` | Entry point (`--baseline-only`, `--output`, `--name`) |
| `va-langgraph/tests/evalsuite/fixtures/corpus-a_tickets.json` | 278 German tickets |
| `results/routing-<ts>.json` | Output (gitignored) |
| `Makefile` | `va-baseline`, `va-eval-routing`, `va-up-bg`, `va-wait` |
