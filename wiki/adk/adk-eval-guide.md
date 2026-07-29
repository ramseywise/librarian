---
title: ADK Eval Guide
tags: [adk, eval, pattern]
summary: ADK evaluation methodology — the eval-fix loop, 8 built-in criteria, evalset schema, tool trajectory gotchas, multimodal eval, and user simulation for dynamic testing.
updated: 2026-07-14
sources:
  - raw/claude-docs/project-g/.agents/skills/adk-eval-guide/SKILL.md
  - raw/claude-docs/project-g/.agents/skills/adk-eval-guide/references/builtin-tools-eval.md
  - raw/claude-docs/project-g/.agents/skills/adk-eval-guide/references/criteria-guide.md
  - raw/claude-docs/project-g/.agents/skills/adk-eval-guide/references/multimodal-eval.md
  - raw/claude-docs/project-g/.agents/skills/adk-eval-guide/references/user-simulation.md
  - raw/agent-skills/adk-eval-guide/SKILL.md
  - raw/agent-skills/adk-eval-guide/references/builtin-tools-eval.md
  - raw/agent-skills/adk-eval-guide/references/criteria-guide.md
  - raw/agent-skills/adk-eval-guide/references/multimodal-eval.md
  - raw/agent-skills/adk-eval-guide/references/user-simulation.md
---

# ADK Eval Guide

ADK has a first-class evaluation framework via `adk eval`. This page covers the eval-fix loop, built-in criteria, evalset schema, critical gotchas, multimodal evaluation patterns, and user simulation for dynamic conversation testing.

For the broader eval landscape, see [[VA Eval Harness]] and [[project-g Eval Architecture]].

---

## The Eval-Fix Loop

**Evaluation is iterative.** Expect 5–10+ iterations.

1. Start small: 1–2 eval cases, not the full suite
2. Run eval: `make eval` (or `adk eval`)
3. Read scores — identify what failed and why
4. Fix: adjust prompts, tool logic, instructions, or the evalset
5. Rerun eval — verify the fix worked
6. Repeat until the case passes
7. Only then add more cases and expand coverage

**Tests (`pytest`) are NOT evaluation.** They test code correctness, not whether the agent behaves correctly. Always run `adk eval`.

---

## Running Evaluations

```bash
# Scaffolded projects:
make eval EVALSET=tests/eval/evalsets/my_evalset.json

# Direct ADK CLI:
adk eval ./app <path_to_evalset.json> --config_file_path=<config.json> --print_detailed_results

# Specific cases:
adk eval ./app my_evalset.json:eval_1,eval_2

# With GCS storage:
adk eval ./app my_evalset.json --eval_storage_uri gs://my-bucket/evals

# Eval set management:
adk eval_set create <agent_path> <eval_set_id>
adk eval_set add_eval_case <agent_path> <eval_set_id> --scenarios_file <path> --session_input_file <path>
```

---

## Choosing the Right Criteria

| Goal | Recommended Criteria |
|---|---|
| Regression testing / CI/CD (fast, deterministic) | `tool_trajectory_avg_score` + `response_match_score` |
| Semantic response correctness (flexible phrasing OK) | `final_response_match_v2` |
| Response quality without reference answer | `rubric_based_final_response_quality_v1` |
| Tool usage reasoning | `rubric_based_tool_use_quality_v1` |
| Detect hallucinated claims | `hallucinations_v1` |
| Safety compliance | `safety_v1` |
| Dynamic multi-turn conversations | User simulation + `hallucinations_v1` / `safety_v1` |
| Multimodal inputs | `tool_trajectory_avg_score` + custom metric (see below) |

**Default when no config provided:** `tool_trajectory_avg_score: 1.0` + `response_match_score: 0.8`

---

## Criteria Reference

### tool_trajectory_avg_score

Evaluates whether the agent called the right tools in the right order.

**Match types:**
- `EXACT` (default) — strict workflow validation, regression testing
- `IN_ORDER` — key actions must happen in sequence, extra tool calls OK
- `ANY_ORDER` — all expected tools must be called, order doesn't matter

**Judge model config** (for LLM-as-judge criteria):
```json
{
  "judge_model_options": {
    "judge_model": "gemini-2.5-flash",
    "num_samples": 5
  }
}
```
Higher `num_samples` reduces LLM variance (majority vote).

**Rubric scoring:** Each rubric returns yes (1.0) / no (0.0). Score = average across all rubrics and invocations.

**Hallucination scoring:** Response segmented into sentences, each labeled `supported`, `unsupported`, `contradictory`, `disputed`, or `not_applicable`. Score = % `supported` + `not_applicable`.

### Full eval_config.json example

```json
{
  "criteria": {
    "tool_trajectory_avg_score": {
      "threshold": 1.0,
      "match_type": "IN_ORDER"
    },
    "final_response_match_v2": {
      "threshold": 0.8,
      "judge_model_options": { "judge_model": "gemini-2.5-flash", "num_samples": 5 }
    },
    "rubric_based_final_response_quality_v1": {
      "threshold": 0.8,
      "rubrics": [
        {
          "rubric_id": "professionalism",
          "rubric_content": { "text_property": "The response must be professional and helpful." }
        }
      ]
    }
  }
}
```

