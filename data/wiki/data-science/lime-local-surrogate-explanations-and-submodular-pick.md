---
title: "LIME Local Surrogate Explanations and Submodular Pick"
tags: [data-science, concept]
summary: "LIME explains one prediction of any classifier by fitting a sparse linear model on weighted perturbations of that instance; SP-LIME picks a small set of instances whose explanations cover the important features."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-07-ribeiro-2016-why-should-i-trust-you.md
  - data/raw/papers/2026-11-08-ribeiro-2016-why-should-i-trust-you.md
---

# LIME Local Surrogate Explanations and Submodular Pick

Ribeiro, Singh and Guestrin (KDD 2016) propose LIME to answer two questions: should a user act on one prediction, and should they trust a model enough to deploy it. The explanation has to be faithful near the instance being predicted (local fidelity) and readable by a person even when the model's own features are not.

## Mechanism

1. Write the instance in an interpretable binary representation: which words are present, or which super-pixels are on. This is separate from the features the model uses.
2. Perturb it by switching parts off, and label each perturbed copy with the black-box model.
3. Weight the copies with an exponential kernel on distance to the original, so near copies count more.
4. Select K features with K-LASSO, then fit least squares on those K. The weights are the explanation.

The objective is the weighted squared gap between the black box and the linear surrogate over the perturbations, plus a complexity penalty on the surrogate. Because it only needs predictions, it works on any classifier or regressor.

## SP-LIME: explaining the model, not one row

Looking at every explanation does not scale, so submodular pick chooses B instances greedily so that their explanations cover the most globally important features (a weighted coverage function). Choosing the best set is NP-hard; the greedy rule gives a constant-factor guarantee of 1 - 1/e (the authors' claim, from the coverage-function argument).

## What the experiments showed (self-reported)

| Experiment | Setup | Result |
|---|---|---|
| Recovering known important words | Sparse logistic regression and a decision tree, each limited to 10 features; books and DVDs reviews; K = 10 | LIME recall 92.1 (books, logistic) and 97.0 (books, tree); 90.2 and 97.8 on DVDs. Parzen 72.8 and 78.9 on books; greedy 64.3 and 37.0 |
| Simulated trust in single predictions | 25% of features marked untrustworthy at random; 100 runs | LIME F1 ranged 91.8-96.7 over classifiers and datasets; parzen 81.7-94.3; greedy 45.0-58.1 |
| Choosing between two classifiers | Human subjects, 100 per setting, K = B = 6, SVM trained on original versus cleaned 20 newsgroups | One extraction gives SP-LIME 89.0% correct against 68.0% for the RP-greedy baseline; the other reads the values off a chart |
| Spurious features | RBF SVM on unigrams, Christianity versus Atheism | 94.0% held-out accuracy, yet explanations exposed irrelevant words; the token "Posting" is in 22% of training examples and 99% of those are Atheism |
| Accuracy picks the wrong model | Same task | Original SVM: 94.0% held-out, 57.3% on a separate religion dataset (819 pages per class); cleaned SVM: 88.6% and 69.0% |
| Husky versus wolf | Logistic regression on 20 hand-picked images with snow in the wolf pictures; 27 graduate students | Subjects who trusted the bad model dropped from 10 to 3 of 27; those naming snow as a possible cue went from 12 to 25 of 27 |
| Cleaning a classifier | Worse newsgroups SVM; 10 instances, 10 words, 3 rounds; 250 classifiers | Crowd workers removing words did better with SP-LIME instances than random ones; the accuracy curve appears only in a figure |

On cost, explaining a 1000-tree random forest with 5,000 perturbations took under 3 seconds on a laptop in one extraction, and an Inception image prediction took about 10 minutes (scikit-learn, no GPU or parallelisation; self-reported).

## Limits

- Experiments cover text and images only. The tabular flu example is an illustration.
- Faithfulness was checked only on interpretable models whose important features are known (sparse logistic regression, trees with at most 10 features); no such check on a black box is reported.
- The trust experiments mark features untrustworthy artificially, and the husky-wolf study is small (27 students), trained a deliberately bad model, and had no control group.
- A highly non-linear model may have no faithful linear explanation near an instance, and some behaviours (a sepia-toned image) cannot be written in super-pixels.
- A good local fit says nothing about fit across the whole model.
- Stability across sampling seeds, the number of samples and the kernel width were not studied; robustness to sampling noise is asserted. K is fixed, and the pick step for images is left unsolved.
- Users saw only sparse linear explanations, and the human studies report no significance tests.
- The two extractions of the paper differ in detail. One gives the human-study percentages and the 10-to-3 husky-wolf counts, while the other reads those results from figures only and describes the husky-wolf test as 10 predictions, 8 of them correct.

## See Also
- [[SHAP Attributions and the Limits of Explanations]] — extends (Kernel SHAP is linear LIME with a different kernel)
- [[What Drives Sentiment: LIME, Per-Class Topics and Log-Odds]] — instance-of
- [[Tree Ensemble Interpretation Beyond Impurity Importance]] — alternative-to (global importance versus a local surrogate)
