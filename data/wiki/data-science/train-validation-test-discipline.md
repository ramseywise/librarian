---
title: "Train, Validation and Test Discipline"
tags: [data-science, pattern]
summary: "The test set is touched once; tuning happens on validation or CV folds, and every score is read against the majority-class base rate."
updated: 2026-11-19
sources:
  - data/raw/repos/learn-ai-engineering/data-science--01-classical-ml--notes--01-statistical-foundations.md
  - data/raw/papers/2026-11-06-varma-2006-bias-error-estimation-when-using.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch05-model-evaluation-improvement.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch01-introduction.md
  - data/raw/papers/2026-11-08-intro-to-ml-with-python-ch08-wrapping-up.md
---

# Train, Validation and Test Discipline

> The test set is touched once, at the end. Everything tuned is tuned on data the test set never saw.

| Split | Used for | Typical share |
|---|---|---|
| Training | Fitting parameters | 60-80% |
| Validation (or CV folds) | Choosing hyperparameters, features, model family | 10-20%, or k-fold over the training part |
| Test | One final estimate of generalisation | 10-20% |

Three splits rather than two because parameters are fit on train, choices are made on validation, and only then does the test set give an honest estimate. scikit-learn's `train_test_split` shuffles and holds out 25% by default; fix `random_state` for reproducibility and pass `stratify=y` for classification so class balance matches.

## Ways to break it

- **Tuning on the test set.** Picking an SVM's `C` by test score turns the test set into a validation set; the reported score is optimistic.
- **Leakage.** Fitting a scaler or feature selector on all data before splitting lets the model see statistics of test rows. See [[Tabular ML Leakage Taxonomy]] and [[Pipelines Prevent Preprocessing Leakage]].
- **Shuffling ordered data.** Time-stamped or grouped rows need a split by time or group, the way production meets data; otherwise offline score is great and live score poor. See [[Time-Series Leakage: Shift and Rolling Windows]].
- **Reading the test set during development.** The score drops the day the model meets real data.

In the book chapter's iris example (150 samples, SVC tuned over a 6x6 grid of C and gamma), tuning on the test set reported 97% while an honest train/validation/test split (84/28/38) gave 92%. Its authors advise holding out a test set used once, selecting on a validation set or by CV on the training part, and tuning ranges and decision thresholds without the test set. Varma and Simon criticise a shrunken-centroid study that picked its parameter using test error as well, and name two older leakage mistakes: choosing features on all the data before CV, and tuning parameters outside the CV loop. Their rule is to repeat every step of the algorithm, tuning included, inside each CV loop; see [[Cross-Validation Variants and Nested Search]].

## Limits

The chapter example is one small dataset on a single split, and the 92% and 97% figures carry no variance. Varma and Simon's evidence is synthetic microarray-shaped data (40 samples, 6,000 features).

The first-model numbers come from one seed with k=1, no interval, cross-validation or tuning, and the chapter never states the mathematical assumptions behind reading the 97% as expected accuracy on unseen irises. The book also does not cover stratified splitting, preprocessing leakage or class-imbalance pitfalls in accuracy, and its code is dated (an early scikit-learn 0.18 era). The closing chapter reports no data, dates from about 2016, gives online testing one paragraph without a sample size, run length, significance test or guardrail metrics, and offers no cost criteria for build against buy.

## The first split in the textbook

Müller and Guido's opening example splits the 150-sample Iris data by default into 112 training and 38 test rows (`random_state=0`), and a 1-nearest-neighbour classifier scores 0.97 on the held-out part. They give the 25% test share as a rule of thumb and call the exact size somewhat arbitrary. They shuffle before splitting because Iris is sorted by label, so the last 25% would hold only class 2, and they fix `random_state` for reproducibility. `X` is a 2-D array of samples by features, `y` is 1-D, and `predict` needs a 2-D array even for one sample.

## Beyond the held-out test: framing and shipping

The closing chapter of the same book is advice with no experiments. Its authors suggest measuring success against a business metric where possible and otherwise bounding the value by imagining a perfect model: in their fraud example, a flawless model saving only $100 monthly is not worth starting, whereas one saving tens of thousands could be. They suggest letting an algorithm handle the easy cases and routing the uncertain ones to people (an illustrative 10% automated is said to be enough to cut response time or cost), and treating modelling as one loop with data collection and error analysis, since collecting more or different data, or recasting the task, may beat further grid searching.

After offline evaluation on the held-out set they add online testing. In an A/B test a portion of users get algorithm A and the rest B without being told, chosen metrics are tracked over a fixed period, and the winner is selected; typically A is the candidate and B the incumbent. They mention bandit algorithms as a more elaborate form. For production they advise weighing reliability, predictability, runtime and memory, asking of each pipeline step what complexity it adds, and scaling in this order: more memory or a rented machine, then learning from chunks on one machine, and a cluster last. See [[A/B Test Lifecycle and Interval Decisions]] for the test itself.

## Read every score against the base rate

On the adult census income table (32,561 rows, target is income over 50k), 0.759 of rows are "<=50K". Always guessing that class is right about three times in four, so accuracy must be read against that number, not against zero. A sensible-looking rule, "predict >50K if `education-num` >= 13", scores 0.752 accuracy, below the baseline. Print the class proportions before fitting anything.

## The estimator API that makes this routine

Every scikit-learn estimator follows `fit`, then `predict` / `transform` / `score`; learned state ends in an underscore, and `fit` returns `self`. Because the shape is uniform, estimators chain in pipelines and plug into hyperparameter search. A custom estimator subclasses `BaseEstimator`, takes every hyperparameter in `__init__` without logic, and returns `self` from `fit`. Look at the data before fitting (a scatter matrix shows whether classes separate and catches unit errors).

## See Also
- [[Bias-Variance Decomposition and Model Complexity]] — prerequisite-for
- [[Cross-Validation Variants and Nested Search]] — extends
- [[Tabular ML Leakage Taxonomy]] — related
- [[Prechelt's Stopping Criteria: GL, PQ and UP]] — related (validation rows used only for stopping)
- [[ImageNetV2 and the Adaptivity Gap in Test-Set Reuse]] — extends
- [[A/B Test Lifecycle and Interval Decisions]] — extends
- [[Model Rollout: Shadow, Canary and A/B]] — related
- [[N-gram Taggers, Backoff and Brill Transformation Rules]] — instance-of
