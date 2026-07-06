---
title: Phase 6 — Refactor: Docker Chat + Web Search
status: ACTIVE
date: 2026-04-21
---

## Goal

Stabilize the codebase (Phase 0), replace the RAG pipeline with Tavily web search for
artist/genre context (Phase 1), then make `docker compose up` produce a working chat
(Phase 3). RAG re-evaluation deferred to Phase 4.

---

## Context

### What was broken coming in

| Issue | Resolution |
|---|---|
| Spotify audio-features 403 (deprecated 2025) | ENOA genre embeddings already in use; Last.fm activation pending |
| ChromaDB in compose — never queried (DuckDB is primary) | Remove service |
| Phoenix/Arize tracing deps — unused, LangFuse is active path | Remove deps |
| Git LFS `listen_wiseer.db` — blocks other envs | Document init-db workaround |
| RAG pipeline (Wikipedia → sentence-transformers → DuckDB) — overbuilt for current value | Suspend; replace with Tavily |

### Comparison with playground va-agent patterns

The playground plans (va-agent-systems, va-infra) established:
- Domain-separated tool modules per sub-agent
- Structured `AssistantResponse` output schema
- SSE streaming gateway (FastAPI in-process)
- Sidecar compose topology (gateway + mcp + postgres)

listen-wiseer uses the same LangGraph skeleton but Chainlit handles streaming/session
natively, so we keep it. Domain tool separation is Phase 2.

---

## Phase 0 — Stabilize (done in this PR)

### 0a. Dead dependencies removed
- `chromadb` — DuckDB is primary vector store; chroma client never called
- `arize-phoenix-otel` — Phoenix tracing unused; LangFuse is active
- `openinference-instrumentation-langchain` — same
- `openinference-instrumentation-anthropic` — same

### 0b. Dead docker-compose services removed
- `chromadb` service + `chromadb-data` volume
- `CHROMA_PERSIST_DIRECTORY` env var from mcp + app
- `ENABLE_RAG`, `RAG_TOP_K`, `WIKIPEDIA_LANGUAGE` env vars (RAG suspended)
- `depends_on: chromadb` from both mcp and app services

### 0c. Dead config settings removed
- `chroma_persist_directory`
- `enable_rag`, `rag_top_k`, `wikipedia_language`

### 0d. Database bootstrapping (manual, documented)
- Move away from Git LFS for `listen_wiseer.db`
- Run `make init-db && make train` on first clone
- Documented in CLAUDE.md gotchas

---

## Phase 1 — Web Search replaces RAG (done in this PR)

### Rationale

The RAG pipeline (Wikipedia ingestion → sentence-transformers → DuckDB vector search →
MS-marco reranker → LLM generation) was Phase 5a. It works but requires a pre-populated
vector store, sentence-transformers loaded at startup (~500ms), and a Wikipedia corpus
that goes stale. Tavily returns grounded, fresh answers in ~1s with zero local state.

RAG is not deleted — `rag_core/` stays and will be re-evaluated in Phase 4 as an
enrichment layer on top of web search. For now, the agent tool calls Tavily directly.

### Changes

- `src/agent/tools.py`: `get_artist_context_tool` now calls `TavilyClient.search()`
  instead of `MusicRAG().get_context()`. Same tool name/description — agent graph unchanged.
- `pyproject.toml`: added `tavily-python>=0.5.0`
- `src/utils/config.py`: `tavily_api_key` was already present
- `.env.example`: added `TAVILY_API_KEY=`
- `docker-compose.yml`: added `TAVILY_API_KEY` env var to app service

### Suspension marker

`src/rag_core/` is left in place. The lazy `_get_music_rag()` singleton in tools.py is
removed; nothing else imports MusicRAG at agent startup.

---

## Phase 2 — Agentic Tools Refactor (planned)

**Goal:** Domain-separated tool modules, structured agent output schema, HITL playlist write.

```
src/agent/tools/
  __init__.py          — exports ALL_TOOLS
  spotify_read.py      — search, recently_played, related_artists, playlists
  spotify_write.py     — create_playlist, add_tracks (HITL confirm)
  recommend.py         — by_track, by_artist, by_genre, by_playlist
  memory.py            — manage_taste_memory, search_taste_memory
  web_search.py        — search_artist_context, search_genre_history
```

Add `AgentResponse` output schema (message, suggestions, track_list, sources) and a
`format_response` node before END.

---

## Phase 3 — Docker Chat (done)

**Goal:** `docker compose up` → working chat, no manual steps.

- Remove chromadb (done in Phase 0) ✓
- Promote postgres from optional profile to always-on (LangGraph checkpointer) ✓
- Add `db-init` one-shot service: bootstraps DuckDB schema + runs model training if models/ empty ✓
- Wire `POSTGRES_URL` into `get_checkpointer()` (replaces InMemoryStore in container env) ✓
- Makefile: `infra-build`, `infra-ps`; fixed `train-cat --model-type catboost`; synced `.PHONY` ✓

---

## Phase 4 — Prompts & RAG Enrichment (done)

- `rag_core/` wired as optional enrichment on top of Tavily in `web_search.py` ✓
- System prompt: added proactive `search_taste_memory` guidance + chit-chat no-tool rule ✓
- Eval harness: Tier 2 wired to live graph via `evaluate_trajectory`; Tier 3 runs tool correctness + RAGAS faithfulness on `final_response` ✓
- `TrajectoryResult.final_response` field added to thread answer text through to Tier 3 graders ✓
