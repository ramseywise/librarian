---
title: Stepwise Selection and Overfitting on Noise
tags: [data-analytics, probability-and-statistics, concept]
summary: "Stepwise regression with more candidate variables than observations can fit pure noise almost perfectly, and its final model is biased and hard to read; check fit on separate data, or use the lasso or no selection."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch08-model-abuse.md
---

# Stepwise Selection and Overfitting on Noise

Stepwise regression selects variables automatically. Forward selection starts with none and repeatedly adds the most significant variable; backward elimination starts with all and drops insignificant ones one at a time. Reinhart's chapter 8 argues against it.

## The watermelon case

A published study rated 43 watermelons on a five-point scale by panelists and used 1,600 acoustic frequencies (1 to 1,000 hertz) as predictors with stepwise regression. It reported predicting 99.9% of ripeness variation, which Reinhart calls implausible for subjective ratings. With more variables than observations a perfect fit is possible even when there is no relationship. In Reinhart's own simulation, random measurements with zero correlation with ripeness were fitted with 99.9% accuracy by stepwise regression (code and seeds not given).

## Why the final model misleads

In underpowered studies a variable enters the model only if its effect was overestimated, so the model is heavily biased (truth inflation, [[Winner's Curse]]). Reinhart adds that an insignificant variable is not thereby shown to have no effect, since the study may simply lack power.

## Advice

- Avoid stepwise selection; consider the lasso or no variable selection.
- Check fit on a separate dataset or by cross-validation such as leave-one-out, where the model is fitted on all but one point and evaluated on that point.
- Be wary of reading a coefficient as what would happen if you intervened on that variable; in practice variables can rarely be changed while everything else stays fixed.
- Watch for confounders; random assignment is the cure. Cited reversals: 1986 kidney stone records (stones under 2 cm: open surgery 93%, PN 87%; stones of 2 cm or more: 73% and 69%; overall the order flips, PN 83% and open surgery 78%); Berkeley 1973 (12,763 applications; 44% of men and 35% of women admitted overall, yet significant bias against women appeared in just 4 of 101 departments and against men in 6); a 448-child meningitis study; and omega-3, where observational studies pointed to fewer heart attacks but a 2013 five-year trial with an olive-oil placebo found no benefit ([[Post-Treatment Segments and Simpson's Paradox]]).

## Limits

- The reference list is absent from the extract, so the watermelon study is unnamed, and Reinhart could not check its leave-one-out claim without the data.
- Reinhart notes that randomisation, and nothing observational, rules out unmeasured confounders.

## See Also
- [[Model Selection Criteria]] — related
- [[Regularisation as a Prior]] — related (the lasso)
- [[Explain vs Predict Modelling]] — related
