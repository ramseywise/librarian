---
title: Build the Checker Before the Generator
tags: [eval, llm, pattern]
summary: When output must satisfy a constraint, write the deterministic validator first and watch it go red — it is free to test, it fixes the definition of done before anything can weaken it, and it turns a vague failure into a mechanical repair instruction.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/guacamayo/skills/design-prototype/SKILL.md
  - data/raw/claude-docs/sisyphus/docs/plans/2026-08-08-ml6-genai-prototyping-loop.md
  - data/raw/repos/sisyphus/.claude--docs--plans--2026-08-08-ml6-genai-prototyping-loop.md
---

# Build the Checker Before the Generator

The instinct on a constrained-output problem (schema conformance, length limits, format
compliance, tool-call validity) is to get *something* generating and bolt validation on
afterwards. The prototype retrospective in guacamayo's `design-prototype` skill records the
inverse as the non-obvious call that generalised past the case it came from:
**whatever decides whether the output is acceptable should exist, and should be red,
before whatever produces the output.**

## Why it pays three times

1. **The validator is a pure function.** No model, no network, no cost. It can be fully
   tested in seconds while the generator is still notional, so the expensive component is
   the last thing built and the only thing debugged.
2. **It fixes "done" before anything can rationalise a weaker definition.** A contract you
   wrote first and watched fail cannot be quietly relaxed.
3. **It turns failure into a repair instruction.** A validator that returns *"shorten
   'headline' from 14 to at most 9 words"* hands the generator a mechanical fix. A
   generator built first tends to produce *"that didn't fit, try again"* — a retry, not a
   repair, and retries do not converge.

The deterministic layer, not the model, is what makes the guarantee.

## Evidence from the run

- The validator was green against its full test set before any LLM existed; two genuine
  defects surfaced from tests written first, both fixed in the source rather than the test.
- **Show the red.** The contract stage names the input that makes the test fail and shows
  it failing. After fixing a later bug, the new regression test was re-run against the
  *reverted* fix to confirm it actually failed — otherwise a test passing for the wrong
  reason is indistinguishable from one passing for the right one.
- **A green suite is evidence about the paths you tested and silent about the rest.** A
  role-separation bug survived a 259-test green suite because every test covered the store
  layer (where the filter worked) and none the API layer (where the filter was never
  passed). At the uncapped end, pick tests by architectural seam, not by count —
  validator, fallback and repair loop carry the contract, so they carry the tests.
- Honest status: the red-test-first ordering is *validated as useful* but *unvalidated
  under time pressure* — the run was uncapped, and the discipline's claim is that it
  survives when the clock bites.

## Stated as a design rule

A take-home prototyping plan deliberately left the generator unwired end to end until the
contract checker existed, with the reason written down: "a repair loop retrofitted onto a
working generator is a patch; a generator written against an existing contract is a
design."

## See Also
- [[Scan-Floor Guard Against Silent No-Op Checks]] — extends (a checker must also prove it ran)
- [[Silence Reads as Clean]] — extends (the green suite that was silent about the API seam)
- [[Asked vs Derived Scaffold Variables]] — instance-of (the same prototype skill's intake stage)
- [[Archived Skills Convention]] — extends (where the rule was preserved when the skill folded)
- [[Verification Loops]] — instance-of
- [[Generation-Under-Contract Eval Harness]] — extends (measuring repair convergence against the checker)
- [[Unit Tests Encode the Checker's Assumption]] — extends (a checker's own tests can share its blind spot)
