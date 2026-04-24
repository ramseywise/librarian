# Plan: Phase 5c — Eval Harness (v2)
Date: 2026-04-06
Based on: `.claude/docs/research/eval-harness.md`

## Goal

A three-tier eval harness (unit → trajectory → e2e) with LangFuse tracing, RAGAS + DeepEval graders, and a hand-crafted music-domain golden dataset that can run deterministic evals in CI and LLM-graded evals on demand.

## Approach

Follow Anthropic's agent eval taxonomy. Start with deterministic Tier 1 evals (intent classification accuracy, route correctness) that need zero LLM calls and catch ~70% of regressions. Wire LangFuse tracing into the graph so Tier 2 trajectory evals capture node sequences. Add RAGAS + DeepEval as Tier 3 graders behind a cost gate. The golden dataset starts small (50 samples) and grows from conversation captures later.

## Open Questions (resolved before planning)

- Q: Where does agent eval code live? A: `evals/agent/` — consistent with existing `evals/` structure.
- Q: LangFuse cloud or self-hosted? A: Cloud free tier for dev. Self-host later if needed.
- Q: RAGAS + DeepEval LLM backend? A: Both configured with `langchain_anthropic.ChatAnthropic` (Haiku) to stay in-stack. DeepEval via `DeepEvalBaseLLM` subclass.
- Q: `pyproject.toml` changes? A: Yes — add `langfuse`, `ragas`, `deepeval` deps. User confirms before touching.
- Q: Phoenix deps removal? A: Deferred to future cleanup — not in scope.

## Out of Scope

- **Phoenix deps cleanup** — `arize-phoenix-otel`, `openinference-*` stay in `pyproject.toml` for now
- **LangSmith integration** — comparison documented in research; implement only if LangFuse proves insufficient
- **CI integration** — `make eval-unit` will be CI-ready but wiring into GitHub Actions is Phase 6+
- **Conversation capture pipeline** — aspirational golden set enrichment, needs production traffic
- **Dashboard / visualization** — Phase 6b
- **Playwright UI testing** — Phase 6a
- **Automated dataset generation** — needs production logs

---

## Steps

### Step 1: Add deps + LangFuse config ✓ DONE — 2026-04-06

**Files**:
- `pyproject.toml` (lines 8-61 — `dependencies` list)
- `src/utils/config.py` (lines 59-62 — add LangFuse fields after `max_tool_validation_retries`)

**What**: Add `langfuse`, `ragas`, `deepeval` to project deps. Add LangFuse config fields to `Settings`.

**Snippet**:
```python
# pyproject.toml — add to dependencies:
"langfuse>=2.0.0",
"ragas>=0.2.0",
"deepeval>=1.0.0",

# src/utils/config.py — add after line 62 (redis_ttl_minutes):
# LangFuse
langfuse_public_key: str = ""
langfuse_secret_key: str = ""
langfuse_host: str = "https://cloud.langfuse.com"
enable_langfuse: bool = False
```

**Test**: `uv sync && uv run python -c "from utils.config import settings; print(settings.enable_langfuse)"`

**Done when**: `uv sync` succeeds, `settings.enable_langfuse` returns `False`, imports for `langfuse`, `ragas`, `deepeval` resolve.

---

### Step 2: LangFuse callback + tracing helper ✓ DONE — 2026-04-06

**Files**:
- `src/utils/langfuse_tracing.py` (new)
- `tests/unit/agent/test_langfuse_tracing.py` (new)

**What**: Create a LangFuse callback factory that returns a `CallbackHandler` when enabled, `None` when disabled. No changes to `build_graph()` or `graph.py` — tracing is opt-in at invocation time via the `config["callbacks"]` pattern. The module-level `graph` stays unchanged.

**Snippet**:
```python
# src/utils/langfuse_tracing.py
from __future__ import annotations
from langfuse.callback import CallbackHandler
from utils.config import settings
from utils.logging import get_logger

log = get_logger(__name__)

def get_langfuse_handler(
    session_id: str | None = None,
    user_id: str | None = None,
    trace_name: str = "listen-wiseer",
) -> CallbackHandler | None:
    """Return a LangFuse CallbackHandler if enabled, else None."""
    if not settings.enable_langfuse or not settings.langfuse_public_key:
        return None
    handler = CallbackHandler(
        public_key=settings.langfuse_public_key,
        secret_key=settings.langfuse_secret_key,
        host=settings.langfuse_host,
        session_id=session_id,
        user_id=user_id,
        trace_name=trace_name,
    )
    log.info("langfuse.handler.created", session_id=session_id)
    return handler
```

