---
title: Claude Workflow System
tags: [context-management, llm, pattern]
summary: Personal Claude Code harness — global skills, PreCompact hook, phase checkpoints, and session notes — that automates context management across multi-phase engineering workflows.
updated: 2026-07-06
sources:
  - raw/sessions/claude-2026-04-11-i-want-to-refactor-this-insights-skill-f-394ba556.md
  - raw/sessions/claude-2026-04-14-key-insights-re-claude-docs-restructurin-a6a9bcf4.md
  - raw/sessions/claude-2026-04-22-the-user-just-ran-insights-to-generate-a-198e7d2c.md
  - raw/claude-docs/_user/CLAUDE.md
---

# Claude Workflow System

## What It Is

A personal Claude Code harness built around `~/.claude/` that manages context, skills, and session continuity across multi-phase engineering work. The system enforces a research → plan → execute → review pipeline using [[SKILL.md Pattern|skills]] and a [[Prefix Caching|PreCompact]] hook.

## Components

### Global Skills (`~/.claude/skills/`)

22 skills auto-discovered in every project. Split by role:

| Category | Skills |
|----------|--------|
| Pipeline | research-review, plan-review, execute-plan, code-review |
| Session | compact-session, quick-pr, quick-commit |
| Product | define-epic, plan-epic, execute-tasks, github-projects |
| Tech domain | langgraph, mcp-builder, prototype, adk-python |

Tech-domain skills are grounded in this wiki (see [[SKILL.md Pattern]]). Pipeline skills live directly in `~/.claude/skills/`.

### PreCompact Hook (`~/.claude/hooks/pre-compact.sh`)

Fires on every context compaction (manual or auto-triggered). Reads the JSONL transcript to count tokens, detects the current phase from recent skill invocations, and writes a checkpoint note to `~/.claude/sessions/`.

This ensures no session context is lost on compact, even without explicit `/compact-session` calls.

### Phase Checkpoint Pattern

Each phase skill calls `/compact "phase: X → Y"` at handoff. The `custom_instructions` field is picked up by the PreCompact hook to label the snapshot.

```
research-review  →  /compact "phase: research → plan"
plan-review      →  /compact "phase: plan → execute"
execute-plan     →  /compact "step N: <title>"        (per step)
execute-plan     →  /compact "phase: execute → review"
code-review      →  /compact "phase: review → done"
```

### Session Notes (`~/.claude/sessions/`)

All session notes are centralised here — not project-relative. Sources:
- PreCompact hook (every compact)
- `/compact-session` (explicit end-of-session)
- `uv run python -m tools.cartographer --migrate` (batch migrate JSONL → skeleton notes)

### Skill Pipeline (tech-domain skills)

```
librarian/raw/claude-skills/<name>/<name>.md  ← workshop (grounded in wiki)
         ↓  promote-skill.sh <name>
~/.claude/skills/<name>/SKILL.md              ← active everywhere
```

## Evolution

The system was iteratively developed April 2026:
- **2026-04-10 to 04-14**: `.claude/docs` restructuring — research→plan chain pattern identified; lifecycle model (in-progress / archive / backlog) established
- **2026-04-14**: `a6a9bcf4` — key insight: reviews were disconnected; `/code-review` had no iteration mode; feedback loop from review → plan formalized
- **2026-04-22**: `198e7d2c` — `/claude-insights` skill created; doc-to-linear-tickets skill added
- **2026-04-26**: PreCompact hook wired; phase checkpoints added to all four phase skills; session notes centralised

## Key Design Decisions

- **No project-relative memory**: memory lives at `~/.claude/projects/<slug>/memory/`, not `<repo>/.claude/memory/`, to avoid git-committing private notes
- **PreCompact not Stop hook**: compaction checkpoints fire on compact (context boundary), not on every response — avoids noise
- **500k token gate**: stubbed in hook, not yet enforced — can be activated by uncommenting the threshold constant

## Current Global Skills (as of 2026-07-06)

Full skill inventory from `~/.claude/CLAUDE.md`:

| Category | Skill | What it does |
|---|---|---|
| Session/git | `/compact-session` | Checkpoint: save artifacts, note, memory, commit + push + PR |
| Session/git | `/quick-pr` | Stage → commit → push → draft PR |
| Session/git | `/quick-commit` | Stage → commit (no push) |
| Session/git | `/claude-insights` | HTML report from session notes + JSONL |
| Discovery | `/research-review` | Research phase: write `.claude/docs/research/{name}.md` |
| Discovery | `/plan-review` | Planning phase: write `.claude/docs/plans/{name}.md` |
| Discovery | `/plan-refactor` | Plan a refactor before executing |
| Dev execution | `/execute-plan` | Step through active plan, append to `CHANGELOG.md` |
| Dev execution | `/code-review` | Write `.claude/docs/reviews/{name}.md` + PR |
| Dev execution | `/review-pr` | Review an open PR |
| Dev execution | `/code-debug` | Diagnose and fix a bug |
| Product/Linear | `/define-milestones` | Define milestones: goal, success metrics, initiative list |
| Product/Linear | `/design-sprint` | Ideate: HMW → workstreams → named initiatives |
| Product/Linear | `/scope-initiative` | Initiative → backward mapping, task backlog, Linear hierarchy |
| Product/Linear | `/doc-to-linear-tickets` | Push planning doc into Linear issues |
| Product/Linear | `/execute-tasks` | Step through task list, mark done |
| Product/Linear | `/github-projects` | Manage GitHub Projects V2 |
| Tech domain | `/langgraph` | State design, node/edge patterns, HITL, checkpointing |
| Tech domain | `/prototype` | Rapid prototype: skip tests, skip polish, just build |
| Tech domain | `/mcp-builder` | Build MCP servers (Python FastMCP or Node SDK) |

## Docs Lifecycle Pattern

From `.claude/docs/` conventions:

| Directory | Git-tracked | Purpose |
|---|---|---|
| `research/` | Yes | Permanent knowledge base — architecture decisions, evaluated patterns |
| `tooling/` | Yes | Curated reference for dev tooling |
| `plans/` | No (gitignored) | Local-only implementation specs — delete after execution |
| `reviews/` | No (gitignored) | Local-only code review artifacts — ephemeral |

**Promotion flow:** When a plan is executed, promote key decisions into a `research/` doc and delete the plan file.

## Issue Tracking (Linear ↔ GitHub)

Branch, commit, and PR naming must include `LIN-{id}` for auto-linking:
- Branch: `feature/LIN-123-short-description`
- Commit: `feat(LIN-123): short imperative title`
- PR title: must contain `LIN-123`

Stack: Code → GitHub | Tasks → Linear | Knowledge → Notion

## Commit Style

- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`, `session:`, `checkpoint:`
- Title under 60 chars, imperative mood
- Body: why, not what

See [[Claude Code Hook Architecture]] for how hooks enforce commit and code quality automatically.

## See Also

- [[SKILL.md Pattern]]
- [[Prefix Caching]]
- [[Karpathy LLM Wiki Pattern]]
- [[Session Log]]
- [[Claude Code Hook Architecture]]
