---
title: UNGATED Metric Convention
tags: [eval, pattern]
summary: Every eval metric exists from day one, but a threshold is written only from a *measured* pass rate — until then the metric runs and reports UNGATED rather than being silently skipped, and the CI gate degrades to heuristic-only when judge credentials are absent instead of failing.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/akira/docs/plans/2026-09-04-dis60-lighthouse-ci.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-04-dis60-lighthouse-ci.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-04-dis60-lighthouse-ci.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-04-dis60-lighthouse-ci.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-04-dis60-lighthouse-ci.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-04-dis60-lighthouse-ci.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-04-dis60-lighthouse-ci.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-05-dis168-skip-link-targets.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-05-dis168-skip-link-targets.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-05-dis168-skip-link-targets.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-05-dis168-skip-link-targets.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-05-dis168-skip-link-targets.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-05-dis168-skip-link-targets.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-05-dis168-skip-link-targets.md
  - data/raw/claude-docs/ai-project-template/docs/research/2026-08-29_diskoe-parity_template-conventions.md
  - data/raw/claude-docs/kiez/docs/enrichment.md
  - data/raw/claude-docs/akira/docs/research/2026-09-20-dis264-dis277-enrichment-verification.md
  - data/raw/claude-docs/kiez-archive/docs/research/2026-09-20-dis264-dis277-enrichment-verification.md
  - data/raw/claude-docs/diskoe/docs/research/2026-09-20-dis264-dis277-enrichment-verification.md
  - data/raw/repos/ai-project-template/.claude--docs--in-progress--genesis-dryrun--friction-log.md
  - data/raw/repos/ai-project-template/.claude--docs--in-progress--genesis-dryrun--render-review.md
  - data/raw/repos/ai-project-template/.claude--docs--in-progress--production_hardening--plan.md
  - data/raw/repos/kiez/CLAUDE.md
  - data/raw/repos/kiez/README.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-29-checktargets-fail-closed.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-29-checktargets-fail-closed.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-29-checktargets-fail-closed.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-29-checktargets-fail-closed.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-29-checktargets-fail-closed.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-29-checktargets-fail-closed.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-29-checktargets-fail-closed.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis375-venue-probe-eval-metric.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis375-venue-probe-eval-metric.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis375-venue-probe-eval-metric.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis375-venue-probe-eval-metric.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis375-venue-probe-eval-metric.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-03-dis63-momentcontext-versioning.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-03-dis63-momentcontext-versioning.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-03-dis63-momentcontext-versioning.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-03-dis63-momentcontext-versioning.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-03-dis63-momentcontext-versioning.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-03-dis63-momentcontext-versioning.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-03-dis63-momentcontext-versioning.md
  - data/raw/claude-docs/akira/docs/reviews/2026-09-05-dis141-five-plus-three.md
  - data/raw/claude-docs/diskoe/docs/reviews/2026-09-05-dis141-five-plus-three.md
  - data/raw/claude-docs/kiez-archive/docs/reviews/2026-09-05-dis141-five-plus-three.md
  - data/raw/claude-docs/playground/docs/reviews/2026-09-05-dis141-five-plus-three.md
  - data/raw/repos/akira/.claude--docs--reviews--2026-09-05-dis141-five-plus-three.md
  - data/raw/repos/diskoe/.claude--docs--reviews--2026-09-05-dis141-five-plus-three.md
  - data/raw/repos/playground/.claude--docs--reviews--2026-09-05-dis141-five-plus-three.md
  - data/raw/repos/playground/CLAUDE.md
  - data/raw/repos/nonprofit-success-ai/CLAUDE.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--research--ownership-plan.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--plans--2026-10-07-r10-eval-metrics.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--plans--2026-10-07-r6-pulse-e2e.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--plans--2026-10-07-r8-draft-persistence.md
  - data/raw/repos/nonprofit-success-ai/.claude--docs--plans--2026-10-08-r17-eval-run-1-fixes.md

  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-16-genesis-dryrun.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-16-genesis-dryrun.md
  - data/raw/claude-docs/ai-project-template/docs/plans/2026-07-16-production-hardening.md
  - data/raw/repos/ai-project-template/.claude--docs--plans--2026-07-16-production-hardening.md
  - data/raw/claude-docs/guacamayo/docs/plans/2026-07-18-skills-refs-evals-norm.md
  - data/raw/repos/guacamayo/.claude--docs--plans--2026-07-18-skills-refs-evals-norm.md
  - data/raw/repos/diskoe/CLAUDE.md
  - data/raw/claude-docs/akira/docs/plans/2026-08-27-b18-eval-harness.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-08-27-b18-eval-harness.md
  - data/raw/repos/akira/.claude--docs--plans--2026-08-27-b18-eval-harness.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-08-27-b18-eval-harness.md
  - data/raw/claude-docs/playground/docs/plans/2026-08-27-b18-eval-harness.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-08-27-b18-eval-harness.md
  - data/raw/repos/playground/.claude--docs--plans--2026-08-27-b18-eval-harness.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-03-dis71-resultrationale-judge.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-03-dis71-resultrationale-judge.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-03-dis71-resultrationale-judge.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-03-dis71-resultrationale-judge.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-03-dis71-resultrationale-judge.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-03-dis71-resultrationale-judge.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-03-dis71-resultrationale-judge.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-10-dis223-source-rights-posture.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-10-dis223-source-rights-posture.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-10-dis223-source-rights-posture.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-10-dis223-source-rights-posture.md
  - data/raw/claude-docs/playground/docs/plans/2026-09-10-dis223-source-rights-posture.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-10-dis223-source-rights-posture.md
  - data/raw/repos/playground/.claude--docs--plans--2026-09-10-dis223-source-rights-posture.md
  - data/raw/claude-docs/akira/docs/plans/2026-09-24-dis392-s1-corpus-metrics.md
  - data/raw/claude-docs/kiez-archive/docs/plans/2026-09-24-dis392-s1-corpus-metrics.md
  - data/raw/claude-docs/diskoe/docs/plans/2026-09-24-dis392-s1-corpus-metrics.md
  - data/raw/repos/akira/.claude--docs--plans--2026-09-24-dis392-s1-corpus-metrics.md
  - data/raw/repos/diskoe/.claude--docs--plans--2026-09-24-dis392-s1-corpus-metrics.md
