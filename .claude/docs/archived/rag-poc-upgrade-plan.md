# rag_poc Upgrade Plan — LangGraph Modernization or ADK Migration

**Status:** Draft — pending framework decision (§2)  
**Date:** 2026-04-17  
**Research:** [`adk-samples-patterns-analysis.md`](../research/adk-samples-patterns-analysis.md)  
**Prior plan:** [`rag-architecture-refactoring-plan.md`](./rag-architecture-refactoring-plan.md) (v2 hardening — Phase A/B already implemented)

---

## 0. Context

Phases A and B of the v2 hardening plan are complete:
- Context builder (`app/graph/context_builder.py`) ✓
- Planner structured output ✓
- Hybrid policy flag (`RAG_POLICY_MODE`) ✓
- Post-answer evaluator node (default off) ✓

The codebase is stable but has structural gaps vs. production patterns from ADK samples:
- No streaming chat endpoint (API stub only)
- No history pruning (tool history grows unbounded)
- No summarization node (long sessions degrade)
- System prompts embedded in code
- No guardrail layer (PII, injection)
- No session persistence / thread_id
- No tool call visibility in the web client

This plan proposes the next evolution: **modernize with proven patterns from ADK samples**, using either the LangGraph path (lower migration cost) or the Google ADK path (more powerful, Google-native).

---

## 1. Goals

| Goal | Why |
|------|-----|
| Wire streaming endpoint | The API declares SSE but no route exists — CLI is the only interface |
| Add history pruning + summarization | Token cost and context quality degrade over long sessions |
| Externalize system prompts | Enable prompt iteration without code deploys |
| Add guardrail layer | PII and prompt injection protection before production |
| Add session persistence | `thread_id` checkpointing for multi-turn conversations |
| Enable tool call visibility | Observability beyond LangSmith traces |

Non-goals: replacing the RAG pipeline itself, changing LLM providers, or implementing voice/BIDI.

---

## 2. Framework Decision: LangGraph Modern vs. Google ADK

### Option A — LangGraph Modernization (recommended if staying Anthropic-first)

Adopt ADK patterns **within** LangGraph by porting from `langgraph_agents/native_skill_mcp/`:

**What changes:**
- Add `history_pruning` callback (before each agent node)
- Add summarization node (trigger at 8 messages, Haiku model)
- Add `thread_id` + checkpointer (LangGraph `SqliteSaver` or `PostgresSaver`)
- Move system prompts to `app/prompts/` filesystem dir
- Wire `POST /api/v1/chat` → SSE streaming endpoint
- Port guardrails from ADK `shared/guardrails/` as Python modules

**What stays the same:**
- All existing graph nodes and routing logic
- HITL gates (`interrupt()` + `Command(resume=)`)
- LangSmith + Langfuse observability
- Anthropic as primary LLM provider
- Existing LangChain tool wrappers

**Effort:** Medium (3–4 weeks)  
**Risk:** Low — additive changes, no graph topology changes

### Option B — Google ADK Migration

Rewrite orchestration layer using `google-adk>=1.28.0`, keeping the RAG pipeline (retriever, reranker, context builder) as pure Python tools.

**What changes:**
- Agent definition: `Agent(name=..., instruction=..., tools=[...])` replaces graph nodes
- HITL: ADK's `before_tool_callback` + `after_tool_callback` replaces `interrupt()`
- Skill loading: `SkillToolset` + `SKILL.md` files
- Web client: port to `agent_gateway` pattern or ADK web server
- Model: swap to Gemini (ADK is Gemini-native; Anthropic requires adapters)

**What stays the same:**
- RAG pipeline logic (retriever, reranker, context builder are pure Python)
- MCP server pattern
- Guardrails (importable from `shared/`)

**Effort:** High (6–8 weeks)  
**Risk:** Medium-High — model provider swap, HITL pattern change, new framework primitives

### Option C — Hybrid: ADK for new agents, LangGraph for RAG core

Keep existing LangGraph RAG graph. Add ADK agents as new entry points (e.g. a `BillyAssistant`-style agent that calls the RAG graph as a tool via MCP).

