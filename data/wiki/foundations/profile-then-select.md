---
title: Profile Then Select
tags: [foundations, pattern]
summary: Two-stage ML framing — a transform skill that profiles every column with stated thresholds and recommends without applying, then a select skill that refuses to pick a model family before the profile exists, treats "I don't know" as a first-class parked answer with a revisit trigger, and emits a draft (not confirmed) config when nobody is there to answer.
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/skills/ml-transform/SKILL.md
  - data/raw/claude-docs/galactus/skills/ml-select/SKILL.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-10-ml-capability-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-10-ml-capability-parity.md
---

# Profile Then Select

`/ml-transform` and `/ml-select` split a step that is usually done in one breath — "look
at the data, pick a model" — into two skills with a hard dependency, so the second cannot
run on impressions.

## `/ml-transform`: profile, then plan; never apply

- **Every column appears** in the output, including passthrough columns — a column that is
  missing from the plan is indistinguishable from one that was never examined.
- **Numbers, not adjectives.** "High cardinality" is `> 50 levels or > 5% of rows`;
  near-constant is `>= 99%` one value; rare-level floor is `1%`; strong imbalance is
  `< 20%` minority. A case no stated threshold covers goes to `## Unresolved`, not to an
  invented threshold.
- **Integer-as-categorical check** before any numeric treatment (zip codes, ids).
- **Missingness pattern decides the treatment:** MAR → impute; MNAR → indicator *and*
  impute; "value did not exist yet at prediction time" → leakage candidate, not a missing
  value. Check for an existing indicator column before adding one.
- **Degenerate floor:** when the rare-level rule would collapse a column to one level,
  target-encode inside the fold instead of collapsing.
- **SMOTE vs SMOTE-NC** is decided on *source* dtypes, not on the encoded matrix.
- The placeholder example deliberately contains no real figures: *"if a figure in your
  output matches one in this file, you copied it."*

## `/ml-select`: refuses to select before the profile

The skill will not choose a family without a profile on disk (exception: pre-data framing,
marked `Status: PRE-DATA`). It then walks seven questions with read-back; the ones that
carry non-obvious rules:

- **Q2 outcome vs effect.** Treatment columns present → the task is *uplift*, not
  propensity, and this is parked as blocking if the operator cannot confirm. *"A tool's
  coverage is not evidence about the problem"* — the fact that a classifier library is to
  hand does not make it a classification problem.
- **Q3 target definition and horizon** — "the most expensive available error, invisible in
  every metric": a target defined at the wrong horizon scores perfectly on itself.
- **Q4 decision sets metric.** Cost thresholds make calibration a *requirement*, not a nice-to-have.
- **Q5 time present → temporal split. Q6 grouping present → group split.**
- **Q7 cost asymmetry is business input, not a hyperparameter** to tune.

## "I don't know" is first-class

Unanswered questions go to `## Parked` with a **concrete revisit trigger**; a park with no
trigger is blocking. A parked value is never silently filled with a default — the config
gets a placeholder, a `provisional` mark, and the park entry. *"A value with a named
source is decided; a value with no source is a default wearing a decision's clothes"* —
hence `calibrate: true  # from the brief, §3`.

## Non-interactive runs produce a draft

When nobody can answer, the skill emits a **draft config** and says so; it does not mark
anything confirmed. *"Do not simulate consent."* This is the same abstention rule as
[[Auditable Track Router]]'s low-confidence branch.

## Why the profiling phase exists

The ML capability-parity research that led to these skills found the agentic pipeline
(design → research → plan → execute → review) had a spine that carried over unchanged,
but **no phase where the data is interrogated before the plan is written**. In agentic
work, research answers questions about the system being built. In ML the main risk is in
the data you were handed, and you find it by looking, not by reasoning. *"Planning an ML
project before profiling the data produces a plan against an imagined dataset."* So the
ML variant of the quick-start spike inserts profiling before planning. Its "failing test
that defines done" becomes a baseline metric plus a passing leakage check.

## See Also
- [[Deferred Decision Status]] — alternative-to (parked questions with revisit triggers, applied to ML config)
- [[Derived-and-Hidden Design Decisions]] — extends (every unstated threshold is a hidden decision)
- [[ML Frame Sourcing — License, Horizon, Prevalence]] — extends
- [[Auditable Track Router]] — extends (abstain rather than default)
- [[Assumption Audit]] — extends (defaults as a hiding place)
- [[Named-Trigger Deferral]] — instance-of (parked question with a concrete revisit trigger)
- [[Tabular ML Leakage Taxonomy]] — extends (leakage candidates resolved with the operator)
- [[Prototype Genesis Interview]] — alternative-to (demo-mode interview that withholds the profile until framing ends)
- [[Calibrated Score, Deterministic Decision Rule]] — extends (target definition before model choice)
- [[ML Stage Layering with Typed Contracts]] — prerequisite-for (parked questions travel in `RunConfig`)
