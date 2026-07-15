---
title: Session Insights
tags: [context-management, llm, pattern, project]
summary: Compiled insights from 42 facet-analyzed Claude Code sessions — friction patterns, recurring themes, skill candidates, and learning outcomes.
updated: 2026-07-14
sources:
  - raw/sessions/
  - raw/sessions/claude-2026-04-10-what-is-this-analyzer-folder-aren-t-thes-1900854e.md
  - raw/sessions/claude-2026-04-11-can-we-transfer-the-code-from-cs-agent-a-deb81c96.md
  - raw/sessions/claude-2026-04-11-librarian-chat-is-the-front-end-right-so-356746ec.md
  - raw/sessions/claude-2026-04-11-resolving-deltas-100-72-72-completed-wit-fe1c0bd1.md
  - raw/sessions/claude-2026-04-11-shhould-src-agents-infra-live-under-src-f5cfe1b3.md
  - raw/sessions/claude-2026-04-14-i-want-librarian-to-remain-as-solely-a-h-48cd8a0e.md
  - raw/sessions/claude-2026-04-14-key-insights-re-claude-docs-restructurin-a6a9bcf4.md
  - raw/sessions/claude-2026-04-14-one-thing-that-i-m-realizing-is-that-my-ec44fece.md
  - raw/sessions/claude-2026-04-14-what-is-the-difference-between-playgroun-3def7093.md
  - raw/sessions/claude-2026-04-15-i-ve-added-app-agent-nodes-retriever-tha-b669eebb.md
  - raw/sessions/claude-2026-04-16-help-support-rag-agent-rag-poc-git-retr-314ac54a.md
  - raw/sessions/claude-2026-04-17-cade-we-code-review-changes-to-graph-is-c44fa991.md
  - raw/sessions/claude-2026-04-19-looks-like-linting-has-some-errors-still-1bafe007.md
---

# Session Insights

Compiled from `~/.claude/usage-data/facets/` (42 sessions with LLM-analyzed outcomes). See [[Session Log]] for the full chronological index.

---

## Outcomes Summary

| Outcome | Count |
|---------|-------|
| Fully achieved | 21 |
| Mostly achieved | 16 |
| Partially achieved | 4 |
| Not achieved | 1 |

89% of sessions fully or mostly achieved their goal. Partial/not-achieved cases are the most instructive (see below).

---

## Recurring Work Themes

**Refactoring / code review** (12 sessions — the dominant category):
- RAG POC codebase simplification and modularisation (poc project, April 15–19)
- Package restructure: `rag_core/`, `librarian/`, `orchestration/` layout decisions
- LangGraph orchestrator decoupling from ADK runtime

**Architecture / planning** (7 sessions):
- LangGraph vs ADK parity and compatibility analysis
- Terraform restructure for GitHub CI/CD
- `.claude/docs` lifecycle redesign (research→plan→archive model)

**Claude workflow system** (5 sessions):
- Insights skill refactoring → `claude-insights`
- `.claude/docs` restructuring; three-folder lifecycle
- Doc-to-linear-tickets skill creation
- Workspace CLAUDE.md generation

**Infrastructure** (3 sessions):
- Terraform restructure (48 files, new infra layout)
- VA agent: RDS Postgres for LangGraph checkpointer + EFS for Billy SQLite (62 prompts — longest session)
- Playground infra consolidation and secrets audit

---

## Friction Patterns

20 of 42 sessions had recorded friction. Root causes cluster into four types:

### 1. Claude hit usage limit mid-task (3 sessions)
- `dd36bdeb`: Terraform restructure — resumed after limit, continued successfully
- `64095580`: Workspace structure analysis — diverged after reset, commit org incomplete
- `efd3b13a`: Graph module refactor — codebase diverged post-limit, left partially done

**Pattern**: Long execution sessions (100k+ output tokens) risk hitting limits. Phase checkpoints mitigate this — `/compact "step N"` preserves state at each step boundary.

### 2. Wrong assumption about naming / intent (6 sessions)
- `a6a9bcf4`: Claude's initial archive/scope/build split misaligned with user's mental model (took several iterations)
- `ec44fece`: Red squiggles were from TypeScript Language Server, not ruff — wrong tool diagnosed
- `314ac54a`: English query transform against German corpus → zero results on first smoke test
- `a419a1f1`: Claude wrote research from knowledge, not from reading the codebase first
- `b669eebb`: Deleted `app/rag/` thinking it was a duplicate, but it was the primary domain — destructive error
- `356746ec`: Began exploring files instead of proposing a plan for the end-session hook wiring

