---
title: Agile Workflow Definitions
tags: [llm, pattern]
summary: Definition of Ready, Definition of Done, WIP limits, weekly cadence, and ceremony-to-skill mapping for the Claude Code workflow system.
updated: 2026-08-03
sources:
  - raw/claude-docs/_user/rules/agile.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/references/definition-of-done.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/references/interview-mode.md
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

## DoD as a review-time assessment

The DoD above is authored per-repo and checked at ship time. A reviewing agent faces the
inverse problem — arriving at an unfamiliar repo and needing *some* DoD to assess against.
Parallax resolves this with an explicit precedence chain rather than a fixed list:

```text
Repository-specific DoD  (a CONTRIBUTING.md section, a PR template checklist)
→ Team/project DoD
→ Skill default
```

A repository-specific DoD "always wins over this file's defaults," and the reviewer is
instructed to look for one before falling back. The default it falls back to is
dimension-shaped rather than process-shaped — intended behavior complete, important edge
cases handled, tests sufficient, evaluation sufficient, documentation updated,
observability present, migration handled, rollout understood, rollback understood,
security reviewed, handoff complete, limitations recorded.

The two lists differ because they answer different questions: this page's DoD asks *did
our process run*, the fallback asks *is this change actually finished*. Note that "tooling
ledger row added" would be invisible to a generic reviewer — which is exactly why
repository-specific DoD takes precedence over any default.

## Interview mode — review as an explainable artifact

Parallax can render a review as a walkthrough instead of a finding list: a 60-second
summary, how the review was approached, what the PR does well, the top three concerns
(each with observation, scenario, impact, recommendation, validation, and blocking
status), clarifying questions, alternative designs and trade-offs, testing strategy, how
new constraints would change the decision, and a final merge recommendation.

Only the orchestrator assembles it, "it needs every subagent's findings to pick the top
three concerns" — an individual dimension contributes candidate concerns, never the
assembled document. Selecting the top three is a cross-dimension judgment, the same reason
merge synthesis sits with the orchestrator in
[[Parallel Dimension Scanner Architecture]].

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
- [[Parallel Dimension Scanner Architecture]] — extends (DoD assessed per review dimension)
- [[Evidence Classification Model]] — extends (how review findings against DoD are qualified)
