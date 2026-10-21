---
title: Scan-Floor Guard Against Silent No-Op Checks
tags: [patterns, infra, eval, pattern]
summary: A check that walks files or rows and reports "clean" must refuse to pass when it scanned implausibly little — a check that cannot tell "clean" from "didn't run" is worse than no check.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/research/2026-09-03-dis36-production-smoke.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-dis36-production-smoke.md
  - data/raw/claude-docs/akira/docs/research/2026-09-03-rls-closure.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-03-rls-closure.md
  - data/raw/claude-docs/akira/docs/research/2026-09-04-dis159-colour-contrast.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-04-dis159-colour-contrast.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-04-dis159-colour-contrast.md
  - data/raw/claude-docs/playground/docs/research/2026-09-04-dis159-colour-contrast.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-dis36-production-smoke.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-dis36-production-smoke.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-03-rls-closure.md
  - data/raw/claude-docs/playground/docs/research/2026-09-03-rls-closure.md
  - data/raw/claude-docs/ai-project-template/docs/reviews/AIT-43-review.md
  - data/raw/repos/ai-project-template/.claude--docs--reviews--AIT-43-review.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-02-dis48-design-tokens.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-02-dis48-design-tokens.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-02-dis48-design-tokens.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-02-dis48-design-tokens.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-02-dis48-design-tokens.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-02-dis48-design-tokens.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-02-dis48-design-tokens.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis46-restore-drill.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis46-restore-drill.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis46-restore-drill.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis36-production-smoke.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis36-production-smoke.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis36-production-smoke.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis36-production-smoke.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis36-production-smoke.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis36-production-smoke.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis36-production-smoke.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-23-dis371-enrichment-vocabulary.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-07-dis46-restore-drill.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-07-dis46-restore-drill.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-07-dis46-restore-drill.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-07-dis46-restore-drill.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-07-dis46-restore-drill.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-07-dis46-restore-drill.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-07-dis46-restore-drill.md
---

# Scan-Floor Guard Against Silent No-Op Checks

A failure class found while hardening a Next.js + Postgres product's CI (akira): several
"guard" scripts had a shape where the *absence of findings* and the *absence of a scan*
produced the same green result.

## The mechanism

A typical guard is walk → match → fail-if-any-hit:

1. Walk a tree (source files, migrations, tables).
2. Apply a matcher (regex, SQL probe).
3. Exit non-zero if anything matched.

If step 1 walks the wrong directory, a glob stops matching after a refactor, or the
query returns zero rows because a connection failed quietly, step 3 sees zero hits and
passes. Nothing distinguishes "I looked and found nothing" from "I looked at nothing".

**The fix is a floor on the scan itself:** record how many units were inspected and fail
when the count is implausibly low (`MIN_FILES = 30`, "at least N tables probed"). The
floor is a cheap, explicit encoding of "this check has preconditions". Set it from the
current real count with headroom, and treat a floor trip as a configuration bug, not a
finding.

Two related rules from the same hardening pass:

- **Return exit codes, don't `process.exit` deep in the script.** A guard that exits from
  inside a helper cannot be composed with other guards or tested; return a status and let
  the entrypoint decide.
- **A rule enforced by a check that cannot see half its violations is not enforced.** A
  design-token lint found hard-coded hex literals but not the equivalent utility-class
  palette names, so most violations were invisible to it. Likewise, an accessibility audit
  that only inspects *rendered* states flagged 9 issues against ~150 static hits for the
  same contrast rule — the audit measured what rendered, not what the rule covers. Before
  trusting a check's zero, enumerate what it structurally cannot see and either widen the
  matcher or state the blind spot next to the rule.

## When it bites

- Smoke checks run against production right after deploy — the environment where a wrong
  base URL or missing credential turns every assertion into a vacuous pass.
- Row-count security probes (see [[Artifact Is Not Evidence: Push and Probe]]) — an empty
  result cannot distinguish "policy blocked me" from "table is empty".
- Any guard introduced to protect a rule nobody has violated yet: it has never produced a
  red, so its wiring has never been exercised.
- A guard adopted from a third-party rule. An "unused modules" lint rule could not run
  under the linter's current config format without a shim — and **with** the shim, a
  planted orphan module still passed clean. Caught by a negative test, not by reading
  docs; shipping it would have been a guard that always passes. It was replaced by a
  small script that builds the import graph itself, verified both directions (clean
  render exits 0 naming the module count; planted orphan exits 1 naming the file). Its
  first real run found a 229-line security module nothing imported.

## A gate that passed three ways while seeing nothing (token-lint, akira)