---

# UNGATED Metric Convention

Two independently built projects (diskoe, kiez) converged on the same eval discipline,
which is what made it a candidate for the shared template.

## The invariant

> Every scoring dimension and enrichment attribute needs an eval metric. Heuristic
> graders for deterministic functions, LLM judges for prose only. Thresholds come from a
> *measured* pass rate — unmeasured metrics stay commented and report `UNGATED`.

Three parts, each doing a separate job:

1. **Coverage is unconditional.** A new scoring dimension lands with its metric. The
   metric may have no threshold yet, but it exists and runs.
2. **Thresholds are measured, never guessed.** `targets.yaml` holds a threshold only
   after a pass rate has been observed. kiez states it the same way: fixtures are
   hand-authored from the spec's rule text, and "all ungated until a threshold is set
   from a measured rate."
3. **An ungated metric reports `UNGATED`.** This is the load-bearing word. A metric
   without a threshold is not skipped, hidden, or counted as passing — it prints a
   distinct state in the report so the gap is visible on every run. It is the eval
   analogue of recording a skipped reporter with its reason
   ([[Scope-Gated Reporter Dispatch]]).

The convention is a code pattern in the grading pipeline rather than a file, which is
why the template research recommended carrying it in the eval README rather than as
scaffolded source.

## Architecture it sits in

A single wiring point (`registry.ts` — every metric registers here), `targets.yaml` for
thresholds, graders split into `heuristic/` and `judges/`, fixtures as JSONL, and
`grade` / `report` pipelines. Hand-written fixture expectations come from the spec text,
not from running the code, so the fixture catches the code drifting from the document.

## The CI-safe eval gate

CI runs `eval:grade --gate` with a **blank** judge API key in the environment. Judge
metrics degrade gracefully to a heuristic-only run and the step exits 0; heuristic
thresholds still gate. This gives a merge-blocking eval step without spending on judges in
CI and without a credential dependency that would make the gate flaky.

## Gate the Grader, Not the Model

An enrichment verification split two numbers that had been reported as one. **Grader vs
human agreement** (1.0 over 45 cases) is a property of deterministic code and is gated.
**Model compliance** (28/30) varies run to run and stays UNGATED. Related rules from the
same pass:

- **Fixtures whose oracle is the function under test pass by construction.** They stay
  UNGATED until labels come from a human or the requirement. One label had been fitted to
  the constant it was checking and was relabelled.
- **Pick a threshold as the lowest value that flags every real case with zero false
  positives** on the labelled set. A duplicate-copy threshold moved 8 → 6 this way.
