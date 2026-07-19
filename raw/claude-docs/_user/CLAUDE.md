# Global Claude Code Instructions

## Developer Identity

Founding staff AI engineer fluent in Python and TypeScript agent systems. Frameworks in active use:
Vercel AI SDK, Google ADK, Anthropic Claude API, LangGraph, LangChain. Primary focus: platform engineering
for NYC-DSSG (a nonprofit) — building operational and technical support tools for volunteer cohorts and
nonprofit client engagement. Skip basics unless asked.

## Communication

- Brief and direct. Lead with the action.
- No filler, no trailing summaries of what you just did — EXCEPT the completion format below.
- File:line references over prose descriptions.
- Don't add unsolicited comments, docstrings, or refactors to code I didn't ask to change.
- When I correct a mistake, update the appropriate CLAUDE.md level — ask if unclear.

### Completion format (non-trivial / multi-step tasks only)

When a task involved editing/creating multiple files, executing a plan phase, or
anything I'd hand to a fresh session, close with three sections (skip for one-liners,
questions, and read-only answers — those stay conversational):

1. **Summary** — 2–3 lines, what changed and the verification result.
2. **Files created/edited** — bulleted `path:line` list (markdown links).
3. **Open issues** — each with a one-line fix recommendation. For anything that
   warrants its own session, include a fenced **spawn prompt** (repo + plan-doc path +
   phase command, per Session hygiene) I can paste into a new VS Code Claude session.
   Write "None" if there are none — don't invent issues to fill the section.

## Tooling — skills, refs, and rules

### Skill groups (20 global skills in `~/.claude/skills/`)

**`code-`** — implementation (4 skills):
`/code-debug` (quick fix from error), `/code-refactor` (quality-driven, invokes native
`/simplify` as finishing pass), `/code-review` (standing quality review on diff — leveled:
1=lint, 2=+tests+akira, 3=+sanyi), `/code-pr` (review an open PR).

**`design-`** — architecture & planning artifacts (4 skills):
`/design-sprint` (full design sprint from scratch), `/design-initiative` (initiative →
backlog), `/design-milestones` (initiative → phase checkpoints), `/design-prototype`
(spike/explore).

**`workflow-`** — process pipeline (5 skills):
`/workflow-research` (phase 1 — structured research artifact; `fan-out` mode for parallel
haiku investigation) → `/workflow-plan` (phase 2) → `/workflow-execute` (phase 3) →
`/workflow-review` (phase 4 — plan fidelity). `/workflow-insights` (usage analytics, feeds
retro). `/workflow-retro` (tooling retrospective + config audit — closes the feedback loop).

**`git-`** — git operations (2 skills):
`/git-commit` (stage + commit), `/git-pr` (stage + commit + PR).

**Cross-cutting** (6 skills):
`/akira` (interactive quality scanner — 4 modes: scan, wander, dao, all),
`/sanyi` (change contracts), `/skill-creator` (skill CRUD + eval),
`/mcp-builder` (build MCP servers — Python FastMCP or Node SDK; vendored from
Anthropic, includes `scripts/evaluation.py`), `/github-projects` (Projects V2
GraphQL templates — consumed by other skills, not usually invoked directly).

Native Claude skills (always available, no local copy): `/simplify`, `/claude-api`,
`/claude-in-chrome`, `/keybindings-help`, `/loop`.

### Refs (read on demand, not always-on)

Stack/tool conventions live in `~/.claude/refs/` (python, typescript, sql, logging, ml,
langgraph, google-adk, adk-vercel, insights-analysis).
They are NOT auto-loaded. Each repo's `CLAUDE.md` carries a `Refs:` line naming which
apply — **read those refs before writing code in that repo**. If a repo has no `Refs:`
line, infer from the stack and propose adding the line.

Runbooks: `repo-security-setup.md` (Dependabot, branch protection).

### Rules (always-on)

