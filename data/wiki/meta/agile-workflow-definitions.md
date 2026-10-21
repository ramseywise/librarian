---
title: Agile Workflow Definitions
tags: [llm, pattern]
summary: Definition of Ready, Definition of Done, WIP limits, weekly cadence, and ceremony-to-skill mapping for the Claude Code workflow system.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/skills/workflow-refine/SKILL.md
  - raw/claude-docs/_user/rules/agile.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/references/definition-of-done.md
  - data/raw/claude-docs/Parallax/skills/parallax-shared/references/interview-mode.md
  - data/raw/claude-docs/guacamayo/skills/workflow-refine/SKILL.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-20-agile-workflow-system.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-20-agile-workflow-system.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-28-GUA-42-auto-label-hook.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-28-GUA-42-auto-label-hook.md
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

## Why a board at all: retro output had no destination

The agile layer was added because a retro produced 10 findings across 8 threads with
nowhere to put them. The output was too large to act on and **evaporated when the
transcript scrolled**. The global CLAUDE.md pointed at a backlog file that did not
exist. Plan docs had four statuses with no BLOCKED and no refinement stage, so an idea
and a fully scoped ticket looked the same. With no cadence forcing a re-check, half the
tooling ledger stayed at `hypothesis` indefinitely.

The decision split ownership by kind of content: **issues hold state, markdown holds
thinking.** Issues carry ticket state, labels and the cross-repo view. A plan doc
carries research, plan and review, but never authoritative state. An inbox file holds
ideas that have not earned a ticket. The first run routed every retro finding by tag:
*stop* and *just do* were applied that session, *keep* graduated to `verified` in the
ledger, and *improve* became six backlog issues. Several of those issues became their
own design pages ([[Pipeline-Absorbed Skills]], [[Config Reference Rot]],
[[Harness Events Are Not Task Failures]]).


## Skill invocations drive label transitions

Labels went stale because transitions were manual: a fleet dispatch ran 14 agents across 7
repos without updating a single label. The workflow skills already *are* the state
machine, so a hook enforces it. A PostToolUse hook on the `Skill` tool does the following:

1. Maps the skill to a transition: plan moves `backlog → refinement`, refine (pass) moves
   `refinement → ready`, execute moves `in-progress → in-review`.
2. Parses the branch for `PREFIX-NUM-`, with a prefix → repo table.
3. Checks the current labels first, so the edit is idempotent.
4. Calls `gh issue edit`.

Design constraints:

- **Advisory sync, never blocking.** Every `gh` failure is caught and logged, and the hook
  still exits 0.
- **Graceful skips.** No branch, `bug/`/`spike/` branches, or an unknown prefix make the
  hook a no-op.
- **PostToolUse cannot see "start".** The `ready → in-progress` transition would need a
  PreToolUse hook, so the MVP only records completion.
- `closed` stays native to the platform via the PR merge.

## See Also
- [[Claude Workflow System]] — extends
- [[Branch Naming Convention Pattern]] — prerequisite-for
- [[Specification by Example]] — extends (requirement-as-example, sharpens DoR)
- [[TDD as Coding-Agent Harness]] — extends (test authored before agent implements)
- [[Plan-Doc Status Enum]] — extends (state vocabulary behind DoR/DoD gates)
- [[Parallel Dimension Scanner Architecture]] — extends (DoD assessed per review dimension)
- [[Evidence Classification Model]] — extends (how review findings against DoD are qualified)
- [[Chain Length Beats Point Total in Sprint Planning]] — extends (sprint feasibility beyond point totals)
- [[Retro Open-Hypotheses Loop]] — extends (the retro whose findings now land as issues)
- [[Exposure-Tiered Dependency Triage]] — related (unplanned dependency work that the DoD did not cover)
