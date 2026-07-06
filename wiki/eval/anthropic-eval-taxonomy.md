---
title: Anthropic Three-Tier Eval Taxonomy
tags: [eval, pattern, concept]
summary: Practical agent evaluation framework from Anthropic — three tiers (unit/trajectory/e2e) mapped to cost, determinism, and failure coverage. Unit covers ~70% of regressions cheaply; trajectory checks routing paths; e2e is sparingly used for quality gates.
updated: 2026-07-06
sources:
  - raw/claude-docs/listen-wiseer/docs/research/evaluation/eval-harness.md
---

# Anthropic Three-Tier Eval Taxonomy

Reference: [Anthropic — Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

A practical agent eval framework built around three tiers that differ by cost, determinism, and failure coverage. The key principle: start with Tier 1, which covers ~70% of regressions cheaply.

---

## The Three Tiers

### Tier 1 — Unit Evals

**Properties:** Deterministic, fast, CI-safe, no LLM calls

Test individual components in isolation:
- Tool selection accuracy given a query
- Parameter extraction from user input
- Intent classification routing
- Response formatting validation

**Example:** Given "who is Aphex Twin?", assert `intent == artist_info` and `confidence >= 0.33`. Pure function — no agent invocation needed.

**Coverage target:** ~70% of regressions. Most classification and routing failures are deterministic and catchable at this tier.

---

### Tier 2 — Trajectory Evals

**Properties:** Semi-deterministic, LangFuse-traced, cost-gated

Test the sequence of agent decisions/actions:
- Assert on the ordered list of nodes visited
- Assert on tools called and their arguments
- Can be deterministic (assert exact tool sequence) or LLM-graded (judge if path was reasonable)

**Example:** "recommend tracks like Radiohead" → assert graph visits `classify_intent → rewrite_query → agent → call_tools(search_tracks) → validate → ...` in this order.

**How to run:** Replay golden queries through the graph with mocked tools. LangFuse captures full trace with latency per node.

**Cost gate:** These require tool calls and graph traversal — more expensive than unit evals. Gate behind `CONFIRM_EXPENSIVE_OPS=1`.

---

### Tier 3 — End-to-End Evals

**Properties:** LLM-graded, most realistic, most expensive, use sparingly

Test final output quality from the user's perspective:
- LLM-as-judge for faithfulness, relevance, completeness
- RAGAS metrics: `faithfulness`, `answer_relevancy`, `context_precision`, `context_recall`
- DeepEval: `ToolCorrectnessMetric`, `GEval` (custom rubric)

**Example:** Judge whether a recommendation response actually contains relevant tracks with useful descriptions.

**When to use:** Quality gates before releases, not in every CI run. Use RAGAS for RAG-backed responses; DeepEval for agent-specific quality (tool correctness, custom criteria).

---

## Tier Mapping by Component

| Component | Tier |
|---|---|
| Intent classifier (keyword-based, deterministic) | Tier 1 |
| Route function (deterministic conditional) | Tier 1 |
| Tool call validation | Tier 1 |
| Full graph trajectory with mocked tools | Tier 2 |
| Agent LLM response quality | Tier 3 |

---

## Grading Frameworks

### RAGAS (RAG quality)
- `faithfulness` — is the answer grounded in retrieved context?
- `answer_relevancy` — does the answer address the question?
- `context_precision` — are retrieved chunks relevant?
- `context_recall` — were all needed chunks retrieved?
- Native LangFuse integration: scores auto-attach to traces
- Configure evaluator LLM: `langchain_anthropic.ChatAnthropic` (Haiku for cost efficiency)

### DeepEval (agent quality)
- `ToolCorrectnessMetric` — did the agent call the right tools with right params?
- `AgentTaskCompletionMetric` — did the agent achieve the goal?
- `GEval` — custom criteria LLM-as-judge with your own rubric
- `HallucinationMetric` — detect unsupported claims
- `deepeval test run` CLI, pytest integration via `@deepeval.test_case`

**How they complement each other:** RAGAS for RAG-specific quality (faithfulness, context); DeepEval for agent-specific quality (tool correctness, custom criteria). Both log scores to LangFuse traces.

---

## Golden Dataset Design

```python
class AgentGoldenSample(BaseModel):
    sample_id: str                           # e.g. "intent_artist_001"
    query: str                               # user input
    expected_intent: str                     # one of N intents
    expected_confidence_min: float           # lower bound for threshold tuning
    expected_tools: list[str]                # tool names query should trigger
    expected_entities: dict[str, list[str]]  # {"mood": [...], "artist": [...]}
    expected_route: str                      # e.g. "rewrite_query" | "clarify_or_proceed"
    difficulty: str                          # easy | medium | hard
    eval_tier: int                           # 1=unit, 2=trajectory, 3=e2e
    notes: str = ""
```

**Coverage targets** (40-60 samples):
- 8-10 per intent (for Tier 1 intent classification)
- 5-10 trajectory cases (multi-tool chains, clarification paths)
- 5-10 edge cases (ambiguous queries, multi-intent, entity-rich)

**Note:** Hand-crafted datasets risk testing what you think the classifier does, not what users actually ask. Mitigate by including adversarial/ambiguous cases and planning conversation capture for future enrichment.

---

## Makefile Flow

```makefile
make eval-unit         # Tier 1 — deterministic, CI-safe, no gate
make eval-trajectory   # Tier 2 — LangFuse-traced, cost-gated
make eval-e2e          # Tier 3 — RAGAS + DeepEval, cost-gated
CONFIRM_EXPENSIVE_OPS=1 make eval-trajectory  # unlock gated runs
```

---

## See Also
- [[VA Eval Harness]]
- [[RAG Evaluation]]
- [[Galactus Eval Architecture]]
- [[HITL Annotation Pipeline]]
- [[Observability — LangFuse vs LangSmith Decision]]
