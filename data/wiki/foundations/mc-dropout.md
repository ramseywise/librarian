---
title: MC Dropout
tags: [foundations, pattern]
summary: Keep dropout switched on at test time and average several stochastic forward passes; the paper argues this approximates Bayesian inference in a deep Gaussian process and gives the spread of the passes as a model-uncertainty signal at no change to training.
updated: 2026-11-08
sources:
  - data/raw/papers/2026-11-08-gal-2015-dropout-as-bayesian-approximation.md
---

# MC Dropout

The paper asks whether dropout training is a form of approximate Bayesian inference, specifically for a deep Gaussian process, which would let any dropout network report model uncertainty. Their answer is a theory plus a recipe called **MC dropout**: leave dropout active at test time, run T stochastic forward passes, and take the mean as the prediction and the variance as the uncertainty. Standard dropout, by contrast, multiplies each weight matrix by its keep probability at test time (weight averaging) and returns one point value.

## Mechanism

The theory frames dropout training as variational inference using a Bernoulli distribution on the weights; the dropout objective minimises the KL divergence to the Gaussian-process posterior. Model precision is linked to weight decay through tau = p l^2 / (2 N lambda), as the paper's eq. 7 gives it. The log-likelihood is estimated from the T passes with a log-sum-exp, and the passes can run concurrently, so the claimed running time equals that of standard dropout.

## Results (self-reported)

- **UCI regression** (Boston Housing: N=506, one hidden layer of 50 units, 20 splits): MC dropout RMSE 2.97 against 4.32 for VI and 3.01 for PBP; log-likelihood -2.59 against -2.90 for VI and -2.57 for PBP. It beat both on nearly all ten sets by RMSE and test log-likelihood; Yacht Hydrodynamics (N=308) is the exception, where PBP has better RMSE. Dropout probability 0 hurt Boston Housing RMSE.
- **CO2 extrapolation** (5-layer ReLU, 1024 units): standard dropout predicts a confident value far from the data, while MC dropout's standard deviation grows. With TanH the uncertainty stays bounded because the units saturate. A small T gave reasonable estimates; the main figures used T=1000.
- **Rotated MNIST digit** (LeNet, dropout 0.5, 100 passes, 12 rotations): one class can get a softmax output near 1 even though the uncertainty bands on the pre-softmax values of several classes overlap, so the softmax output does not measure confidence.
- **Reinforcement learning** (2D agent task; p=0.1 dropout ahead of each weight layer; 25 burn-in batches): Thompson sampling with a dropout Q-network reached reward above 1 within 25 batches; epsilon-greedy needed 175.

## Limits

- Derivations and setup details sit in an external appendix (arXiv 1506.02157), not in the extracted PDF.
- The predictive distribution is highly multi-modal; mean and variance only partly describe it.
- How good the uncertainty is hinges on the nonlinearity and the weight regulariser, which set the GP covariance; that study is deferred.
- UCI dropout probabilities and tau were tuned by Bayesian optimisation on small networks; Yacht is a counter-example.
- In the RL task improvement halts near 1K batches, since the agent keeps taking random moves; the result is one run.
- Standard errors in an older arXiv version were inflated by a factor of 4.5 (corrected October 2016).
- The extraction notes that later work disputes whether the Bayesian reading gives calibrated posteriors; the paper checks only log-likelihood.

## See Also
- [[Regularisation as a Prior]] — related (dropout and weight decay read probabilistically)
- [[Logprobs as Confidence Signal]] — related (another route to a confidence estimate)
- [[Gaussian Processes and Bayesian Optimisation]] — prerequisite-for
- [[Thompson Sampling and Bandit Regret]] — related (the RL use)
- [[Probability Calibration and Reliability Curves]] — related (calibration is the check the paper does not run)
