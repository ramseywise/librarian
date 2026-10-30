---
title: Positive-Only Judge Fixtures Measure Recall
tags: [eval, pattern]
summary: "When a judge harness feeds each fixture's expected text to the model as the candidate and has no ground-truth label, a set of all-good fixtures measures only recall (does the judge accept honest output), never precision. Allow one calibration pass that edits only the prompt, never the fixtures. Watch for a null-on-error contract that hides a provider schema rejection as nJudge 0."
updated: 2026-10-30
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis71-resultrationale-judge.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-15-dis274-enrichment-judges.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-15-dis274-enrichment-judges.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-15-dis274-enrichment-judges.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-15-dis274-enrichment-judges.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-15-dis274-enrichment-judges.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-15-dis274-enrichment-judges.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-15-dis274-enrichment-judges.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis71-resultrationale-judge.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis71-resultrationale-judge.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis71-resultrationale-judge.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis71-resultrationale-judge.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis71-resultrationale-judge.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis71-resultrationale-judge.md
---

# Positive-Only Judge Fixtures Measure Recall

From akira's first concrete LLM-judge metric. It grades whether a short "why this fits"
rationale line is grounded in the event and the user's request. The plan was to write
the judge, the fixtures and the registry entry, and then replace an asserted `0.8`
threshold with an observed one.

## What the fixture set can and cannot measure

The judge base class has no way to compare the model's verdict with a label declared in
the fixture. A heuristic grader runs a function and checks its output against
`expected.shouldFail`. A judge fixture's `expected` field goes straight into the prompt
as *the candidate text to grade*. So the judge pass rate is simply the fraction of
fixtures the model marked correct. There is no way to encode "this one is supposed to
fail" without lying to the judge.

The plan therefore wrote ten hand-authored, defensibly grounded fixtures, and stated the
limit wherever the number lives (the registry comment and the `targets.yaml` comment),
not only in the plan:

- **Verified: recall.** The judge recognises known-good, rubric-satisfying snippets as
  good, so the rubric does not reject honest output.
- **Not verified: precision.** Nothing in the set is bad, so the judge's ability to
  reject a hallucinated or leaky snippet is untested.

An adversarial fixture set needs a ground-truth-label mechanism in the base class and the
case schema. A second judge will need the same mechanism. The plan treated building it for
one metric as the wrong order, and logged it as named follow-up work.

## One calibration pass, prompt only

The rule for a low observed rate was tightened to close any reading that allows tuning
until it passes:

- Calibrate only if the rate is **below 0.5**. Otherwise write the first-run number,
  even if it lands on the old guess. Matching the guess by coincidence is fine.
  Inheriting it without measuring was the bug.
- **Only the system prompt may change, never a fixture.** Editing a fixture's candidate
  or input so the judge agrees turns "the judge correctly rejected this" into "the
  fixture was fixed".
- **Only a demonstrated misreading qualifies.** An example is the judge flagging a field
  named one way in data and phrased another way in prose. If the reasoning shows the
  judge applied the rubric correctly and simply disagreed on the merits, that is a result.
- **Exactly one pass.** The second number is final whether it goes up, down or stays the
  same. If it is still low, write the true rate as a known-low baseline.

## The first real call found a base-class defect

The live run reported `nJudge: 0`. All ten `grade()` calls returned `null` under the base
class's documented contract, "on any call/parse error, return null". Calling the SDK
directly showed the cause. The shared verdict schema declared
`dimensions: z.record(z.string(), z.number())`. The AI SDK turns that into JSON Schema
with `propertyNames`, and OpenAI's strict structured-output endpoint rejects it with
`400 invalid_json_schema`. Removing that one field fixed the call.

No concrete judge subclass had existed before, so the shared schema had never met a real
API. The first subclass took the hit for every future judge. The plan's scope ruled out
editing the base class, so execution stopped and reported rather than patching shared
infrastructure from inside a single-metric plan.

The takeaways:

