---
title: Grid Posteriors Over Several Parameters
tags: [data-analytics, bayesian-analysis, pattern]
summary: "Enumerate hypotheses on a grid and run one update routine that only needs a likelihood; with two parameters read joint, marginal and conditional posteriors, and with two levels solve each lower level first and feed its normalising constant up."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-think-bayes-ch01-bayess-theorem.md
  - data/raw/papers/2026-11-08-think-bayes-ch02-computational-statistics.md
  - data/raw/papers/2026-11-08-think-bayes-ch09-two-dimensions.md
  - data/raw/papers/2026-11-08-think-bayes-ch14-hierarchical-model.md
---

# Grid Posteriors Over Several Parameters

Downey's *Think Bayes* (1st edition) keeps a posterior as a map from hypothesis to probability and updates it by multiplying each prior by its likelihood and normalising.

## One update, many problems

Hypotheses that are mutually exclusive and jointly exhaustive form a suite, which makes the normalising constant an ordinary sum. In the cookie problem (bowls of 30/10 and 20/20 vanilla/chocolate), drawing a vanilla cookie raises the chance of Bowl 1 from one half to three fifths. In the M&M problem (the 1994 bag has 20% yellow and 10% green, the 1996 bag 14% yellow and 20% green) a yellow from the 1994 bag and a green from the 1996 bag makes the first hypothesis 20/27 likely. In Monty Hall, switching wins 2/3; in the variant where Monty always picks B whenever he can, seeing B opened is uninformative (1/2 each). The chapter 2 code makes the update identical across these, and each problem supplies only a Likelihood (template-method pattern). Any common factor in the likelihoods cancels. When the data-generating process changes, re-derive the likelihood.

## Two parameters

The paintball problem locates a shooter from where spatters land on a wall: a 30 x 50 ft arena, spatters at 15, 16, 18 and 21 ft, uniform prior over an integer (alpha, beta) grid, and a likelihood from a turret firing at a uniform angle. Each hypothesis is a tuple.

- Marginal posterior of alpha: median 18, 50% credible interval (14, 21). Of beta: 50% interval (5, 31), and beyond 10 ft the marginal is almost uniform, so the data do not separate those depths.
- Conditional on beta of 10, alpha is narrow, and wider for larger beta (10, 20, 40 tried), so the two parameters are dependent. Identical conditionals would mean independence.
- Marginals cannot recreate the joint; conditionals can.
- Multi-dimensional credible intervals can use the highest-probability values summing to the target mass, possibly non-contiguous. Counting how many of nested 75, 50 and 25% intervals contain each cell visualises them.
- Grid cost is n to the power d for d parameters of n values each: a million hypotheses covers 1000^2, 100^3 or 10^6.

## Two levels

Chapter 14's Geiger counter infers two things, the particle count n in one second and r, the long-run rate of emission, from a detector count k with detection fraction f. With f of 0.1 and k of 15, the posterior of n centres on 150 (k over f), and so does r's, somewhat tighter. Downey draws the general claim that longer-run parameters can be estimated more certainly than single-period quantities, from this example only. The recipe: reason from parameters to data (the forward problem), then invert with Bayes; arrange the model with causes above and effects below; for each r compute the posterior of n, using the update's normalising constant as that r's likelihood, then get n's posterior as a mixture weighted by r's. Underflow and speed fixes for larger grids are on [[Approximate Bayesian Computation with Summary Statistics]].

## Limits

- Uniform prior over the room; the author says a map could justify a richer prior. The turret model wrongly implies that shooters close to the wall hit it most, and exercise 9.1 asks for an improved model. Only four spatters; Figs 9.2 to 9.5 carry the rest.
- The Geiger example is one problem with one observation, with no comparison to pooled or unpooled alternatives and no partial pooling across groups. Its r grid for one figure is not stated.
- Textbook level, first edition of 2012, Python 2 code, chapter 1 has no empirical results, and chapter 2 reports no timing or scale results.

## See Also
- [[Beta-Binomial Updating and Credible Intervals]] — prerequisite-for
- [[Bayes Rule and the Base Rate Fallacy]] — prerequisite-for
- [[Partial Pooling and Multilevel Models]] — related (hierarchical models with groups)
- [[MCMC and Metropolis Sampling]] — alternative-to
