---
title: Integrated Gradients
tags: [data-science, deep-learning, pattern]
summary: "Integrated gradients attributes a network's output to its input features by accumulating gradients along a straight path from a baseline to the input; Sundararajan et al. derive it from two axioms, Sensitivity and Implementation Invariance (self-reported)."
updated: 2026-11-20
sources:
  - data/raw/papers/2026-11-08-sundararajan-2017-axiomatic-attribution-deep-networks.md
---

# Integrated Gradients

Sundararajan, Taly and Yan (2017) ask what properties an attribution method for deep networks must have and which method follows. They hold that a method lacking Sensitivity or Implementation Invariance is fundamentally flawed. Everything below is the authors' own (self-reported).

## Mechanism

Feature i's attribution is its input-minus-baseline difference multiplied by the integral, for alpha from 0 to 1, of the derivative of F with respect to x_i at points on the straight line from baseline to input. It is computed as a Riemann sum with m steps on an existing network, with no retraining.

- **Sensitivity(a):** a single differing feature that changes the prediction must get a non-zero attribution.
- **Implementation Invariance:** two networks computing the same function must receive the same attributions.
- **Completeness:** the attributions add up to F at the input minus F at the baseline. Developers are advised to check the sum and raise m when it is off.
- **Symmetry-preserving:** symmetric variables with the same input and baseline values receive the same attribution. Among path methods, integrated gradients is the unique one that preserves symmetry; the authors cite Friedman (2004) for the result that only path methods meet all four of Implementation Invariance, Sensitivity(b), Linearity and Completeness.

## Worked examples and results

- Plain gradients fail Sensitivity. For f(x) = 1 - ReLU(1 - x) the output rises from 0 (baseline 0) to 1 (input 2) while its gradient attribution is 0.
- On two functionally equivalent networks (input x1=3, x2=1, reference 0,0), DeepLift and LRP give (2, -1) for one and (1.5, -0.5) for the other; integrated gradients returns (1.5, -0.5) on both.
- Between 20 and 300 steps came within 5% of the integral on the authors' image and text models. The LSTM-based GNMT translation model needed 100-1,000. For a 100x100-input recognition network they put its cost at 20-300 network calls, where Shapley-Shubik needs n calls per path over n! paths.
- A W2N2 graph-convolution model (PCBA-58432, one molecule, zeroed baseline) credits bonded atom pairs with 46% of the score in total and all remaining pairs with -3%. On W1N2 it revealed a bug: atoms of equal type and bond count got identical attribution, since features were not fully convolved.
- On min(x1, x2), going from (0,0) to (1,3), integrated gradients gives x1 all the credit while Shapley-Shubik gives each feature half.

## Limits

- Attribution quality is not evaluated quantitatively; the authors argue that experiments cannot tell model errors from method errors.
- Feature interactions and the network's internal logic are outside its scope.
- Output depends on the baseline, which should score near zero and signal absence. An all-zero text embedding is not a real input, defended only by the small norms of unimportant words.
- Other methods meet the axioms too; Shapley-Shubik, which averages over paths, does.
- The applications omit their step counts, network sizes and training details.

## See Also
- [[SHAP Attributions and the Limits of Explanations]] — alternative-to (Shapley-style attribution)
- [[Influence Functions for Black-Box Predictions]] — related (attributes to training points, not input features)
- [[Attention Head Roles, Pruning and Faithfulness]] — related (compares attention with gradient-based importance)
