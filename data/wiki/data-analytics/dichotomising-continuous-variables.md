---
title: Dichotomising Continuous Variables
tags: [data-analytics, probability-and-statistics, concept]
summary: "Splitting a continuous measurement into two groups, at the median or at the cutoff with the best p value, throws away information and inflates false positives; use regression on the continuous variable or a cutoff fixed in advance."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch07-continuity-errors.md
---

# Dichotomising Continuous Variables

To dichotomise is to split a continuous measurement into two groups. A median split divides the sample into two equal halves. Reinhart's chapter 7 gives three costs. The first two are reported from footnotes missing from the extract; the third, the yacht ANOVA, is a hypothetical example.

## Costs

- **Lost information.** Reinhart says the loss of power and precision is comparable to discarding a third of the observations.
- **Cutoff hunting.** Searching for the cutoff with the lowest p value can multiply the false positive rate by as much as 10. Studies of breast cancer S-phase fraction in the early 1990s separated large from small fractions at the median or at the best-p cutoff; each looked significant, but none did after correction for multiple comparisons ([[Multiple Comparisons Corrections]]).
- **Spurious effects from correlated predictors.** In Reinhart's hypothetical, wealth and yacht length both predict health-care quality and are correlated. Splitting both at the median and running a two-way ANOVA finds a spurious effect for the irrelevant one, and how often depends on the test's power rather than the nominal 5%. A regression on the unsplit variables holds false positives at the expected level.

Regression estimates the marginal effect of each variable, such as the health impact of each extra pound of weight, not merely a contrast between the two sides of a chosen threshold.

## Advice

- Don't split a continuous variable arbitrarily; use a procedure that uses the continuous values.
- When a split cannot be avoided, decide it beforehand: copy one from comparable earlier work, or take an external standard such as a clinical definition.
- Never pick the cutoff that maximises significance.
- Prefer regression to dichotomised ANOVA when controlling for confounders.

## Limits

- The chapter has no data or simulation of its own; its quantitative claims rest on footnotes not in the extract.
- The yacht example is hypothetical.
- The chapter admits that even regression struggles to tell strongly correlated predictors apart.

## See Also
- [[Regression Covariate Adjustment]] — related (control for continuous confounders in the model)
- [[Double Dipping and Selection on the Test Data]] — related (searching for the best cutoff is selection on the outcome)
- [[Functional Form Misspecification]] — related
