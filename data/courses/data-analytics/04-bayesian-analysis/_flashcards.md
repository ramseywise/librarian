---
generated_by: tools/slides/flashcards.py
decks:
- data-analytics/04-bayesian-analysis/slides/deck.yaml
cards:
- front: What are the five steps of a Bayesian analysis?
  back: A posterior is prior times likelihood, renormalised, and everything else in the pillar follows from that.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: How do you use a closed form when you also have a sampler?
  back: Where a closed form exists, use it, and use it to check the sampler before you trust the sampler elsewhere.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: Why can one recipe handle counts, lies, launches and serial numbers?
  back: The same recipe handles counts, lies, launches and serial numbers, because only the story changes.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What wastes draws in step size, and what do you read to judge a chain?
  back: Both too small and too large waste draws, so read effective sample size and never the raw draw count.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What does the non-centred form change, and what does it remove?
  back: The non-centred form leaves the model unchanged and removes the funnel the sampler could not cross.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: When do priors matter most, and where should you spend your care?
  back: Priors matter most when data is thin, so spend your care on small segments and early looks.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How does Thompson sampling choose an arm, and where does exploration come from?
  back: Sample once from each posterior, play the highest, and exploration follows from the remaining uncertainty.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: Which outputs of a Bayesian A/B test drive the decision?
  back: P(B > A) is only one of the outputs, and the lift interval and expected loss are the ones that drive the decision.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: When does the prior change the answer in a Bayesian A/B test?
  back: With this much data the prior barely matters, but on day one it changes the answer from 0.950 to 0.689.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: Does calling a test Bayesian make daily stopping safe, and what do you do instead?
  back: Calling it Bayesian does not make daily stopping safe, so choose the rule and judge it by its error rates.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: What is the Bayes action, and what makes it move?
  back: The Bayes action minimises expected loss under the posterior, and it moves when the costs move.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Under asymmetric costs, is the mean the best action?
  back: With asymmetric costs the best action is not the mean, and using the mean has a price you can compute.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Why can the same posterior say ship or wait?
  back: The same posterior can say ship or wait, depending on what shipping costs, so put that cost in the calculation.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Which method does each week of the coursework teach?
  back: Each method answers the same posterior question at a different point on the trade-off between speed and exactness.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What is the ELBO's gap to the log evidence, and what does raising it do?
  back: The ELBO's gap to the log evidence is the KL divergence from the true posterior, so raising it improves the approximation.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What does mean-field variational inference misstate, and how do you check it?
  back: Mean-field variational inference is fast and misstates correlated uncertainty, so check it against NUTS on a small version.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What is the partial pooling weight, and how much did a 5-user market move?
  back: Partial pooling beat no pooling in 96% of datasets, because it trusts each group exactly as far as its data allows.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: When do you use clustered standard errors, fixed effects and a multilevel model, and what did each give on correlated data?
  back: Pick by the question, and when a group effect may correlate with a predictor, add its group mean or use fixed effects.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Across 1,000 simulated datasets, how did pooling change the winner's overstatement, the pick and the coverage?
  back: Pooling almost removes the overstatement and improves the pick, and it still leaves you short of the truly best segment.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: In which scenarios does pooling stop paying, and what happens to a true outlier?
  back: Shrinkage works against the rare real winner, so follow up a large raw effect with a new test.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How well can 3 markets estimate tau, and what did a tight half-normal prior do when tau was really 2?
  back: With few groups the prior decides, so report a range of priors. As Gelman and Loken warn, inference can be sensitive to model assumptions.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What are most Bayesian failures, and what does each one have?
  back: Most Bayesian failures are unchecked models and unpriced decisions, and each one has a check you can run.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Where to go next
  back: The next step is to run chapter 4 on your own test's counts and price the decision in chapter 5.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
---
