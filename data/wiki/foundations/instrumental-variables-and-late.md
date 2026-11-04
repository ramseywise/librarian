---
title: Instrumental Variables and LATE
tags: [foundations, pattern]
summary: "An instrument moves treatment but affects the outcome only through it, so the Wald ratio of the instrument's effect on outcome over its effect on treatment recovers the effect for compliers despite unmeasured confounding; weak first stages and an untestable exclusion restriction are the failure modes."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--04-correlation-and-causation.md
---

# Instrumental Variables and LATE

When treatment is self-selected on an unmeasured trait, find Z that moves X and affects Y only through X. A randomised nudge, such as an invitation banner shown to half the users, is the standard analytics instrument.

## Mechanism

Wald ratio = (effect of Z on Y, the reduced form) / (effect of Z on X, the first stage).

Simulation (true effect of joining 3.00): OLS of spend on joining gives 8.80, inflated by unobserved keenness. The first stage: invitation raises joining by 0.558 (F = 18,372); reduced form 1.557; Wald ratio 2.79 (SE about 0.18). Two-stage regression on fitted join gives the same 2.79 but its reported standard errors are wrong; use a proper 2SLS routine.

## Assumptions and warnings

- Relevance: testable; report the first-stage F. A weak first stage makes the ratio unstable. A randomised invitation raising joining by 10 points and spend by 0.50 gives 0.50 / 0.10 = 5 per joiner; with a 1-point first stage the same spend effect would imply 50.
- Exclusion restriction and independence: untestable, argued from how the world works.
- The estimate holds only for compliers, the people the instrument moves (the local average treatment effect). Always-joiners and never-joiners tell you nothing.

## See Also
- [[Causal Design Selection Beyond Randomisation]] — related
- [[Potential Outcomes and Selection Bias]] — prerequisite-for
- [[Regression Discontinuity]] — related (another local estimate)