- **Use a round-robin stratified sampler** so small strata appear in every sample.
- **A notebook finding has to move into tested code before it can gate.**
- An environment override pointing at a dead gateway made a run silently use the wrong
  endpoint. Print the resolved endpoint at the start of every measurement.

## The Inexpressible Metric: a Custom-Grader Slot (genesis dry-run)

A template dry-run found the convention's inverse failure. The design interview let a
project name a primary metric that the template's fixed set of heuristic graders could not
express (a per-row agreement score from a domain-specific rubric). `targets.yaml`
accepted a threshold for it, and the gate printed `n/a — skipped` and went **green**. That
is a gated-looking line on a metric nothing measured. UNGATED-by-comment is honest.
UNGATED-by-skip, behind a threshold that reads as enforced, is not.

The fix was a **custom-grader slot**. A project registers
`@register("name") def score(golden_row, generated) -> float | None`, scores land in the
heuristic report's `custom_scores`, and the target check falls back to them before
declaring a metric absent. The production-hardening plan generalised the same idea: the
design interview's evaluation section feeds `targets.yaml` and the eval gate directly, so
"the design artifact binds the build instead of decorating it." A target with no grader
behind it should fail the gate, not skip it.

## Unmeasurable targets pass green

The opposite failure: in a scaffold whose design targets flow design → `targets.yaml` →
`eval --gate` (exit 1 on miss), a target key with no matching metric was reported
"n/a — skipped" and the gate stayed green. A declared target the harness cannot measure
must fail or be registered explicitly; the fix was a custom-grader registry
(`@register` → `custom_scores`) so project-specific targets get a real metric.

### Both join directions, fail closed (akira, 2026-08)

The same hole in a TypeScript gate: `checkTargets()` looped over registered metrics and
never over `targets.yaml`. A target key with no registered metric was never visited — no
UNGATED line, no failure, no log, exit 0. A comment in the YAML documented the trap;
comments cannot enforce. The fix is a second pass over the target keys against the set of
registered keys, exiting non-zero and naming each orphan. The two directions are not
symmetric and must stay that way: *registered with no target* is the deliberate UNGATED
state (judge metrics awaiting calibration); *target with no metric* is the error. Guard
the script's `main()` behind an ESM entry check (`import.meta.url` against `argv[1]`) so
`checkTargets` can be imported and tested directly.

## The same rule for performance budgets (akira Lighthouse CI, 2026-09)

The convention transfers beyond eval metrics. Lighthouse budgets were introduced at `warn`,
not `error`; thresholds are written from a measured floor on `main` (at least five CI runs)
and only ratcheted upward. Promotion to `error` waits until **every gated URL has been
measured** — a later accessibility plan found two of seven gated URLs had never produced a
score, so an `error` budget on them would have been an aspirational number dressed as a gate.
Operational choices from the same plan: the job runs on push-to-`main` plus manual dispatch
only (on every PR it would roughly triple CI-minute overage), and it stays out of the local
`make gate` behind its own target. The first four green runs produced no readable reports at
all — see the artifact-upload instance in [[Silence Reads as Clean]].

## Zero activated targets: warn in CD, fail at readiness

The aggregate case is easy to miss. A scaffold ships `targets.yaml` **fully commented
out on purpose**, because its golden set is example data. So a fresh project's
`--gate` loads `{}` and exits 0 silently. That is a no-op that *reads* as enforcement.
Two obvious fixes are both wrong. Seeding default thresholds asserts a bar against
example data. Hard-failing blocks the first canary build, so deploy iteration becomes
hostage to eval setup.

The resolved contract splits enforcement across stages ("see it early, block late"):

- **CI** runs the gate as a non-blocking signal.
- **CD** runs it inside the canary job before the image build, with a harness flag
  (`--warn-empty`). When no targets are activated, it prints one loud banner saying the
  gate is not enforcing, then passes. A real activated target that misses still exits 1.
- **The readiness audit** (`/deploy-check`) treats zero activated targets as a FAIL. A
  project is not launch-ready until at least one target is real.

Net effect: **CD never green-washes and never blocks the first canary, and the readiness
audit holds the real line.** Once real targets are uncommented, the same step starts
enforcing with no further wiring. The flag was put in the harness rather than as a
`grep` in workflow YAML so the logic stays testable. By default the gate runs only the
free, deterministic heuristic layer, so it needs no API key.

## Filling the registry from the unit suite (akira B-18)

