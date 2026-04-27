---
title: Session Log
tags: [context-management, llm, project]
summary: Chronological index of all Claude Code and Codex sessions captured in raw/sessions/ — what was worked on, which project, and approximate token spend.
updated: 2026-04-26
sources:
  - raw/sessions/
---

# Session Log

Operational activity log compiled from `raw/sessions/`. Each row is one session. First-prompt summary indicates the primary intent; token counts are from session frontmatter.

---

## Codex Sessions — 2025-09

All on the `txmatch` project, `ramsey-feature-dev` branch (Shine — document-for-transaction validation and scoring system).

| Date | Session | Prompts | Topic |
|------|---------|---------|-------|
| 2025-09-14 | 4998c107 | 54 | Transaction autoassignment notebook, scoring system |
| 2025-09-14 | 8713027f | 3 | Document-for-transaction validation |
| 2025-09-14 | a2b0ddde | 30 | `_build_ground_truth_sets`, validation scoring |
| 2025-09-14 | ef78d2bb | 24 | Validation + transaction matching |
| 2025-09-15 | 76cb019f | 4 | Validation tabs, transaction match vectorised |
| 2025-09-16 | 58516737 | 21 | Validation refactor |
| 2025-09-16 | dabddaa4 | 20 | Scoring system finalisation |

---

## Claude Code Sessions — April 2026

### 2026-04-10 (Workspace)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 1900854e | 3 | 139k | Librarian folder restructure — `analyzer/` belongs in ingestion or eval; research how to reorganise `librarian/` |

### 2026-04-11 (Workspace)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| deb81c96 | — | — | Transfer code from CS agent; architecture refactors |
| 394ba556 | — | — | Refactor insights skill |
| 356746ec | — | — | Librarian chat front-end orientation |
| fe1c0bd1 | — | — | Git delta resolution |
| f5cfe1b3 | — | — | Source layout — `src/agents/infra/` placement question |

### 2026-04-12 (Workspace)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 406fcc7f | — | — | Google ADK masterclass added to workspace; context engineering comparison |
| 8d1a71b0 | — | — | ADK vs LangGraph comparison doc |

### 2026-04-14 (Workspace — heavy day: 8 sessions)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 53ef9ef6 | 3 | 80k | LangGraph-ADK compatibility; rebuild as Python LangGraph copilot |
| a419a1f1 | 3 | 58k | Research ts-copilot-upgrades tradeoffs; update plan |
| dd36bdeb | 1 | 162k | Execute terraform-restructure → unblocks GitHub CI/CD |
| 4a5c5ba3 | 3 | 93k | Python copilot: ts_google_adk parity + copilot upgrades research |
| 48cd8a0e | 4 | 41k | Librarian as RAG-only service; bring to engineering standard |
| a6a9bcf4 | 8 | 125k | `.claude/docs` restructuring — research→plan chains, archive lifecycle |
| ec44fece | 5 | 21k | Ruff linter misconfigured for TS in polyglot repo; disable for ts folder |
| 3def7093 | 2 | 78k | `playground/src/clients` vs `interfaces` cleanup; LangGraph-ADK compat plan |
| 42826f2b | 1 | 65k | Priority order: infra-interfaces → orchestration-rollout → terraform → langgraph-adk-compat |

### 2026-04-15 (poc project — Help Support RAG Agent)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 578a75d8 | 3 | 120k | `.gitignore` audit |
| b269ccf1 | 4 | 50k | rag-poc vs playground/librarian comparison; LangGraph copilot best practices |
| 17811ed1 | 7 | 47k | Switch LLM to Anthropic API; RAG components reuse |
| eeebbd1e | 7 | 110k | Unit tests for `app`; code review; translation support (FR/DE/DA) |
| b669eebb | 6 | 231k | `app/agent_nodes/retriever` → `rag/`; orchestration domain reorg |
| 7c4e1442 | 4 | 6k | `Literal["q&a", "task_execution"] = None` typing fix |
| c2109cb9 | 3 | 79k | Code quality pass; changelog write; commit grouping |
| 92643c18 | 1 | 1k | Find `.env` with Anthropic API key |

### 2026-04-16 (poc project)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 314ac54a | — | — | `make lint` pass; mypy errors |
| 06b9a503 | 3 | — | Intensive code review — simplify and condense |
| efd3b13a | 5 | — | Demo data placement |
| ca037b9e | 1 | — | Eval cleanup and simplification |

### 2026-04-17 (Workspace + poc)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 7a25dbd0 | 11 | — | ADK samples scan — context engineering (.agent/.claude/.agents), native_skill_mcp comparison |
| 9fc31735 | — | — | mypy/ruff linting errors |
| c44fa991 | 5 | — | Code review graph changes; simplify agentic system |

### 2026-04-18 (Workspace + poc)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 29a60696 | 5 | — | `.env` for CS agent RAG pipeline notebooks |
| 57042538 | 4 | — | Eval cleanup — graders vs metrics vs tasks; eval root simplification |
| 0ef44b3d | 5 | — | Google ADK parity with adk-agent-samples; shared protocols vs skills |

### 2026-04-19 (poc project)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 6765bd2b | 12 | — | Linting errors |
| 1bafe007 | — | — | mypy errors after ruff pass |
| 9e66674c | 3 | — | `ingestion/` vs `embedding/` vs `preprocessing/` — single indexer decision |

### 2026-04-20 (Workspace + poc)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 64095580 | 17 | — | playground/.claude vs adk-agent-pocs/.claude overlap; ADK research into docs |
| ba67f0c4 | 3 | — | Sensitive data audit before merging open PR |

### 2026-04-21 (Workspace + playground + wiseer)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| dd86ca38 | 5 | — | Compare playground VA agents vs listen-wiseer setup; listen-wiseer restart |
| 46a3b186 | 25 | — | Playground sensitive data audit; infra folder consolidation |
| 9a091358 | 12 | — | listen-wiseer phase 3 refactor continuation |
| 826a1a97 | 62 | — | Track B Phase 3 — RDS Postgres for LangGraph checkpointer + EFS for Billy SQLite |
| ecf3e696 | 1 | — | Auto-generate CLAUDE.md for codebase |

### 2026-04-22 (Workspace)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 198e7d2c | 3 | 9k | `/insights` report analysis; create doc-to-linear-tickets skill; push to Linear |

### 2026-04-24 (Workspace)

| Session | Prompts | ~Tokens | Topic |
|---------|---------|---------|-------|
| 108c3f61 | 10 | 92k | Playground infra → GitHub; secrets audit; consolidate settings.json; name "librarian" chosen for wiki repo |

---

## Notes

- `poc` project = Help Support RAG Agent (early RAG POC, pre-librarian-wiki era)
- `wiseer` / `listen-wiseer` = Spotify recommendation agent
- `playground` = Billy VA agent + infra
- `txmatch` = Shine transaction matching (Codex, 2025)
- Token counts omitted where not available in frontmatter (many sessions lacked full stats in migrated skeleton notes)

## See Also

- [[Librarian Project]]
- [[Librarian KB — Build Plan]]
- [[VA Agent Project]]
- [[Listen-Wiseer Project]]
- [[Claude Workflow System]]
- [[Session Insights]]
