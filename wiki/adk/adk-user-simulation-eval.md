---
title: ADK User Simulation Eval
tags: [adk, eval, pattern]
summary: Dynamic conversation testing in ADK using ConversationScenario and a user simulator LLM — replaces static turn sequences when agent response order is unpredictable.
updated: 2026-07-14
sources:
  - raw/claude-docs/galactus/.agents/skills/adk-eval-guide/references/user-simulation.md
  - raw/agent-skills/adk-eval-guide/references/user-simulation.md
---

# ADK User Simulation Eval

User simulation replaces fixed conversation transcripts with a **dynamically-generated user** backed by an LLM. Use this when the agent may ask for information in different orders or respond in unexpected ways — static `conversation` arrays can't handle this variability.

---

## When to Use

Use `conversation_scenario` instead of `conversation` when:
- The agent's question order is unpredictable
- You want to verify multi-turn flows without hardcoding every user turn
- You're testing safety/hallucination properties that require realistic user back-and-forth

---

## ConversationScenario Schema

An eval case must have exactly one of `conversation` or `conversation_scenario`, not both:

```json
{
  "eval_set_id": "dynamic_tests",
  "eval_cases": [
    {
      "eval_id": "booking_flow",
      "conversation_scenario": {
        "starting_prompt": "I need to book a flight to London",
        "conversation_plan": "Provide your name (John Smith) and email (john@example.com) when asked. Confirm the booking when the agent offers a flight."
      },
      "session_input": {
        "app_name": "my_app",
        "user_id": "test_user",
        "state": {}
      }
    }
  ]
}
```

- `starting_prompt` — fixed first user message
- `conversation_plan` — guidelines for how the simulated user should behave in subsequent turns

---

## Compatible Criteria

Only these criteria work with user simulation (no ground truth is available):

| Criterion | Compatible |
|---|:-:|
| `hallucinations_v1` | Yes |
| `safety_v1` | Yes |
| `rubric_based_final_response_quality_v1` | Yes |
| `rubric_based_tool_use_quality_v1` | Yes |
| `per_turn_user_simulator_quality_v1` | Yes |
| `tool_trajectory_avg_score` | **No** |
| `response_match_score` | **No** |
| `final_response_match_v2` | **No** |

Example config:
```json
{
  "criteria": {
    "hallucinations_v1": {
      "threshold": 0.5,
      "evaluate_intermediate_nl_responses": true
    },
    "safety_v1": 0.8
  }
}
```

---

## User Simulator Configuration

Override default simulator behavior in `eval_config.json`:

```json
{
  "criteria": { "...": "..." },
  "user_simulator_config": {
    "model": "gemini-2.5-flash",
    "model_configuration": {
      "thinking_config": {
        "include_thoughts": true,
        "thinking_budget": 10240
      }
    },
    "max_allowed_invocations": 20,
    "custom_instructions": "..."
  }
}
```

- `max_allowed_invocations` — max user-agent turns before forced termination. Set higher than your longest expected conversation.
- `custom_instructions` — override default simulator instructions. Must include `{stop_signal}`, `{conversation_plan}`, and `{conversation_history}` placeholders.

---

## Creating Eval Sets with Scenarios

```bash
adk eval_set create <agent_path> <eval_set_id>

adk eval_set add_eval_case \
  <agent_path> <eval_set_id> \
  --scenarios_file conversation_scenarios.json \
  --session_input_file session_input.json
```

**Scenarios file:**
```json
{
  "scenarios": [
    {
      "starting_prompt": "What can you do for me?",
      "conversation_plan": "Ask the agent to search for flights to Paris. After results, ask to book the cheapest option."
    }
  ]
}
```

---

## Evaluating Simulator Quality

Use `per_turn_user_simulator_quality_v1` to verify the simulator follows the conversation plan:

```json
{
  "criteria": {
    "per_turn_user_simulator_quality_v1": {
      "threshold": 1.0,
      "judge_model_options": {
        "judge_model": "gemini-2.5-flash",
        "num_samples": 5
      },
      "stop_signal": "</finished>"
    }
  }
}
```

---

## See Also

- [[ADK Eval Guide]]
- [[VA Eval Harness]]
- [[Galactus Eval Architecture]]
