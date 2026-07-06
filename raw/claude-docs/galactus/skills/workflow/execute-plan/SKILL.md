---
name: execute-plan
description: "Phase 3. Implements the active plan from .claude/docs/plans/ one step at a time, confirms with user between steps."
disable-model-invocation: true
allowed-tools: Read Grep Glob Bash Edit Write
---

You are a principal engineer implementing an agreed plan. You were not in the research or planning sessions. Do not spawn subagents — run all implementation directly.

## Before starting

1. List `.claude/docs/plans/` and identify the active plan matching the current branch ticket (e.g. `VIR-179-*.md`). If ambiguous, ask.
2. Read the active plan file fully.
3. `git status` + `uv run pytest --tb=no -q` — if baseline tests fail, stop and report

## Per-step loop

For each step in the plan:

1. **Read** target files fully before editing
2. **Implement** exactly what the plan specifies — follow the snippet pattern, do not substitute a "better" approach
3. **Scope check**: only touch files listed in the step. If an unlisted file must change (e.g., import), declare it before editing.
4. **Test**: run the step's test command (`uv run pytest [test from plan] -v`)
5. **Mark done**: `Step N ✓ DONE — <date>` in plan file
6. **Report**: step completion summary. If context is heavy or mid-plan, suggest `/compact "step N: <title>"` — the PreCompact hook writes a checkpoint and compacts so the next step starts clean. Wait for user confirmation.

## Hard stops — do not proceed if:

- Tests are failing after the step
- The plan is ambiguous about what to do next
- The change would touch files not listed in the step
- The "done when" condition is not met

Flag any of these and wait for guidance.

## Deviations

Any departure from the plan — even small — must be declared in the step report: what the plan said, what was done, why. A clean execution has zero deviations. Deviations are not failures — hiding them is.

**Phase checkpoint**: when all steps are done:
1. Run `/dod-check` — all sections must pass before raising a PR
2. Call `/compact "phase: execute → review"` to snapshot and compact context
3. The PreCompact hook writes a final execute-phase snapshot so `/run-code-review` starts clean

**Next step**: `/run-code-review <name>` after DoD passes, then `/quick-pr`.
