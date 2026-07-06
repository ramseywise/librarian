---
name: eval-pipeline
description: "Galactus BKH eval pipeline extension guide — copy-paste templates for adding graders, datasets, metrics, and runners. Use when adding anything new to evals/."
---

Extension guide for the galactus eval pipeline. Start here when adding a new grader, dataset, metric, or pipeline entry point. The canonical operator runbook is `evals/README.md`; this skill should not invent Makefile targets.

## Architecture in one sentence

`uv run python -m evals.pipelines.run ...` → pipeline module (`evals/pipelines/`) → loads JSONL via `load_turn_tasks()` / `load_conversation_jsonl()` → runs graders → aggregates into `MetricResult`s → `evaluate_suite()` → renders reports.

---

## Adding a new LLM grader

### 1. Create the grader class in the relevant grader package

```python
from __future__ import annotations
from typing import Any
from ._client import get_client as _get_client, parse_json as _parse_json
from .base import Grader, GraderOutput

class MyNewGrader(Grader):
    grader_type = "my_new_grader"   # must match GRADER_REGISTRY key and THRESHOLDS key

    def __init__(self, model: str = "gemini-2.0-flash"):
        self.model = model

    async def grade(
        self,
        query: str = "",
        response: str = "",
        context: list[str] | None = None,
        **kwargs: Any,
    ) -> GraderOutput:
        if not response.strip():
            return GraderOutput(grader_type=self.grader_type, score=0.0, is_correct=False, reasoning="Empty response")

        prompt = f"""\
<your scoring prompt here>

Return ONLY valid JSON:
{{
  "score": <float 0.0-1.0>,
  "reasoning": <one sentence>
}}"""

        result = _get_client().models.generate_content(model=self.model, contents=prompt)
        data = _parse_json(result.text or "")
        score = float(data.get("score", 0.0))
        return GraderOutput(
            grader_type=self.grader_type,
            score=score,
            is_correct=score >= 0.75,   # match your THRESHOLDS entry
            reasoning=data.get("reasoning", ""),
        )
```

**Conversation-level graders** (like FrictionGrader): receive `turns` via `**kwargs`, not `query`/`response`. Single-turn inputs should return early with `is_correct=False`.

### 2. Register in `GRADER_REGISTRY` (`evals/graders/registry.py`)

```python
GRADER_REGISTRY = {
    ...
    "my_new_grader": MyNewGrader,   # add here
}
```

### 3. Add a threshold (`evals/metrics/_constants.py`)

```python
THRESHOLDS: dict[str, float] = {
    ...
    "my_new_grader": 0.75,   # add here — drives MetricResult.passed
}
```

### 4. Run it

```bash
uv run python -m evals.pipelines.eval_quality \
  --dataset data/bkh/eval_sets/sample_for_llm_graders.jsonl \
  --graders my_new_grader \
  --limit 20   # always cap first to validate prompt
```

---

## Adding a new heuristic metric

Heuristic metrics compute from `compute_stats()` output — no LLM, always free to run.

### 1. Add to `eval_stats_metrics()` (`evals/metrics/stats.py`)

```python
def eval_stats_metrics(stats: dict) -> list[MetricResult]:
    results: list[MetricResult] = []
    # ... existing metrics ...

    # Add your new metric:
    raw_val = stats.get("your_stat_key", 0)
    n = stats.get("n_total", 0)
    if n > 0:
        value = raw_val / n
        results.append(MetricResult(
            metric_name="my_new_heuristic",
            value=round(value, 4),
            threshold=THRESHOLDS.get("my_new_heuristic", 0.70),
            passed=value >= THRESHOLDS.get("my_new_heuristic", 0.70),
            n_graded=n,
            breakdown={
                "raw": raw_val,
                "caveat": "Proxy only — describe limitation here.",
            },
        ))

    return results
```

### 2. Add the threshold

```python
THRESHOLDS["my_new_heuristic"] = 0.70
```

### 3. Ensure `compute_stats()` produces the stat key

If the stat doesn't exist yet, add it in `evals/graders/calculate_stats.py` → `compute_stats()` return dict.

---

## Registering a dataset in the capability harness

After adding a JSONL and running heuristic stats, register it in `data/datasets/eval_config.yaml` so the pytest harness (`tests/eval_harness/test_bkh_harness.py`) picks it up automatically:

```yaml
my_new_dataset:
  <<: *defaults
  description: "What this dataset tests"
  gates:
    - weighted_resolution_score   # which metrics must pass
  metrics:
    weighted_resolution_score: 0.50  # optional dataset-specific threshold override
```