**Pattern**: Intent mismatch is the top friction source. The research→plan→confirm loop prevents most of these.

### 3. Cascading import / structural errors (5 sessions)
- `1bafe007`: Circular import introduced between `datastore/__init__.py` and `factory.py`
- `deb81c96`: Test broke after refactor because it directly imported private `_chunk_hash`
- `c44fa991`: `monkeypatch.setattr` string path missed by sed-based import rewrite
- `fe1c0bd1`: `mv` followed a symlink instead of the real path
- `f5cfe1b3`: TOML edit created wrong subtable structure

**Pattern**: Structural changes (file moves, module renames) are highest-risk. Scope check before touching files, and full test run after each step, are the mitigations.

### 4. Environment issues (3 sessions)
- `6765bd2b`: Docker blocking port + Ollama not installed + Bedrock credentials not available — compounded
- `17811ed1`: `make app-run` target didn't exist, alias needed
- `29a60696`: Added unused AWS env vars to `.env`

**Pattern**: Environment friction is mostly a first-run problem. Makefile hygiene and `.env.example` coverage prevent it.

---

## Partially / Not Achieved Sessions

| Session | Summary | Root Cause |
|---------|---------|------------|
| `356746ec` | End-session → quick-pr hook wiring | Started exploring instead of planning; user interrupted |
| `b669eebb` | RAG codebase domain boundary restructure | Destructive delete of `app/rag/` before intent confirmed |
| `efd3b13a` | Graph module fixture + node rename | Hit usage limit mid-refactor; codebase diverged |
| `64095580` | Workspace structure advice + git commit org | Hit usage limit mid-analysis; commit org incomplete |
| `6765bd2b` | Lint pass + LangGraph agent run | Environment issues (Docker, Ollama, Bedrock) compounded |

---

## Skill Creation Candidates

Based on recurring friction and multi-step patterns that appeared across sessions:

| Candidate | Trigger | Why |
|-----------|---------|-----|
| `env-audit` | Before any infrastructure change | Sessions `29a60696`, `ba67f0c4` both involved `.env` / secrets audits as a prerequisite step — could be a 2-minute automated check |
| `polyglot-lint` | Editing mixed TS/Python repos | `ec44fece` hit repeated ruff-vs-TypeScript confusion; a skill that detects file type and routes linter correctly would eliminate this |
| `import-check` | After any module rename / file move | Circular imports and broken string paths appeared in 5 sessions — a post-edit import resolution check |
| `usage-limit-recovery` | Long execution sessions | `dd36bdeb`, `efd3b13a`, `64095580` all hit limits mid-task; a recovery protocol (checkpoint → summarise state → resume) |

The `env-audit` and `polyglot-lint` patterns are most actionable — they're small, well-scoped, and would eliminate recurring friction.

---

## Learning Outcomes

**Architecture patterns confirmed by practice:**
- Research→plan→confirm prevents the bulk of intent-mismatch friction (sessions `a6a9bcf4`, `a419a1f1`)
- CRAG retry loop and [[Reciprocal Rank Fusion (RRF)]] work well together in production (sessions `1900854e`, `06b9a503`)
- LangGraph `StateGraph` + ADK `InstructionProvider` can coexist in the same repo — Level 1 vocabulary alignment is the right starting scope (session `406fcc7f`)

**What needed more research (sessions where Claude worked from assumptions):**
- Polyglot linting configuration (ruff scope, TypeScript Language Server interaction)
- `AsyncPostgresSaver` usage in multi-worker deployment (runtime topology)
- ADK skill loading strategies A/B/C tradeoffs vs LangGraph equivalents

**Heavy token sessions (cost hotspots):**
- `b669eebb`: 231k output tokens — codebase restructure with 6 prompts
- `dd36bdeb`: 162k — terraform restructure (1 prompt, long execution)
- `826a1a97`: 62 prompts — VA agent Phase 3 (longest in prompt count)
- `64095580` + `4a5c5ba3` + `53ef9ef6`: each 65–93k — architecture planning and analysis sessions

Architecture/planning sessions generate more output tokens per prompt than execution sessions. Keeping plans concise and scoping steps to ≤40% context window addresses this.

---

---

## Insights — 2026-06-04

*Compiled from 24 sessions (2026-06-01 through 2026-06-04), all on galactus (support agent ablation + GT verification).*

### Top Patterns

