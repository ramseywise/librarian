---
description: "Map the full phased workflow; start from a chosen phase with human gates between artifacts."
---

# Workflow — full pipeline

## Phases (in order)

| Phase | Command | Artifact | Gate |
|-------|---------|----------|------|
| 1. Research | `/research <slug>` | `## Research` in `.claude/docs/plans/YYYY-MM-DD-<slug>.md` | Human reviews before continuing |
| 2. Plan | `/plan <slug>` | `## Plan` in the same doc | Human reviews before continuing |
| 2.5. Plan Review | `/plan review` | plan section (iterated) | Blockers resolved, questions answered |
| — | `/compact` | — | **Run before execute** |
| 3. Execute | `/execute` | `CHANGELOG.md` | Human confirms each step |
| 4. Review | `/code-review <slug>` | `## Review` in the same doc | Verdict: go / no-go |

One doc per work item: `.claude/docs/plans/YYYY-MM-DD-<slug>.md` with a `Status:` line (PLANNED / IN PROGRESS / EXECUTED). No SESSION.md — `grep -l 'Status: IN PROGRESS' .claude/docs/plans/*.md` finds the active doc.

**Plan updates anytime:** `/plan review` re-runs the review and patches the active plan.

Ad-hoc (skip pipeline): `/code-debug`, `/code-review`, `/plan-refactor`.

## On invoke

1. If the user asked to **run the full workflow**: run only the first applicable phase. Do not auto-chain — gates matter.
2. If the user named a **specific phase** (e.g. "just plan"): run that phase only.
3. If unclear: show the table above and ask.

## All commands run in current context

Do not spawn subagents or use the Agent/Skill tools for any pipeline phase. Run research, plan, plan-review, and execute directly in the main conversation using Read, Write, Grep, Glob, Bash, and WebSearch tools.
