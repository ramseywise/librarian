---
title: "Error Analysis, Bias and Variance Gaps"
tags: [foundations, pattern]
summary: "Diagnose which gap to attack first: human level to train error (avoidable bias), train to train-dev (variance), train-dev to dev (data mismatch), dev to test (overfit to dev); count an error category before building a fix, since its share of mistakes is the ceiling on the gain."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--notes--03-structuring-ml-projects.md
  - data/raw/repos/learn-ai-engineering/data-science--02-deep-learning--README.md
---

# Error Analysis, Bias and Variance Gaps

Orthogonalisation means each symptom has one lever: poor fit on train (bigger network, better optimiser, longer training), poor dev (regularisation, more data), poor test (bigger dev set, since you overfit dev), poor real-world performance (change the dev set or metric).

## One metric to optimise

Compare models on one **optimising** metric and make everything else **satisficing**: a threshold that must be cleared, then ignored. With a 5,000-parameter limit on 8x8 digits, a 64-unit network gave 2.78% dev error with 4,810 parameters; a 128-unit network gave 2.41% with 9,610 parameters, which is over the limit and so not a candidate. Change the metric when it stops describing what you want.

## Splits

Dev and test must come from the deployment distribution. With big data, small percentages suffice. Data that differs from deployment goes into training, never test. Add a **train-dev** set (training distribution, held out from training) to separate variance from mismatch.

## Gap diagnosis

The floor is Bayes error; use the best available human as the proxy. Read the gaps in order:

| Gap | Meaning | Lever |
|---|---|---|
| human to train | avoidable bias | bigger model, less regularisation |
| train to train-dev | variance | more data, regularisation |
| train-dev to dev | data mismatch | make training resemble deployment |
| dev to test | overfit to dev | bigger dev set |

Worked case (human 0.5, train 1.0, train-dev 1.5, dev 8.0): the 6.5-point mismatch gap dominates. Once a model beats humans the proxy is gone and gaps are harder to read. See also [[Learning Curves and Bias-Variance Diagnosis]].

## Count before you build

Fixing a category that is 5% of errors improves total error by at most that 5%. On digits: 24 dev mistakes (4.44%); the largest pair, 8 read as 1, was 5 mistakes, a ceiling of 0.93 points. Ease and expected help also matter, not just size. Fix mislabelled examples in dev and test together or their distributions diverge; random label noise in a large training set is tolerable, systematic noise is not (see [[Regularisation Under Noisy Labels]]). Splitting a large dev set into an Eyeball set you read (about 100 mistakes) and a Blackbox set avoids overfitting to what you inspect.

## Data mismatch example

Train on clean digits, score on corrupted ones. Clean-only: train 1.60, train-dev 4.67, dev 62.96, test 58.52. Without a train-dev set that looks like variance and invites collecting more of the wrong data. Adding synthetic corruption: dev 14.07, test 17.04, train-dev 9.73, at the price of worse train-dev. Not all corruption is equal: a one-pixel roll alone gave 59.3% error, noise alone 11.5% (clean 2.2%), because each MLP weight is tied to a pixel position; see [[Convolution, Shift Sensitivity and Parameter Sharing]].

## See Also
- [[Learning Curves and Bias-Variance Diagnosis]] — related
- [[Transfer and Multi-Task Learning Conditions]] — related
- [[Bias-Variance Decomposition and Model Complexity]] — prerequisite-for
