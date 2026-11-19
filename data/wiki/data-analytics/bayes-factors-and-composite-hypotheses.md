---
title: Bayes Factors and Composite Hypotheses
tags: [data-analytics, bayesian-analysis, concept]
summary: "The odds form of Bayes's theorem multiplies prior odds by a likelihood ratio (the Bayes factor); a composite hypothesis gets the prior-weighted average of its sub-hypotheses' likelihoods, so how the alternative is specified decides the verdict."
updated: 2026-11-19
sources:
  - data/raw/papers/2026-11-08-think-bayes-ch05-odds-addends.md
  - data/raw/papers/2026-11-08-think-bayes-ch11-hypothesis-testing.md
  - data/raw/papers/2026-11-08-think-bayes-ch12-evidence.md
---

# Bayes Factors and Composite Hypotheses

Three chapters of Downey's *Think Bayes* (1st edition) build one idea. Posterior odds equal prior odds times the **Bayes factor**, the ratio of the probability of the data under A to that under B. A factor above 1 raises the odds of A and below 1 lowers them. Cookie problem in this form: bowls with 30/10 and 20/20 vanilla/chocolate, prior odds 1:1, likelihood ratio 3/2, posterior odds 3:2, probability 3/5.

## Data consistent with a hypothesis can still count against it

Oliver's blood: type O has frequency 60% and type AB 1%, and Oliver is type O. Not being a donor makes the traces a little likelier (0.012 versus 0.01), so the match counts weakly against him.

## The Euro problem

A Belgian one-euro coin was spun 250 times, 140 heads and 110 tails (MacKay's problem). Fair F is x = 50%; the alternative B needs a definition, and the factor, the probability of the data under B over that under F, depends on it:

| Definition of B | Verdict |
|---|---|
| uniform over x, with 50 removed | factor 0.47, i.e. 2.1 in favour of F |
| x is either 0.4 or 0.6, weighted equally | weak evidence for B |
| triangle prior peaking at 50% | weak evidence against B |
| x set to the observed 140/250 (B_cheat) | factor 6.1, but bogus because it uses the data |

A composite hypothesis is a suite of sub-hypotheses, and its likelihood is the prior-weighted average of theirs. The value returned by the suite's update step is that average, so a separate likelihood function is not needed. Define B before seeing the data. Downey reads the factor as an odds multiplier: a factor of 2 takes 50% only to 66%, small next to modelling error, while a factor of 100 from 1:1 gives over 99%. The newspaper's frequentist statement for the same data was that an unbiased coin gives a result this extreme less than 7% of the time. The chapter mentions Jeffreys' verbal scale, whose bands run from barely worth mentioning at 1 to 3 up to decisive above 100, calls its adjectives historical and prefers odds.

## Comparing two people with nuisance parameters

Math SAT 2009, 54 questions: Alice scored 780 and Bob 740. The prior is the College Board score distribution converted to a probability correct, with equal prior on each being better. Treat each person's parameter as a nuisance parameter to estimate, then sum the joint's mass on each side of the diagonal (tie mass from discretisation is split evenly).

- Simple model (equal-difficulty questions, binomial likelihood): P(Alice's parameter is higher) 0.79 and Bayes factor 3.8.
- Efficacy-versus-difficulty model (Gaussian efficacy prior with mean 0 and sd 1.5; uniform difficulties centred at -0.05 with width 1.8): Bayes factor 3.4 and 77% for Alice. The small gap shows the simple model's modelling error was small.
- Predictive check: the chance Alice outscores Bob on a retake is 63%, so confidence in the efficacy ordering (about 3:1) exceeds confidence in the next result (about 2:1).

The efficacy cannot be observed, so Downey validates it through that predictive question.

## Limits

- The chapter says B's specification depends on background information, so reasonable people could differ. The evidence is weak in every non-cheating version.
- The SAT model ignores the quarter-point wrong-answer penalty, assumes equal priors, and uses assumed difficulty and efficacy distributions (the author describes the efficacy choice as largely arbitrary); the difficulty range was calibrated by eye against the raw-score CDF.
- Chapter 5 says that apart from the odds form, its material on sums, maxima and mixtures is distribution arithmetic and not specifically Bayesian.
- Exercises on whether a Bayes factor of 1000 overcomes a very low prior for ESP are raised but not answered. The Euro likelihood snippet has a printed typo; code is Python 2 era.

## See Also
- [[Bayes Rule and the Base Rate Fallacy]] — prerequisite-for
- [[Beta-Binomial Updating and Credible Intervals]] — prerequisite-for
- [[P-Value Misreadings]] — related (the frequentist reading of the same coin data)
- [[Posterior Predictive Checks]] — related (checking through a predictive question)
