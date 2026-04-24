---
name: VA Agent Review Fixes
status: backlog
source: code review (2026-04-21)
---

# VA Agent: Post-Review Fix Plan

Code review of the full VA Agent Improvements initiative (9 phases). Nothing is
blocking current dev use. Items are ordered by priority for production readiness.

---

## Non-blocking (fix before any production handoff)

### 1. S3 backend download silently returns 404

**Files:** `shared/artefact_store.py` (both projects)

`download_artefact` calls `read_local()` which does `Path(storage_key).exists()`.
When `ARTEFACT_BACKEND=s3`, `storage_key` is an S3 key, not a filesystem path —
`path.exists()` returns False and the endpoint silently 404s.

Presigned URLs stored at save time (900s TTL) are also stale almost immediately.

**Fix:** add `read_s3(artefact_id)` that regenerates a presigned URL at read time
from the stored `storage_key`. Branch on `_BACKEND` in both `read_local` (rename
to `read_content`) and `download_artefact`.

---

### 2. `datetime.utcnow()` deprecated in Python 3.12+

**Files:** `shared/artefact_store.py` lines ~78 and ~105 (both projects)

`save()` and `_soft_delete_sync()` use `datetime.utcnow()`.
`memory.py` already uses `datetime.now(timezone.utc)` — artefact_store should match.

**Fix:** replace all `datetime.utcnow()` with `datetime.now(timezone.utc)` and
import `timezone` from `datetime`.

---

### 3. ADK guardrails module is dead code

**Files:** `va-google-adk/agents/shared/guardrails/` (both files)

`prompt_injection.py` (11 categories, 60+ patterns) and `pii_redaction.py`
(full PII scanner) are never imported anywhere. `agent.py` uses a simplified
4-pattern inline copy of the injection check.

**Fix:** either wire `prompt_injection.INJECTION_RE` and `pii_redaction.detect_and_redact`
into `_guardrail_callback` in `agent.py`, or delete the module and own the
inline copy explicitly.

---

### 4. `format_node` and `direct_node` bypass model factory

**Files:** `va-langgraph/graph/nodes/format.py:42-44`,
`va-langgraph/graph/nodes/direct.py:18-20`

Both `_get_structured_llm()` helpers instantiate `ChatGoogleGenerativeAI` fresh
on every node call, defeating `model_factory`'s `@lru_cache` and Gemini prefix caching.
`direct_node` also hardcodes `"gemini-2.0-flash-lite"` instead of using the factory.

**Fix:** replace both `_get_structured_llm()` with calls to `resolve_chat_model()`
from `shared.model_factory`. Use `.with_structured_output(AssistantResponse)` on
the cached instance.

---

### 5. `_sessions` dict is never pruned — memory leak

**Files:** `va-langgraph/gateway/runner.py:41`,
`va-google-adk/gateway/session_manager.py:46`

`GraphRunner._sessions` and `SessionManager._sessions` grow unbounded for the
server process lifetime.

**Fix:** use `collections.OrderedDict` with a `maxsize=1000` eviction policy, or
time-based TTL (evict sessions idle >2h). Simple LRU is fine for now.

---

## Nits (low urgency)

### 6. Inline imports in `memory_node` "forget all" path

**File:** `va-langgraph/graph/nodes/memory.py:54-56`

`import asyncio, sqlite3, os` inside the function body. Move to top-level.

---

### 7. `artefact_url` field description misleads on TTL

**File:** `shared/schema.py` (both projects)

"Valid for ARTEFACT_TTL_DAYS (default 30 days)" conflates file retention with URL
lifetime. For S3 presigned URLs the link expires in 15 minutes; for local backend
the URL is stable indefinitely.

**Fix:** change to `"Download URL for the artefact file."` — leave TTL semantics to env var docs.

---

### 8. `download_artefact` endpoint has no auth — add a comment

**Files:** `gateway/main.py` both projects, line ~185

No `_require_api_key` dependency on `GET /artefacts/{id}/download` (intentional —
frontend loads URL directly). Looks accidental vs the other protected endpoints.

**Fix:** add a one-line comment: `# no auth — URL is unguessable (UUID) and must be loadable by the browser directly`

---

### 9. `history_pruning.py` accesses private ADK internals

**File:** `va-google-adk/agents/shared/tools/history_pruning.py:1-10`

Imports `_add_instructions_to_user_content`, `_get_contents`, etc. — all `_`-prefixed
ADK internals. Pin ADK version in `pyproject.toml` and add a comment flagging the risk.

---

### 10. `tool_response_utils.prefer_structured_tool_response` is unwired

**File:** `va-google-adk/agents/shared/tools/tool_response_utils.py`

`after_tool_callback` is defined but not set on any sub-agent. Wire or remove.

---

### 11. No index on `artefacts.session_id`

**File:** `shared/artefact_store.py` `_DDL` (both projects)

Once a TTL cleanup job is added, the query will full-scan the table.

**Fix:** add to `_DDL`:
```sql
CREATE INDEX IF NOT EXISTS idx_artefacts_session ON artefacts(session_id);
CREATE INDEX IF NOT EXISTS idx_artefacts_created ON artefacts(created_at);
```

---

## Deferred from Phase 9 (noted in original plan)

- Active TTL cleanup job (cron or startup sweep for `created_at + ttl_days < now`)
- `GET /artefacts` listing endpoint (by session)