---

## EvalSet Schema

```json
{
  "eval_set_id": "my_eval_set",
  "eval_cases": [
    {
      "eval_id": "search_test",
      "conversation": [
        {
          "invocation_id": "inv_1",
          "user_content": { "parts": [{ "text": "Find a flight to NYC" }] },
          "final_response": {
            "role": "model",
            "parts": [{ "text": "I found a flight for $500." }]
          },
          "intermediate_data": {
            "tool_uses": [
              { "name": "search_flights", "args": { "destination": "NYC" } }
            ],
            "intermediate_responses": [
              ["sub_agent_name", [{ "text": "Found 3 flights." }]]
            ]
          }
        }
      ],
      "session_input": { "app_name": "my_app", "user_id": "user_1", "state": {} }
    }
  ]
}
```

**Key fields:**
- `intermediate_data.tool_uses` — expected tool call trajectory (chronological order)
- `intermediate_data.intermediate_responses` — expected sub-agent responses (multi-agent systems)
- `session_input.state` — initial session state (overrides Python-level initialization)
- `conversation_scenario` — alternative to `conversation` for user simulation (see below)

---

## Critical Gotchas

### The Proactivity Trajectory Gap

LLMs often perform extra actions not asked for (e.g., `google_search` after `save_preferences`). This causes `tool_trajectory_avg_score` failures with `EXACT` match.

**Solutions:**
1. Use `IN_ORDER` or `ANY_ORDER` match type
2. Include ALL tools the agent might call in your expected trajectory
3. Use `rubric_based_tool_use_quality_v1` instead of trajectory matching
4. Add strict stop instructions: "Stop after calling save_preferences. Do NOT search."

### Multi-turn conversations require tool_uses for ALL turns

`tool_trajectory_avg_score` evaluates each invocation. Missing `tool_uses` for an intermediate turn causes failure even if tools were correct.

```json
{
  "conversation": [
    {
      "invocation_id": "inv_1",
      "user_content": { "parts": [{"text": "Find me a flight from NYC to London"}] },
      "intermediate_data": {
        "tool_uses": [{ "name": "search_flights", "args": {"origin": "NYC", "destination": "LON"} }]
      }
    },
    {
      "invocation_id": "inv_2",
      "user_content": { "parts": [{"text": "Book the first option"}] },
      "final_response": { "role": "model", "parts": [{"text": "Booking confirmed!"}] },
      "intermediate_data": {
        "tool_uses": [{ "name": "book_flight", "args": {"flight_id": "1"} }]
      }
    }
  ]
}
```

### App name must match directory name

```python
# CORRECT — matches the "app" directory
app = App(root_agent=root_agent, name="app")

# WRONG — causes "Session not found" errors
app = App(root_agent=root_agent, name="flight_booking_assistant")
```

### State type mismatch in evalset

```json
// WRONG — initializes feedback_history as string, breaks .append()
"state": { "feedback_history": "" }

// CORRECT — matches the Python type (list)
"state": { "feedback_history": [] }
```

### Model thinking mode bypasses tools

Models with "thinking" enabled may skip tool calls. Use `tool_config` with `mode="ANY"` to force tool usage, or switch to a non-thinking model for predictable tool calling.

---

## Built-in Tools and Trajectory Compatibility