The graph invocation pattern (used by eval runner + Chainlit):
```python
handler = get_langfuse_handler(session_id="eval_run_001")
config = {"configurable": {"thread_id": "..."}}
if handler:
    config["callbacks"] = [handler]
result = await graph.ainvoke(state, config=config)
```

**Test**: Unit test mocks `settings` to verify handler creation when enabled / None when disabled. No real LangFuse calls.

```python
# tests/unit/agent/test_langfuse_tracing.py
def test_handler_none_when_disabled(monkeypatch):
    monkeypatch.setattr("utils.config.settings.enable_langfuse", False)
    from utils.langfuse_tracing import get_langfuse_handler
    assert get_langfuse_handler() is None

def test_handler_created_when_enabled(monkeypatch):
    monkeypatch.setattr("utils.config.settings.enable_langfuse", True)
    monkeypatch.setattr("utils.config.settings.langfuse_public_key", "pk-lf-test")
    monkeypatch.setattr("utils.config.settings.langfuse_secret_key", "sk-lf-test")
    from utils.langfuse_tracing import get_langfuse_handler
    handler = get_langfuse_handler(session_id="test")
    assert handler is not None
```

**Run**: `uv run pytest tests/unit/agent/test_langfuse_tracing.py -v`

**Done when**: Handler factory returns `CallbackHandler` when enabled, `None` when disabled. No changes to graph compilation.

---

### Step 3: Golden dataset models + JSONL files ✓ DONE — 2026-04-06

**Files**:
- `evals/tasks/models.py` (lines 1-44 — add `AgentGoldenSample`, `IntentEvalMetrics`)
- `evals/datasets/golden_intent.jsonl` (new — 50 samples)
- `tests/unit/eval/__init__.py` (new)
- `tests/unit/eval/test_golden_models.py` (new)

