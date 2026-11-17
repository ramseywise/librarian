---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-analytics/04-bayesian-analysis/slides/deck.yaml
cards:
- front: What are the five steps of a Bayesian analysis?
  back: Story (how the data arises), Prior (plausible before data), Likelihood (chance of this data), Posterior (plausible after), and Decision (lowest expected cost).
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: How do you use a closed form when you also have a sampler?
  back: Use the closed form as a test of your sampling setup. Beta(4,4) plus 32 of 50 gives mean 0.6207, sd 0.0632, and NUTS gave 0.6190 and 0.0638, so the sampler agrees with the algebra.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: Why can one recipe handle counts, lies, launches and serial numbers?
  back: Because only the story changes. Each case writes how the data could have arisen, then conditions on what was seen, and returns a direct statement about the unknown with its uncertainty.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: Why does the Bayes factor for the Belgian euro coin flip with the definition of "biased"?
  back: Because a Bayes factor needs a defined alternative. With 140 heads in 250 spins, the data-peeking alternative gives 6.08, two values (0.4 or 0.6) give 1.33, and a uniform prior gives 0.47, which favours the fair coin.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: How does the species problem get a prior when the number of species is itself unknown?
  back: 'It puts a prior on the number of species n as well: a uniform prior on n, then a Dirichlet over n prevalences, then the reads. With 400 reads and 61 species seen, n has mode 72 and a 90% interval of 66 to 79.'
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What wastes draws in step size, and what do you read to judge a chain?
  back: A step that is too small (0.002, ESS 11) or too large (3.0, ESS 278) wastes draws, while 0.1 gave ESS 3594. Read effective sample size, never the raw draw count or acceptance rate.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What does the non-centred form change, and what does it remove?
  back: 'It changes only the parameterisation, sampling raw and setting theta = mu + tau * raw, so the model is unchanged. It removes the funnel between theta and tau: divergences fell from 88 to 2 and tau ESS rose from 64 to 2143.'
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: Which four habits hide a failing sampler, and what replaces each of them?
  back: Running one chain (run four from dispersed starts), reading high acceptance as good (look at ESS and R-hat), adding draws to a bad model (rescale or reparameterise), and ignoring a few divergences (raise target_accept, then reparameterise).
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: When do priors matter most, and where should you spend your care?
  back: Priors matter most when data is thin. Two priors on one coin differ by 0.333 at the start and 0.010 at N=500, so spend your care on small segments and early looks.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: What does a Jeffreys prior fix about flat priors, and what does it still not fix?
  back: 'It fixes dependence on parameterisation: it is proportional to the square root of the Fisher information, so it survives a change of variable. It does not make high-dimensional problems safe; ten normal means with a flat joint prior still go badly wrong.'
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How does Robbins' formula estimate next year's claims without assuming a prior, and where does it fail?
  back: 'It estimates the expected claims for count x as (x + 1) y(x+1) / y(x), using only the counts and no prior family; with 7,840 zero-claim and 1,317 one-claim policies, x = 0 gives 0.168. It is erratic where counts are thin: x = 5 gives 6.00.'
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: Which four prior mistakes does the chapter list, and how do you avoid each?
  back: Calling a wide prior uninformative (simulate outcomes from it), fitting the prior on the same data (use earlier data or other units), putting zero mass at the truth (use generous supports), and a default prior on unscaled inputs (scale first).
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How does Thompson sampling choose an arm, and where does exploration come from?
  back: 'Draw once from each arm''s posterior and play the arm with the highest draw. Exploration comes from the remaining uncertainty: arms with wide posteriors sometimes draw highest, and traffic follows the chance each arm is best.'
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: Which outputs of a Bayesian A/B test drive the decision?
  back: The lift interval and the expected loss. P(B > A) is only one output (0.99999 here); the lift is +0.34 to +0.95 points, and the expected loss is 0.000001 points for shipping B against 0.645 points for keeping A.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: When does the prior change the answer in a Bayesian A/B test?
  back: When data is thin. With the full Larkspur data the prior barely matters, but on day one (900 visitors an arm) Beta(1,1) gives 0.950 while Beta(500,9500) gives 0.689.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: Does calling a test Bayesian make daily stopping safe, and what do you do instead?
  back: No. With no true effect, P(B>A) > 0.95 shipped B in 0.238 of tests when checked daily against 0.047 on the last day only. Instead choose the stopping rule deliberately and judge it by its error rates.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: What is the Bayes action, and what makes it move?
  back: 'The Bayes action is the action that minimises expected loss under the posterior. It moves when the costs move: squared loss picks the mean, absolute loss the median, and narrow zero-one loss the mode.'
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Under asymmetric costs, is the mean the best action?
  back: No. When a shortage costs five times an overstock, stocking the mean (40) costs 15.26, while the Bayes action of 46 costs 9.92.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Why can the same posterior say ship or wait?
  back: Because the decision depends on what shipping costs. The expected gain is $92,906, but net of a $25,000 ship cost it is $67,906 with 0.001 chance of regret, and at $90,000 it is $2,906 with 0.448 chance of regret.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Which three loss-function mistakes does the chapter list, and what fixes each?
  back: Reporting the posterior mean by habit (write the loss down first), averaging outcomes before applying the loss (apply it per draw, then average), and leaving out predictive noise (draw outcomes, not only means).
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Which method does each week of the coursework teach?
  back: Week 2 teaches EM (mixtures), week 4 MCMC (logistic regression), week 5 variational inference and the VAE (the ELBO), and week 6 Gaussian processes and Bayesian optimisation (tuning).
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What is the ELBO's gap to the log evidence, and what does raising it do?
  back: The gap is the KL divergence from the true posterior, so raising the ELBO improves the approximation. With q at the prior the gap is 1.1544; with q at the exact posterior it is 0.0005, which is sampling noise.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What does mean-field variational inference misstate, and how do you check it?
  back: Correlated uncertainty. ADVI gave a correlation of a and b of -0.01 against -0.96 for NUTS, getting both spreads wrong. Check it against NUTS on a small version of the model.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What is the partial pooling weight, and how much did a 5-user market move?
  back: The weight on a group's own data is tau squared over (tau squared + sigma squared / n). The 5-user market had weight 0.16, so its raw $54.26 was pulled to $42.10 (true $45.39), while the 262-user market had weight 0.91 and barely moved.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: When do you use clustered standard errors, fixed effects and a multilevel model, and what did each give on correlated data?
  back: Use clustered SEs when groups are a nuisance, fixed effects or within-between when the group effect may correlate with a predictor, and multilevel when group estimates or their spread are the question. With truth 2, pooled gave 3.04, random intercepts 2.83, and fixed effects and within-between 1.99.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Across 1,000 simulated datasets, how did pooling change the winner's overstatement, the pick and the coverage?
  back: The winner's overstatement fell from +2.93 to +0.09. The pick improved only partly, from a true lift of 1.26 to 1.46 against 1.98 for the truly best segment. The 90% interval coverage was 0.90 in both.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: In which scenarios does pooling stop paying, and what happens to a true outlier?
  back: 'When segments are well measured (ratios 0.93 and 0.99), pooling gives no gain. It also hurts a true outlier: a segment truly at +5.0 is pulled down by 3.74 and its RMSE rises from 3.01 to 3.76.'
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How well can 3 markets estimate tau, and what did a tight half-normal prior do when tau was really 2?
  back: 'Poorly: with a true tau of 6, 3 markets give estimates from 0 to 15.53, and zero in 11% of datasets. A half-normal(0.25) prior when tau was really 2 made estimates worse than raw (ratio 1.25) and its intervals covered only 48%.'
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What does a varying-slopes model add to varying intercepts, and what did 20 cafes teach about the correlation?
  back: It lets each group's slope vary too, with the intercept and slope modelled together so each borrows from the other. With 20 cafes, the correlation posterior mean was -0.42 (89% interval -0.74 to -0.03), so its sign is learned but its size is not.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: When does a non-centred parameterisation help, and does it cure thin data?
  back: It helps most when data is thin. With 30 cafes and 2 visits, divergences fell from 203 to 8 and min ESS rose from 25 to 270; it is not a cure, since 8 divergences remained.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: How far did a noisy predictor pull the slope toward zero, and what did modelling the error recover?
  back: Ignoring the error gave a slope of 0.81 (sd 0.14) against a truth of 1.0. Treating the true values as parameters, with the known standard errors as likelihoods, recovered 0.94 (sd 0.10).
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: Why does a careless imputation model make the slope more confident and more wrong?
  back: Because it ignores the link between the predictor and mass, which shrinks the slope to 0.26 (truth 0.50) and tightens the sd to 0.22, so the estimate is more confident and more wrong. Modelling N as depending on mass gave 0.41.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What are most Bayesian failures, and what does each one have?
  back: 'Most failures are unchecked models and unpriced decisions, and each has a check you can run: simulate the prior, check r_hat, ESS and divergences, fix the stopping rule, and price the mistake with expected loss.'
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
---
