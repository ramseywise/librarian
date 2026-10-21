---
title: Silent Fallthrough in String-Keyed Discovery
tags: [patterns, llm, pattern]
summary: When a tool finds its working target by grepping a literal string, renaming that string doesn't crash — it selects a different target with no error, making the rename a flag-day change whose only defence is a call-site checklist.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/docs/specs/plan-doc-status-enum.md
  - data/raw/repos/diskoe/CLAUDE.md
  - data/raw/repos/diskoe/README.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-21-dis349-preview-to-review-rename.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-21-dis349-preview-to-review-rename.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-21-dis349-preview-to-review-rename.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-21-dis349-preview-to-review-rename.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-21-dis349-preview-to-review-rename.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-08-01-CLA-74-status-writers-validation.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-08-01-CLA-74-status-writers-validation.md
  - data/raw/repos/playground/CLAUDE.md
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

## Dissolving the flag day with a transitional permissive read

The Status migration itself (guacamayo CLA-74) showed that "both must land in one atomic
change" can be avoided. The trick is to sequence the change so that no reader ever sees
a value it cannot match:

1. **Readers first.** Each reader accepts both the old and new forms, using a permissive
   regex (`IN[ _-]PROGRESS`, case-insensitive). A comment marks the regex as temporary.
2. **Writers second.** Writers emit only the canonical form.
3. **Validator last.** It warns only on newly written lines, so existing docs do not
   trigger it.
4. **Cleanup.** The permissive regex is removed in the migration's cleanup step, once
   no old values remain.

The call-site inventory is still required. It just stops being the only safety net. In
this migration the inventory found a tenth reader nobody had listed (a PreCompact hook
in settings.json). The test proof was a planted defect: 41 tests passed on the correct
code, and with the defect planted 33 passed and 8 failed. Doing the work in a worktree
cut from origin/main kept unrelated uncommitted changes out of the migration.

## Further instances (diskoe)

- **A lint grep that sees half its violations.** A "no font-size overrides" check matched only
  the SVG attribute form `font-size="…"`; the inline `style="font-size:…"` form was invisible to
  it, so 10 inline overrides accumulated while the check reported clean. The fix was a grep
  covering both forms. A rule enforced by a check that cannot see half its violations is not
  enforced.
- **An unregistered cross-tab anchor.** In a tabbed single-page design doc, a link to an id on
  another tab resolves only if that id is in a hand-maintained `TAB_OF` map. A missing entry
  falls through to the overview tab with no error. This is now enforced by a doc-paths gate
  instead of by convention.

---

## A Route Rename's Hidden String Keys (akira, 2026-09)

A mechanical rename of a `/preview` review surface to `/review` (3 directory moves, about
80 files, plus a permanent `/preview/:path*` redirect) hit three string-keyed consumers
that no type checker sees:

- **A telemetry series keyed on the raw route string.** Each page passed its own `ROUTE`
  constant to a render timer. The report grouped strictly by that string, with no alias
  table, so every post-rename row started a new series with no join to the old history.
  The choice was to **accept the split and document it** in the decision row instead of
  letting it happen silently. The table was explicitly non-critical, traffic was internal,
  and an alias map would have added permanent complexity to a report-only path for a
  metric nobody had acted on. The named fallback, if the gap proved unacceptable, was a
  one-line alias map at the report's *caller*, not inside the pure function.
- **Over-matching `sed`.** `s#/preview#/review#g` also rewrote `@/lib/previewAdmin`
  imports. That is a capability name, not a route, and it also gates unrelated draft
  viewing. A targeted revert plus a grep proved the fix. The plan had already listed the
  tokens to keep (`preview_admin`, `isPreviewAdmin`, and a `surface: 'preview'` request
  enum that is a calling-context name, not a URL), but a blanket substitution ignored the
  list.
- **An allowlist glob that silently stopped matching.** A lint check's allowlist named the
  pre-move component paths. After the move it matched nothing and still passed. The fix
  repointed it and ran the check directly to confirm it still walked real files.

Before a rename, inventory every place the old string is a *key* (metrics grouping,
allowlists, redirect sources), not just every place it is a *reference*.

## See Also
- [[Plan-Doc Status Enum]] — instance-of
- [[Claude Workflow System]]
- [[SANYI Change-Contract System]]
- [[Parallel Dimension Scanner Architecture]] — extends (prose-only safeguard as the same defect class)
- [[Template Migrations for Structural Moves]] — instance-of (a module relocation that leaves a stale target behind)
- [[Copier Upstream Update Workflow]] — extends (structural renames arriving from upstream)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — extends (the generic guard against this class)
- [[Cached Derivation Without a Recompute Path]] — related (a stored value whose writer vanished)
- [[Hydration Gap Silent Input Loss]] — instance-of (the same class in a UI runtime)
- [[Read-Every-Consumer Migration]] — extends (the migration discipline that catches string-keyed consumers)
- [[Silence Reads as Clean]] — extends (the general form: absence emitted as a clean result)
- [[The Untested Copy Wins]] — related (a tested-but-uncalled rule is the same shape as a never-matched key)
- [[Collapse Site Detection]] — extends (the design-time pass that hunts this class)
- [[Silent Failure Catalogue]] — extends (the code-review checklist of the class)
