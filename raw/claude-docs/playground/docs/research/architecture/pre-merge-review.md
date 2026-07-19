# Pre-merge Refactor — Completed

**Status:** All items resolved. Archived from plans/ after session 2026-04-29.

Source: Code review of all playground/ changes before first merge to main.

---

## Criticals — all done

### 1. Live credentials in `.env`
- Zeroed out GOOGLE_API_KEY, BACKEND_API_TOKEN, LANGSMITH_API_KEY in `.env`
- Added LangSmith entries to `.env.example`
- Keys must be re-entered from dashboards (Google Cloud Console, LangSmith Settings)

### 2. Broken `hc-rag-agent` Dockerfile
- Fixed: `infrastructure/containers/hc-rag-agent/Dockerfile` now copies all actual source dirs (`orchestrator/`, `rag/`, `core/`, `clients/`, `guardrails/`, `evals/`, `ingest/`)

### 3. Missing Postgres init for `hc_rag` database
- Created `infrastructure/containers/postgres-init/init.sql` with idempotent `CREATE DATABASE hc_rag` guard

### 4. Hardcoded `thread_id: "adk-support"` in support agent
- Fixed in `va-google-adk/sub_agents/support_agent.py` → `tool_context.state.get("session_id", "adk-support")`

---

## Should-fixes — all done

### 5. `format.py` / `direct.py` bypass model factory
- Both nodes now use `resolve_chat_model()` — `LLM_PROVIDER` env var is honoured throughout

### 6. `regression.py` unused `thresholds` parameter
- Removed: parameter accepted but never enforced; signature cleaned up

### 7. `hc-rag-agent` guardrails disabled in compose
- Fixed: `RAG_GUARDRAILS_ENABLED=true` set in `docker-compose.yml`

---

## Cleanup — all done

| # | Issue | Status |
|---|-------|--------|
| 8 | Session memory leak in runner.py | → moved to `hardening.md` |
| 9 | Empty tool sets graceful failure | → moved to `hardening.md` |
| 10 | `datetime.utcnow()` deprecated | Fixed in `va-langgraph/eval/models.py` |
| 11 | `_ANGLE_URL_RE` defined after use | Fixed in `eval/ingest/ticket_ingest.py` |
| 12 | Missing unit tests | → moved to `hardening.md` |
| 13 | Anthropic model ID format | Closed — IDs match what the API expects |

---

## Intentional / no-action

- Write tools pending test account — `TODO(2)` markers, well-documented
- Injection regex false positive on "favourite assistant" — `TODO(3)`, benign tradeoff
- RAG corpus / Track 1 RAG migration — deferred until help docs are scraped
- `model_factory.py` duplicated across packages — acceptable; uv workspace isolation keeps drift low