One plan wired every uncommented `targets.yaml` key with a heuristic grader and a JSONL
fixture, then uncommented the CI gate. That was 15 keys, not the 13 in the issue, because
two had been added since. Fixtures were *lifted from the existing Vitest golden cases*
rather than invented, 5–15 per metric, and every target gated at 1.0, so any miss is a
regression against written behaviour. Lessons:

- **A grader cannot do what a test's mock did.** The QC test mocked the model. The grader
  had to call only the synchronous parse path and check its output shape, never the
  model-backed function.
- **Uncomment the gate last.** A grader with the wrong argument shape passes 0.0 forever.
  Enable the gate only after every metric has been observed at 1.0, or it blocks every PR.
  Run the grade after each metric is added, not at the end.
- **Collapsing assertions loses granularity.** A vocabulary grader folds many checks into
  one `isCorrect`. When it fails, the unit test is where you find out which check broke.
- **The registry comment drifts from the targets file.** Count keys from the file, not
  from a comment or the issue text.
- Lifted fixtures share their oracle with the unit tests, so they are a regression layer,
  not independent evidence. The spec-text fixtures above are the stronger form.
- The κ-dependent judge metrics stayed commented until the human ceiling arrived
  ([[Human Agreement Ceiling Protocol]]).

## Registry before threshold (first judge metric)

The first concrete judge metric's plan ordered its steps around the inert-key hole above:
the registry entry lands two steps before the observed threshold is written into
`targets.yaml`, so following the plan in order cannot reach the silent no-op. The
threshold that was already in the file (`0.8`) had been typed once and never checked, so
it was treated as a hypothesis to test rather than a value to carry forward. See
[[Positive-Only Judge Fixtures Measure Recall]] for what such a fixture set can measure,
and for the live run that graded zero cases.

## A new vocabulary value is a fixture, not a metric (akira, 2026-09-10)

Adding `business` to the `audience_fit` vocabulary looked like it needed eval coverage
of its own. Three registered metrics (validation, sanitize, flatten) already read
`audience_fit` generically, and all three were gated at 1.0 on measured rates: 1,200-payload
parity runs for two of them, 28 fixtures for flatten. A fourth "is `business` accepted"
metric would have shipped UNGATED with nothing to ever observe. The structural question it
asked was the one the existing three already answer. The plan called that "process
theatre" and added fixture cases using the new value to the three existing metrics. Before
registering a metric, ask whether it has a behavioural question left to measure.

## Three postures, and the grader that agrees with itself (akira, 2026-09-24)

A corpus-metrics plan named the three legitimate gating postures in one place:

| Posture | Example | Gate |
|---|---|---|
| **Own function as oracle**: expected values recorded by running the real function once | input shaping, ranking eligibility | UNGATED (a 1.0 proves fixture fidelity, not correctness) |
| **No measured baseline**: the rule is sound, but no real-corpus rate has been observed | QC verdict, interaction coverage, per-tier field population | UNGATED |
| **Hand-fixtured against rule text**: expected values worked out from the spec before the code ran | precheck, date density, a slate-flatness check | GATED at 1.0 |

A slate whose scores are all equal within the ranker's tie epsilon is a **structural**
failure, so its grader was hand-fixtured (including boundary rows either side of the
epsilon) and gated. Field population stayed UNGATED because enriched and probed tiers are
different populations by construction, so one target across tiers would compare unlike
things.

The same plan caught a grader tautology at execute time. As first written, `isCorrect`
compared recomputed booleans to an `expected` that the same arithmetic had produced at
export time. It read 1.000 on every row, forever. Computing pass/fail from the input alone
gave 0.475, which moves with the data. If `expected` and the grader share an arithmetic,
`expected` can only be a fixture-integrity cross-check, never the pass condition. See
[[Dead Modifier Trace]] for the trace that ran alongside it.


## Grade Against the Weaker Real Truth (akira, 2026-09-24)

A venue-probe metrics plan assumed an independent human review of 40 rows would be the
ground truth for the verdict combiner. When checked, that review covered **v0** of the
probe and used continuous scores, so it did not exist in a usable form. The plan did not
fabricate a stronger oracle. It graded the verdict against the **judge's recorded `pass`
bit**: weaker, but real and independent of the combiner. That gave 33/40, a number that
can move. The heuristic-flag metric scored 40/40, but only against its own recorded output.
That is fixture fidelity (the "own function as oracle" posture above), and both shipped
UNGATED. The grading code was moved to a lower layer for import rules, with a re-export
shim so existing callers kept working.

