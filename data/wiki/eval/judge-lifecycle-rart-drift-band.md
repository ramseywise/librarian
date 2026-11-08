---
title: Judge Lifecycle with RART and a Drift Band
tags: [eval, llm, pattern]
summary: "A production-judge lifecycle from a Netflix workshop paper: a rationale-annotated benchmark, RART rubric tuning that scores specificity 3:1:1, a bounded-retry revision gate, and a weekly human sample that triggers re-tuning when the judge falls more than 2 standard deviations below the rater mean; the re-tune path never fired online (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-kong-2026-lifecycle-llm-as-judge-large.md
---

# Judge Lifecycle with RART and a Drift Band

Kong et al. (Netflix; arXiv 2608.18300, 2026; accepted at the Lifelong Agents and AIMS workshops at COLM 2026, so a workshop paper) argue that a production LLM judge for recommendation explanations should be managed through four phases.

1. **Birth.** A human-labelled benchmark with rationales: about 900 explanations, roughly 54% FAIL, deliberately class-balanced, growing by about 300 a week. The authors state its metrics measure agreement on that enriched set, not defect rates on live traffic.
2. **Training.** RART tunes the judge's rubric with a signal that includes rationale agreement. The tuning score is s = 3*Spec + 1*Rec + 1*RAneg, where Spec is the share of human-FAIL examples the judge also fails and RAneg the share where judge and human both fail and agree on why, decided by a meta-judge. Specificity gets the weight because the authors say the two error types are not symmetric online. A right verdict for the wrong reason counts as an error, since the judge's reason is the revision instruction given to the generator.
3. **Deployment.** The judge gates explanations and acts as critic in a bounded-retry revision loop.
4. **Monitoring.** A weekly human sample of about 300 items, at least 3 raters each with the majority label as truth, triggers re-tuning when the judge falls below the human band.

## The drift rule

For each metric, the judge must score no worse than mean(rater scores) minus 2 standard deviations across raters (judge and each rater are scored against the same majority label). The band widens when raters disagree, so hard samples do not penalise the judge. It runs on the full weekly sample and separately on newly added titles. The extraction notes the band is one-sided: it never flags a judge that looks suspiciously better.

## Results (self-reported)

- **Drift.** During the A/B test the judge stayed in the band on every metric every week, including on new titles, so re-tuning did not fire online.
- **Rationale meta-judge.** Its verdicts matched trained raters 98.6% of the time on 300 agreed-fail rationale pairs. The paper's appendix says this narrow task is not evidence that the primary judge matches humans at that rate.
- **RART against label-only reflection.** 3 must-have criteria, 8 seeds reshuffling the split, held-out test, two-sided sign test. On criterion 1 RART improved specificity more, at a recall cost; on criterion 2 the default rubric was near ceiling and the methods were indistinguishable; on criterion 3 the label-only variant collapsed specificity and reasoning agreement in every iteration, so its best checkpoint was the default rubric (lift 0). The extraction read no per-metric lift values.
- **Revision budget.** 1,000 generated explanations, four generators: the three strong generators capture at least 80% of their achievable lift by k=3 to 4; one stays below 50% even at k=12. The deployment uses K=3.
- **Online A/B.** Explanations against a no-explanation control, mobile app, tens of millions of members, 5 weeks: +0.2% relative on novel content and +0.3% relative in sessions with a successful play (both p<0.05). The extraction notes this compares explanations with none, so it does not test the judge.
- **Long tail.** Weekly human review found borderline phrasing, genre-specific problems and explanations that pass every criterion yet read as confusing; the authors say aggregate drift detection is blind to these and fix them by revising the guidelines.

## Limits

Months of controlled experiments, not continuous operation; one surface (mobile) and one explanation family; RART is not compared with GEPA or TextGrad; the drift re-tune path has not fired online, so its response is validated offline only; criteria, generator and judge identities are withheld; the judge and meta-judge share a base model family, so their errors are plausibly correlated; the rater protocol is internal and the work is not reproducible. The extraction adds that no judge-versus-human numbers (Spec, Rec, RAneg, kappa) are given for the final judge beyond the lifts, that the newly-added-title sample size is unknown, and that a band estimated from as few as 3 raters is noisy. Its takeaway to invest in the benchmark before the judge is asserted, not tested.

Internal inconsistencies noted by the extraction: the abstract says hundreds of thousands of explanations a week and Section 3 says over 75% pass at a retry budget of 3, but Section 6.1 shows only curves and no text value at k=3; the abstract says everything reported comes from online member-facing experiments, yet the RART ablation and meta-judge validation are offline; the extraction observes that RAneg cannot exceed Spec since both use all human-FAIL examples as the denominator.

## See Also
- [[Judge Calibration (TPR, TNR and Corrected Pass Rate)]] — extends (a drift trigger and weekly human sample for a calibrated judge)
- [[LLM-as-Judge Evaluation]] — extends (the production lifecycle of a judge)
- [[Human Agreement Ceiling Protocol]] — related (rater disagreement sets the band here)
- [[Online Eval Sampling]] — related (a human sample over live traffic)
