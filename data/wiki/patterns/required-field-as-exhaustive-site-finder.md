---
title: Required Field as Exhaustive Site Finder
tags: [patterns, infra, pattern]
summary: "When a new field must reach every construction site of a type, add it as required, not optional: the compiler then lists every literal that needs it, a repo-wide grep of a sibling field cross-checks the list, and a compile failure is treated as a missed site to fix — never as a reason to make the field optional, which would let a site silently default and recreate the dead-input bug the field was added to fix."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-dis392-s4-reputation-flag.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-25-dis392-b130-s3.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-25-dis392-b130-s3.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-25-dis392-b130-s3.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-25-dis392-b130-s3.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-25-dis392-b130-s3.md
---

# Required Field as Exhaustive Site Finder

Used twice in the same week in a TypeScript ranking codebase (repo akira, 2026-09-25),
both times to fix the same class of problem: a scoring input that was "wired" in one
place but silently absent in another.

## The move

1. Add the new field to the type as **required** (`place_subtype: string | null`,
   `reputation_penalty: number`), not optional.
2. Run the type-checker. Every object literal that builds the type now fails. That is
   the list of sites.
3. Cross-check with a repo-wide grep for a **sibling field** that every literal already
   carries (e.g. `subtype_fit_penalty:`). The grep catches literals the compiler can't
   see, such as ones cast `as never` or with a different object shape that needs a
   human decision.
4. Fix each site deliberately. Pass the real value through, compute it, or write a
   static `0` where that component never computes the term, with a reason.

The plan wrote the rule into Risks: **a compile failure is a missed site to fix, not a
reason to make the field optional.** An optional field defaults to `undefined` at every
missed site, which is exactly how a modifier ends up dead in one code path (see
[[The Eval Harness Has Its Own Adapter]]).

## What it cost and caught

- Widening a `Modifiers` type for a new capped penalty touched about ten files: 9
  compiler errors across 8 files, plus the grep pass. One file the grep surfaced was
  correctly excluded because its object had a different shape. Another had zero
  compiler errors because its literals passed through `as never`, so it was updated by
  hand.
- Adding a field to the eval corpus type surfaced two hand-built test builders that
  needed a default.
- The trade is a large review diff in exchange for **no silent miss**. The plan named
  that trade in its Approach section.

## Pairing it with red-then-green

For the new penalty's regression test, the builder deleted the penalty term from the
modifier sum, confirmed the new test **failed**, then restored it and confirmed it
passed. A test that has never been seen failing has not shown it tests the term.

## See Also
- [[The Eval Harness Has Its Own Adapter]] — related (the dead-input bug this prevents)
- [[Characterization Pins Before Extraction]] — related (compiler and tests as a refactor safety net)
- [[Specificity-Adaptive Ranking and Slate Composition]] — instance-of (the reputation penalty that widened the modifier stack)
- [[Kiez Project]] — instance-of
