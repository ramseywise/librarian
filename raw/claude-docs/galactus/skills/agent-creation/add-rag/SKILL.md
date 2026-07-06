---
name: add-rag
description: "Add or upgrade Bedrock KB retrieval (with optional CRAG loop) to any existing galactus agent. Works on new or existing agents — reads the target first, generates code that fits what's already there. Triggers on: 'add RAG', 'wire up retrieval', 'add CRAG', 'upgrade retrieval', 'add knowledge base'."
allowed-tools: Read Grep Glob Bash Write
---

You are adding Bedrock KB retrieval to an existing galactus agent. Read before you write.

## Step 1 — Read the ref docs

Before generating any code, read:
1. `docs/rag/retrieval-improvements.md` — CRAG loop, confidence gate, multi-query
2. `docs/rag/bedrock-kb.md` — KB IDs, retrieval modes, field mapping, score thresholds
3. `docs/support-agents/observability.md` — what retrieval must emit for tracing

## Step 2 — Read the target agent

From `$ARGUMENTS` parse the agent path (e.g. `src/support_agents/hc_lg`). Read:
- `agent.py` or `main.py` — framework (LangGraph or ADK), existing tool wiring
- `config.py` — existing env vars and feature flags
- `retrieval.py` if it already exists — understand what's there before changing it

If no agent path given, ask: "Which agent? (e.g. `src/support_agents/hc_lg`)"

## Step 3 — Generate the retrieval module

Write `{agent_dir}/retrieval.py` with:

```python
from __future__ import annotations
import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING

import boto3
from botocore.config import Config

from .config import settings

KB_ID = settings.bedrock_kb_id
SCORE_THRESHOLD = 0.4
TOP_K = 5
RRF_K = 60


@dataclass
class Passage:
    text: str
    url: str
    score: float

    @classmethod
    def from_bedrock(cls, result: dict) -> "Passage":
        loc = result.get("location", {})
        url = loc.get("s3Location", {}).get("uri", "") or loc.get("webLocation", {}).get("url", "")
        return cls(
            text=result["content"]["text"],
            url=url,
            score=result.get("score", 0.0),
        )


def _rrf_merge(query_result_lists: list[list[dict]]) -> list[dict]:
    """Merge multi-query results with Reciprocal Rank Fusion."""
    seen: dict[str, dict] = {}
    scores: dict[str, float] = {}
    for results in query_result_lists:
        for rank, r in enumerate(results):
            key = r["content"]["text"][:200]
            contribution = 1 / (RRF_K + rank + 1)
            if key in scores:
                scores[key] += contribution
                if r.get("score", 0) > seen[key].get("score", 0):
                    seen[key] = r
            else:
                scores[key] = contribution
                seen[key] = r
    return sorted(seen.values(), key=lambda r: scores[r["content"]["text"][:200]], reverse=True)


async def fetch_passages(queries: list[str]) -> list[Passage]:
    """Retrieve passages from Bedrock KB for one or more queries, merged via RRF."""
    client = boto3.client("bedrock-agent-runtime", config=Config(region_name=settings.aws_region))

    async def _query(q: str) -> list[dict]:
        resp = await asyncio.to_thread(
            client.retrieve,
            knowledgeBaseId=KB_ID,
            retrievalQuery={"text": q},
            retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": TOP_K}},
        )
        return resp.get("retrievalResults", [])

    raw_lists = await asyncio.gather(*[_query(q) for q in queries])
    merged = _rrf_merge(list(raw_lists)) if len(queries) > 1 else list(raw_lists[0])
    return [Passage.from_bedrock(r) for r in merged if r.get("score", 0) >= SCORE_THRESHOLD]
```

## Step 4 — Wire retrieval into the agent

**LangGraph agent** — add retrieval node to graph:
```python
# In graph/nodes/retrieval.py
from ...retrieval import fetch_passages

async def retrieval_node(state: AgentState) -> dict:
    passages = await fetch_passages(state["queries"])
    return {"passages": passages, "context": "\n\n".join(p.text for p in passages)}
```

**ADK agent** — register as a FunctionTool:
```python
# In agent.py, inside create_agent()
from .retrieval import fetch_passages

async def fetch_support_knowledge(queries: list[str]) -> str:
    passages = await fetch_passages(queries)
    return "\n\n".join(f"[{p.url}]\n{p.text}" for p in passages)

tools = [fetch_support_knowledge]
```

## Step 5 — Add config vars

Add to `config.py` (Pydantic BaseSettings):
```python
bedrock_kb_id: str = Field(..., env="BEDROCK_KB_ID")
aws_region: str = Field("eu-west-1", env="AWS_REGION")
retrieval_top_k: int = Field(5, env="RETRIEVAL_TOP_K")
score_threshold: float = Field(0.4, env="SCORE_THRESHOLD")
```

Add to `.env.example`:
```
BEDROCK_KB_ID=          # from docs/rag/bedrock-kb.md
AWS_REGION=eu-west-1
```

## Step 6 — Add CRAG loop (optional)

If the user asks for CRAG or the agent is LangGraph-based, add the confidence gate:

```python
# In retrieval.py
CRAG_HIGH_CONFIDENCE = float(os.getenv("CRAG_HIGH_CONFIDENCE", "0.7"))

def confidence_gate(passages: list[Passage]) -> bool:
    """True if top passage score is above threshold — skip rewrite."""
    return bool(passages) and passages[0].score >= CRAG_HIGH_CONFIDENCE
```

Then in the graph: `retrieve → grade → conditional(rewrite | generate)`.
Full CRAG pattern: `docs/rag/retrieval-improvements.md`.

## Done when

- `retrieval.py` exists in the agent directory
- `fetch_passages` is wired to the agent's tool list or graph node
- `BEDROCK_KB_ID` is in `config.py` and `.env.example`
- Run: `uv run pytest tests/ -k "retrieval" --tb=short -q`
