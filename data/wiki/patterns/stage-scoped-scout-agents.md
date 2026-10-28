---
title: Stage-Scoped Scout Agents
tags: [patterns, llm, pattern]
summary: Sub-agents that execute exactly one pipeline stage per invocation (execute | review | fix; research | plan | refine), never skip forward, never commit or push, and stop on the first blocker — so the orchestrating skill, not the sub-agent, owns stage transitions.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/agents/plan-refine-scout.md
  - data/raw/claude-docs/playground/agents/build-scout.md
  - data/raw/claude-docs/guacamayo/agents/build-scout.md
  - data/raw/claude-docs/guacamayo/agents/plan-refine-scout.md
  - data/raw/claude-docs/guacamayo/skills/workflow-scope/SKILL.md
  - data/raw/claude-docs/guacamayo/skills/workflow-build/SKILL.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-dis126-ratify-dc2.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-dis126-ratify-dc2.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-20-build-orchestrator.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-20-build-orchestrator.md
  - data/raw/repos/nonprofit-success-ai/.claude--skills--workflow-triage--SKILL.md
  - data/raw/repos/nonprofit-success-ai/.claude--skills--workflow-build--SKILL.md
---

# Stage-Scoped Scout Agents

Two guacamayo agent definitions, `build-scout` and `plan-refine-scout`, share one design
rule: **one pipeline stage per invocation**. `build-scout` is dispatched by
`/workflow-build` with a stage argument of `execute`, `review`, or `fix`; `plan-refine-scout`
is dispatched by `/workflow-scope` with `research`, `plan`, or `refine`. The agent does
that stage's work, writes its artefact, reports, and exits.

## The constraints

- **Never skip to a later stage.** An execute-stage scout that notices a review-worthy
  problem reports it; it does not start reviewing. A research-stage scout does not draft
  the plan. Stage transitions are the orchestrator's decision because the orchestrator
  holds the gate criteria and the operator's approval.
- **Never commit or push.** Scouts edit files and leave the working tree for the
  orchestrator (and ultimately the operator) to inspect and commit. This keeps the git
  history a record of reviewed decisions rather than sub-agent side effects.
- **Blocker → report and stop.** A missing input, an ambiguous plan step, or a failing
  precondition ends the invocation with a structured blocker report. The scout does not
  guess past it, and does not retry with a different interpretation.
- **A relayed approval does not authorize a blocker fix.** In one akira fix round, the
  dispatch prompt said "the operator explicitly approved fixing the blocker". The fix-stage
  scout still left the `merge_impact: blocker` finding unapplied, because an approval relayed
  through another agent is never enough on its own. It applied the non-blocking suggestion,
  re-ran the gate, and reported the blocker for a human (or a re-dispatched round that
  reclassifies it). Authority for the riskiest edits has to arrive first-hand.

## Why not one agent that runs the whole pipeline

A sub-agent that runs execute→review→fix in one invocation reviews its own work with
the same context that produced it — the review stage inherits every assumption the
execute stage made. Splitting stages into separate invocations gives the review stage a
fresh context whose only input is the artefact, which is the property that makes
reviewing worth doing. It also keeps each invocation short enough that a blocker is cheap
to abandon.

The cost is orchestration overhead: the dispatching skill must carry state between
stages (which plan, which branch, what the previous stage reported). In this system that
state lives in the plan doc and the branch, which the next scout re-reads, rather than in
the orchestrator's context — the same "read the actual state first" discipline the
identity skills use.

## The orchestrator loop above the scouts

One-stage-per-invocation scouts need an orchestrator, or an issue stalls short of done —
observed when two triaged issues each stopped after `plan`. The scope orchestrator runs
research → plan → refine as sequential foreground subagents until the plan is READY, with
**one retry per stage, then the main model resolves** rather than looping. The build
orchestrator takes a READY plan through execute → review → fix for **at most 3 review
rounds**, logging one JSONL row per stage/round; exhausting rounds or an
`insufficient_context` verdict escalates instead of continuing. Retry rate is logged as
the quality signal — high retries mean bad routing or weak subagents.

## Control through the dispatch prompt (build orchestrator plan)

The build orchestrator's plan made one rule explicit: **no changes to the stage skills
it consumes.** It controls them only through the scout's prompt. The execute stage gets
"do not auto-dispatch review", and the review stage gets `Authorization: auto-post`,
which the review skill's existing "if authorized" branch already honoured. Three more
resolved choices. Blockers always escalate, and the fix stage gets only `important |
suggestion | nit` findings. The orchestrator assumes a branch and PR already exist, with
git setup left to the caller. And the per-stage scout was renamed from `triage` to
`plan-refine-scout`, so that "triage" names the orchestrator level, not an agent.

## See Also
- [[Claude Workflow System]] — instance-of (the build and scope pipelines these serve)
- [[REUSE/ADAPT/SKIP Asset Verdicts]] — extends (the sibling research scout's output contract)
- [[Corrective Follow-Up Dispatch]] — extends (the fix stage as a separately dispatched round)
- [[Plan-Insufficient Is Not Blocked]] — prerequisite-for (the stop outcome for an unsound plan)
- [[Multi-Step Graph Orchestration]] — instance-of
- [[Orchestrate Around the Human Gate]] — extends (the orchestrator layer above the scouts, including the meta loop's human gate)
