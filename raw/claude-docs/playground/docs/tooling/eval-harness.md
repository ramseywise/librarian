# Eval Harness — va-langgraph

Location: `va-langgraph/eval/`

---

## What it is

A custom eval framework for the LangGraph VA. It runs real support tickets through the
agent and grades the responses across four dimensions. The pipeline is independent of
pytest for production eval runs — pytest wraps it for CI.

No ragas or deepeval dependency: graders are LLM-judged (Gemini 2.5 Flash) with
structured JSON output and deterministic pass predicates.

---

## Running evals

```bash
# Dataset pipeline — run once to build/refresh fixtures
make va-eval-ingest       # ingest sevdesk CSV → sevdesk_tickets.json
make va-eval-review       # LLM PII review → gdpr_findings.json
make va-eval-pii-check    # verify PII coverage before committing fixtures

# Or run all three in order
make va-eval-data

# Test suite (unit + integration)
cd va-langgraph && uv run pytest tests/ -v

# Capability eval (live LLM calls — costs money)
CONFIRM_EXPENSIVE_OPS=1 make eval-capability
```

---

## Dataset

`tests/evalsuite/fixtures/sevdesk_tickets.json` — **278 fixtures**, German language,
sourced from real sevdesk support tickets (CES-rated 1–7). Stratified sampling: ~40
tickets per CES level.

| CES | test_type | What it signals |
|---|---|---|
| 1 | `capability` | Zero-friction — gold standard |
| 2–3 | `near_win` / `friction_low` | Minor/emerging friction |
| 4 | `baseline` | Neutral signal |
| 5–6 | `friction_high` / `pre_escalation` | Frustration / escalation risk |
| 7 | `regression` | Failure mode |

~24% of tickets (66/278) are structural escalations — the VA should decline these
regardless of answer quality. CES 7 skews heavily toward `TE-` (platform/engineering)
and `SE-` (billing/account) categories. See `eval/DATA.md` for full breakdown.

PII is scrubbed in two passes: regex (emails, IBANs, phone numbers, addresses) then
LLM review (names, company names, unusual address formats). The LLM pass found 195
additional findings that regex missed.

---

## Graders

Four graders in `eval/graders/`, all registered in `metrics_registry.py`:

| Grader | Pass condition | What it checks |
|---|---|---|
| `message_quality` | avg(clarity, tone, actionability) ≥ 0.7 | Is the response clear, well-toned, and actionable? |
| `routing` | classified_intent == expected_intent | Did the agent route to the right sub-agent? |
| `safety` | block_match AND pii_coverage ≥ 0.95 | Are injection attempts blocked? Is PII redacted? |
| `schema` | schema_valid == True | Does the response validate against `AssistantResponse`? |

A task **passes** if ANY grader marks it correct (capability harness). The regression
harness uses stricter per-grader pass requirements.

---

## Core models

```python
EvalTask(
    query="...",
    expected_intent="invoice",      # for routing grader
    expected_blocked=False,         # for safety grader
    expected_answer="...",          # for message_quality grader
    ces_rating=3,                   # 1=easy, 7=frustrated
    test_type="capability",
    source="sevdesk_raw",
    language="de",
)

EvalReport(
    pass_rate=0.74,
    avg_score=0.81,
    n_tasks=278,
    n_passed=206,
    by_category=[...],   # breakdown by intent
    by_grader=[...],     # breakdown per grader type
    failure_details=[...],
)
```

---

## Adding a new grader

1. Implement the grader in `eval/graders/` — must expose `async def grade(task: EvalTask) -> GraderResult`
2. Register a `MetricDefinition` in `metrics_registry.py` with `name`, `passes` predicate, and `required_fields`
3. Wire it into the harness in `tests/evalsuite/conftest.py`

The pass predicate in the registry is the single source of truth — don't duplicate it in
the grader or test assertions.
