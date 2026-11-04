---
title: Confounders, Mediators and Colliders
tags: [foundations, concept]
summary: "Control for a confounder, leave out a mediator if you want the total effect, and never condition on a collider; each mistake has a measured cost, and plotting the data beats trusting a single correlation coefficient."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--04-correlation-and-causation.md
  - data/raw/repos/learn-ai-engineering/data-analytics--03-experimentation-and-causality--notes--05-matching-and-weighting.md
---

# Confounders, Mediators and Colliders

Control for everything sounds cautious and is wrong. Whether a variable belongs depends on the causal graph, so draw it first.

| Variable | Path | Control? |
|---|---|---|
| Confounder | Z causes X and Y | yes |
| Mediator | X to M to Y | no, for the total effect |
| Collider | X to C from Y | no: conditioning creates a spurious X-Y link |

## Confounder

A shared cause makes X and Y correlate. A simulated temperature drives ice-cream sales and drownings: r = 0.517 (p = 2.2e-26). The partial correlation given temperature is 0.027 (p = 0.61); the regression coefficient falls from 0.0269 to 0.0026 with temperature included. Partial correlation and regression remove only measured confounders; randomisation breaks the arrow from all of them. See [[Regression Covariate Adjustment]].

## Collider

Admitting people on the sum of two independent scores: r = -0.013 across everyone, -0.682 among the 15% admitted. Any analysis limited to survivors of a filter has the risk (reviewers of purchased products, users who finished onboarding, customers still active). With a cutoff low enough that nearly everyone is admitted, the correlation returns to about -0.01.

## Mediator

A randomised coupon works by bringing people back. Total effect 1.921 (true 1.9); controlling for visits gives 0.331, only the direct part. Anything measured after treatment is suspect as a control, as mediator or as collider.

## A bad control that helped, and why the rule stands

In a loyalty-club dataset, adding a post-treatment sessions count halved the regression gap from 4.20 to 2.01 pounds, because sessions partly proxy an unlogged engagement trait and do not cause spend. In a second world where the club works through sessions (14.10 pounds per session, same true ATT 23.38), the same control cut the estimate to 0.79 and erased a real effect. The data cannot distinguish the worlds; the arrow from sessions to spend is an assumption. A pre-treatment proxy (sessions before launch) gives the benefit without the risk. The formal rule is [[Backdoor and Front-Door Criteria]].

## Describing association

Pearson r is linear and outlier-sensitive; Spearman uses ranks. One outlier moved Pearson from 0.985 to 0.583 while Spearman stayed 0.983. Four classic datasets share mean y 7.50, r about 0.816 and the line y = 3.00 + 0.500x yet look nothing alike (a curve, an outlier, a vertical stack). Plot before correlating; treat a correlation heatmap as a list of things to investigate. See [[Statistical Test Selection]].

## See Also
- [[Backdoor and Front-Door Criteria]] — extends
- [[Post-Treatment Segments and Simpson's Paradox]] — related
- [[Independence Pitfalls]] — related (shared cause makes correlation that vanishes when conditioned on)
- [[Potential Outcomes and Selection Bias]] — related
