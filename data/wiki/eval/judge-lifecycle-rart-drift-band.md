---
title: Judge Lifecycle with RART and a Drift Band
tags: [eval, llm, pattern]
summary: "A production-judge lifecycle from a Netflix workshop paper: a rationale-annotated benchmark, RART rubric tuning that scores specificity 3:1:1, a bounded-retry revision gate, and a weekly human sample that triggers re-tuning when the judge falls more than 2 standard deviations below the rater mean; the re-tune path never fired online (self-reported)."
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-06-kong-2026-lifecycle-llm-as-judge-large.md
---

# Judge Lifecycle with RART and a Drift Band

Kong et al. (Netflix; arXiv 2608.18300, 2026; a workshop paper at COLM 2026, in the Lifelong Agents and AIMS workshops) argue that a production LLM judge for recommendation explanations should be managed through four phases.

1. **Birth.** A human-labelled benchmark with rationales: about 900 explanations, roughly 54% FAIL, deliberately class-balanced, growing by about 300 a week. The authors state its metrics measure agreement on that enriched set, not defect rates on live traffic.
2. **Training.** RART tunes the judge's rubric with a signal that includes rationale agreement. RART optimises s = 3*Spec + 1*Rec + 1*RAneg, with Spec the share of human-FAIL examples that the judge fails too; RAneg is the fraction of human-FAIL examples where both fail it and give the same reason, as decided by a meta-judge. The authors weight specificity heavily because, in their words, the two kinds of error are not symmetric online. A right verdict for the wrong reason counts as an error, since the judge's reason is the revision instruction given to the generator.
3. **Deployment.** The judge gates explanations and acts as critic in a bounded-retry revision loop.
4. **Monitoring.** A weekly human sample of about 300 items, at least 3 raters each with the majority label as truth, sets off re-tuning if the judge drops under the human band.

## The drift rule

Per metric, the judge's score must be at least the mean rater score minus 2 standard deviations across raters, with the judge and every rater measured against one shared majority label. The band widens when raters disagree, so hard samples do not penalise the judge. It runs on the full weekly sample and separately on newly added titles. The extraction notes the band is one-sided: it never flags a judge that looks suspiciously better.

## Results (self-reported)

- **Drift.** Across the weekly samples taken during the A/B test the judge remained inside the band for every metric, new titles included, and re-tuning was therefore never triggered online.
- **Rationale meta-judge.** Its verdicts matched trained raters 98.6% of the time on 300 agreed-fail rationale pairs. The paper's appendix says this narrow task is not evidence that the primary judge matches humans at that rate.
- **RART against label-only reflection.** Three must-have criteria, 8 seeds each reshuffling the data split, scored on held-out data with a two-sided sign test. On criterion 1 RART improved specificity more, at a recall cost; on criterion 2 the default rubric was near ceiling and the methods were indistinguishable; on criterion 3 the label-only variant lost specificity and reasoning agreement at every iteration, so its best checkpoint was just the default rubric (lift 0). The extraction read no per-metric lift values.
- **Revision budget.** 1,000 generated explanations, four generators: the three strong generators reach at least 80% of the lift available to them by k=3 to 4; one stays below 50% even at k=12. The deployment uses K=3.
- **Online A/B.** Judge-aligned explanations against a control with none, in the mobile app, over 5 weeks and tens of millions of members: +0.2% relative on novel content and +0.3% relative in sessions with a successful play (both p<0.05). The extraction notes this compares explanations with none, so it does not test the judge.
- **Long tail.** Weekly human review found borderline phrasing, genre-specific problems and explanations that pass every criterion yet read as confusing; the authors say aggregate drift detection is blind to these and fix them by revising the guidelines.

## Limits

The evidence spans months of controlled experiments, not continuous operation, on one surface (mobile) and one kind of explanation. The paper does not compare RART with GEPA or TextGrad. Re-tuning after drift has never fired online, so that response is validated offline only. Criteria, generator and judge identities are withheld. Judge and meta-judge share one base model family, which makes correlated errors plausible. The rater protocol is internal and the work cannot be reproduced. The extraction adds that no judge-versus-human numbers (Spec, Rec, RAneg, kappa) are given for the final judge beyond the lifts, that the newly-added-title sample size is unknown, and that a band estimated from as few as 3 raters is noisy. Its takeaway to invest in the benchmark before the judge is asserted, not tested.

Internal inconsistencies noted by the extraction: the abstract says hundreds of thousands of explanations a week and Section 3 says over 75% pass at a retry budget of 3, but Section 6.1 shows only curves and no text value at k=3; the abstract says everything reported comes from online member-facing experiments, yet the RART ablation and meta-judge validation are offline; the extraction observes that RAneg cannot exceed Spec since both use all human-FAIL examples as the denominator; specificity is called the most critical metric, yet on criterion 1 RART gives up recall for it, justified only by falsely rejected items being regenerated, which ignores the items dropped after K retries; and the "lifelong agent" framing describes a periodic re-tune a human triggers, not continuous learning.

## See Also
- [[Judge Calibration (TPR, TNR and Corrected Pass Rate)]] — prerequisite-for (a drift trigger and weekly human sample for a calibrated judge)
- [[LLM-as-Judge Evaluation]] — prerequisite-for (the production lifecycle of a judge)
- [[Human Agreement Ceiling Protocol]] — related (rater disagreement sets the band here)
- [[Online Eval Sampling]] — related (a human sample over live traffic)
