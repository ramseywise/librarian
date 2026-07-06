---
name: va-eval
description: "VA multi-agent eval pipeline — ADK routing evals, LangSmith experiment loop, and chat quality scoring. Use when adding eval sets, running va_google_adk or va_langgraph evals, or wiring new graders into the VA pipeline."
---

Legacy VA multi-agent eval notes. The current checkout does not include a
`src/multi_agents/` tree or `evals/pipelines/va/` runners. For current galactus
support-agent evals, use `evals/README.md` and the unified dispatcher.

## Architecture

```bash
uv run python -m evals.pipelines.run live --run-name smoke --jsonl <dataset.jsonl> --endpoint http://localhost:8011/chat --tier heuristic
uv run python -m evals.pipelines.run langfuse --run-name hc-adk --dataset hc-support-agents-golden-597 --endpoint http://localhost:8011/chat --tier calibrated
```

Agents must be running before live evals fire. Start support agents with:
```bash
make sa-up
```

---

## ADK routing + behavior eval (`eval_adk.py`)

### Eval set schema (`data/adk/eval_sets/`)

```jsonl
{
  "eval_id": "list_invoices_routes_to_invoice_agent",
  "query": "show me my invoices",
  "expected_tools": ["list_invoices"],
  "expected_intent": "invoice_agent",
  "golden_response": null
}
```

`expected_tools`: tool names only — args are ignored (trajectory matching is name-level).  
`golden_response`: optional; required only for `final_response_match_v2` scoring.

### Eval config schema (`data/adk/eval_configs/`)

```json
{
  "criteria": {
    "tool_trajectory_avg_score": 0.8,
    "rubric_based_final_response_quality_v1": {
      "rubric": "Response must be in the same language as the query.",
      "weight": 1.0
    }
  }
}
```

### Run

```bash
make eval-adk-routing AGENT=http://localhost:8001
make eval-adk-quality AGENT=http://localhost:8001
```

Output → `data/adk/evals/routing_<timestamp>.json` and `data/adk/evals/quality_<timestamp>.json`.

### Adding a new eval case

1. Add a line to `data/adk/eval_sets/routing_eval.jsonl`
2. If you need a new rubric, add an entry to `data/adk/eval_configs/behavior_eval_config.json`
3. Run `make eval-adk-routing` and check pass rates in the JSON output

### Adding a new grader to eval_adk.py

The runner uses `ToolTrajectoryGrader` and `AgentBehaviorGrader` from `evals/graders/judges/routing.py`. To add a grader:

1. Create the grader in `evals/graders/judges/` following the base contract (see `grader_interface.md`)
2. Import and instantiate in `eval_adk.py` → `_build_graders()`
3. Add a threshold in `evals/metrics/base.py` → `THRESHOLDS`
4. Add a `PassRateMetric` entry in the runner's `_build_metrics()` function

---

## LangSmith eval loop (`eval_langsmith.py`)

### Seed a dataset from existing JSONL

```bash
make eval-langsmith-seed \
  SOURCE=data/datasets/bkh/eval_sets/regression_main.jsonl \
  DATASET=va-google-adk-eval-v1
```

Or from the SDK:
```python
from langsmith import Client
client = Client()
dataset = client.create_dataset("va-google-adk-eval-v1")
# add examples — see tooling/langsmith.md
```

### Run an experiment

```bash
make eval-langsmith \
  DATASET=va-google-adk-eval-v1 \
  AGENT=http://localhost:8001 \
  GRADERS="grounding completeness routing" \
  PREFIX=adk-eval
```

Output → `data/va_staging/langsmith_<timestamp>.json` + experiment record in LangSmith UI.

### Available graders for LangSmith experiments

| Key | Grader | What it measures |
|---|---|---|
| `grounding` | `GroundingGrader` | Claim-level grounding ratio vs. retrieved passages |
| `completeness` | `CompletenessGrader` | Sub-question coverage in the response |
| `routing` | routing accuracy | predicted intent vs. expected_intent in dataset |
| `escalation` | `EscalationGrader` | Correct escalation decisions |

Graders live under `evals/graders/judges/` and are registered through
`evals/graders/registry.py`. Prefer the current eval dispatcher for galactus
support-agent runs.

---

## Support agent evals (same runner, different data)

For support-agent evals, use the unified dispatcher:

```bash
uv run python -m evals.pipelines.run live --run-name hc-adk-smoke --jsonl <dataset.jsonl> --endpoint http://localhost:8011/chat --tier heuristic
uv run python -m evals.pipelines.run langfuse --run-name hc-adk --dataset hc-support-agents-golden-597 --endpoint http://localhost:8011/chat --tier calibrated
```

Data: `data/datasets/support-agents/hc_adk/` and `data/datasets/support-agents/hc_lg/`.

---

## Key files

| File | Purpose |
|---|---|
| `evals/pipelines/va/eval_adk.py` | ADK routing + rubric eval runner |
| `evals/pipelines/va/eval_chat.py` | Chat quality scoring runner |
| `evals/pipelines/va/eval_langsmith.py` | LangSmith experiment loop |
| `evals/graders/judges/routing.py` | ToolTrajectoryGrader, AgentBehaviorGrader |
| `data/adk/eval_sets/` | Routing eval cases (JSONL) |
| `data/adk/eval_configs/` | Rubric configs (JSON) |
| `data/datasets/support-agents/` | SA-specific eval sets and configs |
