---
title: Calibrated Score, Deterministic Decision Rule
tags: [foundations, pattern]
summary: "A ranked score is not a decision: in tabular ML the model supplies a probability and deterministic code turns it into an action with a cost-based threshold. That makes calibration a correctness requirement, puts the target definition (ability vs propensity vs uplift) ahead of model choice, and makes logistic regression the required explainability floor."
updated: 2026-10-17
sources:
  - data/raw/claude-docs/galactus/docs/plans/2026-08-10-ml-capability-parity.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-10-ml-capability-parity.md
  - data/raw/claude-docs/galactus/docs/plans/2026-08-11-gal-4-phase2-ml-fraud-poc.md
  - data/raw/repos/galactus/.claude--docs--plans--2026-08-11-gal-4-phase2-ml-fraud-poc.md
---

# Calibrated Score, Deterministic Decision Rule

This came out of galactus's ML capability-parity research for a collections-style tabular
case study (who to contact about an unpaid balance). The finding that made the case study
fit the repo, instead of sitting next to it, was this: **the binding constraint is a
decision rule, not a model.**

## The thesis, carried across domains

The repo's generation case study reads *"counting characters is a job for code; the
model's job is content"*: a pure-function validator owns correctness, and the model's
cooperation is an optimisation, not a dependency. The tabular version is exact:

- The model produces a probability.
- The threshold that turns it into "contact this person" is **arithmetic** over the cost
  of a wasted contact versus the cost of a missed recoverable account. That cost is a
  business input, not a hyperparameter.
- So **calibration is a correctness property**. If the threshold uses the score, 0.7 has
  to mean roughly 70% will pay. Otherwise the arithmetic runs on a number that does not
  mean what it says.

The sibling voice research applied the same rule to a third domain: turn-taking,
confirming critical slots, and cancelling on barge-in are deterministic control problems.
The model supplies the content, and code decides when it may speak (see
[[Duplex Voice Breaks Discrete-Turn Assumptions]]).

## Define the target before choosing a model

- **Ability to pay vs propensity to pay** are different targets with different features.
  A model that mixes them ranks the wealthy above the willing, and spends effort on people
  who would have paid anyway.
- **Propensity vs uplift.** If past collection actions are in the data, a naive
  propensity model learns "accounts we chased, paid" and recommends chasing everyone. The
  real target may be uplift (the *effect* of contacting). The plan kept uplift modelling
  out of scope until that question was answered, because the answer changes the whole
  approach. [[Profile Then Select]] encodes the same check as a blocking interview
  question.
- **A bandit comes third, not first.** A contact-strategy bandit allocates *actions*, and
  only becomes workable once a calibrated score exists and outcomes are logged. Starting
  with it would solve the policy problem before the prediction problem.

## Model choice, settled by evidence

- **Logistic regression is the required baseline.** In a regulated domain it is the
  explainability floor. If boosting cannot beat it by a meaningful margin, that tells you
  something real about feature quality.
- **CatBoost before neural or foundation tabular models.** Benchmarks cited in the
  research show its advantage is largest on mixed-type, categorical-heavy data. Tabular
  foundation models lead single-model rankings, but CatBoost moves back ahead without
  multi-configuration ensembling, and it is cheaper to interpret, deploy, and defend to a
  regulator.
- **Text models only as feature encoders.** If free text exists (call notes), encode it
  into a few features for the tree model. Do not replace the tabular model with it.

## Sequencing: the leakage check before the library

The plan put the leakage review dimension and a data-profiling stage *before* building the
training library. Its reason: *"a library built without a leakage check is a faster way to
produce a confidently wrong model."* A leaked feature raises no error. It returns AUC 0.97,
which reads as success. See [[Tabular ML Leakage Taxonomy]].

## When the frame cannot support a threshold

The decision rule needs enough positive cases to choose an operating point from. On a
thin frame (14 positives, 2–3 per fold), the toolkit reported a cost-minimising threshold
with three-decimal precision that caught zero positives. The correct output there is a
refusal ([[Data Sufficiency Refusal]]). The constraint on a thin frame is evidence, not
compute: the whole run took about 12 seconds.

## See Also
- [[Confidence That Is Not a Probability]] — extends (calibration needs a real probability and a reader that acts on it)
- [[Data Sufficiency Refusal]] — extends (when no defensible threshold exists)
- [[Profile Then Select]] — prerequisite-for (the target-definition questions asked before model choice)
- [[Tabular ML Leakage Taxonomy]] — prerequisite-for (leakage check before the library)
- [[LightGBM vs CatBoost Comparison]] — extends (Brier/log-loss for calibrated scores)
- [[Build the Checker Before the Generator]] — instance-of (deterministic code owns the verdict)
- [[ML Stage Layering with Typed Contracts]] — prerequisite-for (training never chooses a threshold)