The key must match the JSONL stem (filename without `.jsonl`). Any key in this file that has a matching file in `data/datasets/bkh/eval_sets/` is automatically parameterized into the capability tests. Keys starting with `_` are skipped (used for YAML anchors like `_defaults`).

To add a gate for a new LLM grader once it's validated:
```yaml
my_new_dataset:
  gates:
    - weighted_resolution_score
    - my_grader          # add after grader is registered and threshold calibrated
```

Run the relevant pytest gate before committing, for example `uv run pytest tests/unit_tests/test_evals/ -q`.

---

## Adding a new dataset / eval set

### 1. Drop the JSONL into `data/datasets/bkh/eval_sets/`

Schema (turn-level, loaded by `load_turn_tasks(..., fmt="auto")`):
```jsonl
{"task_id": "t001", "query": "...", "response": "...", "expected_urls": ["https://..."], "rating": 1.0, "metadata": {"source": "my_dataset", "eval_set": "my_dataset"}}
```

`rating`: `1.0` or `"like"` = liked, `"dislike"` = disliked, `null`/`0.0` = unrated.
`metadata.eval_set` is used by `sentiment()` fallback when `rating` is absent.

### 2. Add a stem rename if needed (`evals/pipelines/eval_stats.py`)

```python
STEM_RENAMES = {
    ...
    "my_long_filename": "short_name",   # controls report filenames
}
```

### 3. Run heuristic stats

```bash
uv run python -m evals.pipelines.run stats --file data/datasets/bkh/eval_sets/my_long_filename.jsonl
uv run python -m evals.pipelines.run stats --dir data/datasets/bkh/eval_sets/
```

Reports land in:
- `evals/reports/bkh/eval_stats/{stem}_stats.html`
- `evals/reports/bkh/eval_suite/{stem}_suite.html`
- `data/datasets/bkh/stats/{stem}_stats.json`

### 4. For conversation-level data (friction)

Use `ConversationTask` schema instead of `QATask`. Load with `load_conversation_jsonl()`. Run via `evals.pipelines.eval_friction`.

```jsonl
{"task_id": "c001", "conversation_id": "abc", "turns": [{"turn": 1, "query": "...", "response": "..."}], "n_turns": 3, "conv_outcome": "resolved"}
```

---

## Adding a new pipeline entry point

Prefer extending `evals/pipelines/run.py` only when the workflow is a first-class operator command. Otherwise keep the module executable under `evals/pipelines/`. Key wiring:

```python
# 1. Load tasks
tasks = load_turn_tasks(path, fmt="auto")   # or load_conversation_jsonl for conv-level

# 2. Instantiate graders
graders = [MyNewGrader()]

# 3. Grade (async)
report = await evaluate_quality(tasks, graders)   # returns EvalReport

# 4. Build MetricResults
metric_results = [PassRateMetric("my_new_grader").compute(outputs)]

# 5. Suite report
suite = evaluate_suite(metric_results, suite_name="my run")
render_suite_html(suite, Path("evals/reports/my_report.html"))
```

Document the command and flags in `evals/README.md`. Only add a Makefile target
if it is a core convenience shortcut that cannot be expressed clearly through
`uv run python -m evals.pipelines.run ...`.

---

## Re-rendering reports without re-running

```bash
uv run python -m evals.pipelines.run render data/datasets/bkh/stats/base_stats.json
```

Stats JSON is always dumped alongside HTML — use `--render` to regenerate HTML without re-grading.

---

## Key gotchas

- **`sentiment()` fallback order**: explicit `rating` → `metadata.eval_set` → `metadata.source` → `metadata.failure_type`. New datasets need at least one of these set, or all turns will be `unrated`.
- **`e_grounding_share` is circular**: `has_sources AND dislike` → grounding error proxy approaches 1.0 by construction. Always note this in reports until we have LLM-verified grounding labels.
- **`sample_for_llm_graders.jsonl` excluded from `--dir`**: it's the LLM target file; heuristic runner excludes it by default. Pass `--exclude` to override.
- **`GroundingGrader` skips tasks without `expected_urls`**: no sources → no grounding score, not a zero.
- **`load_bkh_prepared_jsonl` vs `load_turn_tasks`**: bkh_prepared uses a flat schema with `source_1/2/3` columns; standard JSONL uses `expected_urls` list. `load_turn_tasks(..., fmt="auto")` auto-detects these formats.
- **`PassRateMetric` threshold source**: defaults to `THRESHOLDS[metric_name]` if not passed explicitly. Always add a threshold entry before adding a metric.