The raw-hex gate that came with a design-token migration hit this class three times
across three review rounds:

- **An empty but existing ROOT** printed `0 arbitrary colours in 0 files` and exited 0. A
  missing ROOT threw loudly. The dangerous case was a valid but wrong ROOT during a
  planned directory move.
- **Mutating `walk()` so it stopped recursing** cut coverage from 72 files to 2, and all 5
  tests still passed. The tests called the matcher on hand-written strings, and never
  exercised the walk or the entry point.
- **The fix for a false positive created a blind spot.** A lookbehind added to stop
  matching `#105` issue refs also stopped matching `var(--x,#1a1a1a)`, gradients and
  inline `style=`. All three compile to real CSS.

Once the entry guard was in place, a mutation test that disabled it now failed the suite.
Full write-up in [[One-Off Codemod, Permanent Gate]].

## The empty-array guard that inverted (restore drill, akira)

A drill verdict function failed the run when every probed table showed no evidence:
`local.length > 0 && local.every(noEvidence)`. The length clause was meant to stop `[].every()`
returning vacuously true. It inverted the intent instead. An empty `local` array, the purest
case of "verified nothing", made the guard false, so the run passed. The fix added a
**separate named field**, `noTablesProbed` (`local.length === 0`), OR-ed into `failed`. It
did not just delete the length check. "No table was probed" (a broken loop, an empty table
list) and "every probed table came back empty" (a truly empty restore) are different
diagnoses, and the operator needs to be told which one happened. The fixer then grepped the
file for every `length > 0` and `.every(` site to confirm there was no other instance of the
same shape.

## A Verification Grep for a Name That Does Not Exist (akira, 2026-09)

A plan justified deleting an enum branch by grepping for its only caller and reported
"only one in-order call". The grepped function name did not exist in the codebase (the real
export had a different name), so the grep returned nothing. The empty output was read as
confirmation. A refine pass reran it and found two tests the deletion would break, one of
them a 1,200-payload parity fuzz suite. **An empty grep is a scan of zero matches:**
before it counts as evidence of absence, check that the pattern matches the thing it is
meant to find ([[Differential Parity Testing Against the Original]]).

## See Also
- [[One-Off Codemod, Permanent Gate]] — instance-of (three review rounds on a raw-hex gate)
- [[Artifact Is Not Evidence: Push and Probe]] — extends (the probe-side version of the same blindness)
- [[Silent Fallthrough in String-Keyed Discovery]] — extends (same defect class: no error signal, confident wrong result)
- [[Verification Loops]] — part-of (a verifier that can vacuously pass is not a verifier)
- [[Write-Only Fields and the Reader Map]] — complements (both are audits of what a check or a column actually reaches)
- [[Landed Is Not Complete]] — instance-of (a conditional audit check over a population of zero, headlined VERIFIED)
- [[An Unrun Scan Is Not a Clean Scan]] — alternative-to (absence emitted as a `question` finding rather than enforced as a floor)
- [[Mutation Score Artifact from Zero-Test Runs]] — instance-of (mutants that ran zero tests read as Survived)
- [[Build the Checker Before the Generator]] — extends
- [[Every Registration Site Needs a Guard]] — extends (an arbiter test blind to three of five sites)
- [[A Check Must Say Why It Could Not Check]] — extends (the undiagnosed-failure half)
- [[Adoption Ban Needs an Escape Hatch]] — related (a contract with no budget reports a clean pass)
- [[A Secret Scanner Must Never Echo Its Match]] — instance-of (a client-bundle secret gate with a MIN_FILES floor and loud misordering)
- [[Restore Drill: Rebuild-from-Migrations Visibility Probe]] — instance-of (zero-tables-probed passed as clean)
- [[Single-Definition Grep Guard]] — instance-of (a grep pattern in the wrong regex dialect matched nothing)
- [[Render-Blind Test Layer]] — related (the token gate that was green while the contrast defect was live)
- [[Logger Redact Guardrail]] — instance-of (a stdout spy that could not see sonic-boom's writes)
- [[Characterization Pins Before Extraction]] — related (mutation proof that refactor pins are live)
- [[Differential Parity Testing Against the Original]] — related (the parity test a zero-match verification grep failed to find)
- [[Offline Pipeline Seed Harness]] — prerequisite-for (a no-duplicates assertion that passed vacuously on starved tables)
- [[Vacuous Check Turns Backwards on Policy Change]] — alternative-to (vacuous because nothing qualifies)
- [[Ambient Tool Resolution Phantom]] — extends (the opposite error: a check that measured the machine, not the repo, and reported 6 phantom breaks)