**What**: Add `AgentGoldenSample` model alongside existing `GoldenSample` (don't modify existing models). Create 50 hand-crafted golden samples covering all 5 intents (10 per intent), each annotated with expected intent, confidence range, route, tools, and entities. Add `IntentEvalMetrics` for results.

**Snippet**:
```python
# evals/tasks/models.py — add after RetrievalMetrics (line 44):

class AgentGoldenSample(BaseModel):
    """Golden sample for agent eval — intent, routing, and tool selection."""
    sample_id: str
    query: str
    expected_intent: str
    expected_confidence_min: float = 0.0
    expected_tools: list[str] = []
    expected_entities: dict[str, list[str]] = {}
    expected_route: str = "rewrite_query"  # or "clarify_or_proceed"
    difficulty: str = "easy"
    eval_tier: int = 1  # 1=unit, 2=trajectory, 3=e2e
    notes: str = ""


class IntentEvalMetrics(BaseModel):
    """Aggregate intent classification eval results."""
    accuracy: float
    per_intent_f1: dict[str, float]
    confusion: dict[str, dict[str, int]]
    n_samples: int
    confidence_threshold: float
```

**JSONL samples** (10 per intent, 50 total). Intent distribution:
- `artist_info` × 10: "who is Aphex Twin?", "tell me about Radiohead", edge cases
- `genre_info` × 10: "what is zouk?", "explain ambient music", edge cases
- `recommendation` × 10: "recommend tracks like X", "suggest chill music", edge cases
- `history` × 10: "what have I been listening to?", "my recent plays", edge cases
- `chit_chat` × 10: "hello", "thanks", "how are you", edge cases

Include 5-8 adversarial samples (ambiguous, multi-intent, low-confidence) spread across intents.

**Test**:
```python
# tests/unit/eval/test_golden_models.py
def test_golden_samples_load_and_validate():
    ...  # load JSONL, validate with AgentGoldenSample, check 50 samples

def test_all_intents_covered():
    ...  # assert all 5 intents have >= 8 samples

def test_adversarial_samples_exist():
    ...  # assert difficulty="hard" samples exist
```

**Run**: `uv run pytest tests/unit/eval/test_golden_models.py -v`

**Done when**: 50 samples load and validate. All 5 intents covered. Hard samples present.

---

### Step 4: Tier 1 — Deterministic intent + route eval ✓ DONE — 2026-04-06

**Files**:
- `evals/agent/__init__.py` (new)
- `evals/agent/intent_eval.py` (new)
- `tests/unit/eval/test_intent_eval.py` (new)

**What**: Evaluator that runs `classify_intent()` and `route_after_classify()` against every golden sample. Computes accuracy, per-intent F1, confusion matrix. Imports `QueryAnalyzer` directly (no DuckDB chain). No LLM calls — fully deterministic.

**Snippet**:
```python
# evals/agent/intent_eval.py
from __future__ import annotations
from collections import defaultdict
from evals.tasks.models import AgentGoldenSample, IntentEvalMetrics
from rag_core.orchestration.query_understanding import QueryAnalyzer
from utils.config import settings
from utils.logging import get_logger

log = get_logger(__name__)
_analyzer = QueryAnalyzer()

def evaluate_intent(samples: list[AgentGoldenSample]) -> IntentEvalMetrics:
    """Run deterministic intent classification eval. No LLM calls."""
    confusion: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    correct = 0
    for sample in samples:
        result = _analyzer.analyze(sample.query)
        predicted = result.intent
        expected = sample.expected_intent
        confusion[expected][predicted] += 1
        if predicted == expected:
            correct += 1
    # compute per-intent F1 from confusion matrix
    ...
    return IntentEvalMetrics(
        accuracy=correct / len(samples),
        per_intent_f1=f1_scores,
        confusion=dict(confusion),
        n_samples=len(samples),
        confidence_threshold=settings.intent_confidence_threshold,
    )

def _route_after_classify(intent: str, confidence: float) -> str:
    """Replicated from agent.nodes — avoids DuckDB import chain."""
    if intent == "chit_chat":
        return "rewrite_query"
    if confidence < settings.intent_confidence_threshold:
        return "clarify_or_proceed"
    return "rewrite_query"

def evaluate_routing(samples: list[AgentGoldenSample]) -> dict:
    """Check route matches expected_route for each sample.

    Uses replicated routing logic (not imported from agent.nodes)
    to avoid the DuckDB import chain.
    """
    correct = 0
    for sample in samples:
        result = _analyzer.analyze(sample.query)
        predicted_route = _route_after_classify(result.intent, result.confidence)
        if predicted_route == sample.expected_route:
            correct += 1
    return {"route_accuracy": correct / len(samples), "n_samples": len(samples)}
```

**Test**:
```python
# tests/unit/eval/test_intent_eval.py — synthetic samples, not golden file
def test_evaluate_intent_perfect():
    samples = [AgentGoldenSample(sample_id="t1", query="who is Aphex Twin?",
               expected_intent="artist_info", ...)]
    metrics = evaluate_intent(samples)
    assert metrics.accuracy == 1.0

def test_evaluate_routing_correct():
    ...  # high confidence → rewrite_query, low → clarify_or_proceed
```

**Run**: `uv run pytest tests/unit/eval/test_intent_eval.py -v`

**Done when**: `evaluate_intent` returns accuracy + F1 + confusion matrix. `evaluate_routing` returns route accuracy. Both work with synthetic fixtures.

---

### Step 5: Tier 2 — Trajectory eval with LangFuse tracing ✓ DONE — 2026-04-06

**Files**:
- `evals/agent/cost_gate.py` (new — env-var-driven cost gate)
- `evals/graders/answer_eval.py` (update — import from `cost_gate` instead of hardcoded bool)
- `evals/agent/trajectory_eval.py` (new)
- `tests/unit/eval/test_trajectory_eval.py` (new)
- `tests/unit/eval/test_cost_gate.py` (new)

**What**: Create an env-var-driven cost gate (`evals/agent/cost_gate.py`) so Makefile targets can toggle it. Update `evals/graders/answer_eval.py` to import from the new gate instead of using its hardcoded `False`. Run golden queries through the compiled graph with mocked tools. Record which nodes were visited and which tools were called. Assert tool calls match `expected_tools`. Optionally attach LangFuse `CallbackHandler` for full trace capture. Cost-gated — requires `CONFIRM_EXPENSIVE_OPS=true` env var (LLM calls for `agent_node` and `rewrite_query`).

**Snippet**:
```python
# evals/agent/cost_gate.py
"""Env-var-driven cost gate for LLM-calling eval tiers.

Reads from the CONFIRM_EXPENSIVE_OPS env var so Makefile
targets can toggle it: CONFIRM_EXPENSIVE_OPS=true make eval-trajectory

All eval modules (including evals/graders/answer_eval.py) import from here.
"""
from __future__ import annotations
import os

CONFIRM_EXPENSIVE_OPS: bool = os.getenv("CONFIRM_EXPENSIVE_OPS", "").lower() in ("true", "1")
```

```python
# evals/graders/answer_eval.py — replace the two hardcoded lines:
#   CONFIRM_EXPENSIVE_OPS = False  # flip consciously, never commit as True
#   CONFIRM_EXPENSIVE_OPS = False  # never commit as True
# with:
from evals.agent.cost_gate import CONFIRM_EXPENSIVE_OPS
```

```python
# tests/unit/eval/test_cost_gate.py
def test_cost_gate_default_false(monkeypatch):
    monkeypatch.delenv("CONFIRM_EXPENSIVE_OPS", raising=False)
    # Re-import to pick up env change
    import importlib
    import evals.agent.cost_gate as cg
    importlib.reload(cg)
    assert cg.CONFIRM_EXPENSIVE_OPS is False

def test_cost_gate_true_when_set(monkeypatch):
    monkeypatch.setenv("CONFIRM_EXPENSIVE_OPS", "true")
    import importlib
    import evals.agent.cost_gate as cg
    importlib.reload(cg)
    assert cg.CONFIRM_EXPENSIVE_OPS is True
```

```python
# evals/agent/trajectory_eval.py
from __future__ import annotations
from dataclasses import dataclass
from evals.tasks.models import AgentGoldenSample
from evals.agent.cost_gate import CONFIRM_EXPENSIVE_OPS
from utils.langfuse_tracing import get_langfuse_handler
from utils.logging import get_logger

log = get_logger(__name__)

@dataclass
class TrajectoryResult:
    sample_id: str
    query: str
    actual_intent: str
    expected_intent: str
    tools_called: list[str]
    expected_tools: list[str]
    tool_match: bool
    intent_match: bool
    node_sequence: list[str]  # for future trajectory assertions

async def evaluate_trajectory(
    samples: list[AgentGoldenSample],
    graph,  # CompiledStateGraph
    *,
    enable_tracing: bool = False,
) -> list[TrajectoryResult]:
    """Run graph on each sample and collect trajectory. Cost-gated."""
    if not CONFIRM_EXPENSIVE_OPS:
        raise RuntimeError(
            "Set CONFIRM_EXPENSIVE_OPS=true env var for trajectory eval."
        )
    ...
```

Uses the integration conftest mock pattern (`patch("agent.tools._engine", mock_engine)`) to avoid real Spotify/DuckDB calls. The LLM calls (Haiku) are real — that's what we're evaluating.

**Test** (no LLM — mock `_llm_with_tools.ainvoke`):
```python
# tests/unit/eval/test_trajectory_eval.py
def test_extract_tools_from_messages():
    ...  # verify tool extraction from AIMessage.tool_calls

def test_trajectory_result_tool_match():
    ...  # verify match logic
```

**Run**: `uv run pytest tests/unit/eval/test_trajectory_eval.py -v`

**Done when**: `TrajectoryResult` captures tools called + intent + match status. Unit tests pass with mocked graph.

---

### Step 6: Tier 3 — RAGAS + DeepEval graders ✓ DONE — 2026-04-06

**Files**:
- `evals/agent/graders.py` (new)
- `tests/unit/eval/test_graders.py` (new)

**What**: Wrap RAGAS faithfulness/relevancy and DeepEval tool correctness as grader functions. Configure both with Anthropic Haiku as the evaluator LLM. Cost-gated behind `CONFIRM_EXPENSIVE_OPS`. Scores log to LangFuse traces when enabled.

**Snippet**:
```python
# evals/agent/graders.py
from __future__ import annotations
from langchain_anthropic import ChatAnthropic
from evals.agent.cost_gate import CONFIRM_EXPENSIVE_OPS
from utils.config import settings
from utils.logging import get_logger

log = get_logger(__name__)

HAIKU_MODEL = "claude-haiku-4-5-20251001"

def get_ragas_llm() -> ChatAnthropic:
    """Return Haiku instance for RAGAS grading."""
    return ChatAnthropic(model=HAIKU_MODEL, api_key=settings.anthropic_api_key)

def grade_faithfulness(question: str, answer: str, contexts: list[str]) -> float:
    """RAGAS faithfulness score. Cost-gated."""
    from ragas.metrics import faithfulness
    from ragas import evaluate
    ...

def grade_tool_correctness(
    query: str,
    expected_tools: list[str],
    actual_tools: list[str],
) -> float:
    """DeepEval tool correctness. Deterministic — no LLM needed for exact match."""
    if not expected_tools:
        return 1.0 if not actual_tools else 0.0
    matches = set(expected_tools) & set(actual_tools)
    return len(matches) / len(expected_tools)
```

**Test** (no LLM — test the deterministic `grade_tool_correctness` and mock RAGAS):
```python
# tests/unit/eval/test_graders.py
def test_tool_correctness_perfect_match():
    assert grade_tool_correctness("q", ["search_tracks"], ["search_tracks"]) == 1.0

def test_tool_correctness_partial():
    assert grade_tool_correctness("q", ["search_tracks", "recommend_for_artist"],
                                   ["search_tracks"]) == 0.5

def test_tool_correctness_no_expected():
    assert grade_tool_correctness("q", [], []) == 1.0
```

**Run**: `uv run pytest tests/unit/eval/test_graders.py -v`

**Done when**: `grade_tool_correctness` works deterministically. RAGAS + DeepEval wrappers defined (LLM-graded paths tested only with `CONFIRM_EXPENSIVE_OPS`).

---

### Step 7: Eval runner CLI + Makefile targets ✓ DONE — 2026-04-06

**Files**:
- `evals/run_agent_eval.py` (new)
- `Makefile` (lines 82-86 area — add `eval-unit`, `eval-trajectory`, `eval-e2e`)
- `tests/unit/eval/test_run_agent_eval.py` (new)

**What**: Single CLI entry point with `--tier` flag. `eval-unit` runs Tier 1 (free). `eval-trajectory` and `eval-e2e` require `CONFIRM_EXPENSIVE_OPS=True`.

**Snippet**:
```python
# evals/run_agent_eval.py
"""
Listen-wiseer agent eval harness.

Usage:
    # Tier 1 — deterministic intent/route eval (free, CI-safe):
    PYTHONPATH=src uv run python -m evals.run_agent_eval --tier 1

    # Tier 2 — trajectory eval with LangFuse (costs money):
    CONFIRM_EXPENSIVE_OPS=true PYTHONPATH=src uv run python -m evals.run_agent_eval --tier 2

    # Tier 3 — e2e with RAGAS + DeepEval graders (costs money):
    CONFIRM_EXPENSIVE_OPS=true PYTHONPATH=src uv run python -m evals.run_agent_eval --tier 3

    # All tiers:
    CONFIRM_EXPENSIVE_OPS=true PYTHONPATH=src uv run python -m evals.run_agent_eval --tier all
"""
```

**Makefile targets**:
```makefile
eval-unit:
	PYTHONPATH=src uv run python -m evals.run_agent_eval --tier 1

eval-trajectory:
	CONFIRM_EXPENSIVE_OPS=true PYTHONPATH=src uv run python -m evals.run_agent_eval --tier 2

eval-e2e:
	CONFIRM_EXPENSIVE_OPS=true PYTHONPATH=src uv run python -m evals.run_agent_eval --tier 3
```

**Test**:
```python
# tests/unit/eval/test_run_agent_eval.py
def test_load_golden_samples():
    from evals.run_agent_eval import load_golden_samples
    samples = load_golden_samples()
    assert len(samples) >= 50

def test_tier1_runs_without_llm():
    ...  # verify tier 1 doesn't raise CONFIRM_EXPENSIVE_OPS error
```

**Run**: `uv run pytest tests/unit/eval/test_run_agent_eval.py -v`

**CLI smoke**: `PYTHONPATH=src uv run python -m evals.run_agent_eval --tier 1`

**Done when**: `make eval-unit` runs end-to-end and prints accuracy + F1 for intent classification. Tier 2/3 raise cost-gate error without `CONFIRM_EXPENSIVE_OPS`.

---

### Step 8: Regression ✓ DONE — 2026-04-06

```bash
uv run pytest tests/unit/ -k "eval or intent_routing or nodes or state" --tb=short -q
PYTHONPATH=src uv run python -m evals.run_agent_eval --tier 1
```

**Pass criteria**:
- All new eval tests pass (≥12 new tests)
- Existing 65 agent/rag tests still pass
- Tier 1 eval runs end-to-end: accuracy + per-intent F1 printed
- No regressions in intent routing or state tests

---

## Test Plan

| Step | Command | Verifies |
|------|---------|----------|
| 1 | `uv sync && uv run python -c "from utils.config import settings; print(settings.enable_langfuse)"` | Deps install, config fields |
| 2 | `uv run pytest tests/unit/agent/test_langfuse_tracing.py -v` | LangFuse handler factory |
| 3 | `uv run pytest tests/unit/eval/test_golden_models.py -v` | Golden dataset loads + validates |
| 4 | `uv run pytest tests/unit/eval/test_intent_eval.py -v` | Deterministic intent eval |
| 5 | `uv run pytest tests/unit/eval/test_cost_gate.py tests/unit/eval/test_trajectory_eval.py -v` | Cost gate + trajectory data structures |
| 6 | `uv run pytest tests/unit/eval/test_graders.py -v` | Tool correctness grader |
| 7 | `uv run pytest tests/unit/eval/test_run_agent_eval.py -v` + `make eval-unit` | CLI runner + Makefile |
| 8 | `uv run pytest tests/unit/ -k "eval or intent_routing or nodes" --tb=short -q` | Full regression |

---

## Dependency Map

```
Step 1 (deps + config) ← independent
  ↓
Step 2 (LangFuse handler) ← needs Step 1
  ↓
Step 3 (golden dataset) ← needs Step 1 (models)
  ↓
Step 4 (Tier 1 eval) ← needs Step 3
  ↓
Step 5 (Tier 2 eval + cost_gate.py) ← needs Steps 2 + 3 + 4
  ↓
Step 6 (Tier 3 graders) ← needs Steps 1 (deps) + 5 (cost_gate)
  ↓
Step 7 (runner + Makefile) ← needs Steps 4 + 5 + 6
  ↓
Step 8 (regression) ← needs all
```

---

## Risks & Rollback

### Step 1: Add deps + LangFuse config
- **Risk**: `langfuse` / `ragas` / `deepeval` version conflicts with existing LangChain ecosystem
- **Blast radius**: Local — only affects dep resolution
- **Rollback**: `git checkout pyproject.toml src/utils/config.py && uv sync`
- **Verify rollback**: `uv run python -c "from utils.config import settings"` succeeds

### Step 2: LangFuse callback
- **Risk**: `langfuse.callback.CallbackHandler` API changes between versions
- **Blast radius**: Local — handler is opt-in, default graph unchanged
- **Rollback**: `git revert HEAD --no-edit`
- **Verify rollback**: `uv run pytest tests/unit/agent/ --tb=short -q` passes

### Step 3: Golden dataset
- **Risk**: Golden samples have wrong expected_intent (keyword classifier behaves differently than annotator assumed)
- **Blast radius**: Local — JSONL files only, no production code affected
- **Rollback**: Edit JSONL — no code changes needed
- **Verify rollback**: Re-run `uv run pytest tests/unit/eval/test_golden_models.py`

### Step 5: Cost gate + trajectory eval
- **Risk (cost_gate.py)**: Changing `answer_eval.py` to import from `cost_gate.py` could break the existing `test_answer_eval_raises_without_flag` test if import path changes incorrectly
- **Mitigation**: Existing test calls `run_answer_eval()` which internally checks the flag — import source is transparent to the caller
- **Verify**: `uv run pytest tests/unit/rag/test_retrieval_eval.py::test_answer_eval_raises_without_flag -v`
- **Risk (trajectory)**: LLM calls in `agent_node` cost more than expected for 50 samples
- **Blast radius**: Local (cost) — `CONFIRM_EXPENSIVE_OPS` gate prevents accidental spend
- **Rollback**: `git revert HEAD --no-edit && uv run pytest tests/unit/rag/test_retrieval_eval.py -v`
- **Verify rollback**: Run without `CONFIRM_EXPENSIVE_OPS` env var → RuntimeError raised

### Step 6: RAGAS + DeepEval graders
- **Risk**: RAGAS defaults to OpenAI, fails without OpenAI key if Anthropic config not wired correctly
- **Blast radius**: Local — graders are cost-gated, won't run in CI
- **Rollback**: `git revert HEAD --no-edit`
- **Verify rollback**: `uv run pytest tests/unit/eval/test_graders.py` (deterministic tests still pass)

### Global rollback
If multiple steps need reversal:
```bash
git revert HEAD~N..HEAD --no-edit  # where N = steps applied
uv sync
uv run pytest tests/unit/agent/ --tb=short -q  # verify baseline
```
