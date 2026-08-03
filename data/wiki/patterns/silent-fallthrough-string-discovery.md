---
title: Silent Fallthrough in String-Keyed Discovery
tags: [patterns, llm, pattern]
summary: When a tool finds its working target by grepping a literal string, renaming that string doesn't crash — it selects a different target with no error, making the rename a flag-day change whose only defence is a call-site checklist.
updated: 2026-08-03
sources:
  - data/raw/claude-docs/guacamayo/docs/specs/plan-doc-status-enum.md
---

# Silent Fallthrough in String-Keyed Discovery

A failure mode in agent and skill pipelines that discover their working target by
grepping for a literal string.

## The mechanism

A skill locates the doc it should operate on with something like:

```sh
grep -l 'Status: IN PROGRESS' .claude/docs/plans/*.md
```

Rename the state to `IN_PROGRESS` and this returns nothing. Crucially, that is
**not an error** — the discovery step falls through to its next rule (e.g. "most
recent `Status: PLANNED`") and picks up a *different document*. The pipeline runs
happily against the wrong target.

Contrast with a crash: a missing file, a bad import, or a schema violation stops
the run and names the problem. Silent fallthrough produces confident work on the
wrong input.

## Why it forces a flag-day change

Because there is no error signal, you cannot deploy the reader change and the data
change independently and let failures tell you what you missed. Both must land in
one atomic change, and the **only** defence is an exhaustive call-site inventory
compiled before the rename.

Building that inventory requires the same tolerance the audit is about: a naive
`grep '^Status:'` missed bold-key and leading-whitespace variants, producing an
undercount that propagated into a published success metric. Audit greps must be
written to over-match, then be narrowed by hand.

## Mitigations

- **Inventory every read and write site** of the literal before renaming; treat the
  list as the migration checklist.
- **Distinguish readers from writers** — a writer emitting the old value is
  recoverable; a reader keyed to it silently mis-targets.
- **Prefer a fail-loud discovery step**: if the primary selector matches nothing,
  error rather than falling through to a broader rule.
- **Use single-token values** so validation is a set-membership test rather than a
  normalize-then-compare — this is exactly why `IN_PROGRESS` beat `IN PROGRESS`.

---

## See Also
- [[Plan-Doc Status Enum]] — instance-of
- [[Claude Workflow System]]
- [[SANYI Change-Contract System]]
- [[Parallel Dimension Scanner Architecture]] — extends (prose-only safeguard as the same defect class)
- [[Template Migrations for Structural Moves]] — instance-of (a module relocation that leaves a stale target behind)
- [[Copier Upstream Update Workflow]] — extends (structural renames arriving from upstream)
