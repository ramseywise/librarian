---
title: Prior Shift Correction for Oversampled Defaults
tags: [foundations, pattern]
summary: When bad outcomes are oversampled, a model's probabilities describe a population that does not exist; adding a constant to the log odds fixes the level without changing ranking, so Gini and KS cannot reveal the error, and the approve/decline cutoff must come from costs on the corrected probability.
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--06-applied-analyses--notes--02-credit-scoring.md
---

# Prior Shift Correction for Oversampled Defaults

## The trap

A loan sample was 30% bad while the real book runs at about 5%. The scorecard's mean predicted default probability was 0.265 instead of about 0.05. Using those probabilities for decisions means deciding about a population that does not exist.

## The fix

Bayes: posterior odds = prior odds x likelihood ratio. Oversampling changes the prior and leaves the likelihood ratio alone, so swap one prior for the other: add ln(true prior odds) - ln(sample prior odds) to every log odds (here -2.097). Mean PD became 0.047, using population weights to evaluate (each good counts true_good_rate/sample_good_rate, each bad true_bad_rate/sample_bad_rate).

Ranking is unchanged, so Gini stayed 0.480. A reviewer looking only at Gini and KS never sees the error; compare the mean PD to the known population bad rate. See [[Bayes Rule and the Base Rate Fallacy]].

## Cutoff from costs

Approve while expected loss of accepting is below that of rejecting. With a bad accepted costing 5 and a good rejected costing 1: PD x 5 < (1 - PD) x 1, so PD < 1/6. The rule holds only for a calibrated PD. Per-application cost on the test set at a 5:1 ratio and 5% bad rate:

| Policy | Approved | Cost |
|---|---|---|
| Approve everyone | 100% | 0.250 |
| Sample PD, cutoff 1/6 (prior ignored) | 58.3% | 0.444 |
| True-prior PD, cutoff 1/6 | 92.8% | 0.245 |
| Reject everyone | 0% | 0.950 |

The uncorrected model rejects 42% and is far worse than approving everyone; no ranking skill rescues it. The corrected scorecard improves on approving everyone by only 2%. A lower minimum (0.218 at PD 0.183) was found by looking at the test set, so it must not be quoted (it turns the test set into a tuning set). At 10:1 the comparison is 0.403 vs 0.500, a 19% saving. A scorecard earns its keep when bads are expensive or common, so the cost ratio is the first number to ask the business for.

## See Also
- [[Weight-of-Evidence Logistic Scorecard]] — prerequisite-for
- [[Calibrated Score, Deterministic Decision Rule]] — related
- [[Population Stability Index]] — related
- [[Newsvendor Critical Ratio]] — related (same cost-ratio logic for quantities)
