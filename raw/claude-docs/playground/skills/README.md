# Skills Guide

This directory holds the command-style workflows used in this repo.

## Quick map

| Skill | Use when | What it does | Hook automation? |
|---|---|---|---|
| `research-review` | You need to understand a codebase area, bug, or comparison | Writes a research artifact with evidence, gaps, and recommendations | No |
| `plan-review` | You need an implementation plan from research | Writes or refines a step-by-step plan | No |
| `execute-plan` | A plan is approved and ready to build | Implements one plan step at a time and records progress | Partial |
| `code-review` | Implementation is complete and needs review | Reviews diff against the plan and writes the review artifact | Partial |
| `plan-refactor` | You want an opportunistic quality refactor | Proposes improvements, then applies them one at a time | Partial |
| `code-debug` | You have a specific traceback or failing test | Focused diagnose/fix/verify loop | No |
| `design-sprint` | Starting a new product or platform initiative | Produces a structured sprint backlog | No |
| `scope-initiative` | An initiative is already named and agreed on | Produces a Linear-ready backlog and hierarchy | No |
| `quick-commit` | You want a branch + commit only | Creates a feature branch and commits safely | Partial |
| `quick-pr` | You want commit + push + PR flow | Handles staging, commit, push, PR creation, optional merge | Partial |
| `claude-insights` | You want workflow signals from session logs | Summarizes friction patterns, attribution, and skill candidates | No |
| `compact-session` | Mid-session or end of session | Saves artifacts, writes session note, commits + pushes + PR; mid-session also compacts context | No |

## Stale assumptions to watch

- `CHANGELOG.md` should be treated as optional unless a workflow explicitly uses it.
- Compact reminders are a single workflow hint, not a repeated instruction everywhere.
- Hooks should own enforcement; skills should describe intent and manual steps.
