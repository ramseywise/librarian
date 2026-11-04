---
title: "Slicing Errors With Correction and the Rate Identity"
tags: [foundations, pattern]
summary: "Slice error cost by nameable subgroups with Wilson intervals, correct the scan for many tests, confirm on unread rows, and expect group error-rate gaps because FPR, PPV and FNR are tied by an identity."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--12-reading-the-errors.md
---

# Slicing Errors With Correction and the Rate Identity

A slice is a nameable subgroup. For each compute error rates with intervals and its share of total cost; the share is the ceiling on what a fix for that slice could gain (a slice with 33.1% of cost from a 590.0 base cannot save more than about 195 per 1,000, and only if every error vanished). Slices may use columns the model never sees. Continues [[Error Analysis by Confusion-Matrix Cell]].

## Scanning many slices

Test each slice's cost against the rest with Welch's t-test, then apply a false-discovery correction ([[Multiple Comparisons Corrections]]). On 21 slices of a 1,500-row eyeball set only 2 survived Benjamini-Hochberg, both slices where cost was low. BH compares the i-th smallest p-value with q x i / m: for p = 0.015 as third of 21 at q = 0.05 the cut is 0.0071, so it fails (it later held on unread data, so BH was cautious on the small set).

- Use Wilson intervals; Wald intervals fail on small counts ([[Confidence Interval Coverage and Wilson]]).
- Small slices mislead: an FNR of 1.000 came from one defaulter in 20 rows. Partial pooling pulls small groups toward the overall rate ([[Small-N Trap and Shrinkage]]).
- An automated slice search runs a one-sided Welch test of each slice's loss against its counterpart, an effect-size threshold, and a false-discovery procedure; for interactive use, where the number of tests is not fixed, it uses alpha-investing instead of Bonferroni or BH. A single offline scan needs only BH.

## Confirm on unread rows

Same slices on a 4,500-row unread set: low limits cost more (under 50k: 709.4 eyeball, 624.268 unread), high limits less (240k+: 422.969 and 431.9), people two or more months behind cost least (372.093 and 288.2) because all are declined and 71% default. High-school education (715 to 605) and bills near the limit faded. Slices surviving BH rose from 2 of 21 to 7 of 21, because a larger set has more power; this is one reason the unread set is bigger. Calibration inside slices held (under 50k: score 0.310, default 0.314; 240k+: 0.144 and 0.130).

## Group error rates are tied by an identity

A model that never sees a column can still show error gaps across it, since groups differ on features and base rates. With prevalence p:

FPR = p/(1-p) x (1-PPV)/PPV x (1-FNR)

On the unread set, by a column the model does not use: men n 1,773, prevalence 0.237, PPV 0.408, FPR 0.342, FNR 0.240; women n 2,727, prevalence 0.211, PPV 0.379, FPR 0.318, FNR 0.273 (Wilson FPR intervals 0.317 to 0.368 and 0.299 to 0.338, overlapping). Check for women: 0.267 x 1.639 x 0.727 is about 0.319 against 0.318 observed.

Consequence: if PPV is equal across groups but prevalence differs, FPR and FNR cannot both be equal. You choose which equality to keep. The result concerns equal precision at a threshold; calibration does not imply it, since well-calibrated scores can fail predictive parity at a given threshold. Which gap is acceptable in lending is a legal and policy question, so report the numbers to those who decide. Dropping a column from the inputs does not stop it mattering, so report rates across barred columns.

## See Also
- [[Multiple Comparisons Corrections]] — prerequisite-for
- [[Confidence Interval Coverage and Wilson]] — prerequisite-for
- [[Eyeball and Blackbox Sets and Fixes That Fit the Reading]] — related
- [[Post-Treatment Segments and Simpson's Paradox]] — related
