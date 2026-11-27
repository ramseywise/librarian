---
generated_by: src/librarian/tools/slides/flashcards.py
decks:
- data-analytics/04-bayesian-analysis/slides/deck.yaml
- data-analytics/04-bayesian-analysis/slides/lectures/00-overview.yaml
- data-analytics/04-bayesian-analysis/slides/lectures/01-infer.yaml
- data-analytics/04-bayesian-analysis/slides/lectures/02-compute-and-check.yaml
- data-analytics/04-bayesian-analysis/slides/lectures/03-decide.yaml
- data-analytics/04-bayesian-analysis/slides/lectures/04-bayesian-machine-learning.yaml
- data-analytics/04-bayesian-analysis/slides/lectures/05-many-groups.yaml
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
- front: What does rejection sampling cost in 1,000 dimensions, and what do random-walk Metropolis and Gibbs pay?
  back: For a 1,000-dimensional Gaussian and a proposal with sd 1% larger, rejection sampling accepts about 1 proposal in 20,000. Random-walk Metropolis draws are about (sigma max / sigma min) squared steps apart, and Gibbs on a correlated Gaussian pays a similar squared cost.
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
- front: How many components of a 6-component variational mixture survive under different priors on the mixing weights?
  back: 'A variational mixture switches off components it does not need, and how many survive depends on the prior on the mixing weights: 2 with alpha 0 of 0.001, 3 with 1, and all 6 with 10. So the count is not read off the data alone.'
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
- front: What are the steps of a Bayesian analysis?
  back: Write down how the data could have been generated, put a prior on the unknowns, and compute the posterior, which is what is plausible once the data is in.
  lesson: data-analytics/04-bayesian-analysis/readme
- front: What does a posterior give you that a p-value does not?
  back: Direct answers to how likely and how costly, prior knowledge carried into small samples, and the cost of a mistake inside the calculation.
  lesson: data-analytics/04-bayesian-analysis/readme
- front: What does the module finally tell Larkspur?
  back: P(B > A) of 0.99999, a lift between +0.34 and +0.95 points, and a measured answer to whether peeking is safe, which becomes a ship decision in dollars.
  lesson: data-analytics/04-bayesian-analysis/readme
- front: Which three failure modes does the module name?
  back: A sampler that has not converged, a prior nobody checked, and peeking, which a Bayesian label does not make safe.
  lesson: data-analytics/04-bayesian-analysis/readme
- front: What are the five steps of the Bayesian analysis module?
  back: Infer a posterior; compute it and check the computation; turn it into a decision; carry the ideas into machine learning; read the same test across many groups.
  lesson: data-analytics/04-bayesian-analysis/readme
- front: What habits does step 1 build?
  back: Write the generative story first, use a closed form when one exists, read two-parameter posteriors through marginals and conditionals, and report an interval and a probability about the question asked.
  lesson: data-analytics/04-bayesian-analysis/readme
- front: What are the main lessons of step 3?
  back: Thompson sampling draws once per arm posterior and plays the highest. A bandit saves traffic but biases arm means. P(B > A) says nothing about size. Peeking is not free. Pick the point estimate from the loss.
  lesson: data-analytics/04-bayesian-analysis/readme
- front: What does step 4 warn about EM and variational inference?
  back: EM finds local optima, so restart it. Mean-field ADVI is fast and understates correlated uncertainty, so check it against NUTS on a small version.
  lesson: data-analytics/04-bayesian-analysis/readme
- front: Which numbers show what partial pooling does to the winner?
  back: The raw winner overstated its true lift by 2.93 in the chapter's simulation, and the pooled winner by 0.09.
  lesson: data-analytics/04-bayesian-analysis/readme
- front: How is the Bayesian analysis series organised?
  back: An overview lecture, then one lecture per step, each covering the notes of its step in the README's reading order.
  lesson: data-analytics/04-bayesian-analysis/readme
- front: Which rules of thumb come from steps 1 and 2?
  back: Write the generative story first, report an interval and a probability, a high acceptance rate is not health, check r_hat, ESS and divergences first, simulate from the prior, and shrink lifts picked as winners.
  lesson: data-analytics/04-bayesian-analysis/readme
- front: Which rules of thumb come from steps 3 to 5?
  back: Report the lift interval beside P(B > A), set the stopping rule before the test, pick the estimate from the loss, restart EM, check ADVI against NUTS, partially pool segment effects and run several priors with few groups.
  lesson: data-analytics/04-bayesian-analysis/readme
