---
title: "Eyeball and Blackbox Sets and Fixes That Fit the Reading"
tags: [foundations, pattern]
summary: "Reading errors overfits the rows read: keep a read set apart from a score set, fix classes not rows, count rounds, and expect even a well-argued mechanism fix to vanish on unread data."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--12-reading-the-errors.md
---

# Eyeball and Blackbox Sets and Fixes That Fit the Reading

Nothing is retrained on the rows you read, yet any change made because of them has been fitted to them. Split the development data: an **eyeball** set you read, a **blackbox** set that is scored and never read (1,000 to 10,000 examples), plus a test set read by nobody and used once. If the eyeball score improves much faster than the blackbox score, you have overfit the eyeball set. Here the split was 18,000 train, 1,500 eyeball, 4,500 blackbox, 6,000 test.

## Rules for learning from errors

- **Fix classes, not rows.** A hypothesis names a mechanism and a feature available at prediction time, written down before scoring. "The model cannot see utilisation, so people near their limit look fine" is a class; one row is not. A written class becomes a test every later model must pass (templated cases, invariance and directional tests).
- **Treat a slice scan as many tests** ([[Slicing Errors With Correction and the Rate Identity]]).
- **Count the rounds.** Reusing a holdout adaptively overfits it. With random labels (true accuracy cannot beat 50%), picking 500 of 10,000 attributes with a holdout gave reported accuracy above 63% on both training and holdout. A remedy answers from the holdout only when training and holdout disagree and stops when a budget is spent. Refreshing the eyeball set by moving rows over from the blackbox set or labelling new data is practical advice.
- **Check for hindsight features**: compare each new feature's date with the decision's.

## The demonstration: a noise fix and a mechanism fix

Both fixes were fixed before scoring; 30 seeds (0 to 29), each a new split.

- **Noise fix.** Add ten random columns, cut each into five parts (50 slices), take the highest-cost slice and tune a separate threshold for it on the eyeball rows.
- **Mechanism fix.** From reading rows: absolute amounts hide ratios shallow trees build badly, so add six months of utilisation (bill over limit) and five of payment share (payment over amount due), all dated before the outcome.

Gain in cost per 1,000 applicants (positive is better), mean over 30 seeds:

| Fix | Eyeball | Seeds better | Blackbox | Seeds better |
|---|---|---|---|---|
| Noise | +18.56 | 30 | -8.33 | 3 |
| Mechanism | +4.07 | 18 | -1.08 | 13 |

Base cost 553.7 (eyeball) and 545.7 (unread). The worst noise slice cost 695.9 on the rows that chose it and 547.6 on unread rows: bad by chance, and it does not return. About 2.5 of 50 noise slices reach raw p < .05, exactly chance; BH let one through on 1 seed of 30. You cannot fail to improve on rows you tuned on.

The mechanism fix read well and did not transfer: on seed 0 it gained 15.3 on the rows that suggested it and lost 4.4 unread. Test set, used once on a comparison fixed in advance: baseline 577.7, fix 572.2, gain 5.5 with bootstrap 95% interval -7.3 to 18.2, so no evidence of gain ([[Bootstrap Resampling and Its Failures]]). The cell profile had already warned: false negatives looked like true negatives and the approved group was calibrated, so boosted trees had extracted most of what the columns hold. The next step is a new data source or accepting the limit. The test set is now spent for that comparison.

**Holdout reuse.** Keep a random noise patch if it helps half A of the unread set, for 20 rounds: the reused half reports gains of 2.09, 5.90, 10.47, 16.46 at rounds 1, 5, 10, 20, while the fresh half shows -0.19, 0.90, 2.03, -1.91. Each patch is noise, and no single step looks wrong.

## Same habit elsewhere

Reading traces of a retrieval pipeline or LLM judge is this procedure on text: state the positive class (a judge's false positive passes a bad output), read random items before dramatic ones, slice with a correction, keep dev and held-out sets apart. A prompt rewritten from the failures it was scored on is the noise fix again; a rule naming one failing trace is a row fix.

## See Also
- [[Error Analysis by Confusion-Matrix Cell]] — prerequisite-for
- [[Train, Validation and Test Discipline]] — related
- [[Hyperparameter Search Budgets and Selection Optimism]] — related
- [[Tabular ML Leakage Taxonomy]] — related
