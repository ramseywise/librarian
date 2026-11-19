---
title: Double Dipping and Selection on the Test Data
tags: [data-analytics, probability-and-statistics, concept]
summary: "Using the same data to choose what to test and to test it, picking subjects for extreme values, or stopping a trial when the p value dips, biases results toward false positives and exaggerated effects; split the data or fix the plan in advance."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-statistics-done-wrong-ch06-double-dipping-data.md
  - data/raw/papers/2026-11-08-think-stats-ch07-hypothesis-testing.md
---

# Double Dipping and Selection on the Test Data

Double dipping is using the same data twice: first to select hypotheses or units, then to test them. The test then sees only the lucky ones. Reinhart's chapter 6 covers three forms.

## Selecting then testing

Reinhart's contrived fMRI example picks brain regions by a screening test on the same data and then tests them; the outcome is a difference that does not exist, found several times as often as the test's nominal false positive rate implies (no figure given). He cites a figure of possibly 40% for how often neuroimaging work violates the rules against circular analysis (footnote not in the extract).

## Selecting extreme units

Units picked because their values were extreme drift back toward the average on remeasurement (regression to the mean). Galton first noted it with heights and eminent families; the extraction also cites Secrist's 1933 business book as a fallacy case that Hotelling reviewed critically. To estimate a treatment effect among subjects picked for being extreme, split them randomly into treatment and control groups.

## Stopping early

A stopping rule lets investigators end a trial when the drug clearly works. Reinhart cites medical trials stopped early exaggerating effects by 29% on average against similar trials not stopped. In his simulation (Figure 6-1; start at 10 per group, plan 100, no true effect), checking significance after every added pair eventually drops below p = 0.05, so stopping then gives a false positive. In a survey he cites, over half of academic psychologists owned up to choosing whether to collect further data after seeing the significance result. See [[Peeking and Sequential Testing]] for numbers.

Downey's chi-square test on early, on-time and late births (NSFG, first babies against others) was significant, but the same data were used to explore and to test; he advises confirming on another dataset (Think Stats ch. 7).

## Advice

- If the data decide the analysis procedure, run the analysis on separate data.
- Divide the data: pick regions using one half and analyse the other, accepting lower power; alternatively pick them on grounds unrelated to the contrast being tested, such as known anatomy.
- Confirm exploratory findings on a new, independent and sufficiently powered dataset.
- Settle stopping rules beforehand, using sequential methods or stricter thresholds to cover the repeated tests; file the protocol and choose a handful of checkpoints.

## Limits

- No original experiments; the 29% and 40% figures have footnotes not in the extract.
- The monkey electrode, walrus and penguin fMRI, and Fixitol examples are contrived.
- The advice stops short of explaining how to run sequential analysis or selective inference.

## See Also
- [[Winner's Curse]] — related (selection on significance exaggerates effects)
- [[Peeking and Sequential Testing]] — related
- [[Multiple Comparisons Corrections]] — related
- [[Researcher Degrees of Freedom and Prespecification]] — related
