# Research: Eval Harness (Phase 5c)
Date: 2026-04-06

## Summary

Phase 5c builds an agent eval harness following Anthropic's three-tier eval taxonomy (unit → trajectory → end-to-end). **LangFuse** for tracing/observability, **RAGAS + DeepEval** for grading, hand-crafted music-domain golden dataset. The project already has substantial eval infrastructure (`evals/`) from a prior domain — reusable patterns but new models needed.

## Scope

**Investigated**: Agent graph architecture, existing eval/tracing infrastructure, test patterns, tracing backends (LangFuse vs Phoenix vs LangSmith), grading frameworks (RAGAS, DeepEval), golden dataset format, Anthropic eval taxonomy.

**Out of scope**: Dashboard/visualization (Phase 6b), Playwright UI testing (Phase 6a), production deployment.

**Reference**: [Anthropic — Demystifying Evals for AI Agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

## Findings

### 1. Anthropic Eval Taxonomy — Three Tiers (High)

The Anthropic article establishes a practical agent eval framework with three tiers:

**Tier 1 — Unit evals** (deterministic, fast, CI-safe):
- Test individual components in isolation: tool selection accuracy, parameter extraction, intent classification, response formatting
- Deterministic assertions — no LLM calls needed
- Catch most regressions cheaply
- Example: given "who is Aphex Twin?", assert intent=`artist_info`, confidence>=0.33

**Tier 2 — Trajectory evals** (semi-deterministic):
- Test the sequence of agent decisions/actions — did it take the right path?
- Assert on the ordered list of nodes visited and tools called
- Can be deterministic (assert tool sequence) or LLM-graded (judge if the path was reasonable)
- Example: "recommend tracks like Radiohead" → should visit `classify_intent → rewrite_query → agent → call_tools(search_tracks) → validate → agent → call_tools(recommend_for_artist) → END`

**Tier 3 — End-to-end evals** (LLM-graded, expensive):
- Test final output quality from the user's perspective
- LLM-as-judge for faithfulness, relevance, completeness
- Most realistic but hardest to make reliable and most expensive
- Example: judge whether the recommendation response actually contains relevant tracks with useful descriptions

**Key principle**: Start with Tier 1 (covers ~70% of regressions), add Tier 2 for routing logic, use Tier 3 sparingly for quality gates.

### 2. Agent Graph Architecture (High)

The graph has 7 nodes in a well-defined topology (`src/agent/graph.py:1-89`):

```
START -> trim_history -> classify_intent -> [route]
    -> low confidence  -> clarify_or_proceed -> END
    -> high confidence -> rewrite_query -> agent -> [route]
        -> has tool_calls -> call_tools -> validate_tool_output -> agent (loop)
        -> no tool_calls  -> END
```

**AgentState** (`src/agent/state.py:9-22`): `messages`, `intent`, `intent_confidence`, `entities`, `query_variants`, `tool_validation_retries`.

**Intent classification** (`src/rag_core/orchestration/query_understanding.py:44-157`): Pure keyword matching over 5 intents (`artist_info`, `genre_info`, `recommendation`, `history`, `chit_chat`). Confidence = `min(1.0, matched_keywords / 3)`. Default fallback: `artist_info` at 0.3.

**Tool routing**: 10 tools in `ALL_TOOLS` (`src/agent/tools.py:277-288`). Intent-tool alignment in `_TOOL_INTENT_MAP` (`src/agent/nodes.py:407-419`).

**Eval mapping**: Each node maps cleanly to a tier:
- Tier 1: `classify_intent` (deterministic), `route_after_classify` (deterministic), `validate_tool_output` (deterministic)
- Tier 2: full graph trajectory with mocked tools
- Tier 3: `agent_node` LLM response quality

### 3. Tracing Backend Decision: LangFuse (High)

| Aspect | LangFuse (chosen) | Arize Phoenix (in deps) | LangSmith |
|--------|-------------------|------------------------|-----------|
| **License** | MIT (self-host) / cloud | Apache 2.0 | Proprietary |
| **Hosting** | Self-host or cloud | Self-hosted only | Cloud only |
| **Cost** | Free self-host, cloud free tier (50k obs/mo) | Free but self-host infra cost | Paid ($39/mo+, free dev tier 5k traces) |
| **LangGraph integration** | `CallbackHandler` passed to graph `.invoke()` | `openinference-instrumentation-langchain` | `LANGCHAIN_TRACING_V2=true` env var |
| **Scoring API** | `langfuse.score()` — attach metrics to traces | Experiments framework | Annotation queues + experiments |
| **Dataset management** | Built-in dataset CRUD + versioning | Limited | Full dataset + experiment management |
| **RAGAS integration** | Native (`ragas.integrations.langfuse`) | Via OTEL | Via LangSmith callbacks |
| **DeepEval integration** | Via trace export | Limited | Limited |
| **Already in deps** | No (stub in `retrieval_eval.py:25-35`) | Yes (3 packages) | No |

**LangFuse chosen because**:
- Cloud free tier sufficient for dev (50k observations/month)
- Native RAGAS integration — scores flow directly into LangFuse traces
- Self-host option for production (Docker Compose, no vendor lock-in)
- Existing stub already in codebase (`evals/metrics/retrieval_eval.py:25-35`)
- Better dataset management than Phoenix for golden set versioning

**LangSmith trade-offs to revisit later**:
- Pro: Tightest LangGraph integration (same team), zero-config via env var, richer annotation UI
- Pro: Experiment framework with automatic A/B comparison
- Con: Proprietary, cloud-only, pricing scales with usage
- Con: Vendor lock-in to LangChain ecosystem
- Worth revisiting if LangFuse's LangGraph callback proves insufficient

**Phoenix deprecation**: Phoenix deps (`arize-phoenix-otel`, `openinference-*`) remain in `pyproject.toml` but won't be actively wired. Can remove in a future cleanup.

### 4. Grading Frameworks: RAGAS + DeepEval (High)

**RAGAS** — focused on RAG quality metrics:
- `faithfulness`: Is the answer grounded in retrieved context? (LLM-graded)
- `answer_relevancy`: Does the answer address the question? (LLM-graded)
- `context_precision`: Are retrieved chunks relevant? (LLM-graded)
- `context_recall`: Were all needed chunks retrieved? (LLM-graded)
- Native LangFuse integration via `ragas.integrations.langfuse`
- Scores auto-attach to LangFuse traces
- Uses any LLM as judge (can use Haiku for cost efficiency)

**DeepEval** — general-purpose LLM eval framework:
- `GEval`: Custom criteria LLM-as-judge (flexible, define your own rubric)
- `ToolCorrectnessMetric`: Did the agent call the right tools with right params?
- `AgentTaskCompletionMetric` (coming from task completion eval): Did the agent achieve the goal?
- `HallucinationMetric`: Detect unsupported claims
- Supports custom metrics via `BaseMetric` subclass
- `deepeval test run` CLI for running eval suites
- Pytest integration via `@deepeval.test_case` decorator

**How they complement each other**:
- RAGAS for RAG-specific quality (faithfulness, context) — maps to `get_artist_context` tool quality
- DeepEval for agent-specific quality (tool correctness, task completion, custom criteria)
- Both can log scores to LangFuse traces

### 5. Existing Eval Infrastructure (High)

The `evals/` directory at repo root has reusable patterns from a prior domain:

| File | Reusable? | Notes |
|------|-----------|-------|
| `evals/tasks/models.py` | Pattern only | `EvalRunConfig` snapshot pattern reusable; `GoldenSample` needs music-domain replacement |
| `evals/tasks/tracing.py` | Pattern only | `PipelineTracer`/`FailureClusterer` pattern good but LangFuse replaces the tracing layer |
| `evals/graders/answer_eval.py` | Pattern only | `CONFIRM_EXPENSIVE_OPS` cost-gate pattern reusable; `AnswerJudge` replaced by RAGAS/DeepEval |
| `evals/metrics/retrieval_eval.py` | LangFuse stub | `_log_langfuse_scores()` at line 25-35 is the seed for LangFuse integration |
| `evals/run_local_eval.py` | CLI pattern | Runner pattern reusable for agent eval CLI |
| `evals/trials/` | Directory | Empty — use for storing eval run results |

### 6. Golden Dataset Format — Music Agent (Medium)

New `AgentGoldenSample` model needed (not extending existing `GoldenSample`):

```python
class AgentGoldenSample(BaseModel):
    sample_id: str                           # e.g. "intent_artist_001"
    query: str                               # user input
    expected_intent: str                     # one of 5 intents
    expected_confidence_min: float           # lower bound for threshold tuning
    expected_tools: list[str]               # tool names query should trigger
    expected_entities: dict[str, list[str]]  # {"mood": [...], "time_period": [...]}
    expected_route: str                      # "rewrite_query" | "clarify_or_proceed"
    difficulty: str                          # easy | medium | hard
    category: str                           # "intent", "routing", "e2e"
    eval_tier: int                          # 1=unit, 2=trajectory, 3=e2e
    notes: str = ""
```

**Coverage targets** (40-60 samples):
- 8-10 per intent (5 intents = 40-50 for Tier 1)
- 5-10 trajectory cases (multi-tool chains, clarification paths)
- 5-10 edge cases (ambiguous queries, multi-intent, entity-rich)

### 7. Test Patterns and Import Chain (High)

Tests avoid importing `agent.nodes` directly due to DuckDB import chain (`agent.tools` → `RecommendationEngine` → DuckDB). Two patterns:

1. **Replication pattern** (`tests/unit/agent/test_intent_routing.py:40-56`): Copy node logic inline. Used for Tier 1 evals.
2. **Mock pattern** (`tests/integration/agent/conftest.py:17-25`): Patch `agent.tools._engine`. Used for Tier 2/3 evals.

### 8. Config Surface (High)

Settings eval should tune (`src/utils/config.py`):
- `intent_confidence_threshold: float = 0.4` (line 57)
- `max_tool_validation_retries: int = 1` (line 58)
- `max_agent_iterations: int = 10` (line 54)

New config fields needed:
- `langfuse_public_key: str` — LangFuse project public key
- `langfuse_secret_key: str` — LangFuse project secret key
- `langfuse_host: str` — LangFuse host (default `https://cloud.langfuse.com` or self-hosted)
- `enable_langfuse_tracing: bool` — toggle tracing (default False)

## Assumptions

### Eval Module Location
- **Assumption**: Agent eval code lives in `evals/agent/` alongside existing `evals/` modules.
- **Evidence**: `evals/` pattern established; `pyproject.toml:164` has `pythonpath = ["src"]` but tests import from `evals` via path insertion.
- **If wrong**: Would need to restructure imports or move to `src/evals/`.
- **Confidence**: Likely

### LangFuse Cloud for Dev
- **Assumption**: Use LangFuse cloud free tier for development; self-host later if needed.
- **Evidence**: Free tier = 50k observations/month, sufficient for dev eval. Avoids Docker infra overhead during development.
- **If wrong**: Would need Docker Compose setup for self-hosted LangFuse.
- **Confidence**: Likely

### RAGAS + DeepEval Coexistence
- **Assumption**: RAGAS handles RAG-specific metrics (faithfulness for `get_artist_context`), DeepEval handles agent-specific metrics (tool correctness, custom criteria). No overlap.
- **Evidence**: RAGAS excels at context-grounded eval; DeepEval has `ToolCorrectnessMetric` and custom `GEval`. Different strengths.
- **If wrong**: Could simplify to DeepEval only (it has faithfulness metric too, but RAGAS's is more established).
- **Confidence**: Likely

### Component-First Eval Strategy
- **Assumption**: Phase 5c starts with deterministic Tier 1 evals before LLM-graded Tier 2/3.
- **Evidence**: Keyword classifier is deterministic; tool routing is deterministic after intent. LLM calls are expensive.
- **If wrong**: Would burn API credits before having a deterministic baseline.
- **Confidence**: Confident

### Golden Dataset is Hand-Crafted
- **Assumption**: Music-domain golden set is manually curated (40-60 samples), not auto-generated.
- **Evidence**: No production traffic yet. SESSION.md "store successful conversations as golden eval examples" is aspirational.
- **If wrong**: Would need a conversation capture pipeline first.
- **Confidence**: Likely

### DuckDB Import Chain Avoidance
- **Assumption**: Tier 1 evals import `QueryAnalyzer` directly (no DuckDB chain). Tier 2/3 use the integration mock pattern.
- **Evidence**: All agent unit tests follow this pattern.
- **Confidence**: Confident

## Key Unknowns

1. **LangFuse account setup**: Cloud free tier needs project creation + API keys. Need to add `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST` to `.env.example`.

2. **RAGAS LLM backend**: RAGAS needs an LLM for grading. Default is OpenAI — needs to be configured for Anthropic (Haiku) to stay within our stack. RAGAS supports `langchain_anthropic.ChatAnthropic` as the evaluator LLM.

3. **DeepEval LLM backend**: Similar to RAGAS — defaults to OpenAI, needs Anthropic configuration. DeepEval supports custom model via `deepeval.models.DeepEvalBaseLLM` subclass.

4. **Optimal golden set size**: 40 samples gives 8 per intent for Tier 1. May be thin for confidence calibration. 60 is more robust.

5. **Eval frequency**: Tier 1 is CI-safe (free). Tier 2/3 are cost-gated (LLM calls). Need a `make eval-unit` vs `make eval-full` split.

6. **LangSmith migration path**: If LangFuse proves insufficient for LangGraph tracing, how hard is it to switch? Both use callback patterns — migration is a handler swap, not a rewrite.

## Disconfirming Evidence

- **Phoenix is already paid for**: Three Phoenix packages are in `pyproject.toml`. Switching to LangFuse means those deps are dead weight. Searched for any active Phoenix usage in `src/` — found none. The deps were added speculatively. User confirms Phoenix cost concerns override the sunk dependency cost.

- **RAGAS might be sufficient alone**: RAGAS has faithfulness, relevancy, and context metrics. DeepEval adds tool correctness and custom GEval. Searched for whether RAGAS has tool-use metrics — it does not. DeepEval's `ToolCorrectnessMetric` fills this gap for agent eval.

- **LangSmith might be simpler**: For a LangGraph project, LangSmith's zero-config `LANGCHAIN_TRACING_V2=true` is undeniably easier than LangFuse's callback handler. Searched for LangFuse + LangGraph examples — the callback handler pattern works but requires explicit passing. Trade-off: simplicity (LangSmith) vs openness + cost (LangFuse). User chose LangFuse.

- **Hand-crafted golden set might be biased**: 40-60 manually written samples risk testing what we think the classifier does, not what users actually ask. Mitigated by: (a) including adversarial/ambiguous cases, (b) planning conversation capture for future golden set enrichment, (c) the keyword classifier is simple enough that edge cases are predictable.

## Recommendation

Build the eval harness in three tiers following Anthropic's taxonomy:

**Tier 1 — Unit evals** (deterministic, CI-safe): `evals/agent/` module with `AgentGoldenSample` model. Evaluators for intent classification (accuracy/F1/confusion matrix) and tool routing (precision/recall vs `_TOOL_INTENT_MAP`). 40-60 hand-crafted golden samples. No LLM calls. Run via `make eval-unit`.

**Tier 2 — Trajectory evals** (LangFuse-traced, cost-gated): Wire LangFuse `CallbackHandler` into `build_graph()`. Replay golden queries through the graph with mocked tools. Assert on node visit sequence and tool call sequence. LangFuse captures full trace with latency. Run via `make eval-trajectory`.

**Tier 3 — End-to-end evals** (RAGAS + DeepEval graded, cost-gated): RAGAS for faithfulness/relevancy of RAG-backed responses (`get_artist_context`). DeepEval for tool correctness and custom quality criteria. Scores logged to LangFuse traces. `CONFIRM_EXPENSIVE_OPS` gate. Run via `make eval-e2e`.

New deps: `langfuse`, `ragas`, `deepeval`. Config: LangFuse keys in `.env`.
