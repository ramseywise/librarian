---
title: A Clean Contract Review Is Only as Wide as the Contract
tags: [eval, llm, pattern]
summary: "A contracts review dimension that returns `[]` has only shown that no *written* rule was broken — when the contract declares no budget, scopes an invariant to two paths, or never names a rule that lives elsewhere, a clean verdict is an absent control, not a satisfied one, and a repeated clean-for-that-reason is a signal to amend the contract."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/reviews/2026-09-02-dis51-font-theme.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-02-dis51-font-theme.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-02-dis51-font-theme.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-02-dis51-font-theme.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-02-dis51-font-theme.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-02-dis51-font-theme.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-02-dis51-font-theme.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-dis52-route-boundaries.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-dis52-route-boundaries.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-dis52-route-boundaries.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-dis52-route-boundaries.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-dis52-route-boundaries.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-dis52-route-boundaries.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-dis52-route-boundaries.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-dis58-accessibility-sweep.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-dis58-accessibility-sweep.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-dis58-accessibility-sweep.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-dis58-accessibility-sweep.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-dis58-accessibility-sweep.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-dis58-accessibility-sweep.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-dis58-accessibility-sweep.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-04-dis142-redistribution-posture.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-04-dis142-redistribution-posture.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-04-dis142-redistribution-posture.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-04-dis142-redistribution-posture.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-04-dis142-redistribution-posture.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-04-dis142-redistribution-posture.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-04-dis142-redistribution-posture.md
---

# A Clean Contract Review Is Only as Wide as the Contract

The akira multi-dimension review ran a `contracts` reporter on every diff. It checks
the diff against a written change contract. Across one week of reviews, that reporter
returned clean four times for the wrong kind of reason:

| Diff | Why `contracts` was clean | What it actually meant |
|---|---|---|
| Font/theme change, adding a web-font dependency | The contract declares **no dependency budget** and no typography tunable | "An absent control, not a satisfied one". The same diff family passed this way two rounds running |
| Error/loading route boundaries that relaxed a lint rule | The rule lived in `CLAUDE.md`, not in the contract, so its weakening could only be cleared as "documented elsewhere" | An invariant missing from the contract can be relaxed with the contract reviewer having no grounds to object |
| A 12-file accessibility sweep | The contract's only accessibility invariant has `paths:` limited to two venue-claim files | The diff whose whole subject was accessibility had no contract entry to be judged against, even though the repo enforces axe assertions in the gate |
| Accessibility finding citing that invariant | The correctness reporter cited it, but no file in the diff fell under its paths | The citation did not hold. The contracts reporter checked independently and correctly returned clean |

## The rule

- **Record why a contracts reviewer was clean.** "No rule covers this surface" and "the
  covering rule holds" are different results. The first goes in a carried-forward
  "contract gap" note on the review, separate from the findings, so it isn't counted as
  coverage. See [[A Check Must Say Why It Could Not Check]] for the same idea in gates.
- **A rule the repo enforces belongs in the contract.** A rule enforced through lint,
  `CLAUDE.md` or the gate but not named in the contract is invisible to the reviewer that
  judges exceptions. Amend so that the next exception is *judged* rather than waved past.
- **Path scopes drift narrower than the repo's actual concern.** An invariant scoped to the
  files where it was first written stops covering the surfaces that later matter.
- **Contract changes are deliberate acts.** The reviews flagged the gaps and did not amend
  in-branch, because no contract change was requested for those branches.

## When the literal rule collides with a deliberate design (amend, with conditions)

A migration added three evidence columns, such as a terms URL and reviewed-at/by, that no
code read. The intended reader was a human using the SQL editor. That collides with
"every new column names its reader" ([[Every Column Names Its Reader]]). The review set out
three options, none of them free: build a reader (scope creep), drop the columns (but they
*were* the review tool), or amend the contract. The operator amended it. The rule now
admits a **named human** reader for evidence columns under two conditions. The migration
header must name who reads the column and for what decision, and the column must be
recorded in the data-stack map in the same branch.

The re-review was **briefed adversarially**, because an amendment written to clear a
finding is exactly the case that deserves scrutiny. It checked both conditions against the
tree rather than taking the amendment's word. It confirmed the conditions are what keep the
rule from excusing any dormant column, and that what stays unguarded was logged as debt.

## See Also
- [[Contract-Anchored Findings Get Fixed]] — extends (the converse: findings without a written rule are weaker, and so are clean verdicts)
- [[SANYI Change-Contract System]] — related (the contract the reviewer reads)
- [[Review Reporter Ground Rules]] — related (a bare `[]` without evidence is a non-response)
- [[An Unrun Scan Is Not a Clean Scan]] — related (a clean result from a check that had nothing to look at)
- [[Every Column Names Its Reader]] — related (the rule amended for human readers)
