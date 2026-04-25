# Review: Interfaces & Infrastructure Layer

Date: 2026-04-14
Scope: `src/interfaces/`, `src/librarian/tools/`, `src/clients/llm.py`, `src/orchestration/factory.py`, `src/orchestration/google_adk/`

---

## Automated checks

- Tests: not run (reviewing current main state, no branch diff)

---

## Blocking Findings (10)

### API Layer

1. **No authentication on any endpoint** — `routes.py` all routes
   Zero auth checks. `/ingest` lets unauthenticated callers trigger S3 reads and vector store writes.

2. **Unvalidated `s3_key`/`s3_prefix` passed to S3** — `models.py:71-72`, `routes.py:494-512`
   User-supplied strings forwarded verbatim to `pipeline.ingest_s3_object()`. Can read any key in the bucket. Fix: `Field(..., pattern=r"^raw/")`.

3. **`IngestRequest.document` accepts untyped `dict[str, str]`** — `models.py:73`
   No schema, no required fields, no max lengths. Define a proper `InlineDocument` model.

4. **Production routes import `eval.experiment` private helpers** — `routes.py:253,302,335`
   `_build_adk_context` and `_extract_urls_from_adk_events` are private eval functions. Move to `orchestration/` or `clients/`.

### MCP Servers

5. **No `configure_logging()` in any MCP `main()`** — all three servers
   structlog falls back to unconfigured defaults. No timestamps, no JSON in prod.

6. **Zero exception handling in `call_tool` handlers** — all three servers
   Any error (boto3 `ClientError`, `json.JSONDecodeError`, `KeyError` on missing args) crashes the stdio loop.

7. **S3 path traversal: `get_document`/`trigger_ingestion` accept unrestricted keys** — `s3_server.py:152-154,167-171`
   `put_object` enforces `s3_raw_prefix` but `get_document` does not. Caller can read any object in the bucket.

8. **`ingest` tool never validates required `text` key** — `librarian_server.py:136-137`
   Tool description says "must include 'text' key" but no code-level check.

### Protocols & Tools

9. **`LLMClient.stream` protocol/impl mismatch** — `clients/llm.py:31-33,124`
   Protocol declares sync return of `AsyncIterator[str]`; `AnthropicLLM.stream` is `async def`. Plus `GeminiLLM` has no `stream` at all — `isinstance(LLMClient)` passes but `AttributeError` at runtime.

10. **`BaseTool` protocol is dead infrastructure** — `librarian/tools/base.py`
    Never used as a type annotation anywhere. Name collision with `google.adk.tools.base_tool.BaseTool`. `RetrieverTool.run()` narrows `ToolInput` to `RetrieverToolInput` (LSP violation). Neither LangGraph nor ADK actually types against it.

---

## Non-blocking Findings (20)

### API Layer

11. `allow_credentials=True` with localhost CORS defaults — `app.py:52-58`
12. ADK routes call private `_run_async_impl()` cross-package — `routes.py:256,338`
13. Three ADK handlers instantiate new agent per request — `routes.py:251,290,332`
14. `_BACKEND_LABELS` / `ChatRequest.backend` / `triage.Route` — backend list declared in 3 places
15. `get_generator_agent`/`get_generation_subgraph` dead exports — `deps.py:88-97`
16. `init_graph()` conflates graph + embedder + LLM + Bedrock + Google init — `deps.py:28-77`
17. Duplicated thread-id / langfuse / config setup — `routes.py:147-152,370-376`
18. `/ingest` single try/except — partial success lost if one branch throws — `routes.py:492-536`
19. `confidence or 0.0` falsy-check on float — `routes.py:411`
20. `StreamEvent` model defined but never used — `models.py:37-41`
21. `s3_trigger.py`: `asyncio.run()` per record; no per-record error handling; typed as `Any`

### MCP Servers

22. Separate graph/pipeline instances from API layer — Chroma lock risk if co-located
23. Hardcoded `session_id="mcp"`, no `thread_id` — MCP chat is stateless even with checkpointer
24. `describe_table` regex allows cross-database qualified names — `snowflake_server.py:69`
25. Snowflake connection never closed — stale after session timeout
26. `get_status` leaks infra config to any MCP caller

### Protocols & Factory

27. `create_agents()` imported but never called in ADK factory — `google_adk/factory.py:21`
    `custom_rag_agent.py` builds its own agents. Cache sharing between LangGraph and ADK is broken.
28. `create_librarian()` duplicates component wiring instead of calling `create_agents()`
29. `snippet_retriever` in `create_librarian` but not `create_agents` — ADK never gets snippet routing
30. `RAGResponse.confidence` (string) vs numeric `confidence_score` — parallel but unconverted

---

## Nits (10)

31. `LibrarySettings` unused import in `app.py`
32. `middleware.py` uses `structlog.get_logger()` directly vs `core.logging.get_logger()`
33. `format_sse` unescaped event name — safe today but fragile
34. Triage keyword regex fragility (`\b` + `re.escape` on multi-word phrases)
35. `s3_trigger.py` in `interfaces/api/` but isn't an API module
36. `tools/__init__.py` empty — no facade exports
37. `RetrieverToolOutput.results: list[dict]` untyped; `deduplicated` always equals `total`
38. `Retriever` protocol mixes read+write; `Chunker.chunk_document` takes untyped `dict`
39. `GoldenDataset.load` returns `list[dict[str, Any]]` not `list[EvalTask]`
40. `LLMClientSync` docstring references removed agents (researcher, presenter, cartographer)

---

## Structural Assessment

### What's clean
- `src/interfaces/{api,mcp}` separation is correct
- Protocols are consistently `@runtime_checkable` throughout
- Middleware stack is well-layered (request ID → timeout → logging → CORS)
- Triage is properly centralized and fast (no network calls)
- Factory pattern exists and is directionally correct

### What needs work (themes)

| Theme | Severity | Affected files | Summary |
|---|---|---|---|
| **Security boundaries** | Blocking | routes.py, models.py, s3_server.py | No auth, no input validation at API/MCP boundaries |
| **Factory sharing is broken** | Non-blocking | orchestration/factory.py, google_adk/factory.py | `create_agents()` exists but nobody calls it. LangGraph and ADK build separate component trees |
| **MCP servers are unfinished** | Blocking | all 3 servers | No logging, no error handling, path traversal, no input validation |
| **Dead tool abstraction** | Blocking | librarian/tools/ | `BaseTool` protocol built but unused; LSP violation; name collision |
| **eval ↔ production coupling** | Blocking | routes.py → eval.experiment | Production routes import private eval helpers |

### Verdict

**Needs changes** before proceeding with orchestration-rollout or terraform-restructure.

The MCP servers and API security gaps are the most urgent — they're blocking for any deployment path. The factory sharing and dead tool abstraction are architectural debt that will compound as more orchestration variants land.

---

## Recommended next steps

1. **Harden API + MCP boundaries** (security findings 1–8) — prerequisite to any deploy
2. **Fix `LLMClient` protocol mismatch** (finding 9) — breaks at runtime for Gemini
3. **Wire `create_agents()` through ADK factory** (findings 27–29) — fulfill the design intent from librarian-rag-upgrade
4. **Move eval helpers out of `eval.experiment`** (finding 4) — clean the layering violation
5. **Kill or fix `BaseTool`** (finding 10) — dead protocol is misleading; either adopt it properly or remove it
6. Then resume orchestration-rollout or terraform-restructure
