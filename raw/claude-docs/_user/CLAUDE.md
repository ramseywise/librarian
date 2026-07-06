# Global Claude Code Settings

Personal conventions and cross-project skills. Project-specific rules live in each repo's `CLAUDE.md`.

> Full reference: `~/.claude/README.md` (not auto-loaded — read on demand).

## Skills

Global skills live in `~/.claude/skills/` — auto-discovered in every project. Project-specific skills live in each repo's `.claude/skills/` (e.g. librarian has `ingest`, `lint`, `query`, `adk-context`).

### Skill pipeline

New tech-domain skills are workshopped in `librarian/raw/claude-skills/<tool>/` before being promoted to `~/.claude/skills/`. The raw version is the source of truth for iteration — it's grounded in wiki pages and updated as the wiki grows.

```
librarian/raw/claude-skills/<tool>/<tool>.md   ← workshop: draft, iterate, ground in wiki
~/.claude/skills/<name>/SKILL.md               ← promoted: active, available everywhere
```

To promote a skill: copy the raw file to `~/.claude/skills/<name>/SKILL.md`. When the wiki grows and the skill needs updating, edit the raw source first, then re-promote.

### Session & Git workflow

| Skill | What it does |
|-------|-------------|
| `/compact-session` | Session checkpoint: save artifacts, session note, memory, commit + push + PR. Mid-session: compact and continue. End of session: stop. |
| `/quick-pr` | Stage → commit → push → draft PR end to end |
| `/quick-commit` | Stage → commit (no push/PR) |
| `/claude-insights` | Cartographer HTML report from session notes + JSONL (CE/PE eval) |

### Discovery & planning

| Skill | What it does |
|-------|-------------|
| `/research-review` | Research phase: read sources, write `.claude/docs/research/{name}.md` |
| `/plan-review` | Planning phase: write `.claude/docs/plans/{name}.md` |
| `/plan-refactor` | Plan a refactor before executing |

### Dev execution

| Skill | What it does |
|-------|-------------|
| `/execute-plan` | Execute phase: step through active plan, append to `CHANGELOG.md` |
| `/code-review` | Review phase: write `.claude/docs/reviews/{name}.md` + PR |
| `/review-pr` | Review an open PR: read diff, write review doc |
| `/code-debug` | Diagnose and fix a bug |

### Product / initiative workflow (Linear)

The pipeline from "what do we build" to Linear tickets:

```
/define-milestones  →  goal posts (what by when, which initiatives)
/design-sprint      →  (optional) ideate initiatives when starting from scratch
/scope-initiative   →  initiative → failure modes → task backlog → Linear hierarchy
/doc-to-linear-tickets  →  push the scoped backlog into Linear issues
```

| Skill | What it does |
|-------|-------------|
| `/define-milestones` | Define Linear milestones: goal, success metrics, initiative list |
| `/design-sprint` | Ideate from scratch: HMW → workstreams → named initiatives |
| `/scope-initiative` | Initiative → backward mapping, task backlog, dependency map, Linear hierarchy |
| `/doc-to-linear-tickets` | Push a planning doc into structured Linear issues |
| `/execute-tasks` | Step through task list, mark done |
| `/github-projects` | Manage GitHub Projects V2 (librarian project only) |

### Tech-domain skills

Skills are grounded in wiki pages — they distill accumulated patterns into actionable rules. When the wiki grows, update the skill. New skills start in `raw/claude-skills/<tool>/` and get promoted to `~/.claude/skills/` when ready.

| Skill | What it does | Wiki source |
|-------|-------------|-------------|
| `/langgraph` | State design, node/edge patterns, HITL, checkpointing, streaming, production checklist | [[LangGraph CRAG Pipeline]], [[LangGraph Advanced Patterns]], [[Production Hardening Patterns]] |
| `/prototype` | Rapid prototype: skip tests, skip polish, just build | — |
| `/mcp-builder` | Build MCP servers (Python FastMCP or Node SDK) | [[MCP Protocol]] |

**In workshop** (`librarian/raw/claude-skills/`):
- `google-adk/` — ADK Python patterns (promote when building ADK agents)
- `fastapi/` — FastAPI service conventions (to build)
- `java/`, `web-components/` — archived reference (different stack)

### Integrations

| Skill | What it does |
|-------|-------------|
| `/doc-to-linear-tickets` | Parse a planning doc (pasted, Google Doc, or drafted) → create structured Linear issues with priorities, sizes, and dependencies |

### Meta skills

| Skill | What it does |
|-------|-------------|
| `/skill-creator` | Create, edit, eval, and benchmark skills |

## Issue Tracking

Linear ↔ GitHub integration. Branch, commit, and PR naming must include `LIN-{id}` for auto-linking.

Stack: Code → GitHub | Tasks → Linear | Knowledge → Notion

## Commit style

- Conventional commits: `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`, `session:`, `checkpoint:`
- Title under 60 chars, imperative mood
- Body: why, not what
