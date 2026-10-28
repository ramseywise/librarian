---
title: Skip Steps, Not Jobs, Behind a Path Filter
tags: [infra, pattern]
summary: "When a CI pipeline is path-filtered so docs-only commits stop paying for full runs, gate each expensive step rather than the whole job: a skipped job reports `skipped`, which interacts unpredictably with required status checks, while a job whose steps were skipped still reports a real `success` — at the cost of a one-minute billing floor per job. Verify the negated filter with a mixed commit, and recheck every invariant that said the gate always runs."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis125-ci-path-filter.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis125-ci-path-filter.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis125-ci-path-filter.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-dis125-ci-path-filter.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-dis125-ci-path-filter.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-dis125-ci-path-filter.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-dis125-ci-path-filter.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-dis125-ci-path-filter.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-dis125-ci-path-filter.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-dis125-ci-path-filter.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis125-ci-path-filter.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis125-ci-path-filter.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis125-ci-path-filter.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis125-ci-path-filter.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dsk-300-full-verification-workflow.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dsk-300-full-verification-workflow.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dsk-300-full-verification-workflow.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dsk-300-full-verification-workflow.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dsk-300-full-verification-workflow.md
---

# Skip Steps, Not Jobs, Behind a Path Filter

Found in akira's CI plan (2026-09). About 58% of commits in a 30-day window touched only
`.claude/`, `docs/`, or `*.md` files, but every one of them ran three heavy jobs (unit/lint/build,
end-to-end, and DB integration). The fix was a path filter. The interesting part was *where*
to put the skip.

## Two designs, one real difference

- **Design A, job-level skip.** `if:` on the job itself. A skipped job bills 0 minutes but
  reports the GitHub status `skipped`, not `success`.
- **Design B, step-level skip ("always green").** Every job still starts. A cheap filter
  step runs right after checkout, and every later step carries
  `if: steps.filter.outputs.code == 'true'`. The job reports a real `success` or `failure`
  and never `skipped`. Each job bills at least 1 minute even when it does nothing.

On the measured commit mix, A cost about 4,550 min/month and B about 5,490. The ~940-minute
gap is a few dollars a month. What it buys is **status-check semantics you don't have to
verify.** The private repo's plan tier could not configure branch protection at all (the API
returned 403, not 404), so `skipped` could not block a merge *today*. But the cost model's own
recommendation was to upgrade specifically to get required checks. At that point, how a
`skipped` job satisfies a required check becomes a live question, and its documented behaviour
has changed over time. B makes the question impossible rather than testing it. The plan named
this as a reviewer choice (a measurable cost against an unverifiable risk). It did not decide it
unilaterally.

## Some steps must always run

One job could never be skipped. Two of its checks (a doc-path validator and a design-token
lint) are pure filesystem checks that exist *for* docs-only diffs. Only lint, type-check,
test, build, and the eval gate were skippable. So the split was step-level inside that job
whichever design won. Later, a workflow-YAML parse check was added as a third always-run
step, mirrored in `make gate` for gate/CI parity. A hand-edited workflow file with an indent
error otherwise only surfaces as "workflow file is invalid" after the push.

## The negated filter is a silent-failure class

The filter was negation-only: `code: ['!.claude/**', '!docs/**', '!**/*.md']`, meaning "true
if any changed file falls outside these". If the action evaluates negations per pattern
rather than per changeset, there are two failure directions, and they look identical in a
YAML review:

- A docs-only diff classified as code is safe. You lose the savings and nothing else.
- A code diff mixed with many docs classified as docs-only is dangerous. Real changes skip
  validation.

A filter's correctness is **only observable after a real push**. Verification needs three
commits: docs-only, code-only, and a **mixed** commit (one `.md` file and one `.ts` file).
The two-state test misses the dangerous direction. See
[[Verify CI Steps by Extraction, Not Retyping]] for the same "a filter that stopped matching
reports clean" property.

## Recheck every "the gate always runs" invariant

The change contract stated that CI always runs the eval gate. After filtering, that sentence
became conditional, and a contracts reviewer flagged it as a blocker. Resolving it meant
asking the reviewer's own failure question: **can a diff the filter calls docs-only ever do
the thing the gate exists to catch?** The answer here was no:

- The only two files that can register or threshold a metric match none of the exclusion
  patterns.
- The workflow file itself can never exclude itself.
- On `pull_request`, the filter sees the cumulative PR diff, so a PR that starts docs-only
  and later adds code re-triggers on every push.

The protection held, so the contract's prose was fixed and the CI change stayed. The same
question should be asked of every invariant a path filter touches. See
[[Execution-Made Decisions Leave Stale Invariants]].

## A force-all override is one derived signal (akira, 2026-09-16)

With path filters in place, nothing guaranteed every test layer would run when someone
asked for it. The manual dispatch exposed only a snapshot-update input, and each suite's
gate read only its own path output, so "run everything" happened by accident if at all.
The design:

- **Reuse the existing workflow; don't add a "full verification" workflow.** A second
  workflow would copy the database, browser, secret and grant setup, recreating the
  duplicated dependency graph at workflow scale.
- **One derived `force_all` output** in the existing change-detection job. It is true
  for a boolean dispatch input (default `false`, so narrower dispatch uses keep working)
  or a named PR label (`ci:full`). Every suite gate ORs it with its path result. The
  `labeled` activity is *appended* to the current `pull_request.types` list, which had
  grown since the plan was first written.
- **A parsed-YAML contract test**, because a parse-only workflow lint checks syntax, not
  routing. The test asserts the input exists and defaults false, the label activity is
  allowed, the output is published, each of the three suite gates consumes it, and the
  schedule does *not* force all suites. Read YAML 1.1's `on` key defensively. Removing
  any one connection fails the test. Otherwise a wrong label expression would leave one
  suite filtered without anyone noticing.
- **Keep the weekly full run off** until a real forced run has measured its duration
  against the budget, and CI billing was blocked at the time anyway.
- **A blocker on one proof step does not block the build.** The real dispatch could not
  run while CI billing was blocked. The YAML and the offline test could still be built
  and gate-checked, so the dispatch was demoted to a named operator follow-up instead of
  holding the whole plan at not-ready.

## The savings did not close the ceiling

Recomputing the issue's arithmetic changed the conclusion. A third heavy job had landed on
the same triggers after the cost model was written. That moved the baseline from 8 to 12
min/PR, and the filter cut the bill 53–55% but **no longer fit under the plan allowance**.
The plan corrected both stale documents by name instead of letting the roadmap imply the
problem was closed. If another heavy job lands, the next lever is trigger discipline or moving
a lane off the PR path, not a wider filter. Billing settings and the host's ignored-build step
were named as operator-only non-steps, not dropped.

## See Also
- [[Scaling Axes and Customer-Triggered Cost Cliffs]] — instance-of (the team-velocity axis this filter targets)
- [[Verify CI Steps by Extraction, Not Retyping]] — related (a CI filter that stops matching reports clean)
- [[Execution-Made Decisions Leave Stale Invariants]] — related (the eval-gate invariant made conditional)
- [[Gate vs Ship Make Targets]] — related (the gate/CI parity the YAML check was mirrored for)
- [[Silent Failure Catalogue]] — extends (misclassified mixed diffs skip validation silently)
- [[Plan-Insufficient Is Not Blocked]] — related (another split between "cannot build" and "cannot prove yet")
