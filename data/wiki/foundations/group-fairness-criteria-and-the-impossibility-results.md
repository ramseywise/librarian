---
title: "Group Fairness Criteria and the Impossibility Results"
tags: [foundations, concept]
summary: "Demographic parity, equal opportunity, equalized odds, calibration and predictive parity ask different questions; with unequal base rates and an imperfect score they cannot all hold, so someone must choose and own the metric."
updated: 2026-11-09
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--15-fairness-in-automated-scoring.md
---

# Group Fairness Criteria and the Impossibility Results

An audit does not find out whether a model is fair; it states which gaps exist, how sure you are, which label they were measured against and what closing each would cost. Skip that and you ship whichever definition your default happened to satisfy. Numbers here come from a generated screening task (80,000 applicants, three groups of 70%, 24% and 6%, plus a binary attribute; top 20% advance; differences were planted so an audit has something to find, so they describe the generator, not any real group). Measurement practice is in [[Auditing Selection Rates With Intervals and Intersections]]; labels, proxies and mitigations in [[Label Bias, Proxies and the Cost of Mitigation]].

## The criteria

Selection rate is the share advanced; impact ratio is a group's rate over the highest group's. TPR and FPR are the shares of truly qualified and unqualified people selected.

| Criterion | Equality of | Needs true outcome | Fails when |
|---|---|---|---|
| Demographic parity | Selection rate | No | Base rates differ and the score is accurate |
| Equal opportunity | TPR | Yes | Qualified people in one group are passed over more |
| Equalized odds | TPR and FPR | Yes | As above, or unqualified people in one group get through more |
| Calibration within groups | P(outcome given score) | Yes | Label is biased (it is calibration only against the label held) |
| Predictive parity | PPV at a cutoff | Yes | A calibrated score does not guarantee it at a cutoff |

A perfect predictor always satisfies the odds criteria; parity says nothing about who within a group is selected and methods reaching it indirectly can reorder people within a group. A toy 16-person table (8 per group) shows the arithmetic: group A selection 0.50, TPR 0.75, FPR 0.25, PPV 0.75; group B 0.25, 0.50, 0.17, 0.50. B's rate is half of A's and its TPR two-thirds; all numbers are right and answer different questions.

## Impossibility, in numbers

**The rate identity.** In each group with base rate p, FPR = p/(1-p) x (1-PPV)/PPV x (1-FNR) follows from how a confusion table adds up ([[Slicing Errors With Correction and the Rate Identity]]). Groups sharing PPV and FNR but differing in p cannot share FPR: p 0.4 and 0.3 with PPV 0.6 and TPR 0.7 give FPR 0.311 and 0.2. It concerns predictive parity, not calibration.

**The score-level result.** Let x be the mean score among people without the outcome and y among people with it. Calibration forces (1-p)x + p y = p, i.e. x + p(y-x-1) = 0. For two different p to share one x and one y (balance, equalized odds on the score) both terms must vanish: x = 0, y = 1, the perfect predictor. Hence calibration plus balance needs perfect prediction or equal base rates, and an approximate version means being nearly fair on all three does not rescue it.

On a score trained on 5,000 audited work-sample outcomes (no proxies, recalibrated per group; base rates 0.345 and 0.265; x 0.279 and 0.202, y 0.486 and 0.404), four decision rules on test:

| Rule | sel A | sel B | PPV A | PPV B | FPR A | FPR B | FNR A | FNR B |
|---|---|---|---|---|---|---|---|---|
| One cutoff 0.45 | 0.308 | 0.173 | 0.621 | 0.601 | 0.178 | 0.094 | 0.446 | 0.608 |
| Equal PPV (0.62) | 0.309 | 0.152 | 0.621 | 0.616 | 0.179 | 0.080 | 0.444 | 0.646 |
| Equal TPR | 0.257 | 0.228 | 0.653 | 0.565 | 0.136 | 0.135 | 0.514 | 0.514 |
| Equal TPR and FPR (randomised) | 0.196 | 0.173 | 0.686 | 0.601 | 0.094 | 0.094 | 0.609 | 0.608 |

Equalising PPV leaves B's miss rate 0.646 against 0.444; equalising TPR and FPR spreads PPV 0.686 against 0.601. The identity holds exactly in every row. Equalized odds may need different, possibly randomised, thresholds because group ROC curves cross at few points; here it brought A down to B's point (selection 0.308 to 0.196, miss rate 0.446 to 0.609, with coin flips deciding some) while B gained nothing: **levelling down**. Ask whether a coin flip deciding someone's job is defensible. Set the planted skill gap to zero and one-cutoff FPR reads 0.178 and 0.158, FNR 0.445 and 0.463: the conflict shrinks once base rates match.

Fairness is a social and ethical concept, not a statistical one: someone accountable chooses the primary metric with the people who own the decision and writes down why. Asked for one number that shows the model is fair, answer that none exists; offer the table of ratio, error rates and quality across alternatives, the label each used, and the limits.

## See Also
- [[Classification Metrics, Confusion Matrix and Thresholds]] — prerequisite-for
- [[Probability Calibration and Reliability Curves]] — prerequisite-for
- [[Auditing Selection Rates With Intervals and Intersections]] — extends
- [[Label Bias, Proxies and the Cost of Mitigation]] — extends
- [[LLM Bias and Fairness Survey]] — related (applies group and individual fairness to LLMs)