**Effort:** High but parallelizable  
**Risk:** Low per component, complexity in routing between systems

### Recommendation

**Option A (LangGraph Modernization)** unless there is a specific requirement for:
- Gemini Live (voice)
- A2UI declarative surfaces
- Google Cloud Agent Engine deployment

The ADK samples LangGraph port proves all meaningful patterns are achievable without migrating. The RAG pipeline, HITL gates, and Anthropic model are strong reasons to stay.

---

## 3. Phased Upgrade Plan (Option A — LangGraph)

### Phase 1 — Streaming + History Management (do first; unblocks everything)

**P1.1 — Wire SSE streaming endpoint**
- Add `POST /api/v1/chat` route in `app/main.py`
- Use `graph.astream()` with token streaming
- Emit `event: token`, `event: tool_call`, `event: done` SSE events
- Match playground's `format_sse()` pattern from `src/interfaces/api/streaming.py`
- Update CORS config
- Tests: streaming integration test with real graph

**P1.2 — Add history pruning callback**
- Port `shared/tools/history_pruning.py` from ADK samples
- Register as `before_node` callback on `agent_node` (or equivalent)
- Config: `RAG_HISTORY_PRUNE=true` (default true)
- Keeps: user messages, agent text, current turn tool calls
- Removes: prior `ToolMessage` accumulation

**P1.3 — Add summarization node**
- New node `summarizer` triggered after `answer_node` when `len(messages) >= 8`
- Uses `app/rag/generator/llm.py` Haiku model (not Sonnet — cost control)
- Overlap: preserve last 4 messages post-summary
- Config: `RAG_SUMMARIZATION_ENABLED=true`, `RAG_SUMMARIZATION_THRESHOLD=8`
- Port `prompts/summarizer.txt` pattern (filesystem prompt file)

**Exit criteria:** `POST /chat` streams tokens; long sessions don't balloon context; CI green.

---

### Phase 2 — Session Persistence + Prompt Externalization

**P2.1 — Thread_id + checkpointer**
- Add `SqliteSaver` checkpointer (dev) / `PostgresSaver` (prod) — see [langgraph-persistence skill]
- `thread_id` passed as `config={"configurable": {"thread_id": session_id}}`
- Session ID generated at `/api/v1/sessions` `POST` endpoint
- Enables time travel, replay, HITL resume across requests (fixes current stateless behavior)
- Config: `RAG_CHECKPOINTER=sqlite|postgres|none` (default `sqlite` in dev)

**P2.2 — Externalize system prompts**
- Create `app/prompts/` directory:
  ```
  app/prompts/
  ├── system.txt          # Main RAG agent instruction
  ├── planner.txt         # Planner LLM prompt (if LLM_PLANNER=true)
  ├── summarizer.txt      # Compaction prompt
  ├── answer.txt          # Answer generation prompt
  └── evaluator.txt       # Post-answer evaluator prompt
  ```
- Load with `Path("app/prompts/system.txt").read_text()` at startup
- Remove embedded prompt strings from chain init functions
- No runtime reload needed (loaded once at startup)

**P2.3 — Update FastAPI lifespan**
- Wire checkpointer init into `lifespan()` context manager
- Warm up graph on startup (like ADK `web_client` warmup pattern)
- Emit startup health check log with graph node count, tool count, checkpointer type

**Exit criteria:** Sessions persist across requests; `/chat` `POST` accepts `session_id`; prompts editable without code change.

---

### Phase 3 — Guardrails + Observability

**P3.1 — Port guardrail modules**
- Copy and adapt from ADK `shared/guardrails/`:
  - `app/guardrails/pii_redaction.py` — 13 pattern classes (email, phone, card, SSN, PEM, API keys, Bearer tokens, env vars)
  - `app/guardrails/prompt_injection.py` — 10 injection categories
- Wire as **pre-graph middleware** in FastAPI (`app/interfaces/api/middleware.py`):
  ```python
  class GuardrailMiddleware:
      async def dispatch(self, request, call_next):
          text = await extract_query(request)
          redacted, pii_found = pii_redaction.redact(text)
          if prompt_injection.is_injection(redacted):
              return 400 response
          # continue with redacted text
  ```