**Compaction without context restoration**: All 24 sessions compacted with `[Fill in]` placeholders intact. Checkpoints are being generated but never completed — cold-resumption is unreliable every session.

**Token bloat on eval/analysis work**: 3 sessions exceeded 1M tokens (GT dataset verification: 1.25M; Workspace-wide execute: 1.47M; chat-agent parity: 1.19M). Root cause: re-injecting full codebase context instead of delta updates. One prompt fix: prepend "Before exploring, check cached docs for answers. Only ask new questions on deltas."

**Repeated agent cross-diffing**: "How does X compare to Y?" appeared across 10+ sessions with no cached answer. `docs/frameworks/agent-feature-parity.md` exists but is not being used as a first-stop reference.

**Branch fragmentation**: `vir-179-*` (3 sessions, 301K tokens) and `vir-212-*` (2 sessions, 426K tokens) covering overlapping work → context thrashing, duplicated cache writes.

### Skill candidates

| Skill | Verdict | Rationale |
|-------|---------|-----------|
| `checkpoint-fill` | Generate | Automates completing unfilled template fields after compaction |
| `consolidate <area>` | Generate | Structured cleanup for recurring architectural drift (6+ sessions flagging dead code, duplicate metrics) |
| `compare-agents` | Generate | Cached agent feature matrix to eliminate repeated cross-diffing |

### Cost signals

- **Cache write anomaly**: short sessions showing 3–6× cache_write vs output size → context re-pinned unnecessarily on resume
- **Consolidate branches**: same codebase loaded fresh in 5+ branches → lower prefix cache hit rate
- **Batch eval queries**: pre-filter GT data to unique queries before grading (195 unique from 597)

---

---

## Insights — 2026-04-10 to 2026-04-15 Batch (ingested 2026-07-06)

*20 sessions across `playground` (Workspace project) and `poc` (Help Support RAG Agent). Heavy on refactoring and architecture research.*

### Confirmed friction patterns

**Polyglot linting (session `ec44fece`)**: Ruff flagged TypeScript files in a mixed TS/Python repo because the `src/` ruff config didn't exclude the TypeScript subfolder. Resolution: add `exclude = ["v2/ts_google_adk"]` to `[tool.ruff]` in `pyproject.toml`. This confirms the `polyglot-lint` skill candidate — the fix is a one-liner but requires knowing ruff's scope model.

**Cascading structural errors from file moves (session `fe1c0bd1`)**: `mv` followed a symlink instead of the real path, breaking import resolution after the restructure. The mitigations are: (a) verify the target is a real path before moving, (b) run full import check after every structural change.

**Reviews disconnected from plan iteration (session `a6a9bcf4`)**: 2 of 8 reviewed plans had unresolved "Needs changes" flags with no follow-up — `/code-review` had no iteration mode at that point. The research→plan→confirm→review→revise loop requires an explicit feedback cycle from review back to plan.

### Architecture decisions confirmed

- **Librarian scope**: RAG-only service, not multi-agent copilot — scope locked in session `48cd8a0e`. Prevents architectural drift.
- **Core module pattern**: Shared types in `core/` breaks circular dependency between `storage` and `librarian` modules without requiring a monorepo restructure. Session `deb81c96`.
- **Binary triage without LLM**: For 0/1 routing (is this query for the LLM or not?), a keyword/rule-based classifier in Next.js is preferable to an LLM call — eliminates latency and cost for a deterministic decision. Session `356746ec`.
- **Fargate over Lambda for monolithic Python service**: Lambda cold-start plus 15-min timeout is incompatible with always-warm embedding model and stateful LangGraph checkpointer. Session `fe1c0bd1`.
- **clients/ vs interfaces/ boundary**: `clients/` = stateful external API wrappers; `interfaces/` = stateless internal protocol contracts. Collapsing them creates hidden coupling between transport and domain logic. Session `3def7093`.

---

## Insights — 2026-04-15 to 2026-04-20 Batch (ingested 2026-07-06)

*20 sessions on the `poc` project (Help Support RAG Agent) and Workspace. Primary themes: RAG PoC modularisation, eval harness design, ADK context engineering comparison, multi-repo organisation.*

### Architecture decisions confirmed

- **Domain boundary for data models (session `b669eebb`):** `data_models/models.py` belongs in `core/` alongside agent prompts and state — not in a separate `data_models/` package. Core is the zero-dependency base layer: shared types, state definitions, and static prompts. Everything else imports from it; core imports from nothing.

