---
title: "Drift Seen and Unseen in an Automated Router"
tags: [foundations, concept]
summary: "With a frozen router, covariate drift trips a label-free alarm while the error stays fine, whereas prior and concept drift can leave the alarm green and double the error on automatically paid cases; recalibration fixes only part."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--13-automate-review-or-reject.md
---

# Drift Seen and Unseen in an Automated Router

Freeze the router of [[Review Route Thresholds From Priced Costs]] and change the world three ways (terms from [[Drift Types and What Monitors Can See]]). score_psi is the [[Population Stability Index]] of scores against validation and needs no labels; recal refits Platt scaling on 10,000 fresh labelled cases.

| Scenario | Problem rate | PSI | Paid share | Error on paid | Cost | Cost after recal |
|---|---|---|---|---|---|---|
| No change | 0.061 | 0.001 | 0.602 | 0.014 | 3.339 | 3.345 |
| Prior: twice the problems | 0.114 | 0.009 | 0.575 | 0.027 | 5.116 | 4.632 |
| Covariate: newer suppliers, fewer matches | 0.117 | 0.251 | 0.385 | 0.014 | 4.399 | 4.378 |
| Concept: new fraud type | 0.078 | 0.001 | 0.607 | 0.033 | 5.181 | 4.747 |

- **Covariate drift** rings the alarm (PSI 0.251) but the router handled it: new cases are riskier and it says so, error on paid stays 1.4%. A true alarm, a fine router.
- **Prior drift** (PSI 0.009, "stable" by most playbooks) doubles error on paid to 2.7%.
- **Concept drift** (PSI 0.001; paid share and mean score unchanged) more than doubles error on paid to 3.3%. Only labels on automatically paid cases reveal it, and by construction nobody looks at those, hence the need to audit a random sample.

Recalibration repairs what a slope and intercept can: with twice the problems it restores error to 1.6% but the paid share falls to 23% and cost goes 5.116 to 4.632. With the new fraud type it lifts every score (paid share 25%) but error stays 2.9%, because a slope and intercept cannot single out the affected cases; that needs new labels and a retrain. With no drift, refitting moves paid share from 60% to 56% at almost no cost, since scores are dense near the pay threshold, so do not read a few points of movement in straight-through rate as news.

## See Also
- [[Drift Types and What Monitors Can See]] — prerequisite-for
- [[Population Stability Index]] — related
- [[Learning From Corrections and the Audit Sample]] — extends