- front: How do hypotheses, process models and statistical models relate?
  back: Different process models can imply the same statistical model, so data that fit one statistical model cannot by themselves pick between the hypotheses behind it.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What is the difference between the two views of probability?
  back: A frequentist probability is a long-run frequency of repeated data under a fixed parameter. A Bayesian probability is a degree of belief about the parameter given the data seen.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What are the three parts of a Bayesian update?
  back: The prior is what you believed before the data. The likelihood is how well each hypothesis explains the data. The posterior is the prior times the likelihood, rescaled to sum to one.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: How do three different priors turn into three different posteriors in the bug example?
  back: The posterior is 2p/(1+p), so priors of 0.20, 0.50 and 0.80 give posteriors of 0.33, 0.67 and 0.89.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What three puzzles does the note solve by counting?
  back: Cookies, where P(Bowl 1 given vanilla) = 3/5. M&Ms, where the answer is 20/27 = 0.74. Monty Hall, where switching wins 2/3 of the time.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What happens to the Monty Hall answer when the host's rule changes?
  back: The 1/3 and 2/3 become 1/2 and 1/2, because how the host chooses a door is part of the likelihood.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What is the odds form of Bayes' rule?
  back: Posterior odds equal prior odds times the Bayes factor. In the blood-traces example the Bayes factor is 0.83, so the evidence slightly favours the other hypothesis.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: How is the coin posterior computed in code?
  back: Add the successes to the first Beta parameter and the failures to the second. For Beta(4,4) and 32 of 50, the closed form gives a mean of 0.6207 and an sd of 0.0632.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: How do the MLE, MAP and posterior mean compare for the coin, and how does NUTS compare with the closed form?
  back: MLE 0.640, MAP 0.625, mean 0.621. The closed form gives mean 0.6207 and sd 0.0632, against NUTS at 0.6190 and 0.0638.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What does the euro coin posterior say?
  back: With 140 heads in 250 spins and a flat prior the posterior is Beta(141,111), with a mean of 55.95 and a 90% interval of 51 to 61.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: When does a credible interval beat a Wald interval?
  back: 'With little data. For 1 success in 20 the credible interval is [0.012, 0.238] and the Wald interval is [-0.046, 0.146], which goes below zero. With lots of data they agree: Larkspur gives [0.05363, 0.05802] against [0.05358, 0.05798].'
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What does the switchpoint model's graph show?
  back: Alpha feeds lambda 1 and lambda 2, which with tau feed a deterministic lambda that parameterises the observed Poisson counts.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: How is the switchpoint model written in PyMC?
  back: Two exponential priors for the rates, a discrete uniform for the switch day, a switch function choosing the rate by day, and Poisson counts as the observed variable.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What did the switchpoint model find in the 74 days of text messages?
  back: Lambda 1 is 17.76 and lambda 2 is 22.68. The probability that lambda 2 is higher is 0.9994. Tau is day 45 with probability 0.489 and day 44 with 0.354, so the top four days hold 0.997.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What are the expected message counts at different days?
  back: The posterior expected count is 17.8 on day 10, 20.2 on day 44 and 22.7 on days 45 and 60.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What are the PyMC building blocks?
  back: A model context, distributions for unknowns, observed data attached to a distribution, and sampling from the finished model.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What does the randomised-response model recover?
  back: With 35 yes answers of 100, the posterior mean for the true rate is 0.207 with a 90% interval of [0.035, 0.392]. A direct estimate would be [0.264, 0.448].
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: How is the Challenger model written?
  back: A logistic curve in temperature, with priors on intercept and slope, and Bernoulli outcomes for each of the 23 launches.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What does the Challenger posterior predict?
  back: P(beta<0) = 0.9985. At 31F the mean failure probability is 0.989 with interval [0.900, 1.000]. At 65F the mean is 0.515 with interval [0.226, 0.821].
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What do the posterior predictive checks show for Challenger?
  back: Total failures simulated 7.04 against 7 observed. Below 65F, 3.25 simulated against 4 of 4 observed. At 65F and above, 3.80 simulated against 3 of 19.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: How do two priors change the Bruins series forecast?
  back: A prior sd of 0.3 gives a series probability of 0.58 (the book says 57%), and a prior sd of 0.85 gives 0.80.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What errors does the note flag in the book's game-prediction example?
  back: The book's mean is a typo (2.8 versus 2.7), and its norm.pdf call has the arguments in the wrong order. The 57% in the book is 0.58 here.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What are the Red Line numbers?
  back: The mean gap is 7.5, the biased mean is 8.33, and the mean wait is 4.17. With 15 people at 2 per minute, the elapsed time goes from 4.17 to 7.18.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What do the different German tank estimates say?
  back: Max 912, unbiased 971.8, posterior mean 982, median 958, MAP 912, with an interval of [913, 1186] and P(N>1100) = 0.071.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: How do Metropolis and the simulation check the German tank result?
  back: Metropolis gives 980, 957 and [913, 1175]. In simulation the max-seen estimator has an rmse of 85.0 and the max-plus-gap estimator 62.3.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: How does the locomotive posterior mean depend on the prior's upper bound?
  back: With one train numbered 60 the mean is 207, 333 and 552 at bounds of 500, 1,000 and 2,000. Two further sightings, 30 and 90, pull them to 152, 164 and 171.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What are three pitfalls in stating the prior and the interval?
  back: Reading a confidence interval as a credible one, treating the prior as a hidden knob, and giving a prior zero mass where the truth might lie.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What are three ways to over-trust a Bayesian fit?
  back: Reporting only the posterior mean, extrapolating with a confident band, and trusting a fit without a predictive check.
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: How is the paintball grid posterior computed?
  back: Start from a uniform grid, multiply in the likelihood for each of the four hits, normalise, then sum along an axis for a marginal or slice a column for a conditional.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What do the paintball marginals and conditionals say?
  back: Alpha has a 50% interval of (14, 21) and beta of (5, 31). Given beta = 10, 20 and 40, the sd of alpha is 5.3, 7.9 and 8.8.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What limits a grid posterior?
  back: The cost is n^d for d parameters with n values each. A million hypotheses allow 1,000 values in two dimensions, 100 in three or 10 in six.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What Bayes factors do the euro coin definitions give?
  back: The cheating definition (x = 140/250) gives 6.08, two values (0.4 or 0.6) give 1.33, and uniform gives 0.47. The book's triangular prior gives 0.84.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What three points does the note draw from the euro Bayes factors?
  back: A composite hypothesis scores as its prior-weighted average likelihood. The cheat alternative is bogus because it peeks. Every definition that does not peek gives weak evidence, 1.3 for B and 2.1 (1/0.47) for F.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: How can a Bayes factor and a p-value disagree?
  back: A slope with z = 2.36 at n = 39 has a BIC Bayes factor of 5.49. A slope with z = 3.29 at n = 10,000 has 2.24, below substantial, though far past the usual p-value cutoffs.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: How do the simple and better SAT models compare?
  back: The simple model gives P(Alice higher) = 0.79 and a Bayes factor of 3.8. The better model, with question difficulty and efficacy, gives 3.4 and 77%. A retake predicts only 63% that she scores higher.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: How does simulate-then-slice work?
  back: Simulate many cases forward from a model of growth, record the pairs of age and size, and read the posterior for age off the slice at the observed size.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What does back-calculating at the median growth rate say?
  back: At the median rate the tumour was already 6.1 cm at discharge. Growing from 0.1 cm needs 2.4 volume doublings a year, which only 20% of patients reached.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: How does serial correlation change the tumour age result?
  back: P(older than 8 years) is 0.999 with no serial correlation, 0.995 at 0.4 and 0.978 at 0.8. Serial correlation widens the age range.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What is the structure of the Geiger counter problem?
  back: A rate r goes by Poisson to n particles emitted, and n goes by binomial thinning with f = 0.1 to k = 15 clicks. The posterior for n peaks at k/f = 150.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What does the Dirichlet say about 3 lions, 2 tigers and 1 bear?
  back: With Dirichlet(1,1,1), the posterior means are 44%, 33% and 22%, where the naive maximum likelihood is 50%, 33% and 17%.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What does the species posterior say?
  back: From 400 reads with 61 species seen, the posterior for the number of species has its mode at 72 with a 90% interval of 66 to 79, so 87 is unlikely and exactly 61 nearly impossible.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What do the four train estimators optimise?
  back: 'For i = 60: i gives 60 (maximum likelihood), 3i/2 gives 90 (minimum mean squared error), 2i gives 120 (unbiased) and 2i-1 gives 119 (population mean equals sample mean).'
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: How many grid points does the globe toss need?
  back: A grid of 20 points is already usable and little changes after the first 100. Two parameters at 100 values each cost 10,000 evaluations.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: When does the quadratic approximation fail?
  back: At n = 9 it gives mean 0.67 and sd 0.16, and it puts mass at p = 1, which the data rule out. At n = 18 and 36 the gap closes.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: How do you summarise a grid posterior with samples?
  back: Draw samples from the grid with the posterior as weights. Mass below 0.5 is 0.174 (the grid gives 0.172) and the middle 80% is [0.446, 0.812].
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: How do the percentile interval and HPDI differ for 3 of 3 water?
  back: The percentile interval is (0.708, 0.931) and excludes the mode. The HPDI is (0.839, 0.999) and contains it.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: Which interval widths does McElreath prefer, and why?
  back: He prefers nested 67, 89 and 97% intervals to 95%, which he calls a convention with no defence.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: Which point estimate minimises which loss?
  back: For the 3-of-3 posterior, absolute loss is minimised at the median (0.84), quadratic loss at the mean (0.80), and the MAP is 1.0. Reporting p = 0.5 costs 0.313 in expected absolute loss.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: Why does plugging in one p understate the spread?
  back: At the plug-in p = 0.67, 6 of 9 has probability 0.273, but the posterior predictive gives 0.20, because uncertainty about p spreads the counts out.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What are the pitfalls of marginals, Bayes factors and grid bounds?
  back: Clean marginals with a wrong joint, a Bayes factor for a hypothesis written after the data, weak evidence read as no effect, and a posterior that depends on the grid's upper bound.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What are the pitfalls with logs, intervals and simulation?
  back: Underflow on thousands of points, 50% intervals that disagree, predictions that look too tight, and a simulated posterior with no sensitivity check.
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What are the rules of thumb for Bayesian inference?
  back: Report a distribution not a point. State the prior and show a sceptic's. Check the model by simulating from it. Define a hypothesis before you look.
  lesson: data-analytics/04-bayesian-analysis/readme
