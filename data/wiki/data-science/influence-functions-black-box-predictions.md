---
title: Influence Functions for Black-Box Predictions
tags: [data-science, pattern]
summary: "Koh and Liang trace a prediction back to the training points most responsible using gradients and Hessian-vector products, and check the estimate against leave-one-out retraining on small models (self-reported)."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-koh-2017-understanding-black-box-predictions-influence.md
---

# Influence Functions for Black-Box Predictions

Koh and Liang (2017) ask how to follow a prediction back, through the training procedure, to the training points that drive it. The underlying theory needs a twice-differentiable, strictly convex risk, and the authors test whether the approximation is still useful outside that. Results are their own (self-reported).

## Mechanism

The influence of training point z on test point z_test is the negative test-loss gradient, multiplied by the inverse Hessian, multiplied by the training-loss gradient. It gives how fast the test loss changes if z gets an infinitesimal extra weight. The Hessian is never built: implicit Hessian-vector products do the work, via conjugate gradients or a stochastic estimator from Agarwal et al., and the result is checked against real leave-one-out retraining.

## Results

- Both estimators agree with leave-one-out retraining for logistic regression on 10-class MNIST (n=55,000, 10 repeats, 5,000 iterations, a single misclassified test point).
- Correlation also holds for an unconverged CNN: 2,616 parameters, trained on 10% of MNIST for 500k Adam iterations, damping 0.01, scored on the 100 most influential points. For a linear SVM on MNIST 1s vs 7s, smoothing the hinge (t=0.001) lets influence anticipate retraining; the unsmoothed hinge overestimates.
- Attack on Inception's top layer (dog-vs-fish task; of 600 test images, 591 start out correct; one of 1,800 training images altered, alpha 0.02, 100 iterations): changing one training image flips a majority of correct predictions, and changing 2 flips 77%.
- Logistic regression on hospital readmission (127 features, 20K patients, balanced): influence picks out 4 children as 30-40x more influential than the next-ranked examples, whereas 14 of the 127 features had a coefficient larger than the child indicator.
- Enron1 spam (bag-of-words logistic regression, 10% labels flipped, 40 repeats): ranking by influence fixes flipped labels better than train loss or chance; only curves are given, with no accuracy figure in the text.

## Limits

- Non-convex nets need damping and non-differentiable losses need smoothing, since the theory assumes strict convexity.
- Validation covers only small models: a CNN of 2,616 parameters, plus logistic regression, plus an Inception top layer with the rest frozen.
- The leave-one-out comparison uses one arbitrary test point per plot and just the top 100-500 influential points; the paper asserts other points behave similarly.
- Influence is local and infinitesimal. Effects such as dropping a whole subpopulation are called open by the authors.
- Attacks on discrete data were not run; the authors expect them to be harder with more training data.
- Hardware, runtime and seeds are mostly unstated.

## See Also
- [[EK-FAC Influence Functions for LLMs]] — extends
- [[Integrated Gradients]] — related (attributes to input features, not training points)
- [[SHAP Attributions and the Limits of Explanations]] — related
- [[LIME Local Surrogate Explanations and Submodular Pick]] — related (local explanation in model terms)
