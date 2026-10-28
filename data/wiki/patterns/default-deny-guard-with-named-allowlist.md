---
title: Default-Deny Guard With a Named Allowlist
tags: [patterns, infra, pattern]
summary: A lint or test guard should scan the whole tree and deny by default, with exceptions named in config at the narrowest granularity (value, not file) and a reason each — hardcoded lists and file-level exemptions let regressions ship.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-05-dis168-skip-link-targets.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-05-dis168-skip-link-targets.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-05-dis168-skip-link-targets.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-05-dis168-skip-link-targets.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-05-dis168-skip-link-targets.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-05-dis168-skip-link-targets.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-05-dis168-skip-link-targets.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-05-dis167-admin-contrast.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-05-dis167-admin-contrast.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-05-dis167-admin-contrast.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-05-dis167-admin-contrast.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-05-dis167-admin-contrast.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-05-dis167-admin-contrast.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-05-dis167-admin-contrast.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-05-dis146-console-boundary.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-05-dis146-console-boundary.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-05-dis146-console-boundary.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-05-dis146-console-boundary.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-05-dis146-console-boundary.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-05-dis146-console-boundary.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-05-dis146-console-boundary.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-05-dis146-console-boundary.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-05-dis146-console-boundary.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-05-dis146-console-boundary.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-05-dis146-console-boundary.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-05-dis146-console-boundary.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-05-dis146-console-boundary.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-05-dis146-console-boundary.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis379-db-access-seam.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis379-db-access-seam.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis379-db-access-seam.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis379-db-access-seam.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis379-db-access-seam.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-06-dis168-skip-link-targets.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-06-dis168-skip-link-targets.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-06-dis168-skip-link-targets.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-06-dis168-skip-link-targets.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-06-dis168-skip-link-targets.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-06-dis168-skip-link-targets.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-06-dis168-skip-link-targets.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis197-a1-latlng.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis197-a1-latlng.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis197-a1-latlng.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis197-a1-latlng.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis197-a1-latlng.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis197-a1-latlng.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis197-a1-latlng.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis267-env-inventory.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis267-env-inventory.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis267-env-inventory.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis267-env-inventory.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis267-env-inventory.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-15-dis266-env-guard-a2.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-15-dis266-env-guard-a2.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-15-dis266-env-guard-a2.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-15-dis266-env-guard-a2.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-15-dis266-env-guard-a2.md
---

# Default-Deny Guard With a Named Allowlist

A guard that enumerates what it checks (four routes, three files) only protects what existed
when it was written. A guard that enumerates what it *skips* protects everything added later.
Three akira plans in one week hit the same shape from different directions.

## Scan the tree, list the exceptions

A regression test for skip-link targets listed four routes by hand. Four more routes shipped
without the `<main id>` target and the test stayed green. The fix replaced the list with a
tree scan of every page plus a named `ALLOWLIST` of routes that legitimately lack the target —
new routes are covered by default and must opt out explicitly. (Hoisting `<main>` into a shared
layout was rejected: it would nest landmarks on pages that already render their own.)

## Exempt the value, not the path

A contrast gate exempted the admin directory at file level. That exemption also swallowed a
genuinely failing grey shade in admin views. The allowlist moved to shade level: the lighter
grey that passes contrast on the admin background is allowed there; the failing shade is banned
everywhere. A file-level exemption says "this file is trusted"; a value-level exemption says
"this specific usage was checked" — only the second survives future edits to the file.

A static-text gate (grep for class names) is not a rendered-pixel check, so verification is
layered: the lint gate for regressions, plus a one-time manual visual pass at landing.

## Add the rule before migrating

When introducing a ban (e.g. `no-console` in favour of a structured logger), turn the rule on
first: the lint output becomes the enumerated migration worklist, and "done" is "lint passes".
Exceptions go in the lint config with a reason (a dry-run printer whose diffable line format a
structured logger would break) — never as inline `eslint-disable` comments, which are invisible
to anyone auditing the boundary.

Check the guard actually fires: inject a violation and expect failure. A mis-scoped `ignores`
glob silently exempts the directory you meant to guard (see [[Silence Reads as Clean]]).
Tooling detail from the same run: ESLint 10 rejects `allow: []` on `no-console`; use the plain
`"error"` form.

## Side effects to sweep after the migration

- Tests that spied on `console.*` become vacuous once the code logs elsewhere — they assert
  nothing was called and pass forever. Retarget or delete them.
- The review of the migration found a call expression duplicated inside logger payloads, a
  defect the diff itself introduced. A single-dimension review found one instance; a follow-up
  sweep found a third — see [[Audit the Class, Not the Instance]].

## Risk

A named allowlist can go stale: entries outlive the reason they were added. Keeping a reason
string beside each entry is what makes a later prune possible.


## Size the allowlist by layer, not by grep (akira, 2026-09-24)

A DB-access boundary rule kept its scope to `app/**` and its named allowlist (39 files),
even after a wider grep counted 127 files with raw queries. Most of those were the I/O layer
doing its documented job. See [[Count the Violation, Not the Token]].

## Review lessons on the shape (akira reviews, 2026-09-06 to 09-15)

- **The hardcoded list was the mechanism of drift.** In a skip-link guard, a fixed list of
  routes let four routes drift unguarded. The rewrite scans more than 37 route files, with a
  three-tier allowlist that gives a reason for each entry. A later redaction guard picked the
  tree-scan shape for the same reason: *the violating file is exactly the one nobody thought
  to add to a list.* A rule enforced by a test of one call site still depends on memory.
- **Demonstrate the guard, don't assert it.** Add a scratch second call site, see the guard
  fail and name the file and line, remove the scratch, and confirm the diff is empty.
- **Name the blind spots in the guard file.** A regex sees literal `field:` assignments, but not
  a computed key, a spread, or a mutation after construction. The fix was a header comment
  listing those gaps and naming the AST-based rule that would close them, not a cleverer
  regex. An env-inventory scanner did the same for destructuring and wrapper calls it cannot
  see ([[Env Inventory Gate Enforced in One Direction]]).
- **Match the identifier, not the text.** A coverage test asserting that every writer CLI calls
  the production-write guard started as a regex. A comment such as `// TODO: confirmProductionWrite()`
  satisfied it. Stripping comments with a regex then cut lines that held a URL string, and a
  string literal still passed. The settled version uses the TypeScript compiler API: the check
  holds only if an `Identifier` with the guard's name exists outside an import declaration. It
  has a read-only allowlist and an alternate-guard allowlist, both checked by opening each
  file. Nested-scope shadowing was left as a won't-fix, because the test is a net for a
  *forgotten* guard, not a defence against deliberate evasion
  ([[Production Write Guard: Explicit Override, Never Ambient]]).

## See Also
- [[One-Off Codemod, Permanent Gate]] — extends (the gate half, made default-deny)
- [[Stated Seams Drift, Enforced Seams Hold]] — instance-of
- [[Every Registration Site Needs a Guard]] — extends
- [[Silence Reads as Clean]] — extends (a mis-scoped ignore reads as a pass)
- [[Audit the Class, Not the Instance]] — extends
- [[Count the Violation, Not the Token]] — related (why the rule's scope did not grow with the grep count)