- front: How many evaluations does a grid of 100 points per parameter need at 10 and 20 parameters?
  back: At 100 points each, 10 parameters need 1e+20 evaluations and 20 parameters need 1e+40.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What are the two consequences of getting samples instead of the posterior?
  back: A prior of zero stays zero, and you need thousands of samples because summaries are Monte Carlo estimates whose error shrinks like 1 over the root of the effective samples.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: How did the height example avoid a slow likelihood, and what went wrong with the summaries?
  back: Working in log-likelihood with one sum of squares made the exact grid about 100 times faster. Approximate Bayesian computation took about a second and matched to five digits, but the answer depended on the summary chosen.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What are the steps of one MCMC step?
  back: Start at the current position, propose a nearby position, accept it with a probability set by the density ratio (always uphill, sometimes downhill), record the position whether it moved or not, and repeat.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: Why does the acceptance step not need the normalising constant?
  back: It uses only a ratio of densities, so the constant we could not compute cancels. Rejected proposals are not wasted, because staying put is how the chain spends more time in high-density regions.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What does the coin sampler recover, and what is its one knob?
  back: It reproduces the closed form Beta(36, 22), with mean 0.6201 against 0.6207, and the proposal width is the one knob that decides everything.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: Which of the three step sizes gave a working chain, and what did the others show?
  back: Step 0.1 accepted 57.6% and had 3,594 effective samples. Step 0.002 accepted 98.7% with 11 effective samples and a wrong mean of 0.565. Step 3.0 accepted 2.8% with 278.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What does each of the three trace plots look like?
  back: Step 0.002 drifts slowly and misses the mean, step 0.1 mixes as a dense band around it, and step 3.0 shows long flat stretches between rare jumps.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: Which PyMC sampler handles continuous variables, and which handles categorical ones?
  back: NUTS is the default for continuous variables, Metropolis suits discrete variables and quick experiments, CategoricalGibbsMetropolis handles Categorical assignments, and a compound step mixes them.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: How does the No-U-Turn Sampler avoid hand tuning?
  back: It keeps doubling the trajectory until it starts to turn back on itself, which removes the number of leapfrog steps, and it tunes the step size during warm-up by dual averaging.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: When does NUTS stop doubling the trajectory?
  back: When the angle between the leftmost-to-rightmost vector and the momentum passes 90 degrees.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What did standardising the temperature change in the Challenger fits?
  back: Metropolis on raw Fahrenheit had an ESS of 5 and R-hat 2.16. NUTS on raw data had 304 and 18.8 leapfrog steps per draw. Standardised, NUTS had 2,591 and 3.1 steps.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: When do the authors prefer MCMC and when variational inference?
  back: MCMC for a small, expensive dataset where you trust the model and need precise inferences, and variational inference for a text model on a billion documents. For mixture models where Gibbs is not an option, VI may beat Hamiltonian Monte Carlo even on small data.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What is the generative story of the mixture?
  back: Each point belongs to cluster 0 with probability p, gets a label from a Categorical, each cluster has a centre and a spread, and the value is Normal around its cluster's centre.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What happens when the 300 discrete labels are summed out of the likelihood?
  back: The estimates agree, the ESS rises from hundreds to thousands, and the run takes a sixth of the time.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: Which PyMC distribution sums the labels out?
  back: pm.NormalMixture, given the weights, the centres and the spreads.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: Where does the posterior put even odds between the two clusters, and why not at the midpoint?
  back: Near 147, because cluster 1 has about twice the spread and nearly twice the weight, so it reaches well into the gap. The midpoint of the centres is 159.8.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: How do you get the cluster probability for a new point?
  back: Compare each cluster's weighted likelihood within each joint draw, then average the ratio over draws.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What is label switching and how do you stop it?
  back: Mixture components have no meaning the model can see, so chains can land on either labelling and R-hat is large. An ordering constraint on the centres stops it without assuming where the clusters are.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: Which diagnostics should you look at, and what is healthy for each?
  back: A fuzzy-caterpillar trace, R-hat at most 1.01, ESS in the hundreds or more, autocorrelation near zero within a few lags, zero divergences, and a posterior plot with an interval.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What do burn-in, thinning and the HDI versus the equal-tailed interval mean?
  back: Burn-in drops early draws that reflect the start. Thinning keeps every k-th draw but adds no information. The HDI is the narrowest interval holding a share of the mass, the equal-tailed one cuts equal tails, and az.summary reports an 89% equal-tailed interval.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What is the non-centred fix and what did it change?
  back: Sample raw from Normal(0, 1) and set theta = mu + tau times raw. Divergences fell from 88 to 2 and tau's ESS rose from 64 to over 2,000.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What are the six tips for making MCMC converge?
  back: Start in a sensible place, use priors that rule out nonsense, run several chains, prefer NUTS, rescale inputs, and when it will not converge reconsider the model.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What happened to the chain with flat priors and two observations, and how was it fixed?
  back: With flat priors alpha's mean was 1.8e8 with ESS 8, R-hat 1.29 and 678 divergences. Normal(1, 10) and HalfCauchy(0, 1) priors gave ESS 861, R-hat 1.00 and 1 divergence.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What do sick and healthy chains look like in trace plots?
  back: Healthy chains overlap into a caterpillar and sick ones drift and spike. R-hat is a warning, never a certificate, since 1.00 can come from an invalid chain.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What happens when only a sum of two parameters is constrained, and how many effective samples is enough?
  back: With mu = a1 + a2 and flat priors, a1 wanders to about -1,195 with R-hat 2.83 and 1 effective sample, and Normal(0, 10) priors give 1,223. About 200 effective samples is enough for a posterior mean.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What are the main renames from PyMC3 to current PyMC?
  back: import pymc as pm, pytensor.tensor as pt, sigma instead of sd, initval instead of testval, az.plot_trace and az.summary, idata.posterior for the trace, and tune instead of slicing the burn-in.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: Which sampling pitfalls does the note list?
  back: One chain, reading a high acceptance rate as good, more draws instead of a better model, ignoring a few divergences, shuffling draws between variables, and averaging across chains in a mixture.
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What kinds of prior are on offer and what is the caveat of each?
  back: Flat is not uninformative after a transform. Weakly informative is the modern default. Informative must be defensible. Empirical Bayes risks double-counting. Conjugate is convenience. Jeffreys is invariant but can be improper.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: What share of mass does Normal(0, 10) on the logit put on rates below 1% or above 99%?
  back: 65%. Normal(0, 1.5) puts almost none there and Cauchy(0, 2.5) puts 32%.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: What does Jeffreys' rule say and what does it give for a Poisson rate?
  back: The prior is proportional to the square root of the Fisher information. For a Poisson rate it gives theta to the minus one half, so x = 10 gives a Gamma(10.5) posterior with mean 10.5, against 11.0 under a flat prior.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How do the flat and Jeffreys posteriors compare with the confidence density for the Poisson rate?
  back: The flat-prior posterior sits about 0.5 to the right of the confidence density, and the Jeffreys posterior is nearly on top of it.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: Which distribution suits which kind of parameter?
  back: Beta for rates, Gamma for positive rates, Half-Normal or similar for standard deviations, Normal(0, s) for coefficients, and LKJ for covariance matrices.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: What does the prior predictive check show for Normal(0, 100) on the Challenger model?
  back: It expects all 23 launches to fail, or none, about 29% of the time. Normal(0, 5) gives 18% and Normal(0, 1.5) gives 2%.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: What are the steps of Gelman's default prior?
  back: Scale non-binary inputs to mean 0 and sd 0.5, put independent Cauchy(0, 2.5) priors on the coefficients, and a Cauchy(0, 10) on the intercept.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How do the priors differ under complete separation?
  back: Maximum likelihood has no finite answer. The flat fit stops at slope 100.3, Normal(0, 100) gives 39.1, Normal(0, 10) gives 9.6 with 99% and Gelman's Cauchy gives 3.6 and 86%.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How big is the gap between the flat and the biased prior at N = 0, 32 and 500?
  back: It is 0.333 at N = 0, 0.131 at N = 32 and 0.010 at N = 500.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: What do the washout panels show?
  back: The two posteriors start far apart and are nearly identical by 500 observations. A prior with zero mass at the truth never washes out.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How do posterior means for the fleet size change with the prior and the data?
  back: Flat with train 60 only gives 207, 333 and 552 for bounds of 500, 1,000 and 2,000. Flat with trains 30, 60, 90 gives 152, 164 and 171. A power-law prior gives 131, 133 and 134.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How do the Euro coin and the Bruins series differ in how much the prior matters?
  back: After 250 spins two priors give the same median of 56 and the same 90% interval of 51 to 61. With four games of hockey data a prior sd of 0.3 gives the Bruins 57% of the series and an sd of 0.85 gives 80%.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: Which prior does each frequentist method correspond to?
  back: Ordinary least squares is maximum likelihood with a flat prior, ridge is the MAP with a Normal(0, tau) prior, lasso is the MAP with a Laplace prior, and the penalty strength is the prior precision.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How many observations is a Normal prior on a mean worth?
  back: About n = 1 over sd squared. On the heights data Normal(178, 0.1) equals 100 heights and Normal(178, 20) equals 0.0025 of one. The narrow prior kept mu at 177.86 against 154.61, and sigma jumped from 7.73 to 24.52.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: What does the simulation show about regularising priors out of sample?
  back: Training deviance falls with every added parameter, but test deviance is lowest at three, the true model. Tighter priors make training deviance worse and test deviance better for over-parameterised models, and at N = 100 the data overwhelm even Normal(0, 0.2).
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: What does shrinking by a prior estimated across all experiments do to the winners?
  back: The prior sd is estimated at 0.192 and the shrink factor is 0.290. The mean among winners falls from 0.759 to 0.220, against a truth of 0.246.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: What is Robbins' formula and what does it give for a customer with no claims?
  back: E of theta given x equals (x + 1) y(x+1) over y(x), where y(x) is the number of cases with count x. With 7,840 policies at no claims and 1,317 at one, it gives 0.168 expected claims.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How many new butterfly species does Fisher's estimate predict for half a further trapping period?
  back: Corbet's data had 118 species caught once, 74 twice and 44 three times, and Fisher's estimate gives 45.2 plus or minus 11.2 new species for half the original trapping time.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: What is trial roulette?
  back: Give the expert a grid of bins and twenty chips, have them place chips where they think the value lies, then fit a distribution to the chip histogram.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: What prior pitfalls does the note list?
  back: Calling a wide prior uninformative, fitting the prior on the same data, zero mass at the truth, unscaled inputs with a default prior, and reading lasso as a sparsity belief.
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: What are the rules of thumb for sampling and priors?
  back: A high acceptance rate is not health. Look at r_hat, ESS and divergences before any result. Change the model when a sampler struggles. Simulate from the prior before you fit. Priors matter most when data is thin. Shrink lifts picked as winners.
  lesson: data-analytics/04-bayesian-analysis/readme
- front: What comes after compute and check?
  back: Bandits and Thompson sampling, which turn a posterior into an allocation rule, then the Bayesian A/B test.
  lesson: data-analytics/04-bayesian-analysis/readme
