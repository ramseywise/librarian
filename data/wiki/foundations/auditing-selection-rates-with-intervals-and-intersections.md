---
title: "Auditing Selection Rates With Intervals and Intersections"
tags: [foundations, pattern]
summary: "Report impact ratios with counts and delta-method intervals, never as a pass mark; small groups can read anything, and margins can all clear 0.8 while a pre-chosen crossing fails."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--15-fairness-in-automated-scoring.md
---

# Auditing Selection Rates With Intervals and Intersections

The first audit needs only decisions and a group column: selection rate per group and the impact ratio against the highest group. Always attach counts and an interval. The ratio's interval uses the delta method on the log ratio: se = sqrt(1/k1 - 1/n1 + 1/k2 - 1/n2), interval = ratio x exp(-/+ 1.96 se) ([[Delta Method for Ratio Metrics]]). Criteria this feeds are in [[Group Fairness Criteria and the Impossibility Results]].

Example (unaware model, group and attribute columns dropped, 20,000 test applicants, 20% advance): B against A 0.469 [0.430, 0.512] (515 of 4,817 against 3,178 of 13,937); C against A 0.806 [0.714, 0.910] (229 of 1,246). C's point clears 0.8 but the interval says "passes" is not what the data show.

## The four-fifths rule is a rule of thumb

A US federal employment guideline treats a rate under 80% of the highest group's as generally evidence of adverse impact, and in the same paragraph says smaller differences can still count when significant in statistical and practical terms, and greater differences may not when based on small numbers. It is not a pass mark (0.82 is not compliance), not a finding of discrimination (disparate impact opens an argument about job-relatedness and alternatives), and not portable: it has no validity outside that context, so do not report it as a standard for loans, content ranking or the EU, whose text names no such number. Its legal status was changing as of 2026-11-04 (a rescission was under review, not concluded; the statute remains), so check before relying on it; this is engineering, not legal advice. One city's audit rules require selection rate and impact ratio by sex, race and ethnicity and their intersections, an audit under a year old with published results, no pass threshold in the text, and allow excluding a category under 2% of data with justification and counts reported.

## A low ratio does not name its cause

Rerunning the generator with plants removed (5 seeds per row; ratio for group B):

| World | Unaware model | Proxies dropped |
|---|---|---|
| As planted | 0.497 | 0.640 |
| No recruiter bias | 0.641 | 0.640 |
| No skill gap | 0.763 | 0.988 |
| Neither | 0.979 | 0.988 |

With fair recruiters the ratio is still 0.641: a 0.35 SD skill gap thins the top 20% harder than it moves the mean (work-sample pass rates alone read 0.770). Causes can be the model, the label, the world before applicants arrived, or all three.

## Small groups

One depot's 400 applicants: A 64 of 266 (0.241); B 17 of 104, ratio 0.679 [0.419, 1.103], Fisher p 0.124, 4 short of 0.8; C 2 of 30, ratio 0.277 [0.071, 1.075], p 0.035. Simulation with a 1,000-applicant reference at 0.30 (20,000 repeats):

| Small group n | Equal treatment flagged | True ratio 0.6 passes | Interval wholly below 0.8 |
|---|---|---|---|
| 20 | 0.271 | 0.256 | 0.000 |
| 50 | 0.188 | 0.147 | 0.091 |
| 200 | 0.037 | 0.023 | 0.438 |
| 1,000 | 0.001 | 0.000 | 0.946 |

Coverage stays near 95% at every size (0.949 to 0.957), but at 20 and 50 the interval almost never settles the question. Look at a longer window or comparable use elsewhere, or state that the data cannot support a conclusion; never quietly drop the group the audit exists for. Use [[Confidence Interval Coverage and Wilson]] for rates.

## Intersections

Group cutoffs equalising selection across A, B, C left margins above 0.8 (B 0.90, C 0.84, attribute Y 0.85) yet crossings read B/Y 0.77 and C/Y 0.65. Over 30 other seeds B/Y averages 0.832 and falls below 0.8 on 6, and some crossing falls below 0.8 on 18; the worst crossing read below the worst margin on all 30. The model has no interaction term but learns the gap penalty that pushes Y down within each group. A published audit of commercial gender classifiers found error rates up to 34.7% for darker-skinned women against at most 0.8% for lighter-skinned men; passing predefined groups while failing a structured subgroup is called fairness gerrymandering.

Costs of slicing: cells shrink so intervals widen (report n), and comparisons multiply. Five pre-chosen slices at 5% expect 0.25 false alarms per audit; picking the top slice from six equal slices gave 0.47 false alarms per audit and at least one in 28% of audits. Choose slices before looking and retest unplanned findings on the next window ([[Multiple Comparisons Corrections]]).

## When group data is missing

Estimating B's ratio (truth 0.469): likeliest group per person 0.469 (luck; over five more seeds it erred by up to 0.06 either way), weighting by P(group | postcode band) 0.686 (0.69 to 0.73 on all five seeds against truths 0.48 to 0.56, hiding much of the gap), a voluntary survey with answer rates tied to outcome and group 0.768, reweighted by true answer rates 0.446 (which you will not have). Bias of a thresholded estimate varies strongly with the threshold, and inference never removes the need for a validation set with the true group. A proxy good enough to audit with is good enough to discriminate with. Alternatives need no group data: counterfactual swap tests on text inputs, or purpose-built test data with its construction explained. In the EU, recruitment screening is a high-risk use; data must be examined for bias with appropriate measures and be representative, and a 2026 amendment moved the permission to process sensitive data for bias detection to a separate article with strict conditions (necessity, pseudonymisation, access controls, deletion once corrected, records).

## See Also
- [[Group Fairness Criteria and the Impossibility Results]] — prerequisite-for
- [[Slicing Errors With Correction and the Rate Identity]] — related
- [[Label Bias, Proxies and the Cost of Mitigation]] — extends
- [[Delta Method for Ratio Metrics]] — prerequisite-for
