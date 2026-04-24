## Review: orchestration-rollout
Date: 2026-04-12

### Automated checks
- Tests: **412 PASSED**, 0 failed

### Plan fidelity

| Step | Plan | Implemented | Tests | Status |
|------|------|-------------|-------|--------|
| P1: Vocab alignment | Rename *Subgraph → *Agent, add name/desc/instruction, as_node() | ✅ Done | 393 pass | Match |
| P2: ADK + Bedrock KB | BedrockKBAgent wrapping BedrockKBClient | ✅ Done | 4 tests | Match |
| P3: ADK + Custom RAG | Tools + Agent with Gemini 2.0 Flash | ✅ Done | 10 tests | Match |
| P4: ADK + LangGraph hybrid | LibrarianADKAgent + coordinator | ✅ Done | 5 tests | Match |
| Restructure | clients/, langgraph/, factory move | ✅ Done | All pass | Match |
| Shim cleanup | Remove old re-export files | ✅ Done | All pass | Match |

### Findings

#### [Blocking] Missing tools: query understanding, condenser, confidence gating

**`tools.py` only has 2 tools: `search_knowledge_base` + `rerank_results`.**

The Librarian LangGraph pipeline has 7 nodes (condense, analyze, retrieve, rerank, gate, generate, snippet_retrieve). The ADK custom_rag agent only exposes 2 of these as tools — the LLM has no way to:

1. **Condense multi-turn queries** — no `condense_query` tool. If the user says "what about that one?", Gemini gets the raw query with no history rewriting. The LangGraph pipeline uses `CondenserAgent` (Haiku) for this.

2. **Analyze query intent/entities** — no `analyze_query` tool. The `QueryAnalyzer` does intent classification, entity extraction, sub-query decomposition, and term expansion. Without this, Gemini can't benefit from domain-specific entity recognition or retrieval mode selection.

3. **Check retrieval confidence** — no `check_confidence` tool. The CRAG gate logic (confidence threshold → retry) is implicit in the instruction ("if confidence below 0.3, try again") but the tool returns don't surface `confidence_score` at the right level. `rerank_results` returns confidence but `search_knowledge_base` doesn't — so the LLM has to rerank every time to know if results are good enough.

**Fix**: Add 2 more tools:
- `condense_query(query, conversation_history)` → standalone query (uses CondenserAgent)
- `analyze_query(query)` → intent, entities, expanded_terms, complexity, retrieval_mode

#### [Blocking] No tracing/observability in ADK agents

The LangGraph pipeline has full Langfuse tracing (`librarian/tracing.py` → `build_langfuse_handler` → `make_runnable_config`). The ADK agents have **zero observability integration**:

- `BedrockKBAgent` — no trace emitted
- `CustomRAGAgent` — no `before_tool_callback` / `after_tool_callback` for tool-level tracing
- `LibrarianADKAgent` — passes through to LangGraph which *does* have tracing, but the ADK wrapper layer itself is invisible

ADK provides `before_agent_callback`, `after_agent_callback`, `before_tool_callback`, `after_tool_callback` — these should log to structlog at minimum, and to Langfuse when enabled.

**Fix**: Add callback functions in a new `orchestration/adk/callbacks.py` that log agent/tool invocations to structlog + optionally Langfuse.

#### [Blocking] `_extract_latest_query` is duplicated 3 times

Identical function in `bedrock_agent.py:25`, `hybrid_agent.py:119`, and inline in `custom_rag_agent.py` (via `run_custom_rag_query`). Should be one shared utility.

**Fix**: Move to `orchestration/adk/__init__.py` or a shared `utils.py`.

#### [Non-blocking] `tools.py` uses module-level singletons with mutable global state

`_retriever`, `_embedder`, `_reranker` are module-level globals set via `configure_tools()`. This is thread-unsafe and makes testing fragile — tests must remember to reset state. The LangGraph pipeline uses proper DI (factory injection).

**Fix**: Use a `ToolContext` dataclass or a simple container object instead of module globals. Pass it to `create_custom_rag_agent` which creates closures over it.

#### [Non-blocking] `custom_rag_agent.py` creates a new Runner/SessionService per query

`run_custom_rag_query()` creates a fresh `InMemorySessionService` and `Runner` on every call. For eval this is fine but for API use it would discard session state between calls.

**Fix**: Accept `runner` + `session_service` as optional parameters; create only if not provided.

#### [Non-blocking] `output_key` not set on any agent

ADK's `output_key` field stores the agent's response in the session state dict, making it available to downstream agents in a multi-agent flow. Currently none of the agents set this. The coordinator would benefit from `output_key="response"` on its sub-agents.

#### [Non-blocking] Bedrock citations are lost in the ADK wrapper

`BedrockKBAgent._run_async_impl` gets citations from `resp.citations` but only emits the text in the ADK event. Citations are logged but not returned to the caller. Same issue in `LibrarianADKAgent`.

**Fix**: Include citations in `Event.custom_metadata` or as a second Part in the Content.

#### [Nit] `coordinator.py` type hint says `Agent` but should accept `BaseAgent`

`create_coordinator` types both params as `Agent` but `LibrarianADKAgent` is a `BaseAgent`. Works at runtime (Pydantic coercion) but the type hint is wrong.

#### [Nit] `_INSTRUCTION` in `custom_rag_agent.py` could be loaded from a template file

The instruction is 7 lines. It's fine inline for now, but as it grows (adding condense/analyze tool instructions), extracting to `librarian/generation/prompts.py` or a `.txt` file would be cleaner.

### Stub detection

- `TODO(3)` in `experiment.py:838` — "extract URLs from tool call results" for adk-custom-rag variant. Non-blocking for eval scaffolding but means hit_rate/MRR will always be 0 for this variant. **Should be documented or fixed before real eval runs.**

### Verdict

**[ ] Needs changes** — 3 blocking findings:
1. Missing tools (condense_query, analyze_query) — the ADK agent is missing half the pipeline
2. No tracing/observability callbacks
3. Duplicated `_extract_latest_query`

These are real functional gaps, not style issues. The ADK custom_rag agent as-is would under-perform the Librarian pipeline in eval because it can't do query understanding or multi-turn condensation — not because ADK is worse, but because we didn't give the LLM the same capabilities.

### Recommended next steps (priority order)

1. Add `condense_query` + `analyze_query` tools to `tools.py`
2. Add shared `_extract_latest_query` to `orchestration/adk/utils.py`
3. Add `before_tool_callback` / `after_tool_callback` for structlog tracing
4. Fix the citation pass-through in BedrockKBAgent + LibrarianADKAgent
5. Address the `TODO(3)` for URL extraction in the eval runner
