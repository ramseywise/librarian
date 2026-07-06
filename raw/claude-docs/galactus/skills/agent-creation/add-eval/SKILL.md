---
name: add-eval
description: "Add an eval harness (runner + JSONL dataset + graders) to any galactus agent. Reads the target agent and existing eval layout, generates code that fits. Triggers on: 'add eval', 'add eval harness', 'create eval dataset', 'add grading', 'set up evals for this agent'."
allowed-tools: Read Grep Glob Bash Write
---

You are adding an eval harness to an existing galactus agent.

## Step 1 — Read the ref docs

Before generating any code, read:
1. `docs/evals/eval-harness-patterns.md` — runner patterns, concurrency, dry-run
2. `evals/graders/README.md` (Interface contract section) — BaseGrader contract, GraderOutput schema
3. `docs/evals/eval-architecture.md` — retrieval vs quality eval distinction, Strand A/E/F

## Step 2 — Read the target agent

From `$ARGUMENTS` parse the agent name (e.g. `hc_adk`, `hc_lg`, `va_langgraph`). Check:
- `evals/pipelines/clients/` for any existing client for this agent
- `data/baseline/` for existing gold datasets

If no agent name given, ask: "Which agent? (e.g. `hc_adk`)"

## Step 3 — Generate the eval client

Write `evals/pipelines/clients/{agent_name}/eval_{agent_name}.py`:

```python
from __future__ import annotations
import asyncio, json, uuid
from pathlib import Path
from typing import AsyncIterator

from evals.pipelines.base import BaseEvalRunner, EvalCase, EvalResult


class {AgentName}EvalRunner(BaseEvalRunner):
    """Eval runner for {agent_name}. Reads JSONL, calls agent, collects results."""

    async def run_case(self, case: EvalCase) -> EvalResult:
        from src.{agent_module}.main import run_turn  # adjust import to actual entry point
        response = await run_turn(
            session_id=str(uuid.uuid4()),
            message=case.query,
        )
        return EvalResult(
            case_id=case.id,
            query=case.query,
            response=response.message,
            sources=[s.url for s in response.sources],
            metadata={"agent": "{agent_name}", "PROMPT_VERSION": response.prompt_version},
        )
```

## Step 4 — Generate the JSONL dataset

Write `data/baseline/{agent_name}_qa.jsonl` (or append to existing). Format:
```json
{"id": "001", "query": "...", "expected_intent": "...", "golden_answer": "...", "expected_sources": ["https://..."], "domain": "billing"}
```

Minimum viable dataset: 20 items covering the agent's main intent categories.

## Step 5 — Wire graders

In `evals/pipelines/clients/{agent_name}/`, create `graders.py`:

```python
from evals.graders.registry import GraderRegistry
from evals.graders.heuristic import MRRGrader, NDCGGrader
from evals.graders.judges.quality import GroundingGrader

registry = GraderRegistry([
    MRRGrader(),        # free — URL rank matching
    NDCGGrader(),       # free — URL rank matching
    GroundingGrader(),  # LLM — use --limit 20 on first runs
])
```

## Step 6 — Add Makefile target

```makefile
eval-{agent_name}:
	uv run python -m evals.pipelines.clients.{agent_name}.eval_{agent_name} \
	  --dataset data/baseline/{agent_name}_qa.jsonl \
	  --limit 20 --output evals/reports/output/{agent_name}_eval.json
```

## Done when

- Runner exists and `run_case` returns `EvalResult` with `PROMPT_VERSION`
- JSONL dataset has ≥ 20 items
- `make eval-{agent_name}` runs without errors on `--limit 5 --dry-run`
- MRR + grounding graders are registered
