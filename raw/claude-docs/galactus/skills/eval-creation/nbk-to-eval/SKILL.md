---
name: nbk-to-eval
description: "Promote a notebook-developed grader to the galactus eval pipeline. Use when a grader in nbks/bkh/ is ready to extract to evals/graders/ and wire into the pipeline."
---

The galactus notebook-to-production workflow for LLM graders. Develop in a notebook, promote when stable.

Read `evals/graders/README.md` (Interface contract section) for the full base class, scoring/prompt contracts, and context parameter rules before writing the class.

## When to promote

A grader is ready when:
- Prompt is stable (not changing every run)
- Output JSON parses reliably on 20+ samples (no `KeyError`)
- `is_correct` threshold feels calibrated against real examples
- Reasoning strings make sense on spot-check

## Steps

### 1. Extract the class to `evals/graders/`

Add to `evals/graders/quality.py` or create a new file:

```python
from __future__ import annotations
from typing import Any
from ._client import get_client as _get_client, parse_json as _parse_json
from .base import Grader, GraderOutput

class MyGrader(Grader):
    grader_type = "my_grader"  # must match GRADER_REGISTRY key and THRESHOLDS key

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
            return GraderOutput(grader_type=self.grader_type, score=0.0,
                                is_correct=False, reasoning="Empty response")
        prompt = f"""<your stable prompt>

Return ONLY valid JSON: {{"score": <float 0.0-1.0>, "reasoning": "<one sentence>"}}"""

        result = _get_client().models.generate_content(model=self.model, contents=prompt)
        data = _parse_json(result.text or "")
        score = float(data.get("score", 0.0))
        return GraderOutput(grader_type=self.grader_type, score=score,
                            is_correct=score >= 0.75, reasoning=data.get("reasoning", ""))
```

Conversation-level graders (like FrictionGrader): accept `turns` via `**kwargs`, not `query`/`response`.

### 2. Register in `GRADER_REGISTRY` (`evals/graders/registry.py`)

```python
GRADER_REGISTRY = {
    ...
    "my_grader": MyGrader,
}
```

### 3. Add threshold (`evals/metrics/base.py`)

```python
THRESHOLDS = {
    ...
    "my_grader": 0.75,
}
```

### 4. Add WIP placeholder in `eval_stats_metrics()` (`evals/metrics/stats.py`)

In the `# --- LLM grader metrics (WIP) ---` block at the bottom:
```python
("my_grader", THRESHOLDS["my_grader"], "Requires MyGrader — describe what it measures."),
```
This keeps the suite report honest rather than silently absent.

### 5. Register in `data/bkh/eval_config.yaml`

Add to an existing dataset's gates once threshold is calibrated:
```yaml
regression_main:
  gates:
    - weighted_resolution_score
    - my_grader
  metrics:
    my_grader: 0.70  # optional dataset-specific override
```

To register a **new dataset** so the pytest harness picks it up automatically:
```yaml
my_new_dataset:
  <<: *defaults
  description: "What this dataset tests"
  gates:
    - my_grader
```

### 6. Validate on a small sample

```bash
uv run python -m evals.pipelines.eval_quality \
  --dataset data/bkh/eval_sets/sample_for_llm_graders.jsonl \
  --graders my_grader \
  --limit 20
```

### 7. Verify capability gates still pass

```bash
make eval-capability
```

## Common mistakes

- **Forgetting `eval_config.yaml`**: grader registered in the runner but pytest harness never gates on it.
- **`is_correct` threshold out of sync with THRESHOLDS**: `is_correct = score >= 0.75` but `THRESHOLDS["my_grader"] = 0.70` means the gate and the grader disagree. Keep them matching.
- **Not using `_error_output`**: wrap exceptions with `return self._error_output(exc)` so one bad API call doesn't crash the run.
- **Conversation grader receiving turn-level input**: return early with `is_correct=False` when `not kwargs.get("turns")`.
