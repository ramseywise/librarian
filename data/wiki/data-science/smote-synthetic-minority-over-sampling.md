---
title: "SMOTE: Synthetic Minority Over-sampling"
tags: [data-science, classical-ml, pattern]
summary: "SMOTE adds synthetic minority examples interpolated between a minority point and its k nearest minority neighbours; Chawla et al. (2002) reported ROC-space gains, Elor et al. found balancing comparable to threshold tuning for strong classifiers but not all, and van den Goorbergh et al. found the corrections miscalibrated logistic regression's probabilities."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-08-chawla-2002-smote.md
  - data/raw/papers/2026-11-08-elor-2022-to-smote-or-not.md
  - data/raw/papers/2026-11-08-van-den-goorbergh-2022-harm-class-imbalance-corrections.md
---

# SMOTE: Synthetic Minority Over-sampling

Chawla, Bowyer, Hall and colleagues (2002) ask whether adding synthetic minority examples while also removing majority examples gives classifiers with better ROC-space performance than three alternatives: majority removal alone, varying Ripper's loss ratio, and varying Naive Bayes priors. They expect interpolated points to enlarge the region the classifier assigns to the minority class, while copying existing points makes it smaller.

## Mechanism

For each minority sample, pick one of its k = 5 nearest minority neighbours and create a new point on the segment between them: new = sample + gap x (neighbour - sample), with gap drawn uniformly from [0, 1] per synthetic point. The "amount" of SMOTE (100%, 200%, up to 500% in the paper) sets how many synthetic points are made. ROC curves are built by fixing an amount and sweeping majority under-sampling. SMOTE-NC extends the distance to mixed continuous and nominal features: each differing nominal feature adds the median of the minority class's continuous standard deviations, and the synthetic nominal value is the majority value among the k neighbours. SMOTE-N, for nominal features, was proposed but not evaluated.

## Original results (self-reported)

Setup: nine datasets, C4.5, Ripper and Naive Bayes, 10-fold cross-validation, AUC by the trapezoid rule (Table 3, C4.5 only; scale not stated) and ROC convex hull.

- In 48 experiments SMOTE with under-sampling failed to come out best in just 4; Pima (Naive Bayes dominates), Oil (under-sampled Ripper dominates) and Can (curves overlap) were the exceptions.
- Gaps in best AUC against plain under-sampling were often small: Oil 8537 against 8524, E-state 6828 against 6811, Pima 7307 against 7242. On Oil, 300% SMOTE gave 8161, below plain under-sampling.
- On Adult (48,842 samples, 11,687 minority; 50% SMOTE-NC with C4.5 and Ripper), SMOTE-NC did no better than plain under-sampling; the authors blame overlap of synthetic points with the majority space. The extraction also calls it worse by AUC, though Table 3 prints no AUC for Adult.
- On Phoneme the SMOTE curve dominated the curve from varying C4.5's leaf threshold, shown only as a figure.
- On Mammography, duplicating minority points produced bigger pruned trees and lower minority recall than SMOTE at 100% to 500%, in figures only.

## Later evidence

- Elor and Averbuch-Elor (2022) trained seven classifiers on 73 imbalanced binary datasets. Balancing helped weak classifiers but not the strong gradient-boosted ones on proper metrics such as AUC. For F1 with strong classifiers, balancing and threshold optimisation gave comparable quality, threshold optimisation is cheaper, and with a fixed 0.5 threshold random oversampling was as good as SMOTE variants. Balancing lowered minority log-loss but raised majority and overall log-loss in all cases. With test-tuned hyperparameters all four SMOTE variants beat the baselines, which the authors warn may be hyperparameter overfitting.
- van den Goorbergh and colleagues (2022) trained standard and ridge logistic regression with random under-sampling, random over-sampling and SMOTE. In 24 simulated scenarios no correction gave a higher median AUROC than uncorrected data. At 1% events the median calibration intercept was -4.5 or lower. SMOTE, and to a lesser degree random over-sampling, gave median calibration slopes below 1. On an ovarian tumour case (test n = 674) the intercept went from 0.06 and 0.05 uncorrected to -1.32 to -1.50 corrected, and corrected models had negative Net Benefit from a threshold of 0.3 upward. An intercept-only recalibration restored the median intercepts. The authors conclude imbalance is not a problem in itself. See [[Imbalance Remedies Versus a Tuned Threshold]] for a worked case.

## Limits

- Chawla et al.: evaluation is ranking-based only; probabilities, calibration and log loss are never evaluated, and the shift of the class prior is not discussed. The best SMOTE amount is chosen on the same cross-validation results that are reported, with no variance or significance tests. AUC is given for C4.5 only. Binary classes only; k = 5 only with no sensitivity analysis; 2002-era learners only. The authors concede a minority sample may have a majority neighbour.
- Chawla et al. dataset counts are inconsistent: E-state is 53,220 in the text against 46,869 plus 6,351 in Table 2, and Can is 443,872 in the text against 435,512 plus 8,360.
- Chawla et al. on Adult: the extraction calls SMOTE-NC worse by AUC, but no AUC value for Adult is printed, so that comparison is not checkable.
- Elor et al.: no explanation of why balancing helps weak but not strong classifiers; one classifier is labelled strong in the abstract and weak in the body; binary tabular data only; the filtering dropped datasets where CatBoost's AUC exceeded 0.99; no drift or time split.
- van den Goorbergh et al.: preprint; only standard and ridge logistic regression, with predictors of equal strength and a true c-statistic of about 0.75; the case study is a single split at 20% prevalence; miscalibration for other models is anticipated, not tested.

## See Also
- [[Imbalance Remedies Versus a Tuned Threshold]] — prerequisite-for
- [[Resampling Before the Split Leaks]] — related
- [[Probability Calibration and Reliability Curves]] — prerequisite-for
