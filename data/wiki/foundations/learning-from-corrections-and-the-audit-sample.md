---
title: "Learning From Corrections and the Audit Sample"
tags: [foundations, pattern]
summary: "A review queue only labels what the model chose to show, so silence is not confirmation and correction rate cannot separate a good model from a tired reviewer; measure with a random audit and retrain from audited labels."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--14-learning-from-corrections.md
---

# Learning From Corrections and the Audit Sample

Every correction is a free training label, but only for cases the model chose to show a person. Cases paid without asking are the ones most worth knowing about and nothing in the correction log mentions them. Setup is a simulated review router ([[Review Route Thresholds From Priced Costs]]) with a base rate of 6%; real-data limits are noted where they matter.

## Correction rate reads two things at once

Hold the model fixed, vary the reviewer's catch rate:

| Case | Reviewed | Correction rate | Problems in accepted | Final error |
|---|---|---|---|---|
| Strong model, catch 0.9 | 0.380 | 0.210 | 0.012 | 0.023 |
| Strong model, catch 0.6 | 0.380 | 0.213 | 0.049 | 0.036 |
| Strong model, catch 0.3 | 0.380 | 0.217 | 0.083 | 0.049 |
| Weak model, catch 0.9 | 0.468 | 0.182 | 0.011 | 0.024 |

The catch rate falls from 0.9 to 0.3, hidden problems rise nearly sevenfold, final error doubles, and the correction rate barely moves (it even rises): catching a problem the model would pay and waving through one it would reject both register as corrections. A falling rate can mean a better model, a worse model, or a reviewer who stopped looking; it says something changed, not what.

## Silence is not confirmation: audit a random sample

One month, 50,000 cases, strong model: paid 0.610, reviewed 0.379, rejected 0.012. Truth: error on paid 0.0137, problems among reviewer-accepted 0.0138, wrong final decisions 0.0232. Problems land 14.2% in paid, 71.5% in review, 0.143 in reject; the paid share is never seen. Audit design: 1% of paid, 1% of reviewer-accepted, 10% of auto-rejected, 500 draws:

| Estimator | Mean (5th to 95th) |
|---|---|
| Paid error, silence counts correct (10% of problems surface) | 0.0014 (0.0010 to 0.0017) |
| Paid error, random audit, careful auditor | 0.0138 (0.0034 to 0.0255) |
| Paid error, same reviewer audits | 0.0124 (0.0032 to 0.0241) |
| Final error, silence and acceptance count correct | 0.0008 |
| Final error, audit strata reweighted | 0.0233 (0.0151 to 0.0321) |

Silence is wrong by a factor of ten and narrowly so. The audit (530 of 50,000, 305 paid) is unbiased but noisy. A self-audit inherits the reviewer's misses, so use a second person or seeded problems. The sample must be random, chosen before anyone looks and independent of the score; a sample of suspicious cases measures how suspicious cases behave. Reject inference makes the same point: a model sees outcomes only for what it lets through.

**Audit size.** Error on paid 1.3%, drift to 3.3%, one-sided test at 5% false alarm: 100 audited has power 0.421, 300 has 0.775, 1,000 has 0.995 (3,000 currency units per period at the reviewer's price), 3,000 has 1.000. The rule of three bounds the error near 3/n after a clean audit, so 300 clean means only "under 1%". Normal approximation for 80% power, two-sided, both rates estimated: 878 per period ([[Confidence Interval Coverage and Wilson]]).

## The loop over eight months

Retrain monthly on the last four months; a new fraud type arrives in month 3 (case: any round-amount, or only those that otherwise look clean). Mean cost per case, months 3 to 8, audit cost included: audit 4.224, never retrained 5.370, reviewed-only 4.515, silence-correct 4.534, true labels 3.941 (hard version: 4.122, 4.954, 4.402, 4.515, 3.790).

- **Silence is correct** was not blind for good: by month 8 it paid almost none of the new type and cost nearly the same (3.905 against 3.890). Its harms: slower recovery (month 5 pays 33% of the new type against 1.1%; costs 0.311 more per case than a 5% audit on 8 of 8 seeds), a persistently higher paid error (1.7% against 1.2%), and a measurement ten times too low.
- **Reviewed only** never sees clean cases and by month 5 believes almost everything is risky: pays 3.6%, reviews 95.6%, costs 0.292 more than the audit.
- **Audit rate** (2% against 5%) made no measurable difference to retraining (+0.005 and -0.023, sd near 0.1): size it for the measurement, not the model.
- Retrain from something: never retraining costs 1.146 more (0.832 hard).
- Unexplained: the audit policy pays less than the true-label ceiling at month 8 (45.7% against 57.8%); auto-rejected cases and reviewer false alarms entering as problems is a plausible, untested cause.

## Failures as test cases

Thirty confirmed failures of a new class added to training three ways; share stopped on the suite, on unseen same-class cases, overall AUC and cost:

| Candidate | Suite | Unseen | AUC | Cost |
|---|---|---|---|---|
| Old model | 0.727 | 0.824 | 0.769 | 4.738 |
| Add the 30 | 1.000 | 0.967 | 0.813 | 4.146 |
| Add the 30, weight 50 | 1.000 | 0.989 | 0.862 | 3.873 |
| Add 3,000 audited | 1.000 | 1.000 | 0.846 | 3.864 |

All pass at 1.000 yet cost differs by 0.282: a suite of past failures can gate a release but cannot rank candidates; fresh data does. Someone had to look at paid cases to confirm those 30 failures ([[Eyeball and Blackbox Sets and Fixes That Fit the Reading]]).

## See Also
- [[Label Quality: Agreement, Noise and Confident Learning]] — prerequisite-for
- [[Choosing Which Rows to Label: Active Learning and Rules]] — related
- [[Drift Seen and Unseen in an Automated Router]] — prerequisite-for
- [[Review Route Thresholds From Priced Costs]] — prerequisite-for
