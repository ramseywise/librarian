---
title: Plan-Insufficient Is Not Blocked
tags: [eval, pattern]
summary: A build loop needs a terminal outcome that means "the plan is wrong", separate from "the code has a blocker". Fixing code against an unsound plan produces a green review of the wrong change, and folding the two outcomes together deletes the only signal that tells upstream planning its output was inadequate.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/playground/skills/workflow-build/SKILL.md
  - data/raw/claude-docs/playground/skills/workflow-triage/SKILL.md
---

# Plan-Insufficient Is Not Blocked

## Two failures that look alike

An execute-review-fix loop can stop in two ways that both read as "not shippable":

| Outcome | Meaning | Who acts |
|---|---|---|
| `blocked` | The **code** carries a blocker finding. The plan stands. | Fix stage |
| `plan_insufficient` | The **plan** is unsound: a step that cannot be implemented as written, a premise the tree contradicts, acceptance criteria that do not match the issue, or scope several times what was sized. | Re-triage |

Route to `plan_insufficient` from **any** stage, execute included. Then stop the loop and
say in the handoff which step failed and what the tree actually shows. The issue re-enters
triage carrying `reopened_from: "PLAN_INVALID"`.

## Why collapsing them is expensive

- **The fix loop converges on the wrong target.** Reviewers grade the diff against the
  plan, and a faithful implementation of a wrong plan passes.
- **Upstream never learns.** In one pipeline, `reopened_from` was non-null in 2 of 88
  triage rows, while refine reported gaps on 72% of plans and READY issues approved on
  round 1 only 16% of the time. Triage cannot improve against a number it never receives
  (see [[Gate Pass Rate Measures Effort, Not Readiness]]).

## Companion rules from the same loop

- **An unparseable reviewer verdict is `insufficient_context`, never `approve`.** A review
  that could not run is an infrastructure failure, not a soft pass.
- **Re-review after every fix round.** A fix is not verified until the reviewer has seen it.
- **Every run ends with a terminal row.** In the same ledger, 10 of 23 runs ended at
  `started` because the log line lived mid-loop and died with the loop (see
  [[Workflow Pipeline Telemetry Audit]]).

## See Also
- [[Stage-Scoped Scout Agents]] — extends (the stage boundary at which the outcome is raised)
- [[Gate Pass Rate Measures Effort, Not Readiness]] — prerequisite-for
- [[Workflow Pipeline Telemetry Audit]] — related
- [[Deferred Decision Status]] — related (another vocabulary that keeps two states apart so a gate can see them)
- [[Readiness Is Pinned to a Tree State]] — extends (how a READY plan becomes insufficient once a dependency lands)