**Model-internal tools (DON'T appear in trajectory):**

| Tool | In Trajectory? | Eval Strategy |
|---|---|---|
| `google_search` | No | Rubric-based |
| `google_search_retrieval` | No | Rubric-based |
| `BuiltInCodeExecutor` | No | Check output |
| `VertexAiSearchTool` | No | Rubric-based |
| `url_context` | No | Rubric-based |

**Function-based tools (DO appear in trajectory):**

| Tool | In Trajectory? | Eval Strategy |
|---|---|---|
| `load_web_page` | Yes | `tool_trajectory_avg_score` works |
| Custom tools | Yes | `tool_trajectory_avg_score` works |
| `AgentTool` | Yes | `tool_trajectory_avg_score` works |

**`google_search` is model-internal** — it injects into `llm_request.config.tools` as `types.Tool(google_search=types.GoogleSearch())`. Search results come back as `grounding_metadata`, not function call events. This causes `tool_trajectory_avg_score` to ALWAYS return 0 for agents using `google_search`.

**Config for `google_search` agents:**
```json
{
  "criteria": {
    "rubric_based_final_response_quality_v1": {
      "threshold": 0.6,
      "rubrics": [
        { "rubric_id": "has_citations", "rubric_content": { "text_property": "Response includes source citations" } }
      ]
    }
  }
}
```

**When mixing both types** (e.g., `google_search` + custom tools): remove `tool_trajectory_avg_score` entirely, or only include function-based tools in `tool_uses`.

**Mock mode for external APIs:**
```python
def call_external_api(query: str) -> dict:
    api_key = os.environ.get("EXTERNAL_API_KEY", "")
    if not api_key or api_key == "dummy_key":
        return {"status": "success", "data": "mock_response"}
    # Real API call here
```

---

## Multimodal Evaluation

`Invocation.user_content` accepts multimodal `Part` types:

```json
{
  "user_content": {
    "parts": [
      { "text": "Describe this image" },
      { "inline_data": { "mime_type": "image/png", "data": "<base64>" } }
    ]
  }
}
```

For GCS-hosted files: `{ "file_data": { "mime_type": "image/jpeg", "file_uri": "gs://bucket/test.jpg" } }`

**What works out of the box:** `tool_trajectory_avg_score` works fine. Response/rubric evaluators work if the agent produces text from multimodal input.

**The text-only gap:** built-in LLM-as-judge evaluators call `get_text_from_content()` which skips `inline_data`/`file_data`. The judge never sees the original image/audio — cannot verify "did the agent correctly describe this image?"

**Solution — custom metric with vision-capable judge:**

```python
async def multimodal_response_quality(
    eval_metric: EvalMetric,
    actual_invocations: list[Invocation],
    expected_invocations: list[Invocation] | None,
    conversation_scenario=None,
) -> EvaluationResult:
    client = _get_genai_client()
    threshold = eval_metric.threshold or 0.8
    per_invocation = []
    for actual in actual_invocations:
        agent_text = "\n".join(p.text for p in actual.final_response.parts if p.text)
        judge_parts = list(actual.user_content.parts) + [
            genai.types.Part.from_text(
                text=f"\n\nAgent response: {agent_text}\n\n"
                     "Does the agent response accurately describe the content above? "
                     "Reply with ONLY a single number from 0.0 to 1.0."
            ),
        ]
        response = await client.aio.models.generate_content(
            model="gemini-3-flash-preview",
            contents=genai.types.Content(role="user", parts=judge_parts),
        )
        score = max(0.0, min(1.0, float(response.text.strip())))
        per_invocation.append(PerInvocationResult(
            actual_invocation=actual, score=score,
            eval_status=EvalStatus.PASSED if score >= threshold else EvalStatus.FAILED,
        ))
    avg = sum(r.score for r in per_invocation) / len(per_invocation)
    return EvaluationResult(overall_score=avg, per_invocation_results=per_invocation,
                            overall_eval_status=EvalStatus.PASSED if avg >= threshold else EvalStatus.FAILED)
```

**Wire in eval_config.json:**
```json
{
  "criteria": { "multimodal_response_quality": 0.8 },
  "custom_metrics": {
    "multimodal_response_quality": {
      "code_config": { "name": "my_app.eval.multimodal_metric.multimodal_response_quality" }
    }
  }
}
```

**Note:** `genai.Client()` does NOT auto-detect `GOOGLE_GENAI_USE_VERTEXAI` — initialize explicitly with `vertexai=True, project=..., location=...` for Vertex AI.

---

## User Simulation

See [[ADK User Simulation Eval]] for the full pattern. Summary:

Use `conversation_scenario` instead of `conversation` for dynamic multi-turn testing where the agent may ask for information in different orders:

```json
{
  "eval_id": "booking_flow",
  "conversation_scenario": {
    "starting_prompt": "I need to book a flight to London",
    "conversation_plan": "Provide your name (John Smith) and email when asked. Confirm when the agent offers a flight."
  }
}
```

**Compatible criteria for user simulation:** `hallucinations_v1`, `safety_v1`, `rubric_based_final_response_quality_v1`, `rubric_based_tool_use_quality_v1`, `per_turn_user_simulator_quality_v1`. Trajectory-based criteria are NOT compatible (no ground truth).

---

## Diagnosing Failures

| Symptom | Cause | Fix |
|---|---|---|
| `tool_trajectory_avg_score` is 0 | Agent uses `google_search` (model-internal) | Remove trajectory metric; use rubric-based |
| Trajectory fails but tools are correct | Extra tools called | Switch to `IN_ORDER`/`ANY_ORDER` |
| Missing `tool_uses` in intermediate turns | Trajectory expects match per invocation | Add expected calls to all turns |
| Agent mentions data not in tool output | Hallucination | Tighten instructions; add `hallucinations_v1` |
| "Session not found" error | App name mismatch | Ensure App `name` matches directory name |
| Score fluctuates between runs | Non-deterministic model | Set `temperature=0` or use rubric-based eval |
| LLM judge ignores image in eval | `get_text_from_content()` skips non-text | Use custom metric with vision-capable judge |

---

## See Also

- [[ADK User Simulation Eval]]
- [[VA Eval Harness]]
- [[project-g Eval Architecture]]
- [[LLM Grader Calibration Insights]]
- [[ADK Python API Reference]]
