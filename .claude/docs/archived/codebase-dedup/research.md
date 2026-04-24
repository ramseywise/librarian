# Research: Codebase Deduplication

**Date:** 2026-04-11
**Status:** Open — blocking items fixed, remaining items queued for planning

## Context

Full codebase audit for duplication across clients, tools, integrations, evals, and storage.
Includes skill compliance check against `/microprofile-server` (Java) and `/web-components` (BCE).

## Findings — Resolved (this session)

### D1: Bare `anthropic.Anthropic()` — [sdk-factory] violation ✅ FIXED
- `src/eval/graders/answer_eval.py` — `AnswerJudge.__init__` and `ClosedBookBaseline.__init__`
- `src/librarian/tasks/generate_synthetic.py` — `generate_from_chunks()`
- **Fix:** Replaced with `create_client()` factory from `core.client`

### D2: Hardcoded `HAIKU_MODEL` constant — [sdk-model] violation ✅ FIXED
- Duplicated `HAIKU_MODEL = "claude-haiku-4-5-20251001"` in `answer_eval.py` and `generate_synthetic.py`
- Hardcoded default in `eval/models.py` `EvalRunConfig.model_id`
- **Fix:** Replaced with `settings.model_haiku` from `core.config.settings.BaseSettings`

## Findings — Remaining

### D3: S3 client init pattern duplicated (Low Risk)
**Files:**
- `src/librarian/ingestion/s3_loader.py` — `S3DocumentLoader._get_client()`
- `src/interfaces/mcp/s3_server.py` — `S3Client._get_client()`

**Pattern:** Near-identical lazy-init `boto3.client("s3", **kwargs)` with optional `region_name`. Both:
```python
def _get_client(self) -> Any:
    if self._client is None:
        import boto3
        kwargs: dict[str, str] = {}
        if self._region:  # or self._cfg.s3_region
            kwargs["region_name"] = self._region
        self._client = boto3.client("s3", **kwargs)
    return self._client
```

**Proposed fix:** Extract `create_s3_client(region: str = "") -> Any` into `core/clients/aws.py`. Both classes delegate to it.

**Risk:** Low — mechanical extraction. Test both callsites.

### D4: Two `parse_json_response` functions — naming collision (Low Risk)
**Files:**
- `src/core/parsing/json.py` — `parse_json_response(raw_text: str) -> Any` — simple strip + parse
- `src/core/client.py` — `parse_json_response(client, response_text, model, system) -> Any` — parse with LLM retry

**Impact:** Confusing for developers. Different signatures, different behavior, same name.

**Proposed fix:** Rename the simple version to `parse_json(raw_text)` or keep as-is since it's only used via import. Rename the retry version to `parse_json_with_retry()`. Update callers.

**Risk:** Low — rename and update imports.

### D5: Two parallel Anthropic client paths (Behavioral-adjacent)
**Files:**
- `src/core/client.py` — Legacy `create_client()` returns raw `anthropic.Anthropic` for researcher/presenter
- `src/core/clients/llm.py` — Unified `AnthropicLLM` with `generate()/generate_sync()` protocols

**Analysis:** The legacy path exists because researcher/presenter use the raw SDK `client.messages.create()` API directly. The unified path wraps this behind protocol methods. Migration would require refactoring all researcher/presenter agent calls from:
```python
client = create_client()
resp = client.messages.create(model=..., system=..., messages=[...])
text = resp.content[0].text
```
To:
```python
llm = AnthropicLLM(model=settings.model_sonnet)
text = llm.generate_sync(system=..., messages=[...])
```

**Proposed fix:** Migrate researcher/presenter to `AnthropicLLM.generate_sync()`. Then deprecate `create_client()`. This also eliminates `core/client.py`'s `parse_json_response` by extracting retry logic.

**Risk:** Medium — touches 5 files in agents/, changes error handling patterns. Each agent call currently does its own response parsing; the unified wrapper strips that.

**Dependency:** D4 should be done first or alongside.

