---
imported_hash: 871785fb0734cb02
title: PLANS.md
summary: This file defines how execution plans are created, updated, completed, and archived.
order: 34
kind: reading
section: Templates / Openai repo template / Docs
source: learn-ai-engineering/ai-engineering/03-harness/templates/openai-repo-template/docs/PLANS.md
---

# PLANS.md

This file defines how execution plans are created, updated, completed, and
archived.

## When A Plan Is Required

Create an execution plan when work:

- spans more than one session
- changes more than one subsystem
- has non-trivial verification or rollout risk
- depends on open decisions that should be logged

## Plan Locations

- `docs/exec-plans/active/`: plans currently driving work
- `docs/exec-plans/completed/`: finished plans kept for future agent context
- `docs/exec-plans/tech-debt-tracker.md`: deferred work and follow-ups

## Minimum Plan Sections

- objective
- scope and out-of-scope
- verification path
- risks and blockers
- progress log
- open decisions

## Operating Rules

- One active plan should have one clearly owned current step.
- Update the plan as work progresses; do not treat it as static prose.
- If a decision changes implementation direction, record it in the plan.
- Move finished plans to `completed/` so agents can still discover prior context.