- Config: `RAG_GUARDRAILS_ENABLED=true`, `RAG_GUARDRAILS_LOG_PII=false`
- Tests: unit test each pattern category

**P3.2 — Tool call visibility in API response**
- Add `tool_calls` array to SSE `done` event payload:
  ```json
  { "event": "done", "data": { "response": "...", "citations": [...], "tool_calls": [{"name": "search_knowledge_base", "duration_ms": 120}] }}
  ```
- Enables web client (Streamlit or Next.js) to render tool steps

**P3.3 — Response timing**
- Inject `X-First-Token-Ms`, `X-Total-Ms` response headers
- Log structured timing: `{"first_token_ms": 340, "llm_ms": 890, "tool_ms": 120, "total_ms": 1100}`

**Exit criteria:** PII redacted before graph; injection attempts blocked; tool call steps visible in response.

---

### Phase 4 — Web Client Upgrade (choose one)

**Option 4A — Streamlit dashboard → chat UI**
- Upgrade `evals/dashboard/streamlit_app.py` to a proper chat interface
- Wire to new streaming endpoint with `st.write_stream()`
- Add session_id management in sidebar
- Add tool call step display (expander per tool call)
- Fastest path — stays Python

**Option 4B — Port playground Next.js frontend**
- Copy `playground/frontend/web-local/` into `rag_poc/frontend/`
- Update `triageAgent()` to route all traffic to rag_poc API
- Update SSE parsing to match rag_poc event schema
- Add tool call step display component
- Better long-term — production-ready stack

**Recommendation:** 4A to unblock demos; 4B when frontend becomes a product priority.

---

## 4. If Choosing Option B (ADK Migration) Instead

If the decision shifts to ADK, the migration sequence is:

1. **Keep RAG pipeline as pure Python** — retriever, reranker, context builder become ADK `FunctionTool`s
2. **Wrap as MCP server** — expose `search_knowledge_base` via FastMCP (pattern: `mcp_servers/billy/`)
3. **Rewrite orchestration** — replace graph with `Agent(instruction=..., tools=[rag_mcp_toolset])`
4. **Port HITL** — `before_tool_callback` for confirmation gates
5. **Add SkillToolset** — if multi-domain skills needed
6. **Port web client** — use `agent_gateway` session manager pattern
7. **Observability** — swap LangSmith for Cloud Trace + ADK eval tooling

**Model consideration:** ADK is Gemini-native. If keeping Anthropic, use `LiteLLM` wrapper or `langchain-anthropic` via `LangchainTool`. This is non-trivial — test early.

---

## 5. Upgrade Checklist

### Phase 1 (Streaming + History)
- [ ] `POST /api/v1/chat` SSE streaming endpoint
- [ ] History pruning callback
- [ ] Summarization node + `prompts/summarizer.txt`
- [ ] Integration tests for streaming
- [ ] Config: `RAG_HISTORY_PRUNE`, `RAG_SUMMARIZATION_ENABLED`, `RAG_SUMMARIZATION_THRESHOLD`

### Phase 2 (Persistence + Prompts)
- [ ] `SqliteSaver` checkpointer wired
- [ ] `POST /api/v1/sessions` endpoint
- [ ] `app/prompts/` directory with all prompt files
- [ ] Prompt loading at startup
- [ ] FastAPI lifespan with graph warmup

### Phase 3 (Guardrails + Observability)
- [ ] `app/guardrails/pii_redaction.py`
- [ ] `app/guardrails/prompt_injection.py`
- [ ] `GuardrailMiddleware` wired
- [ ] Tool call steps in SSE `done` payload
- [ ] Response timing headers + structured log

### Phase 4 (Web Client)
- [ ] Choose 4A (Streamlit) or 4B (Next.js)
- [ ] Wire to streaming endpoint
- [ ] Session ID management
- [ ] Tool call step display

---

## 6. Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-17 | Plan drafted — pending Option A vs B decision | Research phase complete; awaiting framework direction |
| — | (Option A/B confirmed) | — |
| — | Phase 1 start | — |
