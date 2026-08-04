---
title: LangSmith Platform
tags: [infra, eval, concept]
summary: "LangSmith mechanics — auto-instrumentation for LangGraph vs manual @traceable wiring for ADK, datasets, evaluator functions, annotation queues, and experiment comparison; the counterpart to Langfuse Platform."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/generative-ai--04-agentic-frameworks--notes--langsmith.md
---

# LangSmith Platform

Tracing, evaluation, and dataset management from the LangChain ecosystem. This page covers
**how it works**; the choice of whether to adopt it is settled separately in
[[Observability — LangFuse vs LangSmith Decision]], which lands on Langfuse for
self-hosting and GDPR reasons. LangSmith remains the path of least resistance for
LangGraph-native stacks.

## Wiring: the instrumentation asymmetry

The single most important operational fact about LangSmith is that **its instrumentation
depth depends on whether your framework is LangChain-based.**

| Framework | Wiring | What gets traced |
|---|---|---|
| **LangGraph** | Two env vars, no code | Every node, edge transition, LLM call, tool invocation, subgraph state |
| **Google ADK** | Manual, via the LangSmith SDK | Only what is explicitly wrapped with `@traceable` |

LangGraph is native — set the env vars and the whole graph is traced:

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=<key>
LANGCHAIN_PROJECT=va-langgraph
```

ADK does not use LangChain, so `LANGCHAIN_TRACING_V2` **has no effect**. Wiring is manual
through the SDK, and note the differently-named variables — this is a common silent failure,
because setting the `LANGCHAIN_*` vars for an ADK agent produces no traces and no error:

```python
from langsmith import Client
from langsmith.run_helpers import traceable

client = Client()  # reads LANGSMITH_API_KEY from env

@traceable(name="va_google_adk", run_type="chain")
async def run_agent(query: str, session_id: str) -> dict:
    ...
```

```bash
LANGSMITH_API_KEY=<key>
LANGSMITH_PROJECT=va-google-adk
LANGSMITH_TRACING=true          # ADK-specific flag — NOT LANGCHAIN_*
```

The consequence is a **coverage difference that is easy to mistake for a quality
difference**: an ADK agent's trace looks sparse next to a LangGraph agent's not because the
agent did less, but because only the decorated call sites were recorded. Wrapping individual
tool functions in `sub_agents/` with `@traceable` is what closes the gap. Any cross-framework
comparison drawn from trace richness alone is measuring instrumentation, not behaviour — the
same trap documented in [[Experiment Tracking Schemas]].

## Datasets

Collections of input/output examples that evaluations run against.

```python
dataset = client.create_dataset(
    "va-google-adk-eval-v1",
    description="VA ADK routing + quality eval set, seeded from regression",
)

client.create_example(
    inputs={"query": row["query"], "session_id": row["task_id"]},
    outputs={"response": row.get("response", "")},
    dataset_name="va-google-adk-eval-v1",
)
```

**Seeding from traces** is the higher-value path: in the UI, open a run → *"Add to dataset"*.
This turns an observed failure directly into a regression fixture, which is the mechanism
that keeps an eval set tracking real traffic rather than drifting toward whatever cases the
author imagined. Same pattern as Langfuse's — see [[Eval Suite Maintenance]].

## Evaluators

Plain Python functions scoring one run against its expected output. The `key` in the return
value is the score name under which results aggregate:

```python
def routing_accuracy(run, example) -> dict:
    predicted = run.outputs.get("intent")
    expected = example.outputs.get("expected_intent")
    return {"score": 1.0 if predicted == expected else 0.0, "key": "routing_accuracy"}

results = evaluate(
    lambda inputs: run_agent(inputs["query"], inputs["session_id"]),
    data="va-google-adk-eval-v1",
    evaluators=[routing_accuracy, grounding_score],
    experiment_prefix="adk-eval",
)
```

The pattern worth extracting: an evaluator is a **thin adapter, not a grader**. The example
above calls an existing project grader inside the function and returns its score in
LangSmith's shape. Keeping judgement logic in your own grader package and letting the
platform adapter stay dumb is what makes the graders portable across platforms — the same
principle behind the no-unified-adapter position in [[Langfuse Platform]].

A representative evaluator set spans routing, grounding, completeness, escalation
correctness, and answer relevancy — the same axes as the Langfuse score-key registry, which
is unsurprising: the axes are properties of the agent, not of the observability vendor.

## Annotation queues

Native review UI, and a viable upgrade path from a file-based human-review script:

```python
client.create_annotation_queue("va-uncertain-cases", description="Low-confidence grader outputs")

for run_id, score in grader_results.items():
    if score < 0.6:
        client.add_runs_to_annotation_queue(queue_id, run_ids=[run_id])
```

The score threshold is the routing rule: **uncertainty, not failure, is what earns human
attention.** Completed labels export as JSONL and feed back as regression fixtures, closing
the loop with the dataset section above. See [[HITL Annotation Pipeline]].

## Experiment comparison

Every `evaluate()` call creates an experiment, comparable in the Experiments tab or by SDK
query:

```python
client.list_runs(project_name="va-google-adk", filter='eq(feedback_key, "grounding")')
```

Running two frameworks against the **same dataset** with the **same evaluators** is what
makes an ADK-vs-LangGraph comparison meaningful. Note the constraint this inherits from the
wiring asymmetry above: the comparison is only fair for metrics computed on the final
output. Anything trajectory-level favours the auto-instrumented framework by construction.
See [[ADK vs LangGraph Comparison]].

## See Also
- [[Langfuse ADK Tracing Patterns]] <!-- auto-linked -->
- [[Langfuse Platform]] — alternative-to (the same capabilities, self-hostable; the default choice here)
- [[Observability — LangFuse vs LangSmith Decision]] — supersedes (the adoption decision this page's mechanics sit under)
- [[Experiment Tracking Schemas]] — complements (what to record so runs are comparable across platforms)
- [[HITL Annotation Pipeline]] — implements (annotation queues as the review surface)
- [[Eval Suite Maintenance]] — depends-on (trace-seeded datasets as the fixture source)
- [[ADK vs LangGraph Comparison]] — instance-of (the cross-framework comparison experiments enable)
