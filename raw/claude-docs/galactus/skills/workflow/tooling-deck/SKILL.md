---
name: tooling-deck
description: "Create or update the galactus repo tooling overview — a single structured reference that maps every tool/framework to its use case, key files, make targets, and env vars. Triggers on: 'update the tooling doc', 'make a tooling deck', 'create a tooling overview', 'tooling spec', or after major new tooling lands."
---

Creates or updates `docs/OVERVIEW.md` — a compiled, shareable reference of every tool and framework in galactus. Optionally shares it to Notion or Google Drive via `/share`.

## When to use

- New framework or service landed (new runner, new agent, new data store)
- Tooling docs in `docs/` were updated and the overview is stale
- Onboarding a new engineer and need a single entry-point doc
- Preparing a stakeholder update or hackathon brief

## Steps

### 1. Gather current state

Read the tooling sources in this order:
1. `CLAUDE.md` — top-level conventions and skills index
2. `docs/` — all spec files (each covers one tool/framework)
3. `Makefile` — all named targets (source of truth for what can be run)
4. `src/` directory tree — current service structure
5. `evals/` directory tree — current eval pipeline structure
6. `.env.example` — env var inventory

### 2. Draft the overview

Write `docs/OVERVIEW.md` following this template:

```markdown
# Galactus Tooling Overview

> Last updated: <date>
> Generated from: docs/ specs + Makefile

## Repo map

Brief 2-3 sentence description of what galactus is and what it does.

## Services

| Service | Framework | Port | Entry point | Start |
|---|---|---|---|---|
| hc_adk | Google ADK | 8011 | src/support_agents/hc_adk/main.py | make sa-up |
| hc_lg | LangGraph | 8012 | src/support_agents/hc_lg/main.py | make sa-up |
| hc_rag | Custom RAG | 8013 | src/support_agents/hc_rag/main.py | make sa-up |

## Eval pipeline

| Pipeline | Target | What it tests | LLM cost? |
|---|---|---|---|
| Heuristic stats | `uv run python -m evals.pipelines.run stats ...` | Response quality proxies | No |
| Quality graders | `uv run python -m evals.pipelines.run quality ...` | LLM-judged quality | Yes |
| Live agent eval | `uv run python -m evals.pipelines.run live ...` | Calls running agent + grades | Optional |
| LangFuse experiment | `uv run python -m evals.pipelines.run langfuse ...` | Cross-run comparisons in LangFuse UI | Yes |
| Render reports | `uv run python -m evals.pipelines.run render ...` | HTML from existing report-data JSON | No |

## Data stores

| Store | Type | Path | Used by |
|---|---|---|---|
| knowledge.duckdb | DuckDB vector store | data/corpus/datastores/knowledge.duckdb | hc_rag |
| Billy/Shine URL maps | CSV/JSON maps | data/articles/billy/intercom/raw/kb_url_map/ | graders, ArticleLoader, URL normalization |
| Billy Bedrock KB | AWS Bedrock KB | env: BEDROCK_KNOWLEDGE_BASE_ID | hc_adk, hc_lg |

## Observability

| Service | Tracing | Config |
|---|---|---|
| eval pipeline | LangFuse scores | LANGFUSE_PUBLIC_KEY + LANGFUSE_SECRET_KEY |
| hc_adk / hc_lg / hc_rag | observability.py | LANGFUSE_* and agent-specific tracing flags |

## Key env vars

(See .env.example for the full list)

| Var | What it controls |
|---|---|
| BEDROCK_KNOWLEDGE_BASE_ID | Billy Bedrock KB ID |
| VA_RETRIEVAL_MODE | bedrock / rag — switches KB backend for all VA agents |
| LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY | LangFuse tracing + eval experiments |
| GEMINI_API_KEY | Gemini model calls (graders, ADK agents) |
| GOOGLE_API_KEY | Gemini model calls where Google SDK expects this name |

## Tooling reference docs

Each tool has a full spec in docs/:

- [google-adk.md](google-adk.md) — ADK agent patterns, eval framework
- [langgraph.md](langgraph.md) — state design, HITL, streaming, production checklist
- [langsmith.md](langsmith.md) — tracing wiring, dataset management, evaluator patterns
- [bedrock-kb.md](bedrock-kb.md) — Bedrock KB retrieval client
- [hooks-architecture.md](hooks-architecture.md) — Claude Code hook suite
- [evals/eval-harness-patterns.md](evals/eval-harness-patterns.md) — BKH harness architecture
- [evals/grader_interface.md](evals/grader_interface.md) — grader base contract
- [evals/grader_methodology.md](evals/grader_methodology.md) — calibration and judge selection
- [../evals/README.md](../evals/README.md) — operational eval runbook
```

### 3. Review and save

- Fill in any gaps from the actual Makefile / src tree
- Verify all paths and make targets against the current codebase
- Remove any sections that reference future work (keep it factual)
- Save to `docs/OVERVIEW.md`

### 4. Share (optional)

If the user wants to share with stakeholders, trigger `/share` after saving:
- Notion page: `/share notion` → posts to the galactus Notion space
- Google Doc: `/share gdoc` → creates in Google Drive

## Maintenance rule

Update `OVERVIEW.md` when:
- A new service is added to `src/`
- A new eval runner lands in `evals/pipelines/`
- A tooling doc in `docs/` changes significantly
- Ports, env var names, or make target names change

The individual tooling docs are the source of truth. This overview is a compiled summary — always verify against those docs before updating.
