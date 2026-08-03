---
title: Agile Workflow Definitions
tags: [llm, pattern]
summary: Definition of Ready, Definition of Done, WIP limits, weekly cadence, and ceremony-to-skill mapping for the Claude Code workflow system.
updated: 2026-07-22
sources:
  - raw/claude-docs/_user/rules/agile.md
---

# Agile Workflow Definitions

Process definitions for the [[Claude Workflow System]]. Operational conventions (branch naming, commit format, PR body, strict gates) live in `~/.claude/refs/agile.md` — this page covers the process knowledge those conventions serve.

## Definition of Ready

A ticket may be labeled `ready` when ALL hold:

1. Problem stated in one sentence (observed friction, not solution)
2. Acceptance criteria — checkable by someone who didn't scope it
3. Enforcement level chosen (hook > skill > rules > MEMORY.md)
4. Metric named (`absence:` / `count-drop:` / `presence:` / `ratio:`) for tooling changes
5. Sized to one session, or split
6. Dependencies named, none unresolved-blocking

Failing DoR after two refinement passes → back to `backlog` or close.

## Definition of Done

1. Acceptance criteria met — verified by running, not by inspection
2. Tests pass (`make lint` / `make test`)
3. On a named branch (never main) — human committed (Claude never commits)
4. PR merged, or N/A for local-only tooling
5. Tooling ledger row added (`hypothesis` + metric) for tooling changes
6. Plan doc `Status:` updated to `EXECUTED`

A tooling change is not Done when merged — it is Done when the ledger row exists.

## WIP Limit

Three `in-progress` across all repos. One active, one blocked, one in review.

## Cadence

Weekly boundary (not a sprint):
- `/workflow-insights` → `/workflow-retro`
- `hypothesis` rows older than 2 weeks get a verdict or explicit extension
- Backlog reordered
- Cycle time read from issue creation → close

## Ceremony → Skill Mapping

| Ceremony | Skill | Writes |
|---|---|---|
| Groom | akira wander, manual, `/workflow-retro` findings | issue (labeled `backlog`) |
| Research | `/workflow-research` (if needed) | research artifact in plan doc |
| Plan | `/workflow-plan` | plan doc with steps |
| Refine | `/workflow-refine` — DoR gate | label `ready` |
| Execute | `/workflow-execute` | code + plan doc |
| Review | `/code-review`, `/workflow-review` | label `in-review` |
| Ship | `make lint` → `make test` → `make push` → `make ship` | PR + merge |
| Retro | `/workflow-retro` | findings → issues (stop/improve) or ledger (keep) |

## See Also
- [[Claude Workflow System]] — extends
- [[Branch Naming Convention Pattern]] — prerequisite-for
- [[Specification by Example]] — extends (requirement-as-example, sharpens DoR)
- [[TDD as Coding-Agent Harness]] — extends (test authored before agent implements)
- [[Plan-Doc Status Enum]] — extends (state vocabulary behind DoR/DoD gates)
