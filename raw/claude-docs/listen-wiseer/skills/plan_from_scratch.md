---
name: plan_from_scratch
description: "Lightweight planning for small tasks that don't need a full research phase. Loaded by the plan agent when no RESEARCH.md exists and the task is clearly scoped."
---

Use this skill when `/plan` is invoked but no RESEARCH.md exists and the task is small and well-defined. Not every task justifies the full research→plan pipeline.

## Qualifying criteria

A task qualifies for plan-from-scratch if ALL of these are true:

1. **Small scope** — will result in a 1-3 step plan (single module or function)
2. **Well-understood** — the user described what they want clearly enough to plan without research
3. **Low risk** — no data migrations, no API contract changes, no shared schema changes
4. **Familiar territory** — the codebase area is established (existing patterns to follow)

If ANY of these are false, tell the user: "This task would benefit from `/research` first — want me to run that?"

## What to do instead of reading RESEARCH.md

1. Read the target files directly — the same files the plan will reference
2. Identify the existing pattern to follow (use `research_codebase` Phase 3 approach — find 1-2 examples of the same kind of change)
3. Note the pattern briefly in the Approach section of PLAN.md

## PLAN.md adjustments

- `Based on: RESEARCH.md` → `Based on: direct codebase inspection`
- Keep the same template — all fields still required (files, what, snippet, test, done when)
- Risk section can be shorter but still required — even small changes can have rollback needs
- Out of Scope section is especially important — small tasks tend to grow

## Guardrails

- If during planning you discover the task is bigger than expected (>3 steps, unclear dependencies, needs technology comparison): stop and recommend `/research`
- If you find yourself reading >5 files to understand the context: that's research — stop and recommend `/research`
- Do not skip `plan_check` — even small plans get the 7-dimension verification
