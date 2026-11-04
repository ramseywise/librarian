---
title: Backdoor and Front-Door Criteria
tags: [foundations, concept]
summary: "A set Z satisfies the backdoor criterion if it has no descendant of treatment and blocks every path into treatment; any valid set gives the same effect, and when the confounder is unmeasured the front-door criterion chains two identifiable effects through a mediator that carries everything."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--04-correlation-and-causation.md
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--05-matching-and-weighting.md
---

# Backdoor and Front-Door Criteria

A backdoor path is any path between X and Y starting with an arrow into X. A set Z satisfies the backdoor criterion if no node in Z is a descendant of X and Z blocks every backdoor path. The logic: block all spurious paths, leave directed paths from X to Y alone, create no new spurious paths. Then the effect is identified from observational data: P(Y | do(X)) = sum over z of P(Y | X, Z = z) P(Z = z), where do() means setting X rather than observing it.

## Consequences

- Only a sufficient set is needed; an unmeasured variable need not end the analysis if a measured one blocks its path.
- It is not simply "all confounders": a collider sometimes has to be adjusted, along with whatever blocks the path that opens.
- Any valid set gives the same answer. Two defensible sets that disagree mean one is wrong or the estimator is struggling.
- Propensity weighting does not relax this: weights are valid only if the covariates in the weight satisfy the criterion; otherwise they may add bias ([[Matching and Weighting Estimators]]).
- Post-treatment variables (a count of sessions after launch) fail by the descendant clause ([[Confounders, Mediators and Colliders]]).

## Front-door criterion

When the confounder is unmeasured, a mediator set Z can still identify the effect if (1) Z intercepts all directed paths from X to Y, (2) no backdoor path runs from X to Z, (3) all backdoor paths from Z to Y are blocked by X. Chain X on Z (no open backdoor) and Z on Y (backdoor blocked by adjusting for X): P(y | do(x)) = sum over z of P(z | x) sum over x' of P(y | x', z) P(x'), given positivity. In a linear model with a binary treatment it is a product of two slopes. Simulation: true effect 0.40 (0.5 x 0.8); naive difference 1.649; front-door 0.498 x 0.794 = 0.396.

It works because the graph was written to fit. In practice the hidden cause must have no direct link to the mediator and the mediator must carry all the effect, so it is rarer in analytics than the backdoor rule.

## See Also
- [[Confounders, Mediators and Colliders]] — prerequisite-for
- [[Matching and Weighting Estimators]] — extends
- [[Sensitivity Analysis for Unmeasured Confounding]] — related (what to do when the criterion cannot be met)
- [[Causal Design Selection Beyond Randomisation]] — related
