---
title: Single Typed Verdict, Consumers Never Re-Derive
tags: [patterns, eval, pattern]
summary: When a decision such as a merge verdict is derived in several places (driver strings, skill prose), it drifts; compute it once in a pure typed function exposed as a CLI, and have every consumer call that CLI instead of re-deriving it.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-05-multi-agent-orchestration.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-05-multi-agent-orchestration.md
---

# Single Typed Verdict, Consumers Never Re-Derive

Source: the guacamayo multi-agent orchestration plan.

## The drift

The merge verdict was implemented **three times**:
- as bare strings in the review driver
- as prose in Stage 6 of the workflow-review skill
- as prose in a second review skill

Each copy applied slightly different rules. Meanwhile typed `MergeDecision` and
`ReviewReport` schemas already existed in the repo, unused.

## The fix

- A pure `derive_merge_decision` function in `review/verdict.py`. It is carried on the
  driver result and exposed as `review-cli verdict`.
- Both skills call the CLI. **No consumer re-derives the verdict.**
- **Adopt the stricter rule set** rather than adding a mode flag. A mode flag preserves
  the drift under a new name.
- **Keep scope separate from policy.** Exploratory "wander" findings are excluded at the
  call site, not inside the policy. That reviewer emits questions by construction, so
  counting its findings would make "approve" unreachable. That exclusion was still
  undocumented on the skill side, which is a known residual gap.
- **Write the baseline metric row before the change.** Verdict sources went 3 → 1.
  Role-contract coverage went 1/6 → 2/6.

## Wider architecture decisions

- **Skills stay the invocation interface.** Inter-role contracts live in repo code as
  typed schemas. Vendoring the global skills into the repo was rejected.
- The roles are research, dispatch triage, readiness triage, planning, review and
  executor. Each handoff is a schema, not prose.
- **A graph framework was a defended rejection.** Reopen it only when a role loop has to
  suspend across sessions while holding intermediate state.
- **Persistence is bimodal.** SQLite is write-once reporting. Markdown is the runtime
  memory.
- **363 lexical trigger-match evals always pass.** They measure routing plausibility, not
  correctness, and "a metric that always passes is not a metric."
- **Authority to act needs a measured precision baseline.** Mutation safety must gate on
  content invariants, not on whether the diff is empty.

## See Also
- [[Merge Impact and Evidence State]] — extends
- [[Deterministic Review Substrate]] — instance-of
- [[Cross-Dimensional Review Adjudicator]] — extends
- [[Always-Red Check Carries No Signal]] — extends
