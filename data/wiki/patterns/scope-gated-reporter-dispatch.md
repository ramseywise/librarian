---
title: Scope-Gated Reporter Dispatch
tags: [llm, pattern]
summary: Sizing a review to the change by declaring a scope up front, then recording each reporter's skip with its reason in the verdict — so "not run" is visible evidence rather than an absent section a reader mistakes for a clean pass.
updated: 2026-10-16
sources:
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-24-AIT-18-review-verdict.md
  - data/raw/claude-docs/learn-ai-engineering/docs/plans/2026-07-24-LAE-39-review-verdict.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-24-GUA-23-review-verdict.md
  - data/raw/claude-docs/.claude/docs/plans/2026-07-24-GUA-16-review-verdict.md
  - data/raw/claude-docs/atlas/docs/plans/2026-07-24-ATL-22-review-verdict.md
---

# Scope-Gated Reporter Dispatch

A multi-reporter review does not run every reporter on every change. The verdict
opens by declaring a **scope** with a rationale, and that declaration gates which
reporters dispatch:

```text
Scope: Lightweight (chore — vendored skill sync + dependabot workflow + lint)
Rationale: 1 commit syncing vendored skills and adding dependabot
           auto-merge workflow. No code logic changes.
```

## The dispatch table

The mechanism that makes this trustworthy is that **skips are recorded, not
omitted**. Every reporter appears in the table whether or not it ran, each with a
status and a reason:

| Reporter | Status | Findings |
|---|---|---|
| lint/tests | n/a | template repo (CI runs on render) |
| akira-scan | skipped | lightweight scope |
| SANYI | skipped | no SANYI.md |

Three distinct reasons for not running appear here, and conflating them would
lose information:

- **`n/a` — structurally inapplicable.** A template repo has no tests to run
  because CI runs on the *rendered* output, not the template.
- **`skipped` by scope.** The reporter applies but the change does not warrant
  it — a deliberate cost decision.
- **`skipped` by missing precondition.** No `SANYI.md` exists, so the contract
  reporter has nothing to check against. This is a **coverage gap**, not a pass:
  the repo could adopt a contract and the reporter would start producing signal.

## Why the empty row matters

An omitted section reads as a clean pass. A row saying `skipped — lightweight
scope` reads as a decision someone made and can be challenged. This is the same
principle as `insufficient_context` in [[Source Severity vs Merge Impact]] — a
review is permitted to state that it did not conclude, rather than letting
silence imply approval.

It also makes the gate auditable after the fact. If a "lightweight" chore PR
later turns out to have carried a logic change, the verdict shows exactly which
reporter was gated off and on what rationale — the scope call is recoverable
evidence rather than an untracked judgment.

## Observed instances

Five recorded instances, all at `approve`; three lightweight, two with the heavy reporters run:

| PR | Change shape | akira-scan | SANYI |
|---|---|---|---|
| AIT #18 | vendored skill sync + dependabot workflow | skipped (scope) | skipped (no SANYI.md) |
| LAE #74 | structural cleanup + 30 dependabot bumps, 36 commits | skipped (scope) | skipped (no SANYI.md) |
| ATL-22 | dependabot config + workflow template sync | skipped (scope) | skipped (no SANYI.md) |
| GUA-16 | user-level `.claude` config repo — skills, hooks, settings | run (full scope) | skipped (no SANYI.md) |
| GUA-23 | new review-backbone package, 6 plan steps, 79 tests | plan-fidelity ran (0 deviations); lint/tests ran | skipped (no SANYI.md) |

GUA-16 is the useful outlier: a **config repo with no application code** still scored
*full* scope, because its skills and hooks are the logic other repos execute. The lint and
test reporters were recorded as "n/a — no code to lint/test" rather than omitted, which is
the empty-row rule applied to a repo where the usual reporters have nothing to run on.

Note that **commit count does not drive scope** — LAE-39's 36 commits still
scored lightweight, because the axis is *whether code logic changed*, not
diff size. Dependency bumps and whitespace normalization are high-volume and
low-risk; the scope call correctly ignores volume.

## Workspace hygiene as a verdict section

Both verdicts carry a **Workspace Hygiene** table alongside the findings —
stale local branches whose remotes are gone, deleted as part of the review:

| Item | Status |
|---|---|
| `fix/render-ci-setup-uv-cache` (remote gone, 9 commits) | Deleted — superseded by current HEAD |
| `backup-before-lfs` (historical) | Deleted |

Attaching this to the review rather than to a separate cleanup task means branch
rot gets collected at the moment someone is already looking at the repo's state.

## See Also
- [[Corrective Follow-Up Dispatch]] <!-- auto-linked -->
- [[Source Severity vs Merge Impact]] — extends (the same refusal to let silence mean approval)
- [[Merge Impact and Evidence State]] — prerequisite-for
- [[Claude Workflow System]] — instance-of (the review phase this dispatches within)
- [[Parallel Dimension Scanner Architecture]] — alternative-to (run all dimensions vs gate by scope)
- [[Rationale-Blind Worst-Case Review]] — extends (a consequence-only reporter dispatched the same way)
- [[Silence Reads as Clean]] — extends (the general defect this dispatch rule guards against)
- [[Deterministic Signal Detection for Dispatch]] — alternative-to (detected signals vs declared scope as the dispatch input)
- [[Review Reporter Ground Rules]] — extends
- [[Derive the Gate, Don't Copy It]] — extends
- [[Cross-Dimensional Review Adjudicator]] — prerequisite-for
