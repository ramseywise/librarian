---
title: Eval Falsifiability
tags: [eval, pattern]
summary: An eval that cannot fail measures nothing and fails green — test both directions (the negative case is load-bearing), make scripted providers derive output from their actual inputs, run eval at production config, validate fixture tables at load, and keep eval fakes conformant to the port.
updated: 2026-10-30
sources:
  - data/raw/claude-docs/galactus/skills/review-safeguards/SKILL.md
  - data/raw/claude-docs/galactus/skills/proto-harden/SKILL.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-16-dis290-frozen-ranking-baseline.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-16-dis290-frozen-ranking-baseline.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-16-dis290-frozen-ranking-baseline.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-16-dis290-frozen-ranking-baseline.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-16-dis290-frozen-ranking-baseline.md
---

# Eval Falsifiability

The galactus `review-safeguards` dimension calls this its highest-value check, because
the failure **fails green**. Nothing alerts. The headline number just stops being able to
move.

**Evidence case.** A prototype's grounding eval used a scripted provider whose drafts came
from a fixed word list, and that list had been written to match the fixtures. The grounding
rate was really measuring vocabulary overlap with a constant, so it could not drop. A
regression that stopped feeding the model its retrieved facts would have left the metric
unchanged.

## Checks

1. **Both directions are tested.** Every headline metric needs a test that a good input
   scores positive and a test that a bad input scores negative. The negative is the
   load-bearing one. Without it, the positive is unfalsifiable.
2. **Scripted providers respond to their inputs.** A harness double must derive its output
   from what it was actually prompted with (the facts in the prompt), not from constants
   authored to match the fixtures.
3. **Config parity with production.** The eval runs the same constants and budgets as the
   app, through shared definitions with thresholds passed in as parameters, not
   re-hardcoded. An operator override that changes production behaviour must change the
   eval numbers too. Otherwise the harness is measuring a configuration nobody runs.
4. **Fixture tables are validated at load.** A case table keyed by literal ids must fail
   loudly when a case is renamed or a required entry goes missing. Silently falling
   through to a default profile keeps printing plausible numbers while measuring nothing.
   The validator itself runs against the shipped fixtures in CI.
5. **Eval fakes conform to the port** (full signature). Otherwise the harness drifts away
   from the system it grades (see [[A Fake That Conforms to a Broken Seam]]).
6. **Judged fixtures must disagree with the system somewhere.** When a ranking metric
   (NDCG@5, bad-in-top-5) is built on hand-authored judged fixtures before real labels
   exist, a fixture set derived from (or written to agree with) the ranker's own output
   passes by construction. akira's frozen-ranking-baseline plan made it a merge
   condition: at least one fixture case must have judged grades that disagree with the
   ranker's actual order, and a test asserts `ndcg5 < 1` on it. A fixture set that fails
   that assertion is the leakage pattern and gets revised before merge. The plan named
   this the single highest-value review checkpoint for that build.

## Related routing

A safety invariant enforced only by a prompt sentence is the other high-value finding in
the same dimension. It is routed to the contracts dimension as a SANYI `BY-4`, not fixed
in place (see [[SANYI Change-Contract System]]).

## See Also
- [[Always-Red Check Carries No Signal]] — alternative-to (the mirror case: a check that can never pass)
- [[Falsifiable Hypothesis Gate]] — extends (falsifiability applied to the measurement, not the claim)
- [[Eval vs Test Distinction]] — prerequisite-for
- [[A Fake That Conforms to a Broken Seam]] — extends
- [[Prototype Hardening Pass]] — related (part of)
- [[Eval Suite Maintenance]] — extends
- [[Eval Ladder]] — extends
- [[Tested Decision, Untested Expression]] — extends (negative control on the unguarded run)
- [[Generation-Under-Contract Eval Harness]] — extends (scripted provider whose results must vary across cases)
- [[Fixture Eval Blind to the Swapped Component]] — extends (a fixture gate that never runs the model cannot fail when the model changes)
- [[Render-Blind Test Layer]] — extends (a unit-level axe test that cannot fail, deliberately not added)
- [[Single-Definition Grep Guard]] — extends (prove the guard red on the pre-fix tree)
