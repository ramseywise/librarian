---
title: '04 — Bayesian Analysis: multiple choice and worked problems'
summary: Interview-style questions on this module, 4 multiple choice and 1 worked problems with a numeric answer.
questions:
- id: o1
  prompt: You start with a uniform Beta(1, 1) prior on a success rate and observe 3 successes in 3 trials. What
    is the posterior mean?
  options:
  - '1.0'
  - '0.8'
  - '0.75'
  - '0.6'
  answer: '0.8'
  explanation: The posterior is Beta(1 + 3, 1 + 0) = Beta(4, 1), with mean 4/5 = 0.8. The maximum likelihood estimate
    is 1.0, and the prior pulls it back.
- id: o2
  prompt: What does a 95% credible interval state?
  options:
  - 95% of intervals built this way over repeated samples would cover the parameter
  - 95% of the observations fall inside it
  - The null hypothesis is rejected at the 5% level
  - Given the data and the prior, the parameter lies in it with probability 0.95
  answer: Given the data and the prior, the parameter lies in it with probability 0.95
  explanation: A credible interval is a probability statement about the parameter. The first option is the confidence
    interval, a statement about the procedure.
- id: o3
  prompt: With a flat prior, the MAP estimate equals which other estimate?
  options:
  - The maximum likelihood estimate
  - The posterior mean
  - The prior mean
  - The posterior median
  answer: The maximum likelihood estimate
  explanation: MAP maximises likelihood × prior. A flat prior is a constant, so the maximum is where the likelihood
    peaks.
- id: o4
  prompt: As the sample grows, what happens to the influence of the prior on the posterior?
  options:
  - It grows, because the prior is counted once per observation
  - It stays the same
  - It shrinks, because the likelihood dominates
  - It depends only on whether the prior is conjugate
  answer: It shrinks, because the likelihood dominates
  explanation: The likelihood multiplies in once per observation and the prior once in total, so with enough data
    two reasonable priors give nearly the same posterior.
- id: w23
  prompt: Your prior on a conversion rate is Beta(2, 2). You then see 12 conversions and 8 non-conversions. What
    is the posterior mean, to 3 decimal places?
  answer: '0.583'
  explanation: 'The Beta prior is conjugate to the Binomial: add successes to the first parameter and failures to
    the second, giving Beta(14, 10). Its mean is 14 / 24 = 0.5833. The data alone give 12 / 20 = 0.6, and the prior
    pulls that towards 0.5.'
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
---
