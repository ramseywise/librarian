---
title: Capability vs Phase Skills
tags: [meta, pattern]
summary: "Phase skills are positional (research → plan → execute → review), write to the plan doc and advance Status:; capability skills are situational, write their own artifact under decisions/, and never advance Status: — enforced structurally because the status hook only watches the plans tree."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/skills/decide-shared/SKILL.md
  - data/raw/claude-docs/galactus/skills/assumption-audit/SKILL.md
  - data/raw/claude-docs/galactus/skills/fog/SKILL.md
  - data/raw/claude-docs/galactus/docs/specs/track-routing.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-context-engineering-space.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-context-engineering-space.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-orchestrator-design.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-orchestrator-design.md
---

# Capability vs Phase Skills

`decide-shared` — "the `review-shared` of the decide family" — draws the line that keeps a
prototyping pipeline's state machine honest.

| | Phase skill | Capability skill |
|---|---|---|
| Position | Positional — passes the true-dependency test (execute genuinely needs plan's output) | Situational — callable at any point, on any artifact |
| Examples | `/proto-research`, `/proto-plan`, `/proto-execute`, `/proto-review` | `/assumption-audit`, `/war-game`, `/fog` |
| Writes to | the plan doc | its own artifact in `.claude/docs/decisions/`, or chat |
| `Status:` | advances it | **never** touches it |
| Emits | the next phase's input | claims per [[Two-Axis Claim Schema]] |

## Why the separation is structural, not a rule

The plan-doc status hook (`plan_status_validate.sh`) scopes to `.claude/docs/plans/*.md`.
Capability skills write to a different tree, so they *cannot* advance `Status:` even by
accident — the enforcement is in where the file lands, not in a sentence asking the
skill to behave. This is the same move as [[Plan-Doc Status Enum]]'s forbid-and-relocate
policy: make the illegal state unrepresentable rather than discouraged.

The practical consequence: running `/fog` on a plan at `Status: IN_PROGRESS` leaves it at
`IN_PROGRESS`. A human reads the fog report and decides; the pipeline does not move
because an analysis happened.

## Shared contract for capability skills

- **Report, never edit** the target — the human owns the decision.
- **Claims per schema**, ranked impact-major / confidence-minor.
- **Name the blind spot** — every report ends with what it could not see.
- **No domain content** — the shared skill carries method only; no market, profit or
  board material leaks into the contract.
- **Exactly one job verb** — see [[Job Verb Taxonomy for Skills]].
- **Skills orchestrate agents, never the reverse.** An agent may *preload* a shared
  contract (loading is not calling), but an agent that dispatches a skill collapses the
  isolation that made it an agent — see [[When a Lens Earns Agenthood]] and
  [[Skill Preloading via Agent Definition]].

## Thin orchestrators over protocol skills

The track-routing spec extends the same shape to phase skills themselves: a phase becomes
a thin orchestrator that detects the track and loads a `<phase>-<track>` protocol skill
(`proto-research-ml`, `proto-research-agent`) — the pattern `/proto-review` already uses
over its `review-*` dimension skills. The orchestrator owns `Status:`; the protocol skill
owns the method. See [[Auditable Track Router]].

## Invocation model: who may reach for a capability (galactus wiring)

The context-engineering pass that wired galactus's four bands (FRAME, BUILD, REVIEW, CROSS)
added three rules about capabilities:

- **`disable-model-invocation` is a deliberate choice, not a default.** It belongs on skills
  that spend real effort or write artifacts (all of FRAME and BUILD). It does *not* belong
  on CROSS skills (`fog`, `war-game`, `assumption-audit`): they are cheap, read-only, and
  exactly what the model should reach for the moment it notices a load-bearing assumption —
  which is not a schedulable moment. Dropping the flag was the one change that turned three
  skills from unreachable to useful.
- **No position is not no scheduled call sites.** CROSS stays callable from anywhere *and*
  gets two default call sites: the readiness gate (assumption-audit, fog — where an untested
  assumption is most expensive) and post-implementation review (war-game — the artifact now
  exists to test against). Both are **risk-gated**: "a gate that dispatches an advisor on
  every trivial plan trains people to ignore the advisor."
- **One generic agent per contract family** — `review` + `review-shared`, `fog-advisor` +
  `decide-shared`. Per-dimension agents are the previous generation.

A capability has no node in a graph, by construction — giving it a slot in a sequence would
remove the property that makes it useful (see [[Decision-Seat Inventory for a Control Plane]]).

## See Also
- [[Plan-Doc Status Enum]] — extends (the enum these skills may or may not advance)
- [[Job Verb Taxonomy for Skills]] — extends
- [[When a Lens Earns Agenthood]] — extends
- [[Two-Axis Claim Schema]] — extends (the capability-skill output contract)
- [[Auditable Track Router]] — extends (phases as thin orchestrators)
- [[Claude Workflow System]] — instance-of
- [[Skill Preloading via Agent Definition]] — extends (preloading vs calling)
- [[Skill Admission Test: Workflow With a Gate]] — prerequisite-for (decides whether something is a skill at all)
- [[Decision-Seat Inventory for a Control Plane]] — extends (capabilities have no seat in the sequence)