- front: How does an A/B test relate to a bandit?
  back: An A/B test is a bandit that explores uniformly until a fixed N and then exploits. A bandit shifts traffic as it learns.
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: What are the two conjugate cases that cover most arms?
  back: Bernoulli reward with a Beta prior, and Gaussian reward with a Gaussian prior. From Beta(1, 1), 3 successes in 10 pulls gives Beta(4, 8); a N(0, 1) prior with S_4 = 2 gives mean 0.4 and variance 0.2.
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: What are the steps of one round of Thompson sampling?
  back: Draw one sample from each arm's posterior, pull the arm with the largest draw, observe the reward and update that arm's Beta.
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: What does Thompson sampling do over 1,000 pulls on rates 0.85, 0.60 and 0.75?
  back: It pulls the arms [926, 26, 48] times. The 0.85 arm gets 926 pulls and a tight posterior, and the others stay wide.
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: What is regret, and how must it grow for a good strategy?
  back: R_T sums, over rounds, the best arm's true rate minus the chosen arm's rate. Lai and Robbins proved a good strategy's regret must grow at least logarithmically in T.
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: Which strategies have a logarithmic regret guarantee?
  back: Bayes-UCB and Thompson sampling. Random is linear in T, max mean can lock onto a wrong arm, and the fixed 95% bound is measured, with no guarantee claimed.
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: At 2,000 pulls, what regret did each rule reach on rates 0.15, 0.20 and 0.10?
  back: Random 100.0, max mean 28.3, the 95% upper bound 14.6 and Thompson 22.8. The ordering depends on the gaps and the horizon, so it is not a ranking.
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: How is the regret comparison set up?
  back: Each rule maps wins, trials and the round to an arm. The run repeats 300 times and averages the cumulative regret at pulls 100, 500 and 2000.
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: What three results sharpen the regret table?
  back: Bayesian regret averages over the prior and does not bound any single instance. Thompson's bounds are Thm 36.1 and 36.3. In Experiment 36.1 Thompson scored 29.9 against 23.8 for AdaUCB.
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: Why can a misspecified prior fail to wash out in a bandit?
  back: If the prior underestimates an arm, Thompson sampling may rarely or never play it, so no data arrives to correct the belief. Check the arm counts, not only the posterior means.
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: What are the BMH extensions of Thompson sampling?
  back: Minimise instead (take argmin), non-stationary arms (a learning rate below 1 forgets old evidence), non-binary rewards (sample the posterior of the expected reward) and comment ranking (sample a score per comment and sort).
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: What does forgetting buy when two arms swap their rates halfway through?
  back: Mean reward per pull rises from 0.162 to 0.179, about 10% more. On a stationary problem it costs a little, because forgetting throws away evidence.
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: What did a purely greedy learner score on the 10-armed testbed, and why is the exact Bayesian answer not used?
  back: Greedy levelled off near 1 per step against about 1.54 for the best arm, and found the best arm in only about a third of runs. The exact answer has 2^2000 leaves in a 1,000-step tree.
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: When is the Bayes-optimal bandit policy an index policy?
  back: For discounted infinite-horizon reward with geometric discounting and independent arms. It breaks with other discounting, multiple plays per round or a finite undiscounted horizon, and carries no regret guarantee.
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: When do you use a bandit, and when a fixed-horizon A/B test?
  back: A bandit when showing a loser is costly, arms change or there are many arms. An A/B test when you need an unbiased effect to report, a one-off ship decision or guardrail and long-term metrics.
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: Which bandit pitfalls does the note list?
  back: Reporting a bandit's arm means as an effect, trusting a published regret ranking, and a prior that underrates an arm. The fixes are a fixed split or holdout, your own simulation, and checking arm counts.
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: How does the question differ between frequentist and Bayesian A/B tests?
  back: 'Frequentist: if A and B were equal, how surprising is this data? Bayesian: given the data, what is P(B > A)? Bayesian gives a probability and an expected loss, and any N is fine.'
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: What does the PyMC model for two sites estimate, and how does it compare with the closed form?
  back: It samples p_A, p_B and delta = p_A - p_B. It gave P(A better than B) = 0.169, against 0.157 from the closed form.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: What are the three things worth reading off the PyMC result?
  back: B's posterior is wider because it had half the traffic. The draw reversed the truth, so P(A better) is only about 0.17 though A really is better. More data firms the probability up with no change in method.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: How do you get P(B > A) and the expected loss with no sampler?
  back: Draw from each arm's Beta posterior and compare. With 120/1000 against 140/1000, P(B > A) is 0.908 and the loss if you choose B is 0.00064 against 0.02058 for A.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: What were the Larkspur counts and what did the posteriors show?
  back: 2,079 of 42,141 on A (0.0493) and 2,335 of 41,859 on B (0.0558). The posteriors are two narrow peaks that barely overlap.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: What does the head of product get from the Larkspur posterior?
  back: The new checkout is better with probability above 0.9999, shipping a worse one costs 0.000001 pp in expectation, keeping A gives up 0.645 pp, and the lift clears half a point with probability 0.827 but a full point only 0.011.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: What three decision rules does the chapter compare?
  back: A probability threshold (P(B > A) above 0.95), an expected-loss threshold (below epsilon, the smallest difference you care about) and a credible interval that excludes 0.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: What does the choice of prior do on day one and on the whole test?
  back: On day one a flat prior reports +1.77 pp and P(B > A) 0.950, a Beta(500, 9500) prior reports +0.15 pp and 0.689. On the full test all three agree on the decision.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: How are the two stopping rules written in the simulation?
  back: The probability rule ships when the Normal cdf of d over sd is above 0.95. The loss rule ships when the Normal-approximate expected loss is below epsilon, 0.0005.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: How often does each stopping rule ship when B has no effect, costs half a point, or adds a point?
  back: 'Last day only: 0.047 / 0.000 / 0.987. Daily probability: 0.238 / 0.046 / 0.995. Daily expected loss: 0.589 / 0.143 / 1.000. Expected loss from day 14: 0.482 / 0.038 / 1.000.'
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: What does each row of the peeking table show?
  back: Checked once, the probability rule ships a no-effect change 4.7% of the time, checked daily 23.8%. The daily loss rule ships a harmful change 14.3% of the time. Waiting until day 14 cuts that to 3.8%.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: What is the stopping rule the chapter recommends?
  back: An expected-loss threshold, a minimum sample size set in advance, and full weeks. Do not call the test immune to peeking.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: Why does a frequentist stopping rule cost more than 5%, and what does it say about the Bayesian?
  back: A trial scheduled for 30 looks, with a peek at month 20, rejects a true null with probability 0.074, not 0.05. The posterior is untouched by the stopping rule, but that leniency holds only for a prior that reflects real experience.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: What are the raw ratio and the 5th percentile for 999/1, 60/40, 6/4 and 1/0?
  back: Raw 0.999, 0.600, 0.600, 1.000. The exact 5th percentile is 0.995, 0.517, 0.350 and 0.224. The Normal approximation is close except at the smallest count.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: How do seven star ratings become a lower bound?
  back: Map n stars out of 5 to n/5 and sum to S = 6.20 over seven ratings. The mean is 4.43 stars and the lower bound on the 0-1 scale is 0.591.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: How do two prompts with 19 of 20 and 170 of 200 passes compare on the lower bound?
  back: Prompt A has a raw rate 0.950 and a lower bound 0.810. Prompt B has 0.850 and 0.805. With 20 cases, 95% is about the same as 85% on 200.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: Which pitfalls of Bayesian A/B tests does the note list?
  back: Believing the test is immune to peeking, reading P(B > A) as the size of the win, using different priors per arm, a flat prior on day one, using P(B > A) when the change costs money, and ignoring novelty and guardrails.
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: Which losses are in the catalogue, and what does each punish?
  back: Squared (large errors, outlier-sensitive), asymmetric squared (underestimating), absolute (robust), zero-one (right or wrong), log loss (confident wrong probabilities), bounded, pundit and sign-sensitive.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Why might a forecast be biased on purpose?
  back: The forecaster minimises its own loss. The Weather Channel reports a 20% chance of rain when it believes 5 or 10%, since people notice a missed rain forecast more than a false alarm.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: What does minimising squared and absolute loss over a skewed posterior give?
  back: On a Gamma(2, 10) posterior, squared loss gives 20.03, the posterior mean, and absolute loss gives 16.85, the median. The mode is 10.00.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Which loss gives the mean, the median and the mode?
  back: Squared error gives the posterior mean, absolute error the median, and zero-one in the limit the mode, also called MAP.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: How does the zero-one best guess move as the miss width shrinks?
  back: Miss widths 5.0, 1.0 and 0.2 give best guesses 10.95, 9.60 and 9.30, moving toward the mode at 10.00 and getting noisier.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: What posterior mean does the showcase model give, and how does it compare with the closed form?
  back: Sampling gives a posterior mean of 20,000 (sd 3,677). The closed form gives 19,899 (sd 3,712). That is about $15,000 below the prior mean of 35,000.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: How is the showdown loss written?
  back: 'Underbid: lose the gap. Overbid: a fixed risk. Within 250 under: win both, a loss of minus twice the price.'
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: How does the best bid change as the cost of an overbid rises?
  back: From 14,700 at a risk of 30,000 down to 11,800 at 150,000, all well below the posterior mean of 20,000. The chance of overbidding falls from 0.070 to 0.013.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: What does Think Bayes add to the showcase problem?
  back: An empirical prior (a kernel density over 313 past prices) and a rival's record. A best guess of 20,000 moves the posterior mean to 25,096, and the optimal bids are 21,000 and 31,500.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: What does the sign-sensitive loss give for true +0.01 and predictions of -0.01, +0.03 and 0.00?
  back: 0.03, 0.02 and 0.01. The wrong-sign prediction costs most and making no call costs least. Squared error rates the first two equally.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: How does the Bayes action compare with least squares across signal values?
  back: Near a zero signal it is close to zero, and at the extremes it converges to the line. At +0.005 it is 0.0007 against 0.0017, at +0.050 it is 0.0228 against 0.0236. The slope is the same 0.487.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: What four steps did the winning Dark Worlds entry follow?
  back: A prior over halo positions, a likelihood from a physical model of galaxy ellipticities, a posterior by MCMC, and a Bayes action minimising the contest's own metric.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: How far was the posterior mean from the true halo on training sky 3?
  back: 31.15 pixels against 1,773.43 for a random guess, scores of 1.031 against 2.773. It is one guess on two skies, so an illustration and not a benchmark.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: What loss and Bayes action go with each analytics decision?
  back: 'Ship B or keep A: max(p_A - p_B, 0), ship if below epsilon. Inventory: an upper quantile. Fraud: the cost-balancing threshold. Price or bid: shade toward the safe side. Model selection: the business metric.'
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: What stock level minimises cost when running out costs five times a surplus unit?
  back: 46, the quantile 5/6 (0.833) of predictive demand. The cost is 15.26 at the mean and 9.92 at the Bayes action.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: At what fraud probability should you block, if a blocked good customer costs 2 and a missed fraud costs 80?
  back: When P(fraud) is above 2 / (2 + 80) = 0.024. At P = 0.03, blocking costs 1.94 and allowing costs 2.40. It relies on calibrated probabilities.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: What yearly gain does the Larkspur posterior imply for the redesign?
  back: A mean of $92,906 with a 95% interval of $49,559 to $136,395. Net of a $25,000 run cost, $67,906, and P(gain < run cost) is 0.001.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: How does the net of shipping change as the yearly cost rises?
  back: Net 67,906 at 25,000 (regret 0.001), 47,906 at 45,000 (0.015), 32,906 at 60,000 (0.069) and 2,906 at 90,000 (0.448, near a coin flip). The break-even is about $93,000.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: How does a posterior become a decision?
  back: Multiply the posterior of the lift by the business numbers, set that against the cost of each action to get the expected net per action, pick the largest and report the regret risk.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Which pitfalls of Bayesian decisions does the note list?
  back: Reporting the posterior mean by habit, using accuracy on asymmetric costs, treating the loss as objective, a smooth optimiser on a spiky loss, averaging outcomes before applying the loss, and forgetting predictive noise.
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Which inference method does each week of the coursework use?
  back: Week 2 uses EM on a Gaussian mixture, week 4 MCMC on logistic regression, week 5 variational inference on a VAE, and week 6 an exact GP posterior for Bayesian optimisation.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What are the steps of expectation-maximisation?
  back: Start from a guess, compute responsibilities in the E-step, re-fit the parameters from them in the M-step, and repeat until the lower bound on the log-likelihood plateaus.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What does each EM step compute?
  back: The E-step gives responsibilities proportional to the weight times the Normal density, normalised over clusters. The M-step sets the weights, means and covariances from those responsibilities.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: Why does the E-step work in log space?
  back: Multiplying small densities underflows, so the code adds logs and normalises with logaddexp, the log-sum-exp trick.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What happened across ten random restarts of EM?
  back: Eight restarts reached a log-likelihood of -1107.8 and two ended lower, at -1186.9 and -1268.1. The best fit recovered the weights 0.33, 0.5 and 0.17.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: How do EM and MCMC differ on the same model?
  back: EM gives a fast point estimate with no parameter uncertainty and fails on local optima and collapsing covariances. MCMC gives the full posterior, more slowly, and fails on slow mixing and label switching.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What did the three Alice and Bob starts give against the algebra?
  back: Alice averaged about 278 to 279 and Bob about 314 to 315 from every start. The algebra gives 278.6 and 314.3.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: Why check a model on simulated data with known truth?
  back: Simulation shows how far one dataset's estimate can sit from the truth. Here 2,000 simulated rows had a true odds ratio of 2.01, and NUTS gave 1.65 with a 95% interval of 1.27 to 2.12.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: How did Metropolis and NUTS compare on the same regression?
  back: From the same draws, Metropolis had a minimum ESS of 155 of 4,000 and a max r_hat of 1.041. NUTS had 3,306 and 1.001, about twenty times the effective samples.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: Which constraints make the Gaussian, binomial and Poisson the maximum entropy choice?
  back: Ten pebbles in five buckets make the flat arrangement 113,400 ways, with entropy log 5 = 1.609. The Gaussian is highest for a given variance, the binomial for two unordered outcomes with a constant mean, and the Poisson is its limit.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: How did McElreath check that the binomial has maximum entropy?
  back: Of 100,000 random distributions over two draws with expected value 1.4, the largest entropy found was 1.221728, against 1.221729 for the binomial with p = 0.7.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What are the two practical consequences of choosing a likelihood and link?
  back: A link keeps predictions in range, but no coefficient gives a constant change on the outcome scale. WAIC cannot compare models with different outcome distributions.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What did the Berkeley admissions model show with and without department?
  back: Pooled, men had an odds ratio of 1.84 (bm +0.61). With department intercepts the sign reversed to an odds ratio of 0.91 (bm -0.10), because women applied more to departments with low admission rates.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What did WAIC say about gender once department was in the model?
  back: The pooled model beat the intercept-only model by 91.5 WAIC points but fit each department badly. With department intercepts WAIC tied with and without gender, at 5200.9 and 5201.4.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What are the warnings about coefficients, separation and counts?
  back: A log-odds slope of 0.61 can move a probability only from 0.982 to 0.990. With near-perfect separation a flat-prior glm gave a slope of 11.43 with sd 2,955, against 4.02 under Normal(0, 10). Keep counts as counts.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: How does an ordered logit work?
  back: K categories get K-1 cutpoints on the log-cumulative-odds scale, and a linear predictor is subtracted from all of them at once. The book's interaction model had WAIC 36,929.4 against 37,090.3 for the additive one.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What are the intercept-only cutpoints on the trolley data, and are they recovered?
  back: They are the logit of the cumulative proportions. The logits are -1.92, -1.27, -0.72, 0.25, 0.89 and 1.77, and OrderedLogistic recovers -1.91, -1.26, -0.73, 0.23, 0.87 and 1.74.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What does a zero-inflated Poisson model, and how well did the re-run recover it?
  back: A zero comes from not working with probability p or from working and producing none, with likelihood p + (1 - p) exp(-lambda). Our seed 11 estimated 0.13 against 0.20 and 0.85 against 1.00.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: How does a beta-binomial handle over-dispersed counts?
  back: Each row gets its own probability from a Beta with mean pbar and concentration theta. On the Berkeley data without department the book has theta 2.77 (sd 0.96) and our re-run gives pbar 0.41 and theta 2.77 (sd 0.95).
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: How was the deviance simulation built?
  back: y is Normal with mean 0.15 x1 minus 0.4 x2, so the true model has three parameters. Models with one to five parameters are fitted by least squares and scored on a fresh sample of the same size.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: At which number of parameters is test deviance lowest?
  back: At three, the true model. At N = 20 the two-parameter model is worse out of sample than the one-parameter one, and the gap between test and train is close to twice the number of parameters.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What idea does the gap between test and train deviance give?
  back: The gap is close to twice the number of parameters, which is AIC = D_train + 2p. AIC is reliable only with flat priors, a near-Gaussian posterior and N much larger than the parameter count.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: How is WAIC computed?
  back: WAIC = -2(lppd - pWAIC). The lppd sums over observations the log of the average likelihood across draws, and pWAIC sums over observations the variance across draws of the log-likelihood.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: How accurate are DIC and WAIC, and what are their caveats?
  back: In the book's simulation both land within about 1 deviance point of the true average test deviance in most settings, WAIC the closer. They assume test data come from the training process, are hard for time series, and none is consistent for picking the true model.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What did the primate milk comparison show?
  back: The neocortex and log body mass model had WAIC -15.0 and an Akaike weight of 0.93, against -8.3 for the intercept-only model. The difference is 6.7 with a standard error of 7.26, and the ranking reverses with chance 0.18.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: Why can the better predictive model still be the wrong causal one?
  back: In a simulated plant experiment the model with a post-treatment variable, fungus, fits better and still hides a treatment slope of 1.07 behind an estimate of -0.27.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What are the two pitfalls of the first half?
  back: Using one EM start, since two of ten restarts ended in worse optima, and running the coursework on current packages, which no longer provide PyMC3, Theano, TF 1 or grader.
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What do weeks 5 and 6 and the final assignment cover?
  back: Week 5 is a VAE on MNIST with the ELBO, week 6 is Gaussian processes and Bayesian optimisation, and the final assignment, Finding the suspect, combines a VAE with Bayesian optimisation.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: What is the evidence lower bound?
  back: log p(x) is at least the expected log p(x given z) under q minus the KL from q(z given x) to the prior p(z). The gap is exactly the KL from q to the true posterior.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: What does the ELBO table show for x = 2 with x from N(z, 1) and z from N(0, 1)?
  back: The log evidence is -2.2655. From the prior the ELBO is -3.4199 with a gap of 1.1544, and at the exact posterior N(1, 0.71 squared) it is -2.2660 with a gap of 0.0005.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: What does the reparameterisation trick do?
  back: It writes z = m + s times epsilon with epsilon from N(0, 1), so the randomness no longer depends on what we differentiate. Forty noisy gradient steps reached the exact mean of 1.000.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: Which algorithms do Blei et al. centre, and where does the trick belong?
  back: Their main algorithm is coordinate ascent (CAVI), which updates one factor of q at a time, plus a stochastic version (SVI) for large data. The reparameterisation trick is the VAE's route.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: What was the setup of the ADVI against NUTS comparison?
  back: Two inputs with correlation 0.95 and true coefficients of 1 each, 80 points. The posterior over the two coefficients is a narrow diagonal ridge.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: How did ADVI's standard deviations compare with NUTS's?
  back: Marginal sds were about 0.39 under NUTS and 0.13 under ADVI, threefold too narrow. The sd of a + b was 0.181 against 0.113, and the correlation -0.96 became -0.01.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: What does a mean-field approximation look like against a correlated posterior?
  back: The exact posterior is a tilted ellipse, and the mean-field approximation is too narrow because it misses the correlation.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: What do Blei et al. say about VI against MCMC, and its limits?
  back: The relative accuracy 'is still unknown'. CAVI fit a 30-cluster mixture to 10,000 images in under a minute but it was 'not a definitive comparison'. The ELBO is non-convex, and choosing a model by it is 'not justified in theory'.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: What are the parts of a VAE?
  back: An encoder gives the mean and log-variance of q, reparameterisation lets gradients flow through the sampling, a decoder gives p(x given z), and the prior is N(0, I). A conditional VAE adds the label.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: What makes a VAE amortised?
  back: ADVI fits one q per model, while a VAE fits one encoder that outputs a q per data point. That is why a VAE can handle a new image without refitting.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: What defines a Gaussian process?
  back: Any finite set of function values is jointly Normal, with covariance given by a kernel such as the RBF, k(x, x') = sigma squared times exp(-distance squared over 2 ell squared).
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: How is the GP posterior computed by hand?
  back: Build the kernel matrix K for the observed points, solve for alpha, and take the mean as Ks times alpha and the variance as the prior variance minus the explained part.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: How does the GP's sd change across x?
  back: At an observed point the sd is effectively zero. Between points it grows, and at x = 6 the mean drifts to the prior's 0 and the sd reaches 0.987, nearly the prior's own.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: How does Bayesian optimisation use a GP?
  back: The GP is a cheap surrogate for an expensive black-box function. An acquisition function turns its mean and uncertainty into the next point to evaluate, trading exploration against exploitation.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: What does each acquisition function pick?
  back: Expected improvement picks the largest expected gain over the best so far, the upper confidence bound the highest mean plus kappa times the sd, and probability of improvement the highest chance of beating the best.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: What does the expected-improvement curve show?
  back: The top panel is a GP through four observations with its mean and uncertainty band. The bottom panel is the expected improvement over the same range, peaking near 7.7, the next point to evaluate.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: How was the Bayesian optimisation loop run on the gradient-boosted model?
  back: It tuned the learning rate and leaf count on a small built-in dataset, four starting fits then expected improvement over 2,000 random candidates each round, 20 fits in all.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: How did Bayesian optimisation compare with random search on log loss?
  back: Best log loss after 4, 8, 12 and 20 fits was 0.1148, 0.1065, 0.1065 and 0.1016, against a random-search average of 0.1233, 0.1193, 0.1164 and 0.1120.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: Why is the Bayesian optimisation result not a measured advantage?
  back: It is one Bayesian optimisation run against five random runs, on a dataset where each evaluation takes about a second. It shows the shape of the method, and the case grows as each fit gets more expensive.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: What does the final project combine?
  back: Train a VAE on faces, then run Bayesian optimisation over its latent space with a human rating each generated face, to converge on a target face in a few dozen evaluations.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: Which pitfalls does the note list for VI, GPs and the coursework?
  back: Quoting mean-field intervals, ranking models by ELBO, a GP on large n, Bayesian optimisation on cheap fits, and running the coursework on current packages.
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: What are the three ways to estimate one number per group?
  back: No pooling uses the market's own mean, complete pooling gives every market the overall mean, and partial pooling takes a weighted average of the two.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What weight does a market with n users put on its own mean?
  back: tau squared divided by tau squared plus sigma squared over n. Tau is the sd of true market means and sigma the sd of users within a market.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How does the chapter produce the three estimates?
  back: It simulates 40 markets of very different sizes, fits a random-intercept MixedLM with REML, and compares the group means, the overall mean and the fitted values.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How far did the five-user and the 262-user market move?
  back: The five-user market measured 54.26 against a true 45.39, with weight 0.16, so the model pulled it to 42.10. The 262-user market has weight 0.91 and barely moves.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What does the shrinkage plot show against market size?
  back: Each market's own mean and its partially pooled estimate. The smallest markets move up to about 12 dollars towards the overall mean, and the largest barely move.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Which method has the lowest RMSE in each size band?
  back: 'Partial pooling, in all of them: 3.54 overall against 5.69 and 5.47. For small markets complete pooling is close (4.61), and for large markets no pooling is (2.31).'
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How did partial pooling do over 200 new datasets?
  back: RMSE was 3.47 against 5.13 for no pooling and 5.98 for complete pooling. It beat no pooling in 96% of datasets and complete pooling in 100%.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How do the design effects from different market sizes compare?
  back: The mean size of 56 gives 2.98, the user-weighted size of 104 gives 4.74, close to the exact 4.95. The clustered SE from this one dataset implies 3.85.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What is the difference between a random intercept and a random slope?
  back: A random intercept gives each group its own level. A random slope also gives each group its own effect of a predictor.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Why do the four fits share one estimate but not one standard error?
  back: The panel is balanced, so the estimate is 1.300 in all four. Naive OLS gives 0.296 because week varies only within a user, random intercepts alone say 0.222, and random slopes (0.276) and clustered OLS (0.277) agree.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How does the PyMC model draw each user's level and trend?
  back: It draws a correlated pair from an LKJ prior on the covariance, in the non-centred form, then adds each user's level and trend to the fixed effects.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How close are MixedLM and PyMC on the first run?
  back: Every parameter matches within 0.03 and each user's trend correlates at 1.000. Pooling cuts the error on each user's trend from 2.27 to 1.30.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What happens when the true slope spread falls from 2.5 to 1.0?
  back: The fixed effects still agree, but MixedLM reports a slope sd of 0.46 and a correlation of 1.00 with no warning. PyMC gives 0.68 and 0.28 with a 90% interval of -0.27 to 0.79.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Which tool answers which question?
  back: Clustered SEs for a population average with groups as a nuisance, fixed effects for a within-group effect that may correlate with the predictor, and a multilevel model when the group estimates themselves matter.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What did the four estimators give when the market effect was related to the discount?
  back: Pooled OLS gave 3.04 and random intercepts 2.83, both wrong for a true 2. Fixed effects and within-between stayed at 1.99. In the unrelated case all four were centred on 2.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What does each of the three papers add to the choice of tool?
  back: 'Bell and Jones: split the predictor into a group mean and a deviation, and the within coefficient equals fixed effects. McNeish et al.: clustered SEs or GEE are simpler when you only need clustering. Cameron and Miller: cluster anyway.'
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How does the chapter make thousands of replications cheap and still trust them?
  back: Given tau the normal model has a closed form, so a grid over tau replaces sampling. PyMC checks one dataset, and the largest gap in a segment's mean is 0.014.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What did 1,000 simulated experiments show?
  back: RMSE fell from 1.357 to 0.489. The winner's estimate minus its true lift was +2.93 per segment and +0.09 pooled. The segment picked had a true lift of 1.46 pooled against 1.26, and 1.98 for the truly best.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How do Bonferroni and partial pooling differ, and what did Gelman, Hill and Yajima find?
  back: Bonferroni keeps estimates where they are and widens intervals, while pooling moves estimates towards each other, more for uncertain ones. In the eight-schools simulation the classical analysis called 7% significant with 63% in the right direction, the Bayesian 0.5% with 89%.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Why is the segment simulation close to a best case?
  back: The segments are exchangeable by construction, meaning nothing known distinguishes them in advance, and the prior on tau suits the truth.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How much does pooling help under each setting?
  back: The ratio of pooled to raw RMSE is 0.36 at baseline, 0.16 with no real differences, 0.93 and 0.99 when well measured, and 0.55 with only 4 segments.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: In which scenarios did pooled RMSE exceed per-segment RMSE?
  back: A true outlier and a too-tight prior on four segments, both at a ratio of 1.25. The ratio is 0.16 with no differences and 0.93 and 0.99 when well measured.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What are the three cases where pooling does not help?
  back: A real outlier is pulled down by 3.74, RMSE rising from 3.01 to 3.76. A wrong common centre biases small segments by -1.10, fixed by adding size as a predictor. Well-measured segments gain nothing.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Why compare the posterior of the difference, not the intervals?
  back: The two marginal posteriors of the ruggedness slope overlap, yet the probability that the African slope is the smaller is 0.0036.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How wide is the REML estimate of tau by number of markets?
  back: With 3 markets the 5th to 95th percentile runs from 0 to 15.53 and 11% land at zero. With 50 markets it runs from 4.67 to 7.34.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What does the few-groups plot show?
  back: The distribution of REML estimates of the between-market sd by number of markets. With 3 markets it runs from 0 to 15.5, with 50 markets from 4.7 to 7.3, against a true 6.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How do three priors compare over many datasets with 4 segments?
  back: A half-normal(0.25) prior when tau is really 2 gives a ratio of 1.25 and 48% coverage. Half-normal(2) gives 0.55 and 0.85, so pooling still beats raw with a sensible prior.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How do MixedLM and PyMC report tau for five markets?
  back: MixedLM gives 2.52 as a single number and treats it as known. PyMC gives a mean of 3.91 with a 90% interval from 0.37 to 9.74, and a posterior sd of 2.54 for the grand mean.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What did McElreath's 60 simulated ponds show?
  back: Partial pooling has the lower average error at every size of pond, and the gap is widest for the 5-tadpole ponds.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What caveat did Gelman add to the 2012 paper?
  back: Gelman and Loken wrote that with few comparisons or a highly structured problem, inference can be sensitive to model assumptions. Pooling also analyses only the comparisons you put in the model.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How is the conversion model set up?
  back: Each of 30 markets has its own base rate and its own lift on the log-odds scale, in the non-centred form, with binomial counts for control and treated.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How much did pooling cut the conversion errors?
  back: The lift RMSE fell from 1.01 to 0.68 points and the control rate RMSE from 0.83 to 0.71. Both methods picked the same winner and understated it, +5.28 and +5.09 against a true +6.42.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What is the difference between the two kinds of logit coefficient?
  back: A multilevel coefficient is a change within a market, and a pooled logit with clustered SEs describes a change across the population. With a common outcome and a large market spread, 0.500 within a market became 0.306 across the population.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Why do the typical-market rate and the average rate differ?
  back: The rate for a typical market, invlogit(alpha), is 4.89%, but the average across markets is 6.71%, because high-rate markets pull up the mean on the probability scale.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What are the pitfalls in choosing and fitting a multilevel model?
  back: Shipping the raw winner, fitting a multilevel model only to handle clustering, plain random intercepts when the group effect correlates with the predictor, random intercepts when slopes vary, and trusting a boundary estimate.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What are the pitfalls with priors, scale and diagnostics?
  back: Pooling few groups with one prior, pooling groups known to differ, expecting pooling to find the rare winner, reading logit coefficients across model types, and skipping diagnostics.
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: How is WAIC computed in the chapter?
  back: From the pointwise log-likelihood, using logsumexp for the lppd and the variance across draws for pWAIC, because ArviZ 1.x has no az.waic.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: How did pWAIC change between the two models?
  back: 48 free intercepts cost 48.3 effective parameters, and the multilevel model dropped that to 36.9 and improved WAIC by 9.6. The learned sigma was 1.39 against a true 1.6.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What three details matter when reading pWAIC for a multilevel model?
  back: The unit, since the aggregated binomial rows gave pWAIC 22.7 for the same model. The sigma prior, where Exponential(1) is suggested for around five clusters. And a new cluster is predicted with a fresh Normal(a, sigma) draw.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What is McElreath's cafe example?
  back: Morning wait averages 3.5 minutes and the afternoon change averages -1, with sds of 1 and 0.5 and a correlation of -0.7. Busy cafes with long mornings have more to gain.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: How do the centred and non-centred cafe models differ in code?
  back: The non-centred form draws a standard normal z and computes mu plus z times the Cholesky factor. The centred form draws the pair directly from MvNormal.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What did the cafe re-run show?
  back: The correlation posterior mean was -0.42 for a true -0.7, with a 89% interval of -0.74 to -0.03. RMSE fell from 0.233 to 0.192 on intercepts and 0.316 to 0.253 on slopes.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What does McElreath's figure of two-dimensional shrinkage show?
  back: A cafe with an average intercept and an unusually high slope is pulled down on the slope, and because the two are negatively correlated that also moves its intercept, hence the angled lines.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: Which model had the lowest WAIC for UC Berkeley admissions?
  back: The varying-slopes model, at WAIC 5191.4 with weight 0.99, against 5201.2 and 5201.9, even though the average gender slope is near zero.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What is non-centring?
  back: Draw standard-normal z and compute mu plus L z, where L is the Cholesky factor of the covariance, so the sampler explores z instead of a funnel.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: How did centred and non-centred forms compare?
  back: With 20 cafes of 10 visits both were fine, though non-centring had the lower ESS, 811 against 1,210. With 30 cafes seen twice, centred gave 203 divergences and ESS 25, and non-centred 8 divergences and ESS 270.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What are the two costs of treating noisy segment rates as exact?
  back: A noisy outcome is handled by regression anyway, but a noisy predictor attenuates the slope toward zero. In McElreath's states data the slope is -0.55 with the divorce error modelled, roughly half the version that ignores it.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: How does the measurement-error model treat the true values?
  back: The true x and y are parameters, y comes from the regression line around the true x, and each observation is Normal around its true value with its known standard error.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What did the naive and measurement-error models give for a true slope of 1.0?
  back: Ignoring the error gave 0.81 (sd 0.14) with no divergences. Modelling it gave 0.94 (sd 0.10) with 9 divergences.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What do the two panels of McElreath's measurement-error figure show?
  back: The left panel is shrinkage again, with states of larger standard error moving further. The right panel shows the fitted line moving as well, gray without error and blue with it, with a wider band.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What does deleting incomplete rows cost, and what is the Bayesian alternative?
  back: McElreath's primate data keeps 17 of 29 species and drops 12 good mass and energy values. The fix treats each missing value as a parameter with a prior, and a model for the predictor does the imputing.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: How does the code impute a missing predictor?
  back: It passes the predictor as observed data with NaN where values are missing, models it on body mass, and PyMC imputes the NaNs.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What did the three treatments of the missing predictor give?
  back: Complete cases gave 0.49 (sd 0.31), imputing with no link to mass gave 0.26 (sd 0.22), and letting the predictor depend on mass gave 0.41 (sd 0.26), against a true 0.50.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What are the pitfalls of counting parameters, slopes and thin data?
  back: Counting parameters by model size, comparing WAIC across likelihoods, fitting slopes and intercepts as independent, reading the correlation posterior as a measurement, and the centred form with thin data.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What are the pitfalls of non-centring, noisy predictors and missing data?
  back: Believing non-centring always cures divergences, treating a noisy predictor as exact, imputing with a mean-only model, and dropping incomplete rows silently.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What are the three habits this lecture builds?
  back: Partially pool many segment effects before reading a winner, run several priors and report the range when groups are few, and give measurement error and missingness a model rather than averaging or deleting.
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: State Bayes' theorem in words
  back: Posterior is proportional to likelihood times prior; the evidence P(X) only normalises it
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: Credible vs confidence interval?
  back: 'Credible: probability the parameter lies inside, given model and data. Confidence: the procedure covers the true value 95% of the time across repeats'
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What is a conjugate prior?
  back: A prior whose posterior is in the same family, such as Beta for Binomial, so the update is closed-form
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: MLE vs MAP vs posterior mean?
  back: MLE maximises the likelihood; MAP maximises the posterior; the mean averages over it. MAP equals MLE under a flat prior
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: When do Bayesian and frequentist answers agree?
  back: 'Large N with a prior that does not exclude the truth: the likelihood dominates'
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: What is a posterior predictive check?
  back: Simulate data from the fitted model and compare with real data on a quantity of interest
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: Why does the prior not make it all subjective?
  back: It is stated and can be challenged, it fades with data, and any frequentist procedure also makes choices, less visibly
  lesson: data-analytics/04-bayesian-analysis/notes/01-bayesian-inference
- front: Why can't two marginals recreate a joint?
  back: The dependence between the variables is lost; conditionals recover it
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What does a grid cost in d dimensions?
  back: n^d evaluations; a million hypotheses is 1,000 in 2-D, 100 in 3-D, 10 in 6-D
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: How is a Bayes factor for a composite hypothesis computed?
  back: The prior-weighted average likelihood, which `Update` returns as its normalising constant
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: Why can a Bayes factor of 3 be a weak result?
  back: 1:1 prior odds become 3:1, a move from 50% to 75%, small against modelling error
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What is a nuisance parameter?
  back: Something you must estimate to answer the question but do not care about; average it out
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: When do you simulate instead of writing a likelihood?
  back: When the forward model is cheap and the likelihood is not; condition the simulated joint
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: Why a Dirichlet and not independent Betas?
  back: Prevalences must sum to one, so the posterior means do too
  lesson: data-analytics/04-bayesian-analysis/notes/01b-grids-hypotheses-and-simulation
- front: What does MCMC produce?
  back: Correlated samples whose long-run distribution is the posterior; summaries are averages over them
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: Why does Metropolis not need the normalising constant?
  back: Acceptance uses a ratio of densities, so P(X) cancels
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What is R-hat?
  back: Compares between-chain and within-chain variance; near 1 means chains agree. It does not prove they found the whole posterior
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What is effective sample size?
  back: The number of independent draws with the same information as your correlated ones
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: Why NUTS over Metropolis?
  back: Gradients give distant moves that are still accepted, so far less autocorrelation. It needs no hand-tuning, but cannot handle discrete variables directly
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What is a divergence?
  back: The numerical integrator failed, usually on sharp curvature. The sampler cannot explore that region, so estimates can be biased
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What is a non-centred parameterisation?
  back: Sampling a standard Normal and scaling it, which removes the funnel between a hierarchical scale and its group effects
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: What is label switching?
  back: Symmetric mixture components swap identities across chains; fix with an order constraint or informative priors
  lesson: data-analytics/04-bayesian-analysis/notes/02-mcmc-and-pymc
- front: Is a flat prior uninformative?
  back: Only on the scale it is flat on. A uniform p is a bell shape on log-odds
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: What is a weakly informative prior?
  back: One that rules out absurd values and otherwise lets the data speak, such as Gelman's Cauchy(0, 2.5) on scaled inputs
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How do you check a prior?
  back: 'Prior predictive simulation: generate outcomes and ask if they are believable'
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How does ridge relate to Bayes?
  back: Ridge is the MAP under Normal priors; lasso is the MAP under Laplace priors. λ is the prior precision
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: Does a Laplace prior give sparsity?
  back: Only at the MAP. Posterior draws are not zero
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: What is the winner's curse?
  back: Selecting on significance inflates reported effects. Shrinking toward a prior fit across experiments removes most of it
  lesson: data-analytics/04-bayesian-analysis/notes/03-priors-and-bandits
- front: How does Thompson sampling work?
  back: Draw from each arm's posterior, pull the highest draw, and update. Uncertainty drives exploration
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: What is regret, and what is the bound?
  back: The cumulative gap to the best arm. Lai and Robbins' lower bound is logarithmic in T
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: Why not always use a bandit?
  back: Adaptive allocation biases effect estimates, and it is poorly suited to long-term and guardrail metrics
  lesson: data-analytics/04-bayesian-analysis/notes/03b-bandits-and-thompson-sampling
- front: How do you compute P(B > A)?
  back: Sample from each arm's Beta posterior and take the share of draws where B wins, or use the finite sum
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: What is expected loss?
  back: 'E[max(p_A − p_B, 0)]: the average you give up by shipping B, counting worlds where A was better'
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: Is a Bayesian test safe to peek at?
  back: Not with a probability threshold. An expected-loss rule stops for a different reason, and it still needs a minimum sample size
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: Why does the expected-loss rule ship null changes often?
  back: Shipping a no-effect change costs nothing, so the rule has no reason to resist. The harmful-change rate is the thing to check
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: Do Bayesian and frequentist intervals disagree?
  back: With large N and a flat prior they are numerically close. The difference is the interpretation
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: How do priors matter in an A/B test?
  back: Most at the start; they tame early noise and wash out with traffic. Use the same one on each arm
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: How would you rank products with few ratings?
  back: Sort by a lower credible bound of the posterior, not the raw mean
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: How would you compare prompts on eval suites of different sizes?
  back: Lower credible bound of the pass rate, or better, the same suite on both
  lesson: data-analytics/04-bayesian-analysis/notes/04-bayesian-ab-testing
- front: What is a Bayes action?
  back: The action minimising posterior expected loss
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: Which loss gives the mean, median and mode?
  back: Squared, absolute and zero-one in the limit
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: How do you find it for a custom loss?
  back: Compute the loss over posterior samples, average, minimise, by grid if it is spiky
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: How do you set a classification threshold from costs?
  back: Flag when P(positive) > cost_FP / (cost_FP + cost_FN)
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: What is the newsvendor quantile?
  back: short / (short + over) of the predictive distribution
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: What does `pm.Potential` do?
  back: Adds any term to the model's log posterior
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: How would you state a ship decision?
  back: Expected net value with its uncertainty, and the regret risk across plausible costs
  lesson: data-analytics/04-bayesian-analysis/notes/05-loss-functions-and-decisions
- front: What does EM do?
  back: Alternates between computing responsibilities and re-fitting parameters; the likelihood never falls, but it finds a local optimum
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: EM or MCMC for a mixture?
  back: EM for a fast point estimate; MCMC when you need parameter uncertainty
  lesson: data-analytics/04-bayesian-analysis/notes/06-bayesian-machine-learning
- front: What is the ELBO?
  back: 'A lower bound on log evidence: reconstruction minus KL from the prior. The gap to log evidence is the KL to the true posterior'
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: Why the reparameterisation trick?
  back: It moves the randomness out of the parameters so gradients can pass through sampling
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: VI or MCMC?
  back: VI scales and is fast, and it tends to underestimate variance. MCMC is slower and asymptotically exact
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: What is a Gaussian process?
  back: A distribution over functions where any finite set of values is jointly Normal; a kernel sets the covariance
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: What does an acquisition function do?
  back: Turns a surrogate's mean and uncertainty into the next point to try, trading exploration against exploitation
  lesson: data-analytics/04-bayesian-analysis/notes/06b-variational-inference-and-gaussian-processes
- front: What is partial pooling?
  back: Each group's estimate is a weighted average of its own mean and the overall mean, with weights set by its noise and the estimated between-group spread
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What is the weight?
  back: τ² / (τ² + σ²/n). More users or more real spread means more weight on the group's own mean
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What is the ICC?
  back: The share of variance between groups, τ² / (τ² + σ²). It feeds the design effect 1 + (m − 1)ρ, so even a small ICC inflates variance a lot with large clusters
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Clustered SEs, fixed effects or multilevel?
  back: Clustered when groups are a nuisance and the effect is a population average, fixed effects when the group effect may correlate with the predictor, multilevel when group estimates are the question
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Can random effects do what fixed effects do?
  back: Yes, if you split the predictor into a group mean and a deviation. The within coefficient then equals fixed effects (Bell and Jones)
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Why does a segment winner look too good?
  back: It was selected for being high, so it holds positive noise. Pooling removes most of that, and in this chapter's simulation the overstatement fell from 2.93 to 0.09
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Does partial pooling replace Bonferroni?
  back: It moves estimates rather than widening intervals, and GHY argue for it. It still depends on the model, particularly with few or structured comparisons, and Gelman says so too
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: When does it not help?
  back: Well-measured groups, a true outlier, groups known to differ with no predictor for that, and questions only about the overall average
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What goes wrong with few groups?
  back: τ is barely estimated, the REML fit can hit zero, and the prior decides the answer
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Why not `MixedLM` for conversion?
  back: It is linear only. Use a logit multilevel model in PyMC, and be clear whether you report a within-market or a population-averaged effect
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: What does "hierarchical regression" mean in psychology?
  back: Often adding blocks of predictors in stages, which has nothing to do with nested data
  lesson: data-analytics/04-bayesian-analysis/notes/07-multilevel-models-and-partial-pooling
- front: Why does a multilevel model have fewer effective parameters than actual ones?
  back: The varying effects share a learned sigma, so they are not free. pWAIC fell from 48.3 to 36.9 on 48 simulated tanks
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: Why model intercepts and slopes together?
  back: They can covary, and a shrunk slope shifts its intercept. Shrinkage then runs at an angle, not straight to the centre
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: Does it always fix divergences?
  back: No. With thin data it cut 203 to 8 here, and the centred form is fine with plenty of data
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What does ignoring predictor error do?
  back: Attenuates the slope. 0.81 against a true 1.0 here
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: How do you handle a missing predictor?
  back: Give it a prior and a model on the other covariates, and let the model impute. Complete-case analysis is the alternative, at the cost of rows
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: What does imputation assume?
  back: That values are missing at random given what the model sees. Not-at-random missingness needs a model of the missingness
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
- front: Why not compare WAIC for a beta-binomial and a binomial?
  back: WAIC is pointwise and the beta-binomial's latent row-level parameter ties it to the aggregation
  lesson: data-analytics/04-bayesian-analysis/notes/07b-varying-slopes-measurement-error-and-missing-data
---