### D6: Re-export shim modules (Safe)
**Files:**
- `src/core/llm.py` — re-exports `AnthropicLLM` from `core.clients.llm`
- `src/core/logging.py` — re-exports from `core.config.logging`
- `src/eval/judges/llm_judge.py` — re-exports from `eval.graders.llm_judge`

**Analysis:** Backward-compat shims from the package restructure. Currently used by:
- `core/llm.py` → imported by `agents/cartographer/cron.py`
- `core/logging.py` → imported by many files
- `eval/judges/llm_judge.py` → not clear if used externally

**Proposed fix:** Update importers to use canonical paths. Then delete shims. Do `core/logging.py` last (most callers).

**Risk:** Safe — mechanical import path updates.

### D7: Bedrock citation extraction duplicated in Python + TypeScript (Non-blocking)
**Files:**
- `src/librarian/bedrock/client.py` — `_extract_citations()` (Python)
- `frontend/web/src/lib/bedrock.ts` — `extractCitations()` (TypeScript)

**Analysis:** Cross-language duplication. Both flatten Bedrock's nested citation structure into a flat list. Not easily deduplicated without a shared contract (e.g., API response includes pre-flattened citations).

**Proposed fix:** Have the Python API flatten citations before returning to the frontend, so the TS client doesn't need its own extraction logic. This is an API contract change.

**Risk:** Medium — requires API route change + frontend update. Defer unless frontend is being reworked.

### D8: Experiment runners share ~90% structure (Low Risk)
**File:** `src/eval/experiment.py`
- `_run_bedrock_experiment()` (~130 lines)
- `_run_google_adk_experiment()` (~130 lines)

**Analysis:** Both follow identical structure: create client → iterate dataset → call client → build result → collect metrics. Only the client call differs.

**Proposed fix:** Extract `_run_managed_rag_experiment(client_fn, variant, dataset, ...)` generic runner. Both become thin wrappers.

**Risk:** Low — the shared structure is clear and the abstraction is natural.

### D9: Stale `research_agent/` directory (Safe)
**File:** `/repo/research_agent/` — contains only a `.venv/` directory

**Analysis:** Remnant from before restructure to `agents/researcher/`.

**Proposed fix:** Delete the directory. Confirm it's not referenced anywhere.

**Risk:** Safe — no code references it.

## Skill Compliance

### Backend (`/microprofile-server`) — N/A
The skill is for **Java MicroProfile/Jakarta EE**. This repo is Python (FastAPI, LangGraph, Pydantic). The skill does not apply. The Python backend follows its own well-structured patterns:
- Protocol-based abstractions (`core/storage/protocols.py`)
- Factory-driven DI (`librarian/factory.py`)
- Clean layering: interfaces → orchestration → librarian → storage

### Frontend (`/web-components`) — Not followed, intentionally
The skill mandates: web components, lit-html, Redux Toolkit, BCE architecture, no frameworks.

The actual frontend stack:
- **Next.js 14 + React 18 + TypeScript + Tailwind** — framework-heavy
- **Streamlit** — eval dashboard and chat playground
- No BCE, no web components, no lit-html

**Verdict:** The frontend was built for rapid prototyping with familiar tools. The `/web-components` skill is defined for future projects following that architecture. Migrating the existing frontend would be a rewrite, not a refactor. **Skipped by user decision.**

## Recommended Plan Order

| Priority | Item | Effort | Dependency |
|----------|------|--------|------------|
| 1 | D9: Delete stale `research_agent/` | 5 min | None |
| 2 | D6: Remove re-export shims | 30 min | None |
| 3 | D3: Extract S3 client factory | 30 min | None |
| 4 | D8: Unify experiment runners | 45 min | None |
| 5 | D4: Rename parse_json functions | 30 min | None |
| 6 | D5: Migrate agents to AnthropicLLM | 2 hrs | D4 |
| 7 | D7: Flatten citations in API | 1 hr | Frontend decision |

Total estimated: ~4-5 hours. Items 1-4 can be done independently in parallel.
