---
title: "Green Lint Proves Absence, Not That the Rule Fires"
tags: [patterns, infra, pattern]
summary: "A custom lint rule that is checked only by hand proves nothing once it is green. ESLint flat config replaces `no-restricted-syntax` across overlapping glob blocks, so a ban can go dead without any error. Test each rule through the lint API with a virtual file path, because the defect depends on the glob."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/reviews/2026-09-08-guardrails-gate.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-08-guardrails-gate.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-08-guardrails-gate.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-08-guardrails-gate.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-08-guardrails-gate.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-08-guardrails-gate.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-08-guardrails-gate.md
---

# Green Lint Proves Absence, Not That the Rule Fires

Found in akira's guardrails-gate review (2026-09). Two custom `no-restricted-syntax`
rules had been verified by hand, with scratch `.tsx` files that were deleted afterwards.
After that, their only enforcement was "`make lint` passes". That proves *no violations
exist in the tree*. It does not prove that the selectors *fire*. A rule that matches
nothing and a codebase that obeys the rule produce the same green output.

## How a ban goes dead without an error

ESLint flat config **replaces** a rule's options when two config blocks match the same
file. It does not merge them, and the later block wins. Two blocks that both set
`no-restricted-syntax` on overlapping globs leave only the second block's selectors active
for files in the overlap.

This had happened twice in the same repo:

1. An earlier ban sat dead behind a later block's `no-restricted-syntax` entry.
2. **The fix for that recreated the collision.** It widened a cast-ban glob to
   `src/**/*.{ts,tsx}`, which overlapped the existing `src/app/**/*.tsx` block.

Both times "lint is green" was true and meant nothing.

## The fix: test the rule through the lint API

ESLint's Node API, `lintText(code, { filePath })`, runs the real resolved config against
an in-memory snippet. **The virtual `filePath` is the point.** The defect depends on which
globs match a path, not on the shape of the code, so a test has to place the same code at
paths in each glob region. The suite had six cases covering all four selectors across both
glob regions. It also had a negative control: a snippet under the exempt `components/ui/**`
path must produce no error.

The dispatcher re-checked the claim against the code instead of accepting the report.
Removing the `ignores: ['src/app/**/*.tsx']` line turned exactly the three JSX tests red
and left the two cast tests green. Restoring the line returned 6/6. That is
[[Red-Then-Green Proof for Fix-Stage Tests]] applied to configuration.

## Related lessons from the same gate

- **Duplicated selectors drift.** The cast selector existed as two literal copies with a
  "keep the two in sync" comment. It was lifted to one module-scope constant that both
  blocks reference.
- **The doc-drift check had the same blind spot.** The gate's `gate-docs` check validated
  the documented target *sequence* but not the count beside it. Four docs said 14 targets
  when the real count was 15, and the check passed. See [[Derive the Gate, Don't Copy It]].
- **The lower bound is written down.** A heuristic in the doc check ignores lists shorter
  than six items. The review accepted that limit and recorded it in the check's header, so
  it is a documented bound rather than a latent surprise.

## Rules

- Every custom lint rule gets a test that runs the real config through the lint API, with
  at least one positive case per glob region and one exempt-path negative.
- When two config blocks touch the same rule, assume the later one replaces the earlier one,
  and test the files in the overlap.
- Prove that the test can fail: delete the rule or the ignore line, and watch the test go red.

## See Also
- [[Red-Then-Green Proof for Fix-Stage Tests]] — instance-of
- [[Scan-Floor Guard Against Silent No-Op Checks]] — related (a check that passes because it scanned nothing)
- [[Derive the Gate, Don't Copy It]] — related (the gate-docs count false negative)
- [[Adoption Ban Needs an Escape Hatch]] — related (a lint-enforced ban in the same repo)
- [[Default-Deny Guard With a Named Allowlist]] — related
