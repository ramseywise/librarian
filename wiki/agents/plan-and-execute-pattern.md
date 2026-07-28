---
title: Plan and Execute Pattern
tags: [langgraph, pattern]
summary: Separating planning from execution for multi-step agent tasks — Planner, Executor, Replanner, and Responder nodes with HITL confirmation gate.
updated: 2026-04-24
sources:
  - raw/playground-docs/agentic-rag-copilot-research.md
---

# Plan and Execute Pattern

For multi-step action tasks, a single ReAct loop is fragile — the LLM makes tool call decisions at each step without a plan. Plan-and-Execute separates planning from execution.

## Architecture

```
[Planner] → plan: list[Step] → [Executor] → result per step
                                    ↓
                             [Replanner] → done? → [Responder]
                                         → update_plan → [Executor]
```

**Planner** (Sonnet): given the full task + available tools, generate a step list.

```python
class Step(BaseModel):
    id: str
    description: str
    tool: str
    tool_input: dict
    depends_on: list[str]  # step IDs that must complete first
```

**Executor** (Haiku): run one step at a time. Cheaper than Sonnet — use for mechanical execution of a pre-approved plan.

**Replanner** (Haiku): after each step, check if the plan still makes sense. If a step fails or the result changes assumptions, update remaining steps. Max replanning rounds: 3.

**Responder** (Sonnet): synthesize all step results into final user-facing answer.

## LangGraph Implementation

```python
class PlanExecuteState(TypedDict):
    input: str
    plan: list[Step]
    past_steps: list[tuple[Step, str]]   # (step, result)
    response: str | None

plan_graph = StateGraph(PlanExecuteState)
plan_graph.add_node("planner", planner_node)
plan_graph.add_node("executor", executor_node)
plan_graph.add_node("replanner", replanner_node)
plan_graph.add_node("responder", responder_node)

plan_graph.add_edge("planner", "executor")
plan_graph.add_conditional_edges(
    "replanner",
    should_continue,
    {"continue": "executor", "end": "responder"},
)
```

## HITL Confirmation Gate

After planner, before executor — show plan to user:

```python
def confirm_plan_node(state: PlanExecuteState) -> PlanExecuteState:
    interrupt({
        "type": "confirm_plan",
        "plan": [s.description for s in state["plan"]],
        "tool_calls": [s.tool for s in state["plan"]],
    })
    return state  # continues after user approves
```

Resume with `graph.invoke(Command(resume="approved"), config)`.

This is the clean implementation of rag_poc's confirm node — using LangGraph's `interrupt_after=["planner"]` compiler flag instead of custom interrupt logic.

## Parallel Steps with Send API

Steps without dependencies can run in parallel:

```python
def execute_parallel_steps(state: PlanExecuteState) -> list[Send]:
    ready = [s for s in state["plan"] if all_deps_met(s, state["past_steps"])]
    return [Send("execute_step", {"step": s}) for s in ready]
```

## Why Not Pure ReAct?

ReAct is fine for 1-2 tool calls. For "create invoice for customer X with products Y and Z, then send it to their email" (5+ API calls), ReAct can go off-script mid-sequence. Plan-and-Execute makes the sequence explicit and auditable before execution starts.

## Priority

Priority 2 for copilot build (after breakpoints). Effort: ~3 days. Blocks multi-step action tasks.

See [[LangGraph Advanced Patterns]] for the priority order of advanced patterns.

## See Also
- [[LangGraph Advanced Patterns]]
- [[LangGraph CRAG Pipeline]]
- [[ADK vs LangGraph Comparison]]