## Literals Make an Oracle, a Shared Constant Makes a Mirror (akira reviews, 2026-09-03/05)

Two early review rounds bracket the question of what a grader may import from production.

- **Pinning literals keeps the grader independent.** A versioning metric's grader compared
  against the literal `'mc_v1'` and never imported the production version constant. When
  a reviewer bumped the constant to test it, the metric fell to 0.889 and the gate failed,
  which is the behaviour you want. A test table typed as `Record<Union, …>` made each new
  union member a compile error. An array would have stayed silently partial.
- **A grader fitted to its own fixtures cannot fail.** A ranking metric gated at 1.0 had
  weights tuned against the same fixtures it graded. It was ungated. The grader also
  hard-coded a 0.45 cut-off instead of importing the production threshold. Importing it
  would fix the drift but make the grader **blind**: grader and implementation would move
  together. Before re-gating, the plan has to assert absolute score bands per label
  rather than "matches the threshold". The same round found a sort with no secondary
  key. The fix was an id tie-break, plus a comparator that really returns -1/1/0. Only
  the leakage reporter found the self-fit, because its dispatch named the
  implementer-as-fixture-author risk.

Rule: **a grader imports *inputs* from production, never the *decision* (constant,
threshold, version) it is meant to check.**

## The deterministic fallback is the baseline (validation bar for agent features)

A planning doc for a client agent platform set one bar for calling an LLM feature
"validated":

1. The deterministic fallback runs and is tested.
2. At least 20 hand-authored golden cases exist. They are never produced by the function
   under test, because that would make them a mirror and not an oracle.
3. Fallback and model are graded **on the same fixtures**, with the fallback's score as the
   baseline the model has to beat.
4. The gate threshold is set at the measured rate, not at an aspirational one.
5. Judge-scored metrics stay UNGATED.

Item 3 is the non-obvious one. Without a baseline from the fallback, a model score of 0.8
says nothing about whether the LLM adds value over the rule it would replace.

## See Also
- [[Observe-Mode Gate With a Named Enforce Trigger]] — related (the same plan's gate-side decision)
- [[Eval Maturity Ladder]] — extends (how a level-2 deterministic gate is kept honest while judges are still uncalibrated)
- [[RAG Eval Gate Contract]] — related (gate ownership; this page is about what an un-thresholded gate reports)
- [[Experiment Tracking Schemas]] — related (log-only-then-promote is the same idea for grader tiers)
- [[Golden Set Mechanics]] — related (fixtures authored from spec text)
- [[Gate vs Ship Make Targets]] — related (where the eval gate sits in the local loop)
- [[Kiez Project]] — instance-of
- [[Prototype Pipeline Handoff Signals]] — extends (naming GATED/UNGATED at execute time)
- [[Frozen Ranking Baseline from a Pure Ranker]] — instance-of (ranking and slate metrics registered on fixtures, thresholds deferred to an observed rate)
- [[Confidence That Is Not a Probability]] — instance-of (self-report vs self-report proxy registered ungated)
- [[Relevance Is the Score, Enrichability Is the Gate]] — instance-of (calibration against labels the score was built from)
- [[Eval Non-Determinism]] — extends
- [[Execute Every Toggle Configuration]] — related (the same template's other false greens)
- [[Silence Reads as Clean]] — instance-of (a skipped target reads as a passed target)
- [[Scan-Floor Guard Against Silent No-Op Checks]] — related (an empty gate passing vacuously, answered with a warning plus a later hard stop)
- [[Positive-Only Judge Fixtures Measure Recall]] — extends (the first judge metric: what all-positive fixtures measure)
- [[Mask Permitted Spans Before Measuring Copying]] — instance-of (the verbatim grader shipped ungated)
- [[Dead Modifier Trace]] — related (the same slice's diagnosis-only trace and its grader tautology)
- [[Own-Oracle Fixtures and the Blind Relabel Path]] — extends (how an own-oracle metric earns its threshold)
- [[Fixed-Rule Clusters With a Degeneracy Gate]] — extends (a hand-fixtured shape check that may gate)
- [[Closed Judge Vocabulary, Tolerant Parse]] — related (the closed defect vocabulary the venue-probe metrics import)
- [[Demote Judge Findings to Keyless Gates]] — extends (judge findings become keyless lints gated at 1.0; judge keys stay commented until the calibration floor)
