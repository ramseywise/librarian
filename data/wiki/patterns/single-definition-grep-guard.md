---
title: Single-Definition Grep Guard
tags: [patterns, eval, pattern]
summary: "To prove a rule (a password policy, a regex) is defined in exactly one file, run a fixed-string grep as a unit test and assert it returns only the canonical file. Use -F to avoid BRE/ERE escaping traps, treat grep's exit status 1 as no match rather than an error, also grep for the atomic pieces a hand-rolled copy would use, and confirm the test fails on the pre-fix tree."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis57-forms-server-actions.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis57-forms-server-actions.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis57-forms-server-actions.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis57-forms-server-actions.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis57-forms-server-actions.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis57-forms-server-actions.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis57-forms-server-actions.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-14-dis191-content-sources-tab-slice1.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-14-dis191-content-sources-tab-slice1.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-14-dis191-content-sources-tab-slice1.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-14-dis191-content-sources-tab-slice1.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-14-dis191-content-sources-tab-slice1.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-14-dis191-content-sources-tab-slice1.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-14-dis191-content-sources-tab-slice1.md
---

# Single-Definition Grep Guard

A forms refactor in akira found the password policy in four places with two
implementations. Three files carried the same combined regex. A registration form
hand-rolled it as three sequential checks. They were equivalent at the time, so this was
drift risk rather than a live bug. The fix put a single definition in
`schemas/password.ts`, and added a test that fails if a second copy ever shows up.

## The guard

The check is a Vitest test, not a Makefile target, so it runs on every `npm test`. It
shells out to grep:

```ts
function filesContaining(literal: string): string[] {
  try {
    return execSync(`grep -rlF -- '${literal}' src --include='*.ts' --include='*.tsx'`,
      { encoding: 'utf8' }).trim().split('\n').filter(Boolean)
  } catch (e) {
    if ((e as { status?: number }).status === 1) return []   // no match is not an error
    throw e
  }
}
expect(filesContaining('(?=.*[A-Z])(?=.*[^a-zA-Z0-9])')).toEqual(['src/app/schemas/password.ts'])
```

## Three traps the refine pass caught

1. **Wrong regex dialect.** The first draft escaped its metacharacters ERE-style
   (`\(\?=\.\*`) but called plain `grep`, which uses BRE on both macOS and Linux. In BRE,
   `\(` opens a group and `\?` is a GNU quantifier, so the pattern matched nothing.
   Checked against the tree, it returned zero matches where four were expected. The test
   could never have gone red before the fix or green after it. Fix: use `-F`, a fixed
   string, so there is no escaping to get wrong.
2. **Exit status 1 thrown as an error.** `grep -l` exits 1 when nothing matches, and
   `execSync` throws on any non-zero exit. The passing state, no copies, would have
   crashed the test. The repo already had a helper that catches status 1 for exactly this
   case. The draft had not used it.
3. **Only the copy-paste was guarded.** Grepping for the combined regex catches a literal
   copy of it. It would not have caught the duplicate that actually existed: the
   hand-rolled form used the atomic classes `[A-Z]` and `[^A-Za-z0-9]` separately and
   never contained the combined string. A second assertion bans those atomic literals
   outside the canonical file. It was first checked against the tree for false positives:
   the classes appeared in exactly the four known files and nowhere else. The two
   existing copies wrote the special-character class in different orders, `[^A-Za-z0-9]`
   and `[^a-zA-Z0-9]`. They match the same set but are different strings, so the guard
   checks both orderings.

## Make it fail first

Each assertion was run unchanged against `main` before the fix, and each was expected to
fail with a named set of files. After the fix all three arrays had to be empty. That
before-and-after pair is the regression test. A guard that has never gone red has an
unexercised wiring ([[Scan-Floor Guard Against Silent No-Op Checks]]).

## Don't derive the canonical regex from its parts

The combined `PASSWORD_POLICY` regex is written out independently rather than built by
interpolating the atomic constants, because a composed regex can drift from its parts
without anyone noticing. A table test asserts the combined regex and its parts agree on
fixed cases: too short, no capital, no special character, valid. It also covers one known
academic divergence, a literal newline that `.` does not match. That case is documented
inline rather than "fixed".

## Pin an app-layer vocabulary to the migration text

The same "one-copy proof" idea was later applied to vocabularies (akira, 2026-09-14). An
admin form needed the allowed values of four CHECK-constrained columns. The app-layer
constants live in one schema module, and a unit test reads the **migration file** with
`fs`, parses each `CHECK (... IN (...))` clause, and asserts set equality with the
matching constant in both directions. A fifth vocabulary had no CHECK. It was pinned
instead against the literal strings the importer branches on (`content_types.includes('Events')`),
each asserted to appear verbatim in the importer source. Editing a CHECK value or renaming
an importer literal without the matching schema edit now fails the test. It was made to
fail first by editing one value in the migration (`'Parking lot'`), then reverted.

## See Also
- [[The Untested Copy Wins]] — extends (a vocabulary restated in the app layer is a copy; the pin test makes it a guarded one)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — extends (a grep whose pattern is grammatically empty is a silent no-op check)
- [[Eval Falsifiability]] — instance-of (prove the guard fails on the pre-fix tree)
- [[One-Off Codemod, Permanent Gate]] — related (another regex gate whose matcher fixes kept changing what it could see)
- [[Server Shell, Client Leaf]] — related (the forms refactor that introduced the shared schema)
- [[Cross-Surface Order Parity Test]] — related (sharing key constants across three surfaces, guarded by an order test)
