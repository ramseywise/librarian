---
title: "Label Bias, Proxies and the Cost of Mitigation"
tags: [foundations, pattern]
summary: "When the label is a past human decision every label-based metric inherits its bias and calibration can look clean; dropping the sensitive column leaves proxies, and mitigation costs depend on which label you price them with."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--15-fairness-in-automated-scoring.md
---

# Label Bias, Proxies and the Cost of Mitigation

Setting: generated screening task from [[Group Fairness Criteria and the Impossibility Results]]; the model is trained on past recruiter decisions (the log label), and a true outcome (a work sample) exists for everyone only because a generator knows it. Past recruiters' B-against-A ratio was 0.374 against the work sample's 0.770.

## Label bias

Auditing the same selection against each label (naive = all columns incl. group; unaware = group and attribute dropped):

| Model, label | TPR A, B | PPV A, B |
|---|---|---|
| Naive, logs | 0.583, 0.251 | 0.720, 0.613 |
| Naive, work sample | 0.476, 0.131 | 0.650, 0.726 |
| Unaware, logs | 0.540, 0.434 | 0.738, 0.474 |
| Unaware, work sample | 0.437, 0.261 | 0.660, 0.649 |

For the naive model the PPV gap changes sign: worse for B on the logs, better on the work sample because B is held to a higher bar. The unaware PPV gap is 26 points on logs, 1 on the work sample. Calibration is the worst case because it looks clean: naive model mean A-to-B gap across bins 0.033 against logs and 0.124 against the work sample (B passes more often at the same score, e.g. observed 0.490 against 0.341 in the 0.2 to 0.35 bin). If the label is the problem, no metric computed from it can tell you; get a check from outside it, such as a random audit of 5,000 applicants who sit the work sample whatever a recruiter says ([[Learning From Corrections and the Audit Sample]]). A work sample is itself a target choice: validate it. The same failure appears when a health algorithm predicted costs rather than illness.

## Proxies

AUC predicting group B on test: from postcode band alone 0.827; from every unaware column 0.838. Selection of B and ratio: all columns 0.048 and 0.189; group and attribute dropped 0.107 and 0.469; proxies (postcode, gap) dropped too 0.131 and 0.600. Of people either of the first two versions advanced, 83.6% are advanced by both; the 96.5% raw decision agreement is inflated because two unrelated 20% selections already agree on about 68%. Dropping proxies raised work-sample pass rate of those selected from 0.659 to 0.669. With proxy strength 0 the AUC falls to 0.503. Caveats: real features rarely split into clean and tainted; a proxy can carry real signal. Test by predicting the group from your features and asking which helpful features have a job-related reason to be there. 0.600 is still under 0.8: dropping proxies removed the recruiter effect and left the base-rate gap.

## Mitigation at 20% capacity

| Option | sel A | sel B | ratio B | ppv true | ppv logs |
|---|---|---|---|---|---|
| Naive, one cutoff | 0.252 | 0.048 | 0.189 | 0.657 | 0.711 |
| Unaware, one cutoff | 0.228 | 0.107 | 0.469 | 0.659 | 0.699 |
| Unaware, proxies dropped | 0.218 | 0.131 | 0.600 | 0.669 | 0.689 |
| Group cutoffs, equal selection | 0.202 | 0.182 | 0.902 | 0.653 | 0.672 |
| Group cutoffs, equal TPR on logs | 0.223 | 0.131 | 0.584 | 0.660 | 0.692 |
| Group cutoffs, equal TPR on outcomes | 0.211 | 0.162 | 0.771 | 0.656 | 0.678 |
| Audited labels, no proxies, one cutoff | 0.220 | 0.132 | 0.601 | 0.668 | 0.687 |
| Audited labels, no proxies, equal selection | 0.204 | 0.185 | 0.904 | 0.662 | 0.669 |

- **Cost depends on the pricing label.** Equal selection on the unaware model costs 2.7 points on the logs (0.699 to 0.672) but 0.6 on the work sample (0.659 to 0.653); about 31 qualified people (2,585 to 2,554). A business case on biased history overstates the price.
- **Fixing inputs beat fixing outputs**: dropping proxies raised ratio and quality with no group cutoffs (the audited row also changes the label, so the table does not separate the two).
- Equalising selection is not free within groups: unaware PPV for A and B goes 0.660, 0.649 to 0.676, 0.570.
- Equal TPR on a biased label is worth little (B ratio 0.584).
- A fix fitted on one sample is not exact on test: equal-outcome cutoffs read TPR 0.410 for A against 0.358 for B; C's selection is 0.169 not 0.200. Monitor group cutoffs like any threshold.
- Outside this generator, published profit-model results lose profit as constraints tighten (race-blind 99.3%, equal opportunity 92.8%, equalized odds 80.2%, parity 69.8% of maximum on 301,536 credit scores) and trade-offs "can be large in practice"; do not quote 0.6 points as the price of fairness.

**Group cutoffs may be illegal or unavailable.** In US employment, statute bars adjusting scores or using different cutoff scores on protected grounds; whether a model score is such a test is for counsel, so fix features, labels and validation first. A group-threshold post-processor needs the sensitive attribute at deployment time.

## What an audit report states

Decision, model version and threshold; population and window; label provenance and independent check (how many, chosen how); group data method, missingness by decision and validated inference error; rates with counts, ratio and interval per group and pre-chosen slice, with a small-cell rule; error rates and calibration naming the label, and the primary metric, who chose it, why; alternatives tried with selection and quality effects on the same data; jurisdiction, date and legal reviewer; what is not established (cause, job-relatedness, compliance); when it repeats and what triggers sooner. Group metrics do not capture individual experience or procedural justice; an appeals route and a person able to overturn the result are part of the system.

## Pitfalls

Ratio without counts; treating 0.8 as a pass; auditing with the training label; deleting the column and declaring the model blind; chasing every metric at once; stopping at margins; dropping small groups; pricing the fix on biased labels; assuming a low ratio proves model bias (0.641 with fair recruiters); reusing another place's rule.

## See Also
- [[Group Fairness Criteria and the Impossibility Results]] — prerequisite-for
- [[Auditing Selection Rates With Intervals and Intersections]] — prerequisite-for
- [[Label Quality: Agreement, Noise and Confident Learning]] — related
- [[Tabular ML Leakage Taxonomy]] — related