- **src/ vs app/ naming (session `1bafe007`):** Rename `app/` → `src/` for the core Python package when a frontend exists at the repo root. Convention: `src/` = Python business logic + orchestrators; frontend dirs (Next.js, Streamlit) live at root. All orchestrators (LangGraph, ADK) go inside `src/` — they're implementation, not infrastructure.

- **Ingestion/embedding in preprocessing, not retrieval (session `9e66674c`):** See [[RAG Retrieval Strategies]] — Ingestion Pipeline section. Retrieval's scope is query-time only. One indexer, owned by preprocessing.

- **Runtime-agnostic orchestrator plan (session `c44fa991`):** When a RAG PoC grows to support multiple runtimes (LangGraph + ADK), write the refactor plan *before* touching files. The pattern: `orchestrator/{langgraph,adk}/` with shared `orchestrator/{memory,guardrails,prompts}/`. The factory selects the runtime via `ORCHESTRATION_STRATEGY` env var. This is the same pattern already implemented in the Librarian service — the PoC was converging on it independently.

- **Graders vs metrics vs harnesses distinction (session `57042538`):** See [[VA Eval Harness]] — Eval Directory Structure section. The key conceptual point: graders produce metrics; harnesses run graders against evalsets; experiments test variants and push to LangSmith. These are four distinct concepts that should live in four distinct directories.

### Friction patterns (new from this batch)

**Context loss after usage limit (sessions `64095580`, `efd3b13a`):** Both sessions where analysis or refactoring work hit the context limit resulted in partial/diverged outcomes. The `64095580` workspace analysis left commit organisation incomplete; `efd3b13a` left the graph node refactor in a broken state. Mitigation: `/compact "step N"` checkpoints before crossing ~80% context.

**Destructive file delete before intent confirmed (session `b669eebb`):** Deleted `app/rag/` thinking it was a duplicate of `app/agent_nodes/retriever`, but it was the primary domain module. The invariant: never delete a directory without first listing all its callers (`grep -r "from app.rag"`).

**Multi-query smoke test against wrong language corpus (session `314ac54a`):** First smoke test sent an English query against a German corpus → zero results, looked like a bug. The pipeline was correct; the test data was wrong. When standing up a multilingual RAG pipeline, smoke tests must use a query in the corpus language.

**ADK context engineering comparison insight (session `7a25dbd0`):** Scanning `adk-samples-main` confirmed rag_poc uses an implicit Strategy C (one tool always bound). Acceptable for single-domain RAG. Strategy B upgrade is warranted when a second domain is added.

### Skill candidates (new from this batch)

| Candidate | Trigger | Rationale |
|---|---|---|
| `pre-delete-check` | Before any `rm -rf` on a module dir | Sessions `b669eebb`, `06b9a503` — destructive deletes were the root cause of partial outcomes; a caller-grep check takes 5s |
| `smoke-test-lang` | Before first RAG pipeline test | Session `314ac54a` — multilingual RAG needs smoke test in the corpus language, not the developer's default |

---

## Insights — 2026-07-06 to 2026-07-14 Batch (ingested 2026-07-14)

*11 sessions across INTENSO, galactus, and puffin. Mostly prompt-only captures (no recorded assistant transcript) — friction inferred from what was asked, not from resolution logs.*

### New friction patterns

**Operational commands living only in memory, not the README (session `63940e32`):** The user repeatedly has to re-ask how to run a known skill (`/ingest`) and what it actually does end-to-end. Root cause: the answer exists in the skill definition and in the user's head, but not in a discoverable `README.md`. Confirms the `env-audit`-adjacent idea from the April batch — but generalized: any skill whose usage gets re-explained in a session should get a README line as part of that session's wrap-up, not just an inline answer.

**Settings/permissions fragmented across sibling repos (sessions `a3b6ecb6`, `012cfada`):** Working across many repos under one drive root (galactus, playground, INTENSO) produced inconsistent permission-prompt behavior because settings weren't layered consistently. Resolved by treating the drive root as an intermediate settings scope between global (`~/.claude/`) and per-repo (`.claude/`) — see [[Claude Workflow System]] for the resulting three-tier-plus-root model.

### Skill candidate

| Candidate | Trigger | Rationale |
|---|---|---|
| `readme-sync-check` | End of any session where a skill's usage was re-explained | Session `63940e32` — closes the loop the `/ingest` question exposed; a lightweight check for "was this just re-explained verbally and not written down" |

---

## See Also

- [[Session Log]]
- [[Claude Workflow System]]
- [[Production Hardening Patterns]]
- [[SKILL.md Pattern]]
