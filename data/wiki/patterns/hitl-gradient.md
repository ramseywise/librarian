---
title: HITL Gradient
tags: [eval, langgraph, pattern]
summary: "Measure where human involvement stops paying by running the same target at four fixed levels (full control, ask all, ask vital, automated) instead of comparing 'human' with 'unattended'. The level where quality drops is the answer. Each divergence between levels routes to one of three fixes: the template, the seat table, or a preference record."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-gal-23-hitl-gradient.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-gal-23-hitl-gradient.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-15-gal-23-proto-pipeline-dry-run.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-15-gal-23-proto-pipeline-dry-run.md
---

# HITL Gradient

From galactus, measuring an agent-driven prototyping pipeline before automating it. The
first plan framed the experiment as two modes: an attended run (HITL) and an unattended
run. A readiness gate rejected it, and the successor gave two reasons:

1. **Both "modes" had a human in them.** The real variable was *how deeply the human
   interrogated*, not whether a human was present.
2. **The pipeline was not a sequential chain.** It was orchestrated from the scope
   document, so a "where does the chain break" framing modelled the wrong shape.

The fix treats involvement as a **parameter, not a binary**. Then the boundary between
"ask the human" and "show the human" becomes something you observe, not something you
decide: *the level at which quality drops is the answer.*

## The four levels

| Level | Human occupies | Needs a dispatcher? |
|---|---|---|
| **L1 — full control** | every seat; every step interrogated | no |
| **L2 — ask all** | every question raised, nothing volunteered | no |
| **L3 — ask vital** | only the seats the design doc marks permanent | no |
| **L4 — automated** | nothing automatable | yes |

**L3's seat set is cited from the control-plane design's seat table, not restated.** That
makes L3 a test of the table. A failure at L3 on a seat the table marked as ready to hand
over is **a finding against the design doc**, not against the run (see
[[Decision-Seat Inventory for a Control Plane]]). Because the seats are cited rather than
copied, a later change to the table carries through automatically.

If budget is limited, run **L1 and L3**: they give the widest gap that still tells you
something. L1 through L3 need no automation, so they can run before the dispatcher is
built. L4 waits for it, and that dependency was split into a separate work item so the
comparison arm is not built by the work it evaluates.

## Fixed level per run

Escalating mid-run is more realistic, but a run that escalated sits cleanly at no level,
and the comparison loses its meaning. So the default is **one level per run**, deferred
with a trigger ("revisit after the first two runs"). The transition ledger records each
run's path independently of what the operator reports, which guards against an L3
operator who interrogates out of habit.

## Divergence routing

When two levels disagree, exactly one of three things is true, and each routes somewhere
different:

| Divergence | Means | Routes to |
|---|---|---|
| Lower level produced a worse artifact | the template does not carry what the human supplied | a template or skill fix |
| Lower level made a call the human would have made differently | a seat was handed over too early | the seat table: a finding against the design |
| Human stated a preference no artifact records | the preference is unencoded | a preference record; candidate for a skill default |

This routing is the feedback loop. Without it, a gap between levels is just a score.

## Pre-registration and the trail

- The level definitions and the evidence rule are written **before any run**. That is
  what makes them commitments rather than description.
- Each terminal state must be classified from evidence the agent did not author, with
  *undetermined* as a valid outcome (see [[Reproduce to Tell a Break From a Stuck Agent]]).
- The per-run trail lives in one place. The plan holds **a pointer, not a copy**. An
  earlier version duplicated the finding rows in both documents, and the "no duplicated
  text" done-condition was satisfied by a `grep` for the pointer while the duplication
  still existed.
- **An expected null is scoped to the named breaks, not the class.** Both known breaks
  were fixed, so a quiet run was a legitimate pre-registered outcome. But two more cases
  of the same failure class (see [[Audit-Don't-Assert Release Checklist]]) turned up by
  inspection alone during the research. The honest pre-registration reads: "null for the
  two named breaks; open for the class."
- A run that contributes data points toward a separate threshold (here, "build a graph
  orchestrator if loop-backs per run ≥ ~0.5 over ≥ 5 runs") must not reach that verdict
  early. This phase supplies at most four runs.

## See Also
- [[Decision-Seat Inventory for a Control Plane]] — extends (the gradient tests the seat table empirically)
- [[Reproduce to Tell a Break From a Stuck Agent]] — prerequisite-for (the terminal-state evidence rule every level obeys)
- [[Warranted vs Executed Escalation]] — extends
- [[Hoist Irreversible Decisions to the Attended Band]] — extends (what the human must still decide when involvement is low)
- [[Falsifiable Hypothesis Gate]] — extends (pre-registered levels and bets)
- [[Server-Derived Autonomy Tier]] — alternative-to (tiers as an enforced runtime contract rather than a measurement parameter)