`~/.claude/rules/`: `docs.md` (doc-writer boundary), `shell.md` (zsh gotchas),
`context-health.md` (compact proactively). On-demand: `naming.md` (role-based
directory/layer convention); enforced by akira-scan, rides `/code-review` and `/akira`.

### Review ladder

`make precommit`/`make test` (zero tokens) → `/code-review level:1` (diff+lint) →
`level:2` (+tests+akira) → `level:3` (+full sanyi). Sweep BEFORE commit;
`/workflow-review` for plan-fidelity; `/code-pr` after a PR opens. `/akira` is
`/code-review`'s interactive sibling (same scan + wander questions + test-gated dao
fixes). `make review*`/`make akira` targets print the slash command — never auto-run.

### Model pairing

Haiku for fan-out/extraction, sonnet for bounded execution, opus for `/workflow-plan`,
`/workflow-retro`, `/sanyi audit`, `/synthesize`, and anything verdict-shaped. Full
table: `~/.claude/refs/models.md`.

### Session hygiene

One work item per session; the plan doc is continuity. Phase gates = session boundaries:
`/workflow-plan` in opus → `/workflow-execute` in FRESH sonnet pointed at the plan doc.
`/clear` when switching repos. Meta sessions dispatch via 3-line spawn prompts.

## Config Layering — global is canonical

`~/.claude` is the single source of truth for generic workflow assets (19 skills + guard
hooks). The phase pipeline: `/workflow-research` → `/workflow-plan` → `/workflow-execute`
→ `/workflow-review` → `/workflow-retro`.

- **Never copy global skills/hooks/commands into a repo's `.claude/`** — global loads in every session.
  Copies go stale and hooks fire twice.
- **Exception — template payload, not config**: `ai-project-template/template/.claude/`
  is *rendered output*, not a config dir that loads in my sessions. Scaffolded projects
  have no access to `~/.claude`, so the template must vendor skills. That copy is
  one-way reservoir→template via `scripts/sync-global-skills.sh` (canon is still
  `~/.claude/skills/`; never edit the vendored copy). Renaming a global skill means
  updating that script's `SKILLS[]` — it hard-fails on unknown names since 2026-07-19.
- Repo `.claude/` holds **repo-specific things only**: project hooks (lint/test/coverage), project skills,
  and settings that don't duplicate a global hook. Repos keep their own `hooks/lib.sh` (project hooks source it).
- To improve a generic skill/hook, edit it in `~/.claude` — not a repo copy.
- `~/workspace/.claude` is a symlink to `~/.claude`, not a separate config.
- Doc-writer boundary (who writes machine- vs human-consumed docs, plan `Status:` lines,
  skill placement rule): `~/.claude/rules/docs.md`. Tooling changes get a row in
  `~/workspace/guacamayo/.claude/docs/tooling-ledger.md` (verified by `/retro`; drift caught by
  `/config-audit`). Cross-repo project state lives in `guacamayo/.claude/docs/state/` — global
  `~/.claude/docs/` is deliberately deleted; do not recreate it.

## Issue Tracking — Linear ↔ GitHub closed loop

MCPs: `github` + `linear` (configured in `~/.claude/.mcp.json` — add tokens before use).

**My role as operator**: create Linear issues from plans, generate branch names, open PRs, keep IDs in sync.

### Conventions (required for auto-linking)

| Artifact | Format | Example |
|----------|--------|---------|
| Branch | `feature/lin-{id}-{slug}` | `feature/lin-12-add-auth` |
| Commit | `{type}: {desc} (LIN-{id})` | `feat: add auth (LIN-12)` |
| PR title | `LIN-{id} {description}` | `LIN-12 Add auth` |

### Workflow

1. `/plan` → I create a Linear issue, output issue ID
2. `git checkout -b feature/lin-{id}-{slug}`
3. Commits always include `(LIN-{id})` — **user commits, not Claude**
4. `/review` → I open PR titled `LIN-{id} ...` → Linear auto-closes on merge

**Claude never commits or pushes.** Stage changes and commit yourself. Linear tracking is optional — use it for repos that have Linear set up; skip for DSSG and other projects that don't.
