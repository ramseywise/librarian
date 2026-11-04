---
title: "Monitoring Layers and What Each Can See"
tags: [foundations, reference]
summary: "Operations, inputs, predictions and outcomes each catch a different failure; a drift score can fire loudly on a harmless input shift and read zero on an expensive new fraud type, so a random audit is what measures cost, and training on reviewed cases alone destroys automation."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-engineering--06-ml-platform--notes--06-ml-system-framing-to-monitoring.md
---

# Monitoring Layers and What Each Can See

| Layer | Watch | Catches | Cannot catch |
|---|---|---|---|
| Operations | errors, OCR failures, retry share and seconds | a broken step, new scan quality | a confident wrong answer |
| Inputs | field missing rates, new layouts, feature drift | a changed upstream feed | new fraud on normal-looking inputs |
| Predictions | paid share, predicted rate against rate seen | a calibration slip once labels arrive | anything before labels arrive |
| Outcomes | error on paid from audit, catch rate from seeded problems | what it cost | anything quickly |

## The input layer misleads (frozen model, invoice router)

| Change | PSI on the score | Error on paid |
|---|---|---|
| none | 0.001 | 1.4% |
| new fraud type on round-amount invoices | 0.001 | 3.3% |
| inputs shift (covariate) | 0.251 | 1.4% |
| base rate of problems doubles | 0.009 | 2.7% |

The drift score fires on the harmless change and reads what it reads for no change on the expensive one. Recalibrating does not rescue the fraud case (still 2.9%): a model cannot rank what it has never seen. Use input monitors to find broken pipelines and trigger a look; the audit tells you the cost (see [[Drift Triage: Broken Feeds, Benign Shifts and Concept Drift]], [[Population Stability Index]]). Also log training-serving skew samples, and the versions of upstream producers (OCR engine, supplier list), which change for their own reasons.

## The correction loop and what labels to train on

Corrections are biased because the model chooses what reviewers see (a direct feedback loop; mitigation includes some randomisation, i.e. a random audit chosen before anyone looks). Eight simulated months, new fraud type from month 3, mean cost per invoice months 3 to 8:

| Label policy | Cost | Note |
|---|---|---|
| true labels (unbuyable ceiling) | 3.941 | |
| audit 5% | 4.224 | recovers by month 5 |
| audit 2% | 4.229 | same within noise |
| reviewed invoices only | 4.515 | by month 5 pays 3.6%, sends 95.6% to review |
| silence counts as correct | 4.534 | slower recovery |
| never retrained | 5.370 | stays blind |

Training on reviewed invoices only looks excellent (error on paid 0.7%) while destroying the automation: the model never sees clean invoices. Silence nearly caught up by month 8 (3.905 against 3.890) but costs 0.311 per invoice more over months 3 to 8 and mismeasures: it reported error on paid of 0.14% when the truth was 1.37%. The audit rate made no measurable difference to retraining; size it for the measurement needed. With 30 confirmed failures, three candidates all scored 1.000 on the suite while overall cost ran 3.864 to 4.146: a failure suite is a gate, not a ranking. Fix classes of errors, not rows.

## See Also
- [[Drift Triage: Broken Feeds, Benign Shifts and Concept Drift]] — related
- [[Learning From Corrections and the Audit Sample]] — extends
- [[ML System Design: Stages and Handoffs]] — related
- [[Drift Types and What Monitors Can See]] — related
