---
title: Iterative Harness Simplification
tags: [llm, agents, infra, pattern]
summary: "Every harness component encodes an assumption about what the model can't do — when models improve those assumptions expire, so strip load-bearing components one at a time and re-run the eval."
updated: 2026-08-04
sources:
  - data/raw/repos/learn-ai-engineering/ai-engineering--03-harness--notes--08-maturity-and-failure-modes.md
---

# Iterative Harness Simplification

The counterweight to the ratchet in [[Harness Engineering]], and **the practice most teams
lack entirely**.

## Why Components Expire

> **Every component encodes an assumption about what the model can't do on its own.**

When models improve, those assumptions expire — **but the components remain**, adding cost,
latency, and constraint for no benefit. Worse, they can **actively suppress capability the
newer model has**.

Two documented cases: Opus 4.6's improvements allowed **removing sprint decomposition
entirely** while maintaining quality; context resets were needed for Sonnet 4.5 and largely
unnecessary for Opus 4.6 (see [[Long-Horizon Execution]]).

## The Method

**Strip load-bearing components one at a time and re-evaluate.** On every model upgrade:

1. **List components and the weakness each was built to mitigate.**
2. **Disable one; run the eval suite.**
3. **Quality holds → delete it. Quality drops → keep it, note the model version.**
4. **Repeat.**

Step 1 is the step teams skip, and it is the one that makes the rest possible — *a component
whose original justification nobody recorded cannot be evaluated for expiry.*

**This requires the binary eval** (failure mode 5 in
[[Harness Maturity and Failure Modes]]). Without it, subtraction is unmeasurable and nobody
dares — **which is exactly how harnesses calcify.**

## Two Triggers for Subtraction

**A component can be worth removing before any model upgrade.** One production system deleted
its LLM SQL-reviewer for false positives — *not because the model got better, but because the
component never paid for itself* (see [[Verification Loops]]).

> Subtraction has two triggers: **capability arrived**, or **the component was always a net
> negative**. The second is more common and less often checked.

## What Does *Not* Expire

The expiry is anticipated by practitioners, not just vendors — with an important limit:

> **Scaffolding that compensates for a *model weakness* expires; scaffolding that satisfies
> an *external constraint* does not.**

Explicit control over state, recovery, and verification stays essential wherever trust and
traceability are requirements. **Regulated domains don't get to delete the audit trail
because the model improved.**

## Complexity Shifts Rather Than Shrinks

Note the direction of travel. Removing anxiety-mitigation scaffolding **frees budget for
constraints on newly-unlocked failure modes** — a model that can now run twelve hours
unattended needs cost ceilings and rollback that a three-step agent never did.

The harness doesn't get smaller. **It gets re-aimed.**

## See Also
- [[Agent Deployment Anti-Patterns]] <!-- auto-linked -->
- [[Recursive Self-Improvement]] <!-- auto-linked -->
- [[Harness Maturity and Failure Modes]] — extends
- [[Harness Engineering]] — part-of
- [[Long-Horizon Execution]] — complements
- [[Verification Loops]] — complements
- [[Harness Anatomy]] — complements
- [[Evolve Loop]] — complements (both optimize within a frame and neither can interrogate the frame)
