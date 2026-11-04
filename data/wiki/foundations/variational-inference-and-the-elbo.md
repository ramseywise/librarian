---
title: Variational Inference and the ELBO
tags: [foundations, concept]
summary: "Variational inference replaces an intractable posterior with a simple q chosen by maximising the ELBO (reconstruction minus KL to the prior), whose gap to the log evidence equals the KL to the true posterior; it scales well but mean-field versions understate variance under correlation."
updated: 2026-11-04
sources:
  - data/raw/repos/learn-ai-engineering/data-analytics--04-bayesian-analysis--notes--06-bayesian-machine-learning.md
confidence: medium
---

# Variational Inference and the ELBO

When a posterior is too large to sample, approximate it with a simple distribution q and make q as close as possible. This turns inference into optimisation over a KL divergence: usually faster and more scalable than [[MCMC and Metropolis Sampling]], but it tends to underestimate posterior variance. The KL to the true posterior needs the evidence, which is uncomputable, so maximise an equivalent quantity, the **evidence lower bound**:

log p(x) >= E_q[log p(x given z)] - KL(q(z given x) || p(z))

that is, reconstruction minus a regulariser pulling q toward the prior. The gap in the inequality is exactly the KL from q to the true posterior.

## The gap, made visible

One observation x = 2, with x ~ N(z, 1) and z ~ N(0, 1): the log evidence is -2.2655 and the exact posterior is N(1, 0.71^2).

| q | Reconstruction | KL | ELBO | Gap |
|---|---|---|---|---|
| N(0, 1) (the prior) | -3.4199 | 0.0000 | -3.4199 | 1.1544 |
| N(0.5, 1) | -2.5449 | 0.1250 | -2.6699 | 0.4044 |
| N(1, 1) | -1.9200 | 0.5000 | -2.4200 | 0.1545 |
| N(1, 0.71^2) | -1.6694 | 0.5966 | -2.2660 | 0.0005 |

Moving q toward the data costs some KL and gains more reconstruction; at the exact posterior the ELBO reaches the log evidence up to Monte Carlo noise. In a real model that gap cannot be measured. The consequence: an ELBO is a bound, and its gap differs across models, so it is not a safe way to rank models; use held-out predictive scores.

## Reparameterisation trick

Gradient ascent needs a gradient through a sampling step. Write z = m + s * eps with eps ~ N(0, 1) so the randomness no longer depends on the parameters. Forty noisy gradient steps (step size 0.2) took m from 0 to 1.000, the exact posterior mean.

## ADVI against NUTS

ADVI fits an independent Normal q per parameter. On two nearly collinear inputs (80 points) the means agree (a 1.153 against 1.218, b 1.018 against 0.960) but the marginal sds are 0.127 and 0.130 under ADVI against 0.390 and 0.397 under NUTS, about threefold too narrow. The correlation is -0.01 against -0.96, and the well-determined sum a + b gets sd 0.181 against 0.113. A mean-field q cannot express correlation, so check VI against MCMC on a sample of the data before quoting intervals. With an uncorrelated posterior the main error should go away.

## Amortisation and the VAE

ADVI fits one q per model; a variational autoencoder fits one encoder network that outputs the mean and log-variance of q for any input, so a new input needs no refit.

| Part | Role |
|---|---|
| Encoder | amortised posterior q(z given x) |
| Reparameterisation | z = mu + sigma * eps so gradients pass through sampling |
| Decoder | p(x given z), Bernoulli per pixel for binarised images |
| Prior | N(0, I); decoding draws from it generates new items |
| Conditional VAE | condition encoder and decoder on a label to generate a chosen class |

## See Also
- [[Expectation-Maximisation for Gaussian Mixtures]] — alternative-to
- [[MCMC and Metropolis Sampling]] — alternative-to
- [[Divergences and Non-Centred Parameterisation]] — related (posterior geometry)
- [[Gaussian Processes and Bayesian Optimisation]] — related
