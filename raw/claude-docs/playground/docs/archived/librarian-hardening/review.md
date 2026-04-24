## Review: librarian_hardening
Date: 2026-04-10

### Automated checks
- Tests: FAILED (`uv run pytest --tb=short -q` stops on missing optional deps: `fastapi`, `mcp`)

### Plan fidelity
| Step | Plan | Implemented | Tests | Status |
|---|---|---|---|---|
| 1 | Replace `Any` with concrete protocols | Mostly yes; factory/LLM/retrieval surfaces typed | Partial | Match |
| 2 | Drop LangChain deps | Production imports removed, but dev deps still include `langchain-core` | Partial | Deviation |
| 3 | Add multi-turn condenser | `HistoryCondenser` + graph wiring added | PASS | Match |
| 4a | RRF scoring | RRF fused retrieval in backends | PASS | Match |
| 4b | Async embeddings | `aembed_query` + parallel retrieval path | PASS | Match |
| 4c | Query cache | TTL/LRU cache + invalidation added | PASS | Match |

### Findings
- **[Non-blocking]** `pyproject.toml:62` — `langchain-core` is still present in dev dependencies, so the stated “drop LangChain deps” goal is only partially met. If full removal is intended, this should be removed or documented as a transitive-only exception.
- **[Non-blocking]** `src/agents/librarian/orchestration/graph.py:200-212` — `HistoryCondenser` defaults to the same `LLMClient` as generation when callers bypass the factory. That means direct `build_graph()` usage can silently lose the planned Haiku cost-saving behavior unless the caller injects a separate condenser.

### Verdict
[x] Needs changes | [ ] Approved with minor fixes | [ ] Approved
