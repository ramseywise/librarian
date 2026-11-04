---
title: "Per-Group Calibration Offsets by Partial Pooling"
tags: [foundations, pattern]
summary: "When groups share one score but differ in base rate, correct each group with one shrunken log-odds offset: a per-group threshold on few labels pays everything when none are positive, one global threshold ignores real differences."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--13-automate-review-or-reject.md
---

# Per-Group Calibration Offsets by Partial Pooling

A router serving many groups (customers, tenants) on one shared score faces different problem rates: a score of 2% may mean 1% in one group and 5% in another, so one set of thresholds ([[Review Route Thresholds From Priced Costs]]) pays too much for some and reviews too much for others. Fitting a threshold per group fails on few labels: 20 rows may hold no problem, and the fit says the group never has one, so pay everything.

## The method

Correct each group with one number, an offset delta_k added to the score's log-odds (a Platt fit with slope held at one), then apply the same price thresholds to the corrected probability. Estimate delta_hat_k from the group's labels with variance v_k. Estimate tau^2, how much groups truly differ, by moments: average of (delta_hat_k^2 - v_k) weighted by 1/v_k, floored at zero. Shrink:

delta_tilde_k = delta_hat_k x tau^2 / (tau^2 + v_k)

If groups do not differ, tau^2 is near zero and everyone gets the global answer (see [[Partial Pooling and Multilevel Models]]). With true offsets spread at 1.0, tau^2 came out at 0.958. A group with 5,000 labels has v_k near 0.003 and keeps almost all its offset; one with 20 labels has median v_k 0.628 and keeps about 60%.

Zero positives: at a rate near 7%, 19% to 31% of 20-label groups have none, and no finite offset fits; the pooled fit aims at half a problem and drops the group from the tau^2 estimate. Its v_k is about 2.1, so it keeps about 31% of an offset saying "fewer than average": mean -0.321 against -0.115 for groups with one problem. Zero reads as safer than one.

## Result (40 generated groups, 20 seeds; regret = extra cost per case over routing on the true probability)

Mean over group sizes (20, 50, 200, 1,000, 5,000 labels, eight groups each):

| True offset spread | One global threshold | Each group alone | Alone, global if no fit | Partial pooling |
|---|---|---|---|---|
| 0.0 | 0.000 | 0.357 | 0.076 | 0.000 |
| 0.4 | 0.059 | 0.470 | 0.075 | 0.024 |
| 1.0 | 0.421 | 0.323 | 0.102 | 0.068 |

At 20 labels the literal fit reaches 1.883 regret; sending no-fit groups to the global answer cuts 1.278 to 0.250 at wide spread, beating the global threshold's 0.387, but pooling still wins (0.166 at 20 labels). Pooling is at or tied for best in every row; its closest call (0.039 against 0.043 at 200 labels, wide spread) lost on 5 of 20 seeds, within noise. The global column should be flat; its variation (0.361 to 0.539) is noise.

## Limits

- The lab generates exactly the assumed shift in log-odds. If a group's score also ranks differently, one offset cannot repair it; compare its AUC on audited labels with the global AUC (not run).
- Shrinking to zero assumes the shared score is right on average; recalibrate it first (untested). A book of only small groups is untested.
- A live queue labels only what it was sent, so audit a random sample for small groups.
- Log which offset and thresholds decided each case.

## See Also
- [[Partial Pooling and Multilevel Models]] — prerequisite-for
- [[Small-N Trap and Shrinkage]] — prerequisite-for
- [[Review Route Thresholds From Priced Costs]] — extends
