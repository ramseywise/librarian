---
title: Session Insights
tags: [context-management, llm, pattern, project]
summary: Compiled insights from 42 facet-analyzed Claude Code sessions — friction patterns, recurring themes, skill candidates, and learning outcomes.
updated: 2026-04-26
sources:
  - raw/sessions/
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

## See Also

- [[Session Log]]
- [[Claude Workflow System]]
- [[Production Hardening Patterns]]
- [[SKILL.md Pattern]]
