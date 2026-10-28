---
title: Auditable Track Router
tags: [llm, pattern]
summary: "Route a pipeline run to a protocol (ml vs agent) with a resolved record of source, confidence and reason; precedence is declared > repo doc > file signals > default, ambiguity is settled by a stated tie-break, low confidence abstains rather than guesses, and the result is written into the plan as a Track: line."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/specs/track-routing.md
  - data/raw/claude-docs/galactus/skills/archived/design-prototype/ARCHIVED.md
  - data/raw/claude-docs/galactus/skills/archived/design-prototype/SKILL.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-track-routing.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-track-routing.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-14-context-engineering-space.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-14-context-engineering-space.md
---

# Auditable Track Router

A prototyping pipeline whose phases behave differently for ML work (data frames,
temporal splits, sufficiency guards) and agent work (tool schemas, eval traces) needs to
decide which it is looking at. The track-routing spec treats that decision as a thing to
*record*, not just compute.

## The resolved record

```python
@dataclass
class TrackResolution:
    track: Literal["ml", "agent"]
    source: Literal["declared", "repo-doc", "files", "default"]
    confidence: Literal["high", "medium", "low"]
    reason: str          # human-readable, always present
```

Precedence is fixed and short: an explicit **declaration** (flag or plan `Track:` line)
wins; then a **repo doc** that names the track; then **file signals** (frame manifests,
`sklearn`/`torch` imports vs tool-schema files); then the **default**. Whatever won, the
`reason` names the evidence, so a reviewer reading the plan can disagree with the router
on the record rather than discovering the wrong protocol ran after the fact.

## Tie-break and abstention are decisions, not heuristics

When file signals are mixed (an agent that fits a model), **ml wins** — stated once in the
spec, with the reason that ML protocols carry the stricter guards and a false "agent" route
skips them silently. Archived `design-prototype` had already argued the asymmetry: *fitting
a model is the tell; calling a model is not.*

When confidence is `low`, the router **abstains** and asks, rather than defaulting with a
shrug. A default that is never surfaced is a decision wearing a heuristic's clothes — the
same move as [[Deferred Decision Status]] and [[Profile Then Select]]'s named-source rule.

## Writing it down: the `Track:` line

The resolution is persisted as a `Track: ml` line in the plan doc's header, next to
`Status:` (see [[Plan-Doc Status Enum]]). Later phases read the line instead of
re-deriving the track, so a run cannot change protocol halfway because a new file appeared.

## Thin orchestrators over `<phase>-<track>` skills

Each phase skill becomes a router plus a dispatch: `/proto-research` resolves the track
and loads `proto-research-ml` or `proto-research-agent`. The orchestrator owns `Status:`
and the plan doc; the protocol skill owns the method. A third `general` track was
considered and rejected — it would be the place every unroutable run landed, and a
protocol with no commitments enforces nothing. See [[Capability vs Phase Skills]].

## Building it: router first, honest abstention, protocol loading (galactus increment)

The build plan split the router from the phase work at the readiness gate, and recorded
several decisions worth reusing:

- **A router that quietly defaults is worse than no router**, because callers cannot tell
  inference from a coin flip. Abstention is enforced by the **return shape** (`track` is
  `None` at low confidence; a fallback exists only under an explicitly named
  `default_track`) plus a fixture-wide sweep asserting the invariant — not by a sentence in a
  downstream skill.
- **Prove the router against the real corpus before any caller exists** — hand-label the
  existing plan docs, add synthetic fixtures only for branches real docs won't supply
  (both-signals tie-break, zero-signal, declared override).
- **One vocabulary for "ML code."** Doc-text patterns reuse the existing import-pattern lists
  and are restricted to prose with no import equivalent, or the file grows a second
  definition.
- **The increment does not claim the programme's credit.** Shipping the router leaves the
  ML skills exactly as orphaned as before; the plan says so.
- **Load a protocol by `Read`, not by agent, frontmatter or `Skill` tool.** A protocol needs
  neither isolation nor parallelism, so it is reference material, not an agent. Declaring
  both tracks in `skills:` frontmatter loads both every time (the cost routing avoids);
  granting the `Skill` tool lets the orchestrator invoke *any* skill to read one file.
- **Model-uninvocable targets change "unorphaning."** The ML skills were
  `disable-model-invocation: true`, so a protocol can only *name them as ordered steps in the
  emitted plan* — a documentation edge, not a call edge — and verification greps the plan.
- **Evidence gate on speculative modules.** A follow-on step adding `execute-<track>`
  protocols must name ≥3 concrete track-specific behaviours absent from the orchestrator, or
  its deliverable is a written decision *not* to add them — the step can succeed by
  producing nothing.

## See Also
- [[Capability vs Phase Skills]] — extends
- [[Plan-Doc Status Enum]] — extends (adds `Track:` beside `Status:`)
- [[Deferred Decision Status]] — alternative-to (abstain-and-ask vs record-and-defer)
- [[Deterministic Signal Detection for Dispatch]] — instance-of (file signals as deterministic routing input)
- [[Profile Then Select]] — extends (named source over silent default)
