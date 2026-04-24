# Global Claude Code Instructions

## Developer Identity

Python/AI engineer building LLM-powered applications. Comfortable with async Python,
LLM orchestration (LangGraph), Polars, DuckDB, structlog. Skip basics unless asked.

## Communication

- Brief and direct. Lead with the action.
- No filler, no trailing summaries of what you just did.
- File:line references over prose descriptions.
- Don't add unsolicited comments, docstrings, or refactors to code I didn't ask to change.
- When I correct a mistake, update the appropriate CLAUDE.md level — ask if unclear.

## Tooling

- Package manager: **uv** — never pip or poetry
- Pydantic v2, ruff, pytest

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
3. Commits always include `(LIN-{id})`
4. `/review` → I open PR titled `LIN-{id} ...` → Linear auto-closes on merge

