---
title: Idempotent Reconcile Beside a Guarded Create
tags: [patterns, infra, pattern]
summary: Keep the create step non-idempotent and guarded, and split linking or updating into a separate append-only reconcile that adds only what is missing and never removes human text.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-31-CLA-69-quick-pr-existing-pr-linking.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-31-CLA-69-quick-pr-existing-pr-linking.md
---

# Idempotent Reconcile Beside a Guarded Create

Source: the guacamayo `quick-pr` skill (CLA-69). The skill refused to run when a PR
already existed for the branch, so issues opened after the PR never got their
`Closes #N` lines.

## The split

- **Create stays guarded and non-idempotent.** Opening a PR twice is a bug, so the
  existing-PR guard stays where it is.
- **Linking becomes a separate reconcile.** It runs whether the PR is new or old. It
  computes which `Closes #N` refs are missing from the body and appends only those. It
  never rewrites or removes text a human wrote, so running it twice is a no-op.

Do not make the create step idempotent so you can reuse it for updates. Separating the
two means the dangerous operation keeps its guard, and the safe one can run freely.

## Traps found while building it

- **Command substitution eats separators.** `MISSING=$(printf '%s%s\n' "$MISSING" "$REF")`
  strips the trailing newline on every pass. The result is `Closes #69Closes #70`, and
  GitHub silently drops the second ref. The fix is to accumulate a literal `\n` and print
  the result with `printf '%b'`. A test with one issue cannot catch this, so a multi-issue
  acceptance criterion was added on purpose.
- **Use a numeric boundary in the presence check.** Match `Closes #N([^0-9]|$)` so that
  `#7` does not count as present just because `#70` is.
- **Probe PRs must not merge.** Merging a test PR auto-closes the live issues it
  references. Drop `--delete-branch` and close the probe PR by hand.

## See Also
- [[Silent Fallthrough in String-Keyed Discovery]] — alternative-to
- [[Silence Reads as Clean]] — extends
- [[Claude Workflow System]] — instance-of