- **A null-on-any-error contract makes a configuration error look like "judges skipped".**
  `nJudge: 0` with a key present is a failure, not a skip. Gate on the count of graded
  cases as well as the pass rate.
- **Exercise a base class against the live provider before writing subclasses**, or at
  least in the first subclass's plan, as a step with a stop condition.
- **Order the wiring so the gate cannot no-op.** The registry entry lands before the
  threshold, because a `targets.yaml` key with no registered metric is silently inert.
  This is the join-direction hole described in [[UNGATED Metric Convention]].

## Follow-up: the next three judges

The next plan added per-attribute judges for subjective enrichment output (vibe tags,
energy, sociality). It applied the lessons above.

- **The base-class fix came first, as Step 0.** `dimensions` became
  `z.array(z.object({ name, value }))`, and `grade()` converts it back to
  `Record<string, number>`, so the public `GraderResult` shape did not change. The defect
  and the fix were both **proven offline**, by running the AI SDK's own schema converter
  (`zodSchema()`) and asserting that no `propertyNames` appears in the output. No API key
  was needed. That test first collided with a lint rule that bans provider-SDK imports
  outside the model layer. The fix was to re-export the converter through the model
  gateway rather than add an eslint exception. Refine reversed the earlier "shared-infra
  fix deserves its own plan" stance. A judge that returns 400 on every real call delivers
  zero live-judging capability under a "registered" label.
- **A shared base-class change reaches subclasses the plan never listed.** The array
  conversion silently broke the mock in a judge that had been added after the plan's
  research was written. Only the full-suite run caught it. When a base contract changes,
  the full suite is part of the change.
- **Trap negatives as a partial precision check.** There is still no ground-truth field.
  Each file has 7 shared positive cases plus 3 metric-specific traps, where the candidate
  value plainly contradicts the evidence (for example `["elegant","sophisticated"]` for a
  blacked-out warehouse rave). This tests whether the rubric rejects an obviously bad case.
  It does not test fine-grained precision on ambiguous ones.
- **Leakage was avoided by structure.** A fixture's `input` carries only source evidence,
  never another attribute's candidate value. Telling the vibe judge "energy: high" as a fact
  is the only real leakage path when the attribute has no correct answer.
- **One judge per attribute, not one multi-dimension judge.** Each attribute will get its
  own human ceiling (vibe and energy sit in the intrinsically subjective κ band, sociality
  nearer semi-objective). It will therefore get its own `0.8 × κ_HH` threshold. One combined
  judge would force a single threshold onto three ceilings.
- **The plan went stale before it was finished.** Two days after the plan was written,
  another issue deprecated `social_intensity` in enrichment output, so 0 of 22 sampled
  outputs carried it. The executor noticed while re-verifying vocabulary claims. It stopped
  rather than fixture a judge against a field the model no longer emits, and the judge was
  dropped. See [[Readiness Is Pinned to a Tree State]].

## Smaller decisions

- CI has no judge key, so landing the metric does not make it enforce in CI. The plan put
  that in the Makefile comment and the eval README so nobody assumed otherwise.
- Judge variance: a small model can PASS today and FAIL tomorrow on fixtures near the
  rubric boundary. Pinning temperature or averaging N calls was named as future work.

## See Also
- [[UNGATED Metric Convention]] — extends (measured thresholds, and the registry-before-target ordering)
- [[LLM-as-Judge Evaluation]] — extends
- [[LLM Grader Calibration Insights]] — related (calibrating the grader rather than the model)
- [[Eval Falsifiability]] — related (an eval with no negative case cannot fail in the precision direction)
- [[Silent Failure Catalogue]] — instance-of (null-on-error hiding a schema rejection)
- [[Blind Labels Judge No Prompt]] — related (the human labels these judges will be calibrated against)
- [[Human Verdicts as Judge Fixtures]] — prerequisite-for (human wrong verdicts add the negatives)
- [[LLM Judge Biases]] — extends
