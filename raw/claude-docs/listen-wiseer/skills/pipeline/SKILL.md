---
description: "Map the full phased workflow; start from a chosen phase with human gates between artifacts."
---

# Workflow — full pipeline

## Phases (in order)

| Phase | Command | Artifact | Gate |
|-------|---------|----------|------|
| 1. Research | `/research <name>` | `.claude/docs/research/<name>.md` | Human reviews before continuing |
| 2. Plan | `/plan <name>` | `.claude/docs/plans/<name>.md` | Human reviews before continuing |
| 2.5. Plan Review | `/plan-review` | plan file (iterated) | Blockers resolved, questions answered |
| — | `/compact` | — | **Run before execute** |
| 3. Execute | `/execute` | `CHANGELOG.md` | Human confirms each step |
| 4. Review | `/review <name>` | `.claude/docs/reviews/<name>.md` | Verdict: go / no-go |

All phase artifacts live in `.claude/docs/` subdirectories. `SESSION.md` tracks the active plan and research files under `## Active docs`.

**Plan updates anytime:** `/plan-review` re-runs the review and patches the active plan.

Ad-hoc (skip pipeline): `/debug`, `/code_review`, `/refactor`.

## On invoke

1. If the user asked to **run the full workflow**: run only the first applicable phase. Do not auto-chain — gates matter.
2. If the user named a **specific phase** (e.g. "just plan"): run that phase only.
3. If unclear: show the table above and ask.

## All commands run in current context

Do not spawn subagents or use the Agent/Skill tools for any pipeline phase. Run research, plan, plan-review, and execute directly in the main conversation using Read, Write, Grep, Glob, Bash, and WebSearch tools.
